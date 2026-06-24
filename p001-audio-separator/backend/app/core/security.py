"""Security utilities: token generation and rate limiting."""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import TYPE_CHECKING

import redis.asyncio as aioredis

from app.core.config import settings

if TYPE_CHECKING:
    from redis.asyncio import Redis


def generate_task_token(task_id: str) -> str:
    """Generate a unique download token for a task.

    Uses SHA-256 of task_id + random salt to produce an unguessable token.
    """
    salt = secrets.token_hex(32)
    return hashlib.sha256(f"{task_id}:{salt}".encode()).hexdigest()


def generate_task_id() -> str:
    """Generate a short, URL-safe unique task ID."""
    return secrets.token_urlsafe(12)


async def get_redis() -> Redis:  # type: ignore[misc]
    """Create and return a Redis connection."""
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def check_rate_limit(ip: str, redis: Redis) -> tuple[bool, int]:
    """Check if the given IP has exceeded the rate limit.

    Returns:
        (allowed, remaining): whether the request is allowed and how many remain.
    """
    key = f"rate_limit:{ip}"
    now = int(time.time())
    window_start = now - 3600  # 1 hour window

    # Remove entries older than 1 hour
    await redis.zremrangebyscore(key, 0, window_start)

    # Count requests in current window
    count: int = await redis.zcard(key)  # type: ignore[assignment]

    if count >= settings.RATE_LIMIT_PER_HOUR:
        return False, 0

    # Add current request timestamp
    await redis.zadd(key, {str(now): now})
    await redis.expire(key, 3600)

    remaining = settings.RATE_LIMIT_PER_HOUR - count - 1
    return True, remaining


async def get_rate_limit_headers(ip: str, redis: Redis) -> dict[str, str]:
    """Get rate limit HTTP headers."""
    allowed, remaining = await check_rate_limit(ip, redis)
    return {
        "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_HOUR),
        "X-RateLimit-Remaining": str(remaining),
    }
