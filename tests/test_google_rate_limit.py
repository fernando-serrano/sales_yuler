import pytest

from sales_yuler.infrastructure.google.rate_limit import RequestRateLimiter


def test_request_rate_limiter_does_not_sleep_on_first_request():
    sleeps: list[float] = []
    limiter = RequestRateLimiter(
        requests_per_minute=60,
        clock=lambda: 100.0,
        sleeper=sleeps.append,
    )

    limiter.wait_for_slot()

    assert sleeps == []


def test_request_rate_limiter_waits_until_min_interval_is_met():
    sleeps: list[float] = []
    timestamps = iter([100.0, 100.2, 101.0])
    limiter = RequestRateLimiter(
        requests_per_minute=60,
        clock=lambda: next(timestamps),
        sleeper=sleeps.append,
    )

    limiter.wait_for_slot()
    limiter.wait_for_slot()

    assert sleeps == [pytest.approx(0.8)]
