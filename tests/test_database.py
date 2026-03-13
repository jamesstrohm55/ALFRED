"""
Unit tests for memory/database.py - SQLite schema, CRUD, and migration.

Uses :memory: databases to avoid touching disk.
"""
from __future__ import annotations

import json
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestInitDb:
    """Tests for init_db() schema creation."""

    def test_creates_memories_table(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        tables = [
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        assert "memories" in tables
        assert "conversations" in tables
        assert "memory_metadata" in tables
        conn.close()

    def test_idempotent(self):
        """Calling init_db() twice should not raise."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()
            init_db()  # Should not raise

        conn.close()

    def test_memories_schema_columns(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(memories)").fetchall()
        ]
        expected = ["id", "key", "value", "category", "tags", "created_at", "updated_at", "chromadb_id"]
        for col in expected:
            assert col in columns, f"Missing column: {col}"
        conn.close()

    def test_conversations_schema_columns(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info(conversations)").fetchall()
        ]
        expected = ["id", "session_id", "role", "content", "timestamp"]
        for col in expected:
            assert col in columns, f"Missing column: {col}"
        conn.close()


class TestMemoriesCRUD:
    """Direct SQLite CRUD tests on the memories table."""

    @pytest.fixture
    def db(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()
        yield conn
        conn.close()

    def test_insert_and_select(self, db):
        db.execute(
            "INSERT INTO memories (key, value) VALUES (?, ?)",
            ("color", "blue"),
        )
        db.commit()
        row = db.execute("SELECT value FROM memories WHERE key = ?", ("color",)).fetchone()
        assert row["value"] == "blue"

    def test_unique_key_constraint(self, db):
        db.execute("INSERT INTO memories (key, value) VALUES (?, ?)", ("k", "v1"))
        db.commit()
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO memories (key, value) VALUES (?, ?)", ("k", "v2"))

    def test_upsert(self, db):
        db.execute(
            """INSERT INTO memories (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            ("k", "v1"),
        )
        db.execute(
            """INSERT INTO memories (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            ("k", "v2"),
        )
        db.commit()
        row = db.execute("SELECT value FROM memories WHERE key = ?", ("k",)).fetchone()
        assert row["value"] == "v2"

    def test_delete(self, db):
        db.execute("INSERT INTO memories (key, value) VALUES (?, ?)", ("k", "v"))
        db.commit()
        db.execute("DELETE FROM memories WHERE key = ?", ("k",))
        db.commit()
        assert db.execute("SELECT * FROM memories WHERE key = ?", ("k",)).fetchone() is None

    def test_category_filter(self, db):
        db.execute("INSERT INTO memories (key, value, category) VALUES (?, ?, ?)", ("a", "1", "personal"))
        db.execute("INSERT INTO memories (key, value, category) VALUES (?, ?, ?)", ("b", "2", "preference"))
        db.commit()
        rows = db.execute("SELECT * FROM memories WHERE category = ?", ("personal",)).fetchall()
        assert len(rows) == 1
        assert rows[0]["key"] == "a"


class TestConversationsCRUD:
    """Direct SQLite CRUD tests on the conversations table."""

    @pytest.fixture
    def db(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()
        yield conn
        conn.close()

    def test_insert_and_select(self, db):
        db.execute(
            "INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)",
            ("sess1", "user", "hello"),
        )
        db.commit()
        row = db.execute("SELECT * FROM conversations WHERE session_id = ?", ("sess1",)).fetchone()
        assert row["content"] == "hello"
        assert row["role"] == "user"

    def test_session_ordering(self, db):
        db.execute("INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)", ("s", "user", "first"))
        db.execute("INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)", ("s", "assistant", "second"))
        db.commit()
        rows = db.execute(
            "SELECT content FROM conversations WHERE session_id = ? ORDER BY timestamp ASC", ("s",)
        ).fetchall()
        assert rows[0]["content"] == "first"
        assert rows[1]["content"] == "second"


class TestMigrateFromJson:
    """Tests for migrate_from_json()."""

    def test_migration_inserts_data(self, tmp_path):
        """Test that JSON data is migrated into SQLite."""
        json_file = tmp_path / "memory.json"
        json_file.write_text(json.dumps({"color": "blue", "name": "Alfred"}))

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        with patch("memory.database.get_connection", return_value=conn), \
             patch("memory.database.MEMORY_JSON_PATH", json_file):
            from memory.database import migrate_from_json
            migrate_from_json()

        rows = conn.execute("SELECT key, value FROM memories ORDER BY key").fetchall()
        data = {row["key"]: row["value"] for row in rows}
        assert data["color"] == "blue"
        assert data["name"] == "Alfred"

        # JSON file should be renamed to .bak
        assert not json_file.exists()
        assert (tmp_path / "memory.json.bak").exists()
        conn.close()

    def test_migration_skips_when_no_json(self):
        """Migration should silently do nothing if no JSON file."""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        fake_path = Path("/nonexistent/memory.json")
        with patch("memory.database.MEMORY_JSON_PATH", fake_path):
            from memory.database import migrate_from_json
            migrate_from_json()  # Should not raise

        conn.close()

    def test_migration_handles_empty_json(self, tmp_path):
        """Empty JSON should just rename to .bak without inserting."""
        json_file = tmp_path / "memory.json"
        json_file.write_text("{}")

        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        with patch("memory.database.get_connection", return_value=conn):
            from memory.database import init_db
            init_db()

        with patch("memory.database.get_connection", return_value=conn), \
             patch("memory.database.MEMORY_JSON_PATH", json_file):
            from memory.database import migrate_from_json
            migrate_from_json()

        rows = conn.execute("SELECT * FROM memories").fetchall()
        assert len(rows) == 0
        assert not json_file.exists()
        conn.close()
