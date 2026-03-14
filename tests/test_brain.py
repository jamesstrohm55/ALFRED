"""
Unit tests for core/brain.py - Command routing and LLM interactions.
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _mock_execute(data=None):
    """Helper to create a mock Supabase execute() response."""
    result = MagicMock()
    result.data = data or []
    return result


class TestAddToHistory:
    """Tests for conversation history management (Supabase-backed)."""

    @pytest.fixture(autouse=True)
    def mock_supabase(self):
        """Mock Supabase for conversation tests."""
        mock_sb = MagicMock()
        mock_sb.table.return_value.insert.return_value.execute.return_value = _mock_execute()
        eq_chain = mock_sb.table.return_value.select.return_value.eq.return_value
        eq_chain.order.return_value.limit.return_value.execute.return_value = _mock_execute()
        neq_chain = mock_sb.table.return_value.select.return_value.neq.return_value
        neq_chain.order.return_value.limit.return_value.execute.return_value = _mock_execute()

        with patch("core.brain.get_supabase", return_value=mock_sb):
            yield mock_sb

    def test_add_to_history_inserts_to_supabase(self, mock_supabase):
        """Test that add_to_history inserts into the conversations table."""
        from core.brain import add_to_history

        add_to_history("user", "test message")

        mock_supabase.table.assert_called_with("conversations")
        insert_call = mock_supabase.table.return_value.insert.call_args
        row = insert_call[0][0]
        assert row["role"] == "user"
        assert row["content"] == "test message"
        assert "session_id" in row

    def test_get_conversation_history(self, mock_supabase):
        """Test loading conversation history from Supabase."""
        eq_chain = mock_supabase.table.return_value.select.return_value.eq.return_value
        eq_chain.order.return_value.limit.return_value.execute.return_value = _mock_execute(
            [
                {"role": "assistant", "content": "second"},
                {"role": "user", "content": "first"},
            ]
        )
        from core.brain import get_conversation_history

        history = get_conversation_history()
        # Should be reversed to chronological order
        assert history[0]["content"] == "first"
        assert history[1]["content"] == "second"


class TestHandleServiceCommands:
    """Tests for service command routing."""

    def test_weather_keyword_detection(self):
        """Test that weather keywords trigger weather commands."""
        from core.brain import handle_service_commands

        with patch("core.brain.handle_weather_command") as mock_weather:
            mock_weather.return_value = "Weather response"
            result = handle_service_commands("what's the weather like")
            mock_weather.assert_called_once()
            assert result == "Weather response"

    def test_calendar_keyword_detection(self):
        """Test that calendar keywords trigger calendar commands."""
        from core.brain import handle_service_commands

        with patch("core.brain.handle_calendar_command") as mock_calendar:
            mock_calendar.return_value = "Calendar response"
            handle_service_commands("add event to my calendar")
            mock_calendar.assert_called_once()

    def test_system_keyword_detection(self):
        """Test that system keywords trigger system monitor commands."""
        from core.brain import handle_service_commands

        with patch("core.brain.handle_system_monitor_command") as mock_system:
            mock_system.return_value = "System response"
            handle_service_commands("check system status")
            mock_system.assert_called_once()

    def test_no_keyword_returns_none(self):
        """Test that unrecognized input returns None."""
        from core.brain import handle_service_commands

        result = handle_service_commands("random unrelated text")
        assert result is None


class TestBuildMessages:
    """Tests for message building functionality."""

    def test_build_messages_includes_system_prompt(self):
        """Test that built messages include the system prompt."""
        from core.brain import SYSTEM_PROMPT, build_messages

        with (
            patch("core.brain.semantic_search_memory", return_value=None),
            patch("core.brain.get_recent_memories", return_value=[]),
            patch("core.brain.get_conversation_history", return_value=[]),
        ):
            messages = build_messages("test input")
            assert len(messages) >= 1
            assert messages[0]["role"] == "system"
            assert SYSTEM_PROMPT in messages[0]["content"]


class TestGetResponse:
    """Tests for the main get_response function."""

    def test_get_response_handles_memory_commands(self):
        """Test that memory commands are handled first."""
        from core.brain import get_response

        with patch("core.brain.handle_memory_commands") as mock_memory:
            mock_memory.return_value = "Memory response"
            result = get_response("remember that test is value")
            mock_memory.assert_called_once()
            assert result == "Memory response"

    def test_get_response_handles_errors_gracefully(self):
        """Test that errors are caught and a friendly message is returned."""
        from core.brain import get_response

        with patch("core.brain.handle_memory_commands") as mock_memory:
            mock_memory.side_effect = Exception("Test error")
            result = get_response("test input")
            assert "error" in result.lower()
