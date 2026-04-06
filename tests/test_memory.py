"""
Unit tests for memory/memory_manager.py - Supabase-backed memory storage and retrieval.

Mocks the Supabase client and OpenAI embedding generation to run in isolation.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _mock_execute(data=None):
    """Helper to create a mock Supabase execute() response."""
    result = MagicMock()
    result.data = data or []
    return result


@pytest.fixture(autouse=True)
def mock_supabase():
    """Mock Supabase client for all tests."""
    mock_sb = MagicMock()

    # Default: upsert/insert/update/delete return success
    mock_sb.table.return_value.upsert.return_value.execute.return_value = _mock_execute([{"key": "k"}])
    mock_sb.table.return_value.select.return_value.eq.return_value.execute.return_value = _mock_execute()
    mock_sb.table.return_value.delete.return_value.eq.return_value.execute.return_value = _mock_execute()
    mock_sb.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = (
        _mock_execute()
    )
    mock_sb.table.return_value.select.return_value.order.return_value.execute.return_value = _mock_execute()
    mock_sb.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
        _mock_execute()
    )
    mock_sb.table.return_value.select.return_value.ilike.return_value.order.return_value.execute.return_value = (
        _mock_execute()
    )
    mock_sb.table.return_value.update.return_value.eq.return_value.execute.return_value = _mock_execute()

    with (
        patch("memory.memory_manager.get_supabase", return_value=mock_sb),
        patch("memory.memory_manager.generate_embedding", return_value=[0.1] * 1536),
    ):
        yield mock_sb


class TestRemember:
    """Tests for the remember() function."""

    def test_remember_calls_upsert(self, mock_supabase):
        from memory.memory_manager import remember

        result = remember("color", "blue")
        assert result is True
        mock_supabase.table.assert_called_with("memories")
        mock_supabase.table.return_value.upsert.assert_called_once()

    def test_remember_includes_embedding(self, mock_supabase):
        from memory.memory_manager import remember

        remember("color", "blue")
        upsert_call = mock_supabase.table.return_value.upsert.call_args
        row = upsert_call[0][0]
        assert "embedding" in row
        assert len(row["embedding"]) == 1536

    def test_remember_with_category(self, mock_supabase):
        from memory.memory_manager import remember

        remember("color", "blue", category="preference")
        upsert_call = mock_supabase.table.return_value.upsert.call_args
        row = upsert_call[0][0]
        assert row["category"] == "preference"

    def test_remember_with_tags(self, mock_supabase):
        from memory.memory_manager import remember

        remember("pet", "Rex", tags=["animal", "personal"])
        upsert_call = mock_supabase.table.return_value.upsert.call_args
        row = upsert_call[0][0]
        assert row["tags"] == "animal,personal"

    def test_remember_sets_iso_updated_at(self, mock_supabase):
        from memory.memory_manager import remember

        remember("color", "blue")
        upsert_call = mock_supabase.table.return_value.upsert.call_args
        row = upsert_call[0][0]
        assert row["updated_at"] != "now()"
        parsed = datetime.fromisoformat(row["updated_at"])
        assert parsed.tzinfo is not None

    def test_remember_returns_true(self):
        from memory.memory_manager import remember

        assert remember("key", "value") is True

    def test_remember_handles_embedding_failure(self, mock_supabase):
        """Should still store the memory even if embedding generation fails."""
        with patch("memory.memory_manager.generate_embedding", side_effect=Exception("API down")):
            from memory.memory_manager import remember

            result = remember("key", "value")
            assert result is True
            upsert_call = mock_supabase.table.return_value.upsert.call_args
            row = upsert_call[0][0]
            assert "embedding" not in row


class TestRecall:
    """Tests for the recall() function."""

    def test_recall_existing_key(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = _mock_execute(
            [{"value": "blue"}]
        )
        from memory.memory_manager import recall

        assert recall("color") == "blue"

    def test_recall_nonexistent_key(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import recall

        assert recall("nonexistent") is None


class TestForget:
    """Tests for the forget() function."""

    def test_forget_existing_key(self, mock_supabase):
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = _mock_execute(
            [{"key": "color"}]
        )
        from memory.memory_manager import forget

        assert forget("color") is True

    def test_forget_nonexistent_key(self, mock_supabase):
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import forget

        assert forget("nonexistent") is False

    def test_forget_deletes_row_with_embedding(self, mock_supabase):
        """No separate vector deletion needed — embedding is on the same row."""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = _mock_execute(
            [{"key": "color"}]
        )
        from memory.memory_manager import forget

        forget("color")
        mock_supabase.table.return_value.delete.assert_called_once()


class TestListMemory:
    """Tests for list_memory()."""

    def test_list_empty(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import list_memory

        assert list_memory() == {}

    def test_list_all(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.order.return_value.execute.return_value = _mock_execute(
            [{"key": "a", "value": "1"}, {"key": "b", "value": "2"}]
        )
        from memory.memory_manager import list_memory

        result = list_memory()
        assert result == {"a": "1", "b": "2"}

    def test_list_by_category(self, mock_supabase):
        mock_supabase.table.return_value.select.return_value.order.return_value.eq.return_value.execute.return_value = (
            _mock_execute([{"key": "x", "value": "1"}])
        )
        from memory.memory_manager import list_memory

        result = list_memory(category="personal")
        assert len(result) == 1


class TestSemanticSearch:
    """Tests for semantic_search_memory()."""

    def test_returns_results_with_similarity(self, mock_supabase):
        mock_supabase.rpc.return_value.execute.return_value = _mock_execute(
            [
                {"key": "color", "value": "blue", "category": "preference", "similarity": 0.85},
                {"key": "name", "value": "Alfred", "category": "general", "similarity": 0.72},
            ]
        )
        from memory.memory_manager import semantic_search_memory

        results = semantic_search_memory("test query", n_results=2)
        assert results is not None
        assert len(results) == 2
        assert results[0]["similarity"] == 0.85
        assert "color" in results[0]["document"]

    def test_returns_none_for_empty(self, mock_supabase):
        mock_supabase.rpc.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import semantic_search_memory

        results = semantic_search_memory("test query")
        assert results is None


class TestCategorizeMemory:
    """Tests for categorize_memory()."""

    def test_categorize_existing(self, mock_supabase):
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = _mock_execute(
            [{"key": "item"}]
        )
        from memory.memory_manager import categorize_memory

        assert categorize_memory("item", "personal") is True

        update_call = mock_supabase.table.return_value.update.call_args
        row = update_call[0][0]
        assert row["updated_at"] != "now()"
        parsed = datetime.fromisoformat(row["updated_at"])
        assert parsed.tzinfo is not None

    def test_categorize_nonexistent(self, mock_supabase):
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import categorize_memory

        assert categorize_memory("nope", "personal") is False


class TestGetRecentMemories:
    """Tests for get_recent_memories()."""

    def test_recent_memories(self, mock_supabase):
        order_chain = mock_supabase.table.return_value.select.return_value.order.return_value
        order_chain.limit.return_value.execute.return_value = _mock_execute(
            [
                {"key": "c", "value": "3", "category": "general"},
                {"key": "b", "value": "2", "category": "general"},
            ]
        )
        from memory.memory_manager import get_recent_memories

        recent = get_recent_memories(limit=2)
        assert len(recent) == 2
        assert recent[0]["key"] == "c"

    def test_recent_empty(self, mock_supabase):
        order_chain = mock_supabase.table.return_value.select.return_value.order.return_value
        order_chain.limit.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import get_recent_memories

        assert get_recent_memories() == []


class TestSearchByTag:
    """Tests for search_by_tag()."""

    def test_search_finds_tagged(self, mock_supabase):
        ilike_chain = mock_supabase.table.return_value.select.return_value.ilike.return_value
        ilike_chain.order.return_value.execute.return_value = _mock_execute([{"key": "pet", "value": "Rex"}])
        from memory.memory_manager import search_by_tag

        result = search_by_tag("animal")
        assert "pet" in result

    def test_search_empty(self, mock_supabase):
        ilike_chain = mock_supabase.table.return_value.select.return_value.ilike.return_value
        ilike_chain.order.return_value.execute.return_value = _mock_execute([])
        from memory.memory_manager import search_by_tag

        assert search_by_tag("nonexistent") == {}
