"""
Memory management module for A.L.F.R.E.D - persistent fact storage with thread safety.

Provides both JSON-based key-value storage and semantic search via ChromaDB.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

from services.embeddings_manager import store_memory_vector, search_memory
from utils.logger import get_logger

logger = get_logger(__name__)

MEMORY_FILE: Path = Path("data/memory.json")

# Thread safety lock for file operations
_memory_lock: threading.Lock = threading.Lock()

# In-memory cache to reduce file I/O
_memory_cache: Optional[dict[str, Any]] = None
_cache_dirty: bool = False


def _ensure_memory_file() -> None:
    """Ensure the memory file and directory exist."""
    if not MEMORY_FILE.exists():
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        MEMORY_FILE.write_text(json.dumps({}))


# Initialize on module load
_ensure_memory_file()


def load_memory() -> dict[str, Any]:
    """
    Load memory from file, using cache when available.

    Thread-safe implementation that caches data in memory.
    """
    global _memory_cache

    with _memory_lock:
        if _memory_cache is not None:
            return _memory_cache.copy()

        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as file:
                _memory_cache = json.load(file)
                return _memory_cache.copy()
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading memory file: {e}")
            _memory_cache = {}
            return {}


def save_memory(memory: dict[str, Any]) -> None:
    """
    Save memory to file (thread-safe).

    Updates the in-memory cache and persists to disk.
    """
    global _memory_cache, _cache_dirty

    with _memory_lock:
        _memory_cache = memory.copy()
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as file:
                json.dump(memory, file, indent=4)
            _cache_dirty = False
        except IOError as e:
            logger.error(f"Error saving memory file: {e}")
            _cache_dirty = True


def remember(key: str, value: str) -> bool:
    """
    Store a key-value pair in memory.

    Also stores in vector database for semantic search.
    """
    with _memory_lock:
        global _memory_cache
        if _memory_cache is None:
            _memory_cache = load_memory()
        _memory_cache[key] = value

    # Save outside of lock to avoid holding it during I/O
    save_memory(_memory_cache)

    # Also store in vector database (non-blocking)
    try:
        store_memory_vector(f"{key} is {value}", metadata={"key": key})
    except Exception as e:
        logger.warning(f"Failed to store in vector database: {e}")

    return True


def recall(key: str) -> Optional[str]:
    """Retrieve a value from memory by key."""
    memory: dict[str, Any] = load_memory()
    return memory.get(key)


def forget(key: str) -> bool:
    """Remove a key from memory."""
    global _memory_cache

    with _memory_lock:
        if _memory_cache is None:
            _memory_cache = load_memory()
        if key in _memory_cache:
            del _memory_cache[key]
            save_memory(_memory_cache)
            return True
    return False


def list_memory() -> dict[str, Any]:
    """Return all stored memory as a dictionary."""
    return load_memory()


def semantic_search_memory(query: str, n_results: int = 3) -> Optional[list[str]]:
    """
    Search memory using semantic similarity.

    Args:
        query: The search query
        n_results: Maximum number of results to return

    Returns:
        List of matching memory entries or None if no matches
    """
    try:
        results: dict[str, Any] = search_memory(query, n_results)
        matches: list[str] = results.get("documents", [[]])[0]
        return matches if matches else None
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return None


def clear_cache() -> None:
    """Clear the in-memory cache, forcing next load from disk."""
    global _memory_cache
    with _memory_lock:
        _memory_cache = None
