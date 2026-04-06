"""
Memory management module for A.L.F.R.E.D - persistent fact storage via Supabase.

PostgreSQL handles structured data. pgvector handles semantic search.
Embeddings are stored as a column on the memories row — no separate vector store.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from memory.database import generate_embedding, get_supabase
from utils.logger import get_logger

logger = get_logger(__name__)


def _current_timestamp() -> str:
    """Return a UTC timestamp string suitable for timestamptz columns."""
    return datetime.now(timezone.utc).isoformat()


def remember(
    key: str,
    value: str,
    category: str = "general",
    tags: list[str] | None = None,
) -> bool:
    """
    Store a key-value pair in Supabase with its embedding vector.

    Upserts on key — overwrites if the key already exists.
    """
    tags_str = ",".join(tags) if tags else ""

    try:
        embedding = generate_embedding(f"{key} is {value}")
    except Exception as e:
        logger.warning(f"Failed to generate embedding: {e}")
        embedding = None

    row = {
        "key": key,
        "value": value,
        "category": category,
        "tags": tags_str,
        "updated_at": _current_timestamp(),
    }
    if embedding is not None:
        row["embedding"] = embedding

    try:
        sb = get_supabase()
        sb.table("memories").upsert(row, on_conflict="key").execute()
        return True
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return False


def recall(key: str) -> str | None:
    """Retrieve a value from memory by key."""
    try:
        sb = get_supabase()
        result = sb.table("memories").select("value").eq("key", key).execute()
        if result.data:
            return result.data[0]["value"]
        return None
    except Exception as e:
        logger.error(f"Failed to recall memory: {e}")
        return None


def forget(key: str) -> bool:
    """
    Remove a key from Supabase.

    Embedding is deleted automatically since it's a column on the same row.
    No sync bug possible.
    """
    try:
        sb = get_supabase()
        result = sb.table("memories").delete().eq("key", key).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Failed to forget memory: {e}")
        return False


def list_memory(category: str | None = None) -> dict[str, Any]:
    """
    Return stored memories as a dictionary.

    Args:
        category: Optional category filter. If None, returns all.
    """
    try:
        sb = get_supabase()
        query = sb.table("memories").select("key, value").order("updated_at", desc=True)
        if category:
            query = query.eq("category", category)
        result = query.execute()
        return {row["key"]: row["value"] for row in result.data}
    except Exception as e:
        logger.error(f"Failed to list memories: {e}")
        return {}


def semantic_search_memory(query: str, n_results: int = 5) -> list[dict[str, Any]] | None:
    """
    Search memory using semantic similarity via pgvector.

    Returns list of dicts with 'document', 'similarity', 'key', 'category' keys,
    or None if no matches found.
    """
    try:
        query_embedding = generate_embedding(query)
        sb = get_supabase()
        result = sb.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.3,
                "match_count": n_results,
            },
        ).execute()

        if not result.data:
            return None

        return [
            {
                "document": f"{row['key']} is {row['value']}",
                "similarity": row["similarity"],
                "key": row["key"],
                "category": row["category"],
            }
            for row in result.data
        ]
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return None


def search_by_tag(tag: str) -> dict[str, Any]:
    """Find all memories that contain a given tag."""
    try:
        sb = get_supabase()
        result = (
            sb.table("memories").select("key, value").ilike("tags", f"%{tag}%").order("updated_at", desc=True).execute()
        )
        return {row["key"]: row["value"] for row in result.data}
    except Exception as e:
        logger.error(f"Failed to search by tag: {e}")
        return {}


def categorize_memory(key: str, category: str) -> bool:
    """Update the category of an existing memory."""
    try:
        sb = get_supabase()
        result = (
            sb.table("memories")
            .update({"category": category, "updated_at": _current_timestamp()})
            .eq("key", key)
            .execute()
        )
        return len(result.data) > 0
    except Exception as e:
        logger.error(f"Failed to categorize memory: {e}")
        return False


def get_recent_memories(limit: int = 5) -> list[dict[str, str]]:
    """Get the most recently updated memories."""
    try:
        sb = get_supabase()
        result = (
            sb.table("memories").select("key, value, category").order("updated_at", desc=True).limit(limit).execute()
        )
        return [{"key": row["key"], "value": row["value"], "category": row["category"]} for row in result.data]
    except Exception as e:
        logger.error(f"Failed to get recent memories: {e}")
        return []
