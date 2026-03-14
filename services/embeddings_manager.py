"""
Embeddings manager for A.L.F.R.E.D - generates vector embeddings via OpenAI.

Vector storage and search are now handled by Supabase pgvector.
This module only provides the embedding generation function.
"""

from __future__ import annotations

from memory.database import generate_embedding

__all__ = ["generate_embedding"]
