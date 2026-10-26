"""Daily USD price lookup with forward-fill and trade-implied fallback."""

from __future__ import annotations

import bisect
from typing import Protocol

from .models import DAY

STABLES = {
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
    "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
    "0x6b175474e89094c44da98b954eedeac495271d0f",  # DAI
    "usd",
}


def day_of(ts: int) -> int:
    return ts - ts % DAY


class PriceSource(Protocol):
    def daily_prices(self, tokens: set[str], start: int, end: int) -> dict[str, dict[int, float]]:
        """Return {token: {day_ts: usd_price}} covering [start, end]."""
        ...


class PriceBook:
    """Resolves the USD price of a token at a given time.

    Order of preference: market price for that day (forward-filled up to
    `max_stale_days`), then the most recent price implied by one of the
    wallet's own swaps against a priced asset. Unpriced lookups are counted
    so callers can gate on price coverage.
    """

    def __init__(self, series: dict[str, dict[int, float]], max_stale_days: int = 7):
        self._days = {t: sorted(s) for t, s in series.items()}
        self._series = series
        self._implied: dict[str, list[tuple[int, float]]] = {}
        self.max_stale = max_stale_days * DAY

    def market(self, token: str, ts: int) -> float | None:
        if token in STABLES:
            return 1.0
        days = self._days.get(token)
        if not days:
            return None
        i = bisect.bisect_right(days, day_of(ts)) - 1
        if i < 0 or day_of(ts) - days[i] > self.max_stale:
            return None
        return self._series[token][days[i]]

    def price(self, token: str, ts: int) -> float | None:
        p = self.market(token, ts)
        if p is not None:
            return p
        implied = self._implied.get(token)
        if implied:
            i = bisect.bisect_right(implied, (ts, float("inf"))) - 1
            if i >= 0:
                return implied[i][1]
        return None

    def record_implied(self, token: str, ts: int, price: float) -> None:
        if price > 0 and self.market(token, ts) is None:
            bisect.insort(self._implied.setdefault(token, []), (ts, price))
