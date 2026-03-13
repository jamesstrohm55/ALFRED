"""
SQLite database layer for A.L.F.R.E.D - structured storage with schema, indexing, and queries.

Replaces the flat JSON key-value store with a proper relational backend.
ChromaDB remains for vector search; SQLite handles structured data + conversations.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Optional

from utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH: Path = Path("data/alfred.db")
MEMORY_JSON_PATH: Path = Path("data/memory.json")

# Thread-local storage for connections (SQLite connections aren't thread-safe)
_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """Get a thread-local SQLite connection with WAL mode enabled."""
    if not hasattr(_local, "connection") or _local.connection is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = sqlite3.Row
        _local.connection = conn
    return _local.connection


def init_db() -> None:
    """Create tables if they don't exist. Safe to call multiple times."""
    conn = get_connection()
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

        CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
        CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
        CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
        CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
    """)
    conn.commit()
    logger.info("Database initialized successfully")


def migrate_from_json() -> None:
    """One-time migration from data/memory.json to SQLite. Renames JSON to .bak."""
    if not MEMORY_JSON_PATH.exists():
        logger.debug("No memory.json found, skipping migration")
        return

    try:
        raw = MEMORY_JSON_PATH.read_text(encoding="utf-8")
        data: dict[str, Any] = json.loads(raw)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to read memory.json for migration: {e}")
        return

    if not data:
        # Empty JSON — just rename and move on
        backup = MEMORY_JSON_PATH.with_suffix(".json.bak")
        MEMORY_JSON_PATH.rename(backup)
        logger.info("Empty memory.json renamed to .bak")
        return

    conn = get_connection()
    migrated = 0
    for key, value in data.items():
        try:
            conn.execute(
                "INSERT OR IGNORE INTO memories (key, value, category) VALUES (?, ?, ?)",
                (key, str(value), "general"),
            )
            migrated += 1
        except sqlite3.Error as e:
            logger.warning(f"Failed to migrate key '{key}': {e}")

    conn.commit()

    backup = MEMORY_JSON_PATH.with_suffix(".json.bak")
    MEMORY_JSON_PATH.rename(backup)
    logger.info(f"Migrated {migrated} entries from memory.json → SQLite. JSON renamed to .bak")


def close_connection() -> None:
    """Close the thread-local connection if open."""
    if hasattr(_local, "connection") and _local.connection is not None:
        _local.connection.close()
        _local.connection = None
