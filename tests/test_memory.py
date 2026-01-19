"""
Unit tests for memory/memory_manager.py - Memory storage and retrieval.

Note: These tests mock external dependencies (ChromaDB, OpenAI) to run in isolation.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMemoryManagerUnit:
    """Unit tests for memory_manager functions with mocked dependencies."""

    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks before each test."""
        # Mock the embeddings manager module
        self.mock_store = MagicMock(return_value=None)
        self.mock_search = MagicMock(return_value={"documents": [[]], "ids": [[]], "distances": [[]]})

        with patch.dict('sys.modules', {'chromadb': MagicMock()}):
            with patch('services.embeddings_manager.store_memory_vector', self.mock_store), \
                 patch('services.embeddings_manager.search_memory', self.mock_search):
                yield

    def test_load_memory_returns_dict(self):
        """Test that load_memory returns a dictionary."""
        test_data = {"key1": "value1", "key2": "value2"}

        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            with patch('pathlib.Path.exists', return_value=True):
                # Import after mocks are set up
                from memory.memory_manager import load_memory, clear_cache, _memory_lock

                with _memory_lock:
                    # Clear internal cache
                    import memory.memory_manager as mm
                    mm._memory_cache = None

                result = load_memory()
                assert isinstance(result, dict)

    def test_save_memory_writes_json(self):
        """Test that save_memory writes proper JSON."""
        test_data = {"test": "data"}

        m = mock_open()
        with patch('builtins.open', m):
            with patch('pathlib.Path.exists', return_value=True):
                from memory.memory_manager import save_memory, _memory_lock

                import memory.memory_manager as mm
                with _memory_lock:
                    mm._memory_cache = {}

                save_memory(test_data)

                # Verify open was called for writing
                m.assert_called()


class TestMemoryLogic:
    """Tests for memory logic that don't require file I/O."""

    def test_semantic_search_parses_results(self):
        """Test that semantic search correctly parses results."""
        mock_results = {"documents": [["result1", "result2"]], "ids": [["1", "2"]], "distances": [[0.1, 0.2]]}

        with patch('services.embeddings_manager.search_memory', return_value=mock_results):
            with patch('memory.memory_manager.search_memory', return_value=mock_results):
                from memory.memory_manager import semantic_search_memory

                results = semantic_search_memory("test query", n_results=2)
                assert results is not None
                assert len(results) == 2
                assert "result1" in results

    def test_semantic_search_returns_none_for_empty(self):
        """Test that semantic search returns None for empty results."""
        mock_results = {"documents": [[]], "ids": [[]], "distances": [[]]}

        with patch('memory.memory_manager.search_memory', return_value=mock_results):
            from memory.memory_manager import semantic_search_memory

            results = semantic_search_memory("test query")
            assert results is None


class TestThreadSafetyBasic:
    """Basic thread safety tests."""

    def test_lock_exists(self):
        """Test that the memory lock exists and is a Lock."""
        import threading
        from memory.memory_manager import _memory_lock

        assert isinstance(_memory_lock, type(threading.Lock()))

    def test_clear_cache_function_exists(self):
        """Test that clear_cache function exists and is callable."""
        from memory.memory_manager import clear_cache

        assert callable(clear_cache)
