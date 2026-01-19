"""
Embeddings manager for A.L.F.R.E.D - handles vector storage and semantic search.

Uses lazy initialization for faster startup.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from config import OPENAI_KEY
from utils.logger import get_logger

if TYPE_CHECKING:
    import chromadb
    from openai import OpenAI

logger = get_logger(__name__)

# Lazy-initialized clients
_openai_client: Optional[OpenAI] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[Any] = None
_initialized: bool = False


def _ensure_initialized() -> None:
    """Lazy initialization of OpenAI and ChromaDB clients."""
    global _openai_client, _chroma_client, _collection, _initialized

    if _initialized:
        return

    _initialized = True

    try:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_KEY)
        logger.debug("OpenAI embeddings client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")

    try:
        import chromadb
        _chroma_client = chromadb.PersistentClient(path="./data/embeddings_db")
        _collection = _chroma_client.get_or_create_collection("alfred_memories")
        logger.debug("ChromaDB client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using OpenAI."""
    _ensure_initialized()

    if _openai_client is None:
        raise RuntimeError("OpenAI client not initialized")

    response = _openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


def store_memory_vector(memory_text: str, metadata: Optional[dict[str, Any]] = None) -> None:
    """Store a memory text with its embedding in the vector database."""
    _ensure_initialized()

    if _collection is None:
        logger.warning("ChromaDB collection not available, skipping vector storage")
        return

    try:
        embedding: list[float] = generate_embedding(memory_text)
        existing_ids = _collection.get()["ids"]
        new_id: str = str(len(existing_ids))

        _collection.add(
            embeddings=[embedding],
            documents=[memory_text],
            ids=[new_id],
            metadatas=[metadata or {}]
        )

        logger.debug(f"Stored memory vector: {memory_text[:50]}...")
    except Exception as e:
        logger.error(f"Failed to store memory vector: {e}")


def search_memory(query: str, n_results: int = 3) -> dict[str, Any]:
    """Search for similar memories using semantic search."""
    _ensure_initialized()

    if _collection is None:
        logger.warning("ChromaDB collection not available")
        return {"documents": [[]], "ids": [[]], "distances": [[]]}

    try:
        query_embedding: list[float] = generate_embedding(query)
        results: dict[str, Any] = _collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return {"documents": [[]], "ids": [[]], "distances": [[]]}