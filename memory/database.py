"""
Supabase database layer for A.L.F.R.E.D - cloud-backed storage with PostgreSQL + pgvector.

Replaces SQLite + ChromaDB with a single managed backend.
"""

from __future__ import annotations

from utils.logger import get_logger

logger = get_logger(__name__)

# Lazy-initialized clients (singletons)
_supabase_client = None
_openai_client = None


def get_supabase():
    """Get the Supabase client, initializing on first call."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    from supabase import create_client

    from config import SUPABASE_KEY, SUPABASE_URL

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in .env. Get them from Supabase Dashboard → Settings → API."
        )

    _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized")
    return _supabase_client


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for text using OpenAI."""
    global _openai_client

    if _openai_client is None:
        from openai import OpenAI

        from config import OPENAI_KEY

        _openai_client = OpenAI(api_key=OPENAI_KEY)

    response = _openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


def check_connection() -> bool:
    """Verify Supabase connection is working. Returns True on success."""
    try:
        sb = get_supabase()
        sb.table("memory_metadata").select("key").limit(1).execute()
        logger.info("Supabase connection verified")
        return True
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False
