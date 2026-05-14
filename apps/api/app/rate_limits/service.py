from dataclasses import dataclass
from time import time

from redis.asyncio import Redis

RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
  redis.call("EXPIRE", KEYS[1], ARGV[1])
end
return current
"""


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    reset_epoch: int
    retry_after: int
    headers: dict[str, str]


def get_window_start_epoch(now_epoch: int, window_seconds: int) -> int:
    return now_epoch - (now_epoch % window_seconds)


def build_project_rate_limit_key(
    *,
    project_id: str,
    window_start_epoch: int,
) -> str:
    return f"rate_limit:project:{project_id}:window:{window_start_epoch}"


async def check_project_rate_limit(
    redis: Redis,
    *,
    project_id: str,
    limit: int,
    window_seconds: int,
    now_epoch: int | None = None,
) -> RateLimitResult:
    if limit < 1:
        raise ValueError("Rate limit must be at least 1")
    if window_seconds < 1:
        raise ValueError("Rate-limit window must be at least 1 second")

    current_epoch = int(time()) if now_epoch is None else now_epoch
    window_start_epoch = get_window_start_epoch(current_epoch, window_seconds)
    reset_epoch = window_start_epoch + window_seconds
    key = build_project_rate_limit_key(
        project_id=project_id,
        window_start_epoch=window_start_epoch,
    )

    ttl_seconds = window_seconds + 5
    request_count = int(await redis.eval(RATE_LIMIT_SCRIPT, 1, key, ttl_seconds))

    allowed = request_count <= limit
    remaining = max(limit - request_count, 0)
    retry_after = max(reset_epoch - current_epoch, 0) if not allowed else 0
    headers = {
        "X-RateLimit-Limit": str(limit),
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_epoch),
    }
    if not allowed:
        headers["Retry-After"] = str(retry_after)

    return RateLimitResult(
        allowed=allowed,
        limit=limit,
        remaining=remaining,
        reset_epoch=reset_epoch,
        retry_after=retry_after,
        headers=headers,
    )
