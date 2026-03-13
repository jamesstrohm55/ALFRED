"""
Memory management module for A.L.F.R.E.D - persistent fact storage with SQLite + ChromaDB.

SQLite handles structured data (keys, values, categories, tags).
ChromaDB handles vector embeddings for semantic search.
Both stores are kept in sync via chromadb_id tracking.
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

from memory.database import get_connection, init_db
from services.embeddings_manager import (
    store_memory_vector,
    delete_memory_vector,
    search_memory,
)
from utils.logger import get_logger

logger = get_logger(__name__)


def remember(
    key: str,
    value: str,
    category: str = "general",
    tags: Optional[list[str]] = None,
) -> bool:
    """
    Store a key-value pair in both SQLite and ChromaDB.

    Args:
        key: Unique identifier for this memory.
        value: The fact/value to remember.
        category: Category for organisation (general, personal, preference, etc.).
        tags: Optional list of tags for filtering.

    Returns:
        True if stored successfully.
    """
    conn = get_connection()
    chromadb_id = str(uuid.uuid4())
    tags_str = ",".join(tags) if tags else ""

    try:
        conn.execute(
            """INSERT INTO memories (key, value, category, tags, chromadb_id)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET
                   value = excluded.value,
                   category = excluded.category,
                   tags = excluded.tags,
                   chromadb_id = excluded.chromadb_id,
                   updated_at = CURRENT_TIMESTAMP""",
            (key, value, category, tags_str, chromadb_id),
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to store memory in SQLite: {e}")
        return False

    # Store in vector database for semantic search
    try:
        store_memory_vector(
            f"{key} is {value}",
            memory_id=chromadb_id,
            metadata={"key": key, "category": category},
        )
    except Exception as e:
        logger.warning(f"Failed to store in vector database: {e}")

    return True


def recall(key: str) -> Optional[str]:
    """Retrieve a value from memory by key."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT value FROM memories WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else None
    except Exception as e:
        logger.error(f"Failed to recall memory: {e}")
        return None


def forget(key: str) -> bool:
    """
    Remove a key from both SQLite and ChromaDB.

    Fixes the previous sync bug where forget only removed from JSON.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT chromadb_id FROM memories WHERE key = ?", (key,)
        ).fetchone()

        if row is None:
            return False

        chromadb_id = row["chromadb_id"]

        conn.execute("DELETE FROM memories WHERE key = ?", (key,))
        conn.commit()

        # Delete from ChromaDB too
        if chromadb_id:
            try:
                delete_memory_vector(chromadb_id)
            except Exception as e:
                logger.warning(f"Failed to delete vector for '{key}': {e}")

        return True
    except Exception as e:
        logger.error(f"Failed to forget memory: {e}")
        return False


def list_memory(category: Optional[str] = None) -> dict[str, Any]:
    """
    Return stored memories as a dictionary.

    Args:
        category: Optional category filter. If None, returns all.
    """
    conn = get_connection()
    try:
        if category:
            rows = conn.execute(
                "SELECT key, value FROM memories WHERE category = ? ORDER BY updated_at DESC",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT key, value FROM memories ORDER BY updated_at DESC"
            ).fetchall()
        return {row["key"]: row["value"] for row in rows}
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        return {}


def semantic_search_memory(
    query: str, n_results: int = 3
) -> Optional[list[dict[str, Any]]]:
    """
    Search memory using semantic similarity via ChromaDB.

    Returns list of dicts with 'document' and 'distance' keys,
    or None if no matches found.
    """
    try:
        results: dict[str, Any] = search_memory(query, n_results)
        documents: list[str] = results.get("documents", [[]])[0]
        distances: list[float] = results.get("distances", [[]])[0]

        if not documents:
            return None

        return [
            {"document": doc, "distance": dist}
            for doc, dist in zip(documents, distances)
        ]
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return None


def search_by_tag(tag: str) -> dict[str, Any]:
    """Find all memories that contain a given tag."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT key, value FROM memories WHERE ',' || tags || ',' LIKE ? ORDER BY updated_at DESC",
            (f"%,{tag},%",),
        ).fetchall()
        return {row["key"]: row["value"] for row in rows}
    except Exception as e:
        logger.error(f"Failed to search by tag: {e}")
        return {}


def categorize_memory(key: str, category: str) -> bool:
    """Update the category of an existing memory."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE memories SET category = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (category, key),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to categorize memory: {e}")
        return False


def get_recent_memories(limit: int = 5) -> list[dict[str, str]]:
    """Get the most recently updated memories."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT key, value, category FROM memories ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"key": row["key"], "value": row["value"], "category": row["category"]} for row in rows]
    except Exception as e:
        logger.error(f"Failed to get recent memories: {e}")
        return []
