"""
Memory package for A.L.F.R.E.D - persistent fact storage with SQLite + ChromaDB.
"""
from memory.database import init_db, migrate_from_json, get_connection
from memory.memory_manager import (
    remember,
    recall,
    forget,
    list_memory,
    semantic_search_memory,
    search_by_tag,
    categorize_memory,
    get_recent_memories,
)

__all__ = [
    "init_db",
    "migrate_from_json",
    "get_connection",
    "remember",
    "recall",
    "forget",
    "list_memory",
    "semantic_search_memory",
    "search_by_tag",
    "categorize_memory",
    "get_recent_memories",
]
