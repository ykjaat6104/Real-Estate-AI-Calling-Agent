"""Redis-based rate limiting."""
import time
from typing import Optional

import redis.asyncio as redis
from fastapi import Request, HTTPException, Depends

from app.config import get_settings
from app.models.user import User
from app.core.security import get_current_user

settings = get_settings()


class RateLimiter:
    """Rate limiter using Redis sorted sets."""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60,
    ) -> bool:
        """Check if a request is within rate limit. Returns True if allowed."""
        now = time.time()
        window_start = now - window_seconds

        pipe = self.redis.pipeline()
        # Remove old entries outside the window
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiry on the key
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[2]

        return request_count <= limit

    async def check_tenant_rate_limit(
        self,
        tenant_id: str,
        limit: int = 1000,
        window_seconds: int = 3600,
    ) -> bool:
        """Check tenant-level rate limit (per hour)."""
        key = f"rate_limit:tenant:{tenant_id}"
        return await self.check_rate_limit(key, limit, window_seconds)

    async def check_user_rate_limit(
        self,
        user_id: str,
        limit: int = 60,
        window_seconds: int = 60,
    ) -> bool:
        """Check user-level rate limit (per minute)."""
        key = f"rate_limit:user:{user_id}"
        return await self.check_rate_limit(key, limit, window_seconds)


async def get_redis() -> redis.Redis:
    """Dependency that provides a Redis client."""
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


async def rate_limit_dependency(
    request: Request,
    user: User = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis),
):
    """FastAPI dependency for rate limiting."""
    limiter = RateLimiter(redis_client)

    # Check user rate limit
    allowed = await limiter.check_user_rate_limit(
        str(user.id),
        limit=user.tenant.rate_limit_per_minute if hasattr(user, 'tenant') else settings.RATE_LIMIT_PER_MINUTE,
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    # Check tenant rate limit
    tenant_allowed = await limiter.check_tenant_rate_limit(
        str(user.tenant_id),
        limit=settings.RATE_LIMIT_PER_TENANT_PER_HOUR,
    )
    if not tenant_allowed:
        raise HTTPException(
            status_code=429,
            detail="Tenant rate limit exceeded. Please contact support.",
        )
