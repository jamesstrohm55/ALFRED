"""API key authentication and rate limiting for A.L.F.R.E.D."""

from __future__ import annotations

import hashlib
import threading
import time
from collections import deque

from fastapi import Depends, HTTPException, Request

from memory.database import get_supabase
from utils.logger import get_logger

logger = get_logger(__name__)

# In-memory rate limiter state
_rate_lock = threading.Lock()
_request_log: dict[str, deque[float]] = {}

# Cache of valid key hashes → user info (populated on first lookup)
_user_cache: dict[str, dict] = {}
_cache_lock = threading.Lock()
_CACHE_TTL = 300  # 5 minutes
_cache_timestamp: float = 0


def _hash_key(api_key: str) -> str:
    """SHA-256 hash of an API key for safe DB comparison."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def _load_user_cache() -> None:
    """Refresh the user cache from Supabase."""
    global _user_cache, _cache_timestamp
    try:
        sb = get_supabase()
        result = sb.table("api_users").select("id, label, api_key_hash, rate_limit").execute()
        with _cache_lock:
            _user_cache = {row["api_key_hash"]: row for row in result.data}
            _cache_timestamp = time.time()
    except Exception as e:
        logger.warning(f"Failed to load API user cache: {e}")


def _get_user(api_key: str) -> dict | None:
    """Look up a user by their raw API key. Returns user row or None."""
    global _cache_timestamp
    now = time.time()
    if now - _cache_timestamp > _CACHE_TTL:
        _load_user_cache()

    key_hash = _hash_key(api_key)
    with _cache_lock:
        return _user_cache.get(key_hash)


def verify_api_key(request: Request) -> dict | None:
    """FastAPI dependency: validate X-API-Key header. Returns user dict or raises 401."""
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    user = _get_user(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return user


def check_rate_limit(request: Request, user: dict | None = Depends(verify_api_key)) -> dict | None:
    """FastAPI dependency: enforce per-user rate limiting."""
    rate_limit = user["rate_limit"] if user else 30
    identifier = user["id"] if user else (request.client.host if request.client else "unknown")

    now = time.time()
    with _rate_lock:
        if identifier not in _request_log:
            _request_log[identifier] = deque()

        log = _request_log[identifier]
        # Prune entries older than 60 seconds
        while log and log[0] < now - 60:
            log.popleft()

        if len(log) >= rate_limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in a minute.")

        log.append(now)

    return user
