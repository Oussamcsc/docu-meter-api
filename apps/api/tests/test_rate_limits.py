import pytest

from app.rate_limits.service import (
    build_project_rate_limit_key,
    check_project_rate_limit,
    get_window_start_epoch,
)


class FakeRedis:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.expirations: dict[str, int] = {}

    async def eval(self, _script: str, _numkeys: int, key: str, ttl_seconds: int) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        if self.counts[key] == 1:
            self.expirations[key] = ttl_seconds
        return self.counts[key]


@pytest.mark.anyio
async def test_project_rate_limit_allows_until_limit_then_blocks() -> None:
    redis = FakeRedis()
    now_epoch = 1778704596
    window_start = get_window_start_epoch(now_epoch, 60)
    key = build_project_rate_limit_key(project_id="project-1", window_start_epoch=window_start)

    first = await check_project_rate_limit(
        redis,
        project_id="project-1",
        limit=2,
        window_seconds=60,
        now_epoch=now_epoch,
    )
    second = await check_project_rate_limit(
        redis,
        project_id="project-1",
        limit=2,
        window_seconds=60,
        now_epoch=now_epoch,
    )
    third = await check_project_rate_limit(
        redis,
        project_id="project-1",
        limit=2,
        window_seconds=60,
        now_epoch=now_epoch,
    )

    assert first.allowed is True
    assert first.headers["X-RateLimit-Remaining"] == "1"
    assert second.allowed is True
    assert second.headers["X-RateLimit-Remaining"] == "0"
    assert third.allowed is False
    assert third.headers["X-RateLimit-Remaining"] == "0"
    assert third.headers["Retry-After"] == str(third.reset_epoch - now_epoch)
    assert redis.expirations[key] == 65
