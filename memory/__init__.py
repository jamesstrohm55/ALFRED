"""
Memory package for A.L.F.R.E.D - persistent fact storage via Supabase (PostgreSQL + pgvector).
"""

from memory.database import check_connection, generate_embedding, get_supabase
from memory.memory_manager import (
    categorize_memory,
    forget,
    get_recent_memories,
    list_memory,
    recall,
    remember,
    search_by_tag,
    semantic_search_memory,
)

__all__ = [
    "get_supabase",
    "generate_embedding",
    "check_connection",
    "remember",
    "recall",
    "forget",
    "list_memory",
    "semantic_search_memory",
    "search_by_tag",
    "categorize_memory",
    "get_recent_memories",
]
