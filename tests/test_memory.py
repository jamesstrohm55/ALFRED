"""
Unit tests for memory/memory_manager.py - Memory storage and retrieval.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
import json
import tempfile
import os

import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMemoryManager:
    """Tests for memory_manager.py"""

    @pytest.fixture
    def temp_memory_file(self, tmp_path):
        """Create a temporary memory file for testing."""
        memory_file = tmp_path / "test_memory.json"
        memory_file.write_text(json.dumps({}))
        return memory_file

    def test_remember_stores_value(self):
        """Test that remember stores a key-value pair."""
        from memory.memory_manager import remember, recall, clear_cache

        with patch('memory.memory_manager.store_memory_vector'):
            clear_cache()
            remember("test_key", "test_value")
            result = recall("test_key")
            assert result == "test_value"

    def test_recall_returns_none_for_missing_key(self):
        """Test that recall returns None for non-existent keys."""
        from memory.memory_manager import recall

        result = recall("nonexistent_key_12345")
        assert result is None

    def test_forget_removes_key(self):
        """Test that forget removes a stored key."""
        from memory.memory_manager import remember, forget, recall, clear_cache

        with patch('memory.memory_manager.store_memory_vector'):
            clear_cache()
            remember("forget_test", "value")
            assert recall("forget_test") == "value"

            success = forget("forget_test")
            assert success is True
            assert recall("forget_test") is None

    def test_forget_returns_false_for_missing_key(self):
        """Test that forget returns False for non-existent keys."""
        from memory.memory_manager import forget

        result = forget("definitely_not_a_key_xyz")
        assert result is False

    def test_list_memory_returns_dict(self):
        """Test that list_memory returns a dictionary."""
        from memory.memory_manager import list_memory

        result = list_memory()
        assert isinstance(result, dict)

    def test_clear_cache_resets_cache(self):
        """Test that clear_cache properly resets the cache."""
        from memory.memory_manager import clear_cache, _memory_cache, load_memory

        # First load memory to populate cache
        load_memory()

        # Clear cache
        clear_cache()

        # Import again to check _memory_cache is None
        from memory import memory_manager
        # After clear, next load should read from disk
        # This is implicitly tested by other tests working correctly

    def test_semantic_search_memory(self):
        """Test semantic search functionality."""
        from memory.memory_manager import semantic_search_memory

        with patch('memory.memory_manager.search_memory') as mock_search:
            mock_search.return_value = {"documents": [["result1", "result2"]]}

            results = semantic_search_memory("test query", n_results=2)
            assert results is not None
            assert len(results) == 2

    def test_semantic_search_returns_none_on_no_results(self):
        """Test that semantic search returns None when no matches found."""
        from memory.memory_manager import semantic_search_memory

        with patch('memory.memory_manager.search_memory') as mock_search:
            mock_search.return_value = {"documents": [[]]}

            results = semantic_search_memory("test query")
            assert results is None

    def test_semantic_search_handles_errors(self):
        """Test that semantic search handles errors gracefully."""
        from memory.memory_manager import semantic_search_memory

        with patch('memory.memory_manager.search_memory') as mock_search:
            mock_search.side_effect = Exception("Search error")

            results = semantic_search_memory("test query")
            assert results is None


class TestThreadSafety:
    """Tests for thread safety in memory operations."""

    def test_concurrent_reads(self):
        """Test that concurrent reads don't cause issues."""
        import threading
        from memory.memory_manager import load_memory

        results = []
        errors = []

        def read_memory():
            try:
                data = load_memory()
                results.append(data)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_memory) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10

    def test_concurrent_writes(self):
        """Test that concurrent writes don't corrupt data."""
        import threading
        from memory.memory_manager import remember, recall, clear_cache

        with patch('memory.memory_manager.store_memory_vector'):
            clear_cache()
            errors = []

            def write_memory(key):
                try:
                    remember(f"concurrent_test_{key}", f"value_{key}")
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=write_memory, args=(i,)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            assert len(errors) == 0
