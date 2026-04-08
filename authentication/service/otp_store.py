"""
otp_store.py
────────────
Thin abstraction over OTP storage.

• In development  (no REDIS_URL env var) → plain dict in memory.
• In production   (REDIS_URL is set)     → Redis with automatic TTL expiry.

Usage:
    from authentication.otp_store import otp_store

    otp_store.set(key, data_dict)
    record = otp_store.get(key)   # returns dict or None
    otp_store.delete(key)
"""

import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_REDIS_URL = os.getenv("REDIS_URL", "")
_OTP_TTL_SECONDS = 600   # 10 minutes — must match OTP_TTL_MINUTES in router


# ─── Serialisation helpers ────────────────────────────────────────────────────

def _serialize(data: dict) -> str:
    """Convert dict (including datetime values) to JSON string."""
    def default(obj):
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        raise TypeError(f"Type {type(obj)} not serialisable")
    return json.dumps(data, default=default)


def _deserialize(raw: str) -> dict:
    """Restore dict from JSON string, reviving datetime values."""
    def object_hook(obj):
        if "__datetime__" in obj:
            return datetime.fromisoformat(obj["__datetime__"])
        return obj
    return json.loads(raw, object_hook=object_hook)


# ─── Backend implementations ──────────────────────────────────────────────────

class _MemoryStore:
    """Simple in-memory store. Fine for a single-worker dev server."""

    def __init__(self):
        self._store: dict = {}

    def get(self, key: str) -> dict | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        # Lazy expiry
        if datetime.utcnow() > entry.get("expires", datetime.max):
            del self._store[key]
            return None
        return entry

    def set(self, key: str, data: dict) -> None:
        self._store[key] = data

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


class _RedisStore:
    """
    Redis-backed store. Requires:
        pip install redis
        REDIS_URL=redis://localhost:6379/0   (or your managed Redis URL)
    """

    def __init__(self, url: str):
        try:
            import redis
            self._client = redis.Redis.from_url(url, decode_responses=True)
            self._client.ping()
            logger.info("OTP store: connected to Redis at %s", url)
        except Exception as exc:
            logger.error("OTP store: Redis connection failed — falling back to memory. Error: %s", exc)
            self._client = None
            self._fallback = _MemoryStore()

    def get(self, key: str) -> dict | None:
        if self._client is None:
            return self._fallback.get(key)
        raw = self._client.get(f"otp:{key}")
        return _deserialize(raw) if raw else None

    def set(self, key: str, data: dict) -> None:
        if self._client is None:
            return self._fallback.set(key, data)
        self._client.setex(f"otp:{key}", _OTP_TTL_SECONDS, _serialize(data))

    def delete(self, key: str) -> None:
        if self._client is None:
            return self._fallback.delete(key)
        self._client.delete(f"otp:{key}")


# ─── Public singleton ─────────────────────────────────────────────────────────

if _REDIS_URL:
    otp_store = _RedisStore(_REDIS_URL)
    logger.info("OTP store: using Redis")
else:
    otp_store = _MemoryStore()
    logger.info("OTP store: using in-memory store (set REDIS_URL for production)")