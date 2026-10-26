"""Execution venue: what we can actually buy, and what copying there costs.

A leader's trade is only worth following if we can take the same exposure.
On Hyperliquid that means a perpetual future held long at 1x as a proxy for
the leader's spot position. So, per token:

* map it to a listed (non-delisted) perp - by symbol, *confirmed by price*
  (the perp's mid must match the token's market price, or 1,000x for the
  "k" contracts such as kPEPE), so a look-alike token never maps;
* only count days after the perp was listed;
* charge funding (longs pay positive funding) and venue trading costs.

Anything we can't trade is held as cash in the copy, so the venue copy shows
the return we would really have captured. ETH-family and BTC wrappers map to
ETH and BTC directly; stablecoins are cash.
"""

from __future__ import annotations

import statistics as st
import time
from typing import Protocol

from .models import DAY
from .prices import STABLES, day_of
from .providers.http import Http

ETH_FAMILY = {"eth", "0xae7ab96520de3a18e5e111b5eaab095312d7fe84", "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",
              "0xae78736cd615f374d3085123a210448e74fc6393"}
BTC_FAMILY = {"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599", "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf"}


class Venue(Protocol):
    name: str
    cost_bps: float

    def coin_for(self, token: str, symbol: str, price: float | None) -> str | None: ...

    def listed_on(self, coin: str, day: int) -> bool: ...

    def funding_daily(self, coin: str, day: int) -> float: ...


class StaticVenue:
    """A fixed token -> coin map with constant funding; for demos and tests."""

    def __init__(self, coins: dict[str, str], funding_apr: float = 0.10, cost_bps: float = 10.0,
                 listed: dict[str, int] | None = None, name: str = "static"):
        self.coins, self.funding_apr, self.cost_bps = coins, funding_apr, cost_bps
        self.listed, self.name = listed or {}, name

    def coin_for(self, token, symbol, price):
        return self.coins.get(token)

    def listed_on(self, coin, day):
        return day >= self.listed.get(coin, 0)

    def funding_daily(self, coin, day):
        return self.funding_apr / 365


class Hyperliquid:
    URL = "https://api.hyperliquid.xyz/info"
    name = "Hyperliquid perps"

    def __init__(self, cost_bps: float = 10.0, funding_days: int = 90):
        """cost_bps: taker fee (~4.5 bps) plus slippage allowance. Funding is
        fetched for the last `funding_days`; older days use that average."""
        self.cost_bps = cost_bps
        self.http = Http(min_interval=0.25, cache_ttl=12 * 3600)
        meta = self.http.post_json(self.URL, {"type": "meta"})
        self.perps = {u["name"] for u in meta["universe"] if not u.get("isDelisted")}
        self.mids = {k: float(v) for k, v in self.http.post_json(self.URL, {"type": "allMids"}).items()
                     if not k.startswith("@")}
        self.funding_days = funding_days
        self._listing: dict[str, int] = {}
        self._funding: dict[str, dict[int, float]] = {}
        self._funding_avg: dict[str, float] = {}

    def coin_for(self, token: str, symbol: str, price: float | None) -> str | None:
        if token in STABLES:
            return None
        if token in ETH_FAMILY:
            return "ETH" if "ETH" in self.perps else None
        if token in BTC_FAMILY:
            return "BTC" if "BTC" in self.perps else None
        if not price or not symbol:
            return None
        sym = symbol.upper().lstrip("W") if symbol.upper() in ("WSOL", "WBNB") else symbol.upper()
        for coin, scale in ((sym, 1.0), ("k" + sym, 1000.0)):
            mid = self.mids.get(coin)
            if coin in self.perps and mid and 0.9 <= mid / (price * scale) <= 1.1:
                return coin
        return None

    def listed_on(self, coin: str, day: int) -> bool:
        if coin not in self._listing:
            rows = self.http.post_json(self.URL, {"type": "fundingHistory", "coin": coin, "startTime": 0})
            self._listing[coin] = day_of(int(rows[0]["time"]) // 1000) if rows else 0
        return day >= self._listing[coin]

    def funding_daily(self, coin: str, day: int) -> float:
        if coin not in self._funding:
            self._load_funding(coin)
        return self._funding[coin].get(day, self._funding_avg[coin])

    def _load_funding(self, coin: str) -> None:
        start_ms = int((time.time() - self.funding_days * DAY) * 1000)
        hourly: dict[int, list[float]] = {}
        while True:
            rows = self.http.post_json(self.URL, {"type": "fundingHistory", "coin": coin, "startTime": start_ms})
            for r in rows:
                hourly.setdefault(day_of(int(r["time"]) // 1000), []).append(float(r["fundingRate"]))
            if len(rows) < 500:
                break
            start_ms = int(rows[-1]["time"]) + 1
        daily = {d: sum(v) for d, v in hourly.items()}  # hourly rates summed = daily cost
        self._funding[coin] = daily
        self._funding_avg[coin] = st.fmean(daily.values()) if daily else 0.0


def venue_copy(res, venue: Venue, book, lag_days: int) -> tuple[list[float], dict[str, float]]:
    """Daily returns of copying the wallet on `venue`, plus fidelity metrics.

    Untradable (or not-yet-listed) exposure is held as cash. Returns
    (returns, {"tradable_share", "coins"}) where tradable_share is the
    time-averaged fraction of the wallet's non-stable book we could hold."""
    coin_of: dict[str, str | None] = {}

    def coin(tok: str, day: int) -> str | None:
        if tok not in coin_of:
            p = book.price(tok, day + DAY - 1)
            coin_of[tok] = venue.coin_for(tok, res.symbols.get(tok, ""), p)
        c = coin_of[tok]
        return c if c and venue.listed_on(c, day) else None

    out, held = [], {}
    shares = []
    for t, tok_ret in enumerate(res.token_returns):
        d = res.days[t]
        r = 0.0
        for tok, w in held.items():
            c = coin(tok, d)
            r += w * (tok_ret.get(tok, 0.0) - (venue.funding_daily(c, d) if c else 0.0))
        src = t - lag_days
        full = res.weights[src] if src >= 0 else {}
        risk = {k: v for k, v in full.items() if k not in STABLES}
        target = {k: v for k, v in risk.items() if coin(k, d)}
        if risk:
            shares.append(sum(target.values()) / sum(risk.values()))
        traded = sum(abs(target.get(k, 0.0) - held.get(k, 0.0)) for k in set(target) | set(held))
        out.append(r - traded * venue.cost_bps / 1e4)
        held = target
    coins = sorted({c for c in coin_of.values() if c})
    return out, {"tradable_share": st.fmean(shares) if shares else 1.0, "coins": coins}
