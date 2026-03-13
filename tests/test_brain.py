"""
Unit tests for core/brain.py - Command routing and LLM interactions.
"""
from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAddToHistory:
    """Tests for conversation history management (SQLite-backed)."""

    @pytest.fixture(autouse=True)
    def in_memory_db(self, monkeypatch):
        """Use in-memory SQLite for conversation tests."""
        import sqlite3
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
        monkeypatch.setattr("core.brain.get_connection", lambda: conn)
        yield conn
        conn.close()

    def test_add_to_history_basic(self):
        """Test adding a message to conversation history in SQLite."""
        from core.brain import add_to_history, get_conversation_history

        add_to_history("user", "test message")

        history = get_conversation_history()
        assert len(history) >= 1
        assert history[-1]["role"] == "user"
        assert history[-1]["content"] == "test message"

    def test_history_retrieval_limit(self):
        """Test that history retrieval respects limits."""
        from core.brain import add_to_history, get_conversation_history, MAX_HISTORY

        for i in range(MAX_HISTORY * 3):
            add_to_history("user", f"message {i}")

        history = get_conversation_history()
        assert len(history) <= MAX_HISTORY * 2


class TestHandleServiceCommands:
    """Tests for service command routing."""

    def test_weather_keyword_detection(self):
        """Test that weather keywords trigger weather commands."""
        from core.brain import handle_service_commands

        with patch('core.brain.handle_weather_command') as mock_weather:
            mock_weather.return_value = "Weather response"
            result = handle_service_commands("what's the weather like")
            mock_weather.assert_called_once()
            assert result == "Weather response"

    def test_calendar_keyword_detection(self):
        """Test that calendar keywords trigger calendar commands."""
        from core.brain import handle_service_commands

        with patch('core.brain.handle_calendar_command') as mock_calendar:
            mock_calendar.return_value = "Calendar response"
            result = handle_service_commands("add event to my calendar")
            mock_calendar.assert_called_once()

    def test_system_keyword_detection(self):
        """Test that system keywords trigger system monitor commands."""
        from core.brain import handle_service_commands

        with patch('core.brain.handle_system_monitor_command') as mock_system:
            mock_system.return_value = "System response"
            result = handle_service_commands("check system status")
            mock_system.assert_called_once()

    def test_no_keyword_returns_none(self):
        """Test that unrecognized input returns None."""
        from core.brain import handle_service_commands

        result = handle_service_commands("random unrelated text")
        assert result is None


class TestBuildMessages:
    """Tests for message building functionality."""

    @pytest.fixture(autouse=True)
    def in_memory_db(self, monkeypatch):
        """Use in-memory SQLite for build_messages tests."""
        import sqlite3
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
        monkeypatch.setattr("core.brain.get_connection", lambda: conn)
        monkeypatch.setattr("memory.memory_manager.get_connection", lambda: conn)
        yield conn
        conn.close()

    def test_build_messages_includes_system_prompt(self):
        """Test that built messages include the system prompt."""
        from core.brain import build_messages, SYSTEM_PROMPT

        with patch("core.brain.semantic_search_memory", return_value=None), \
             patch("core.brain.get_recent_memories", return_value=[]):
            messages = build_messages("test input")
            assert len(messages) >= 1
            assert messages[0]["role"] == "system"
            assert SYSTEM_PROMPT in messages[0]["content"]


class TestGetResponse:
    """Tests for the main get_response function."""

    def test_get_response_handles_memory_commands(self):
        """Test that memory commands are handled first."""
        from core.brain import get_response

        with patch('core.brain.handle_memory_commands') as mock_memory:
            mock_memory.return_value = "Memory response"
            result = get_response("remember that test is value")
            mock_memory.assert_called_once()
            assert result == "Memory response"

    def test_get_response_handles_errors_gracefully(self):
        """Test that errors are caught and a friendly message is returned."""
        from core.brain import get_response

        with patch('core.brain.handle_memory_commands') as mock_memory:
            mock_memory.side_effect = Exception("Test error")
            result = get_response("test input")
            assert "error" in result.lower()
