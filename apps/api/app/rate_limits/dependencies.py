from fastapi import Depends, HTTPException, Response, status
from redis.asyncio import Redis

from app.api_keys.models import ApiKey
from app.core.config import get_settings
from app.core.redis import get_redis
from app.protected_api.dependencies import require_api_key
from app.rate_limits.service import RateLimitResult, check_project_rate_limit


async def enforce_project_rate_limit(
    response: Response,
    api_key: ApiKey = Depends(require_api_key),
    redis: Redis = Depends(get_redis),
) -> RateLimitResult:
    settings = get_settings()
    result = await check_project_rate_limit(
        redis,
        project_id=api_key.project_id,
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers=result.headers,
        )

    for header_name, header_value in result.headers.items():
        response.headers[header_name] = header_value

    return result
