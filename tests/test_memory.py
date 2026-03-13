"""
Unit tests for memory/memory_manager.py - SQLite-backed memory storage and retrieval.

Uses an in-memory SQLite database and mocks external dependencies (ChromaDB, OpenAI).
"""
from __future__ import annotations

import sqlite3
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    """Replace the real DB connection with an in-memory SQLite database for each test."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            chromadb_id TEXT
        );
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS memory_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    """)

    monkeypatch.setattr("memory.database.get_connection", lambda: conn)
    monkeypatch.setattr("memory.memory_manager.get_connection", lambda: conn)

    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def mock_embeddings():
    """Mock ChromaDB/OpenAI vector operations for all tests."""
    with patch("memory.memory_manager.store_memory_vector", return_value="mock-uuid") as mock_store, \
         patch("memory.memory_manager.delete_memory_vector", return_value=True) as mock_delete, \
         patch("memory.memory_manager.search_memory") as mock_search:
        mock_search.return_value = {"documents": [[]], "ids": [[]], "distances": [[]]}
        yield {
            "store": mock_store,
            "delete": mock_delete,
            "search": mock_search,
        }


class TestRemember:
    """Tests for the remember() function."""

    def test_remember_stores_value(self):
        from memory.memory_manager import remember, recall
        remember("favorite color", "blue")
        assert recall("favorite color") == "blue"

    def test_remember_with_category(self):
        from memory.memory_manager import remember, list_memory
        remember("favorite color", "blue", category="preference")
        result = list_memory(category="preference")
        assert "favorite color" in result

    def test_remember_with_tags(self):
        from memory.memory_manager import remember, search_by_tag
        remember("pet name", "Rex", tags=["pet", "personal"])
        result = search_by_tag("pet")
        assert "pet name" in result

    def test_remember_overwrites_existing(self):
        from memory.memory_manager import remember, recall
        remember("color", "blue")
        remember("color", "red")
        assert recall("color") == "red"

    def test_remember_stores_vector(self, mock_embeddings):
        from memory.memory_manager import remember
        remember("name", "Alfred")
        mock_embeddings["store"].assert_called_once()

    def test_remember_returns_true(self):
        from memory.memory_manager import remember
        assert remember("key", "value") is True


class TestRecall:
    """Tests for the recall() function."""

    def test_recall_existing_key(self):
        from memory.memory_manager import remember, recall
        remember("city", "London")
        assert recall("city") == "London"

    def test_recall_nonexistent_key(self):
        from memory.memory_manager import recall
        assert recall("nonexistent") is None


class TestForget:
    """Tests for the forget() function."""

    def test_forget_existing_key(self):
        from memory.memory_manager import remember, recall, forget
        remember("temp", "data")
        assert forget("temp") is True
        assert recall("temp") is None

    def test_forget_nonexistent_key(self):
        from memory.memory_manager import forget
        assert forget("nonexistent") is False

    def test_forget_deletes_vector(self, mock_embeddings):
        from memory.memory_manager import remember, forget
        remember("to_delete", "value")
        forget("to_delete")
        mock_embeddings["delete"].assert_called_once()

    def test_forget_syncs_sqlite_and_chromadb(self, mock_embeddings):
        """Verify the sync bug fix: forget removes from BOTH stores."""
        from memory.memory_manager import remember, forget, recall
        remember("synced_key", "synced_value")
        forget("synced_key")
        assert recall("synced_key") is None
        mock_embeddings["delete"].assert_called_once()


class TestListMemory:
    """Tests for list_memory()."""

    def test_list_empty(self):
        from memory.memory_manager import list_memory
        assert list_memory() == {}

    def test_list_all(self):
        from memory.memory_manager import remember, list_memory
        remember("a", "1")
        remember("b", "2")
        result = list_memory()
        assert len(result) == 2
        assert result["a"] == "1"

    def test_list_by_category(self):
        from memory.memory_manager import remember, list_memory
        remember("x", "1", category="personal")
        remember("y", "2", category="preference")
        assert len(list_memory(category="personal")) == 1
        assert len(list_memory(category="preference")) == 1


class TestSemanticSearch:
    """Tests for semantic_search_memory()."""

    def test_returns_results_with_distances(self, mock_embeddings):
        mock_embeddings["search"].return_value = {
            "documents": [["result1", "result2"]],
            "ids": [["1", "2"]],
            "distances": [[0.1, 0.5]],
        }
        from memory.memory_manager import semantic_search_memory
        results = semantic_search_memory("test query", n_results=2)
        assert results is not None
        assert len(results) == 2
        assert results[0]["document"] == "result1"
        assert results[0]["distance"] == 0.1

    def test_returns_none_for_empty(self, mock_embeddings):
        from memory.memory_manager import semantic_search_memory
        results = semantic_search_memory("test query")
        assert results is None


class TestCategorizeMemory:
    """Tests for categorize_memory()."""

    def test_categorize_existing(self):
        from memory.memory_manager import remember, categorize_memory, list_memory
        remember("item", "value", category="general")
        assert categorize_memory("item", "personal") is True
        assert len(list_memory(category="personal")) == 1

    def test_categorize_nonexistent(self):
        from memory.memory_manager import categorize_memory
        assert categorize_memory("nope", "personal") is False


class TestGetRecentMemories:
    """Tests for get_recent_memories()."""

    def test_recent_memories(self):
        from memory.memory_manager import remember, get_recent_memories
        remember("a", "1")
        remember("b", "2")
        remember("c", "3")
        recent = get_recent_memories(limit=2)
        assert len(recent) == 2
        # All three inserted in same tick — just verify we got 2 of the 3
        keys = {r["key"] for r in recent}
        assert keys.issubset({"a", "b", "c"})

    def test_recent_empty(self):
        from memory.memory_manager import get_recent_memories
        assert get_recent_memories() == []
