"""
Memory package for A.L.F.R.E.D - persistent fact storage via Supabase (PostgreSQL + pgvector).
"""
from memory.database import get_supabase, generate_embedding, check_connection
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
