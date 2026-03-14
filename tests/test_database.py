"""
Unit tests for memory/database.py - Supabase client initialization and helpers.

Mocks the Supabase client to avoid hitting a real backend.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGetSupabase:
    """Tests for get_supabase() client initialization."""

    def setup_method(self):
        """Reset the singleton before each test."""
        import memory.database as db

        db._supabase_client = None

    def test_returns_client(self):
        import memory.database as db

        db._supabase_client = None

        mock_client = MagicMock()
        mock_create = MagicMock(return_value=mock_client)

        with (
            patch.dict("sys.modules", {}),
            patch("supabase.create_client", mock_create),
            patch("config.SUPABASE_URL", "https://test.supabase.co"),
            patch("config.SUPABASE_KEY", "test-key"),
        ):
            result = db.get_supabase()
            assert result == mock_client

    def test_singleton_returns_same_client(self):
        import memory.database as db

        mock_client = MagicMock()
        db._supabase_client = mock_client

        result1 = db.get_supabase()
        result2 = db.get_supabase()
        assert result1 is result2
        assert result1 is mock_client

    def test_raises_without_credentials(self):
        import memory.database as db

        db._supabase_client = None

        # Mock the supabase import to avoid pyiceberg/pydantic compat issues in test env
        mock_module = MagicMock()
        with (
            patch.dict("sys.modules", {"supabase": mock_module}),
            patch("config.SUPABASE_URL", None),
            patch("config.SUPABASE_KEY", None),
            pytest.raises(RuntimeError, match="SUPABASE_URL"),
        ):
            db.get_supabase()


class TestGenerateEmbedding:
    """Tests for generate_embedding()."""

    def setup_method(self):
        """Reset the OpenAI singleton before each test."""
        import memory.database as db

        db._openai_client = None

    def test_returns_embedding_vector(self):
        import memory.database as db

        db._openai_client = None

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response

        mock_openai_cls = MagicMock(return_value=mock_client)

        with patch("openai.OpenAI", mock_openai_cls), patch("config.OPENAI_KEY", "test-key"):
            result = db.generate_embedding("test text")
            assert result == [0.1, 0.2, 0.3]

    def test_calls_correct_model(self):
        import memory.database as db

        db._openai_client = None

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1])]

        mock_client = MagicMock()
        mock_client.embeddings.create.return_value = mock_response

        mock_openai_cls = MagicMock(return_value=mock_client)

        with patch("openai.OpenAI", mock_openai_cls), patch("config.OPENAI_KEY", "test-key"):
            db.generate_embedding("test")
            call_kwargs = mock_client.embeddings.create.call_args
            assert call_kwargs.kwargs["model"] == "text-embedding-3-small"


class TestCheckConnection:
    """Tests for check_connection()."""

    def test_returns_true_on_success(self):
        mock_sb = MagicMock()
        mock_sb.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()

        with patch("memory.database.get_supabase", return_value=mock_sb):
            from memory.database import check_connection

            assert check_connection() is True

    def test_returns_false_on_failure(self):
        with patch("memory.database.get_supabase", side_effect=Exception("connection failed")):
            from memory.database import check_connection

            assert check_connection() is False
