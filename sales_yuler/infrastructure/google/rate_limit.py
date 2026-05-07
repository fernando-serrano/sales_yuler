import time
from dataclasses import dataclass, field
from typing import Callable


SECONDS_PER_MINUTE = 60.0
GOOGLE_SHEETS_USER_QUOTA_PER_MINUTE = 60
DEFAULT_REQUESTS_PER_MINUTE = 55


@dataclass
class RequestRateLimiter:
    requests_per_minute: int = DEFAULT_REQUESTS_PER_MINUTE
    clock: Callable[[], float] = time.monotonic
    sleeper: Callable[[float], None] = time.sleep
    _last_request_at: float | None = field(default=None, init=False, repr=False)

    def wait_for_slot(self) -> None:
        if self.requests_per_minute <= 0:
            raise ValueError("requests_per_minute debe ser mayor que cero")

        now = self.clock()
        if self._last_request_at is None:
            self._last_request_at = now
            return

        min_interval = SECONDS_PER_MINUTE / self.requests_per_minute
        elapsed = now - self._last_request_at
        remaining = min_interval - elapsed
        if remaining > 0:
            self.sleeper(remaining)
            now = self.clock()

        self._last_request_at = now


def build_read_rate_limiter() -> RequestRateLimiter:
    return RequestRateLimiter(requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE)


def build_write_rate_limiter() -> RequestRateLimiter:
    return RequestRateLimiter(requests_per_minute=DEFAULT_REQUESTS_PER_MINUTE)
