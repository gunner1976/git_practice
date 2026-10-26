"""Group proxy: one portfolio that tracks a group of leader accounts.

For Hyperliquid leaders the positions are public and on the venue we trade,
so the proxy holds the *same* perps:

  1. each leader's book = signed notional per coin / account value;
  2. leaders are weighted by evidence and steadiness (luck-test confidence
     over volatility), capped per leader;
  3. books are combined and netted coin by coin (one long, one short = the
     group's net view);
  4. our limits are applied - max weight per coin and max gross exposure -
     then scaled to our capital.

`fidelity` rebuilds each leader's daily positions from its fills, runs the
proxy with a reaction delay, and compares it with what the leaders actually
earned over the same days: correlation, share of return kept, tracking
error. That number is the honest answer to "can we replicate the group?".
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass, field

from .models import DAY
from .providers.http import Http

URL = "https://api.hyperliquid.xyz/info"


@dataclass
class Book:
    address: str
    account_value: float
    weights: dict[str, float]          # coin -> signed notional / account value
    detail: dict[str, dict] = field(default_factory=dict)


class HyperliquidBooks:
    def __init__(self):
        self.http = Http(min_interval=0.25, cache_ttl=0)
        self.cached = Http(min_interval=0.25, cache_ttl=6 * 3600)

    def book(self, address: str, include_spot: bool = True) -> Book:
        """Positions as a share of the leader's wealth. With include_spot, idle
        stablecoins in the Hyperliquid spot wallet count as wealth too - it's
        collateral they chose not to risk, so weights reflect what share of
        their total they actually put on."""
        d = self.http.post_json(URL, {"type": "clearinghouseState", "user": address}, cache=False)
        av = float(d["marginSummary"]["accountValue"])
        if include_spot:
            spot = self.http.post_json(URL, {"type": "spotClearinghouseState", "user": address}, cache=False)
            av += sum(float(b["total"]) for b in spot.get("balances", [])
                      if b["coin"] in ("USDC", "USDT", "USDE", "USDHL", "USDT0"))
        w, det = {}, {}
        for ap in d.get("assetPositions", []):
            p = ap["position"]
            notional = float(p["positionValue"]) * (1 if float(p["szi"]) > 0 else -1)
            if av > 0:
                w[p["coin"]] = notional / av
            det[p["coin"]] = {"size": float(p["szi"]),  # signed "entry": float(p["entryPx"]),
                              "notional": notional, "leverage": p["leverage"]["value"],
                              "unrealized": float(p["unrealizedPnl"])}
        return Book(address.lower(), av, w, det)

    def fills(self, address: str, start_ms: int) -> list[dict]:
        """All fills since start_ms (paged; the API serves up to the latest 10,000)."""
        out, t = [], start_ms
        for _ in range(10):
            rows = self.cached.post_json(URL, {"type": "userFillsByTime", "user": address, "startTime": t})
            if not rows:
                break
            out += rows
            if len(rows) < 2000:
                break
            t = int(rows[-1]["time"]) + 1
        return sorted(out, key=lambda r: r["time"])

    def closes(self, coin: str, start: int, end: int, step: int = DAY) -> dict[int, float]:
        """Close prices keyed by bucket start (step = 86400 daily or 3600 hourly)."""
        interval = "1d" if step == DAY else "1h"
        rows = self.cached.post_json(URL, {"type": "candleSnapshot", "req": {
            "coin": coin, "interval": interval, "startTime": start * 1000, "endTime": end * 1000}})
        return {(int(r["t"]) // 1000) // step * step: float(r["c"]) for r in rows or []}

    def mids(self) -> dict[str, float]:
        return {k: float(v) for k, v in self.http.post_json(URL, {"type": "allMids"}, cache=False).items()
                if not k.startswith("@")}


def leader_weights(leaders: list[dict], max_weight: float = 0.35) -> dict[str, float]:
    """Evidence over volatility: min(luck vs ETH, luck vs BTC) / daily vol proxy, capped."""
    raw = {}
    for r in leaders:
        conf = min(r.get("dsr_vs_eth", 0.0), r.get("dsr_vs_btc", 0.0))
        risk = max(r.get("max_drawdown", 0.5), 0.05)
        raw[r["address"]] = conf / risk
    tot = sum(raw.values()) or 1.0
    w = {k: v / tot for k, v in raw.items()}
    for _ in range(10):
        over = {k: v for k, v in w.items() if v > max_weight}
        if not over:
            break
        spare = sum(v - max_weight for v in over.values())
        under = {k: v for k, v in w.items() if v < max_weight}
        for k in over:
            w[k] = max_weight
        tot_u = sum(under.values()) or 1.0
        for k in under:
            w[k] += spare * under[k] / tot_u
    return w


def combine_books(books: dict[str, dict[str, float]], alloc: dict[str, float],
                  max_coin: float = 0.35, max_gross: float = 1.5) -> dict[str, float]:
    """Net the leaders' books into one signed weight per coin, then apply limits."""
    net: dict[str, float] = {}
    for addr, w in books.items():
        for coin, x in w.items():
            net[coin] = net.get(coin, 0.0) + alloc.get(addr, 0.0) * x
    net = {c: max(-max_coin, min(max_coin, x)) for c, x in net.items() if abs(x) > 1e-4}
    gross = sum(abs(x) for x in net.values())
    if gross > max_gross:
        net = {c: x * max_gross / gross for c, x in net.items()}
    return net


def reconstruct(fills: list[dict], account_value: dict[int, float], closes: dict[str, dict[int, float]],
                days: list[int], step: int = DAY, current: dict[str, float] | None = None) -> list[dict[str, float]]:
    """End-of-bucket signed exposure per coin (notional / account value) from fills;
    `days` are bucket starts of length `step` (daily or hourly).

    `current` (coin -> signed size now) anchors positions that weren't traded
    inside the window: they were held at that size throughout."""
    pos: dict[str, float] = {}
    traded = {f["coin"] for f in fills}
    for coin, q in (current or {}).items():
        if coin not in traded:
            pos[coin] = q
    first_seen: dict[str, float] = {}
    by_day: dict[int, list[dict]] = {}
    for f in fills:
        t = int(f["time"]) // 1000
        by_day.setdefault(t - t % step, []).append(f)
        first_seen.setdefault(f["coin"], float(f["startPosition"]))
    pos.update(first_seen)                    # position held before the first fill in the window
    out = []
    for d in days:
        for f in by_day.get(d, []):
            sz = float(f["sz"]) * (1 if f["side"] == "B" else -1)
            pos[f["coin"]] = float(f["startPosition"]) + sz
        av = account_value.get(d)
        w = {}
        if av and av > 0:
            for coin, q in pos.items():
                px = closes.get(coin, {}).get(d)
                if px and abs(q) > 0:
                    w[coin] = q * px / av
        out.append(w)
    return out


def fidelity(books_by_day: dict[str, list[dict[str, float]]], actual: dict[str, list[float]],
             alloc: dict[str, float], closes: dict[str, dict[int, float]], days: list[int],
             lag_days: int = 1, cost_bps: float = 4.5, max_coin: float = 0.35, max_gross: float = 1.5,
             step: int = DAY) -> dict:
    """Run the group proxy `lag_days` buckets late; compare with the leaders' own returns.
    Buckets are `step` seconds (daily or hourly); results are annualised accordingly."""
    proxy, group = [], []
    held: dict[str, float] = {}
    for t, d in enumerate(days):
        r = 0.0
        for coin, w in held.items():
            c = closes.get(coin, {})
            p0, p1 = c.get(d - step), c.get(d)
            if p0 and p1:
                r += w * (p1 / p0 - 1)
        src = t - lag_days
        target = combine_books({a: b[src] for a, b in books_by_day.items()}, alloc, max_coin, max_gross) \
            if src >= 0 else {}
        turnover = sum(abs(target.get(k, 0) - held.get(k, 0)) for k in set(target) | set(held))
        proxy.append(r - turnover * cost_bps / 1e4)
        held = target
        group.append(sum(alloc[a] * actual[a][t] for a in actual))
    n = len(proxy)
    if n < 5:
        return {"days": n}
    mp, mg = st.fmean(proxy), st.fmean(group)
    sp, sg = st.pstdev(proxy), st.pstdev(group)
    corr = sum((a - mp) * (b - mg) for a, b in zip(proxy, group)) / n / (sp * sg) if sp and sg else 0.0
    gp = math.prod(1 + x for x in proxy) - 1
    gg = math.prod(1 + x for x in group) - 1
    ppy = 365 * DAY / step
    te = st.pstdev([a - b for a, b in zip(proxy, group)]) * math.sqrt(ppy)
    return {"days": n, "proxy_return": gp, "group_return": gg, "correlation": corr,
            "capture": gp / gg if gg > 0 else 0.0, "tracking_error": te,
            "proxy_sharpe": mp / sp * math.sqrt(ppy) if sp else 0.0,
            "group_sharpe": mg / sg * math.sqrt(ppy) if sg else 0.0}
