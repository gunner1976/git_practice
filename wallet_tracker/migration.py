"""Detect wallets that hand their book over to a new wallet.

A *migration* is a single withdrawal worth at least MIN_SHARE of the wallet's
value, sent to an address that is not a labelled exchange or mixer, after
which the old wallet stops trading. If the destination is also a screened
wallet that started out around then, the migration is *verified*: the two
are linked as one operator and their records are stitched into one.

Unverified destinations may be a fresh wallet, cold storage or an exchange
deposit address (those are unique per customer and unlabelled), so they are
reported as possible migrations only.
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass, field

from .labels import EXCHANGES, MIXERS
from .metrics import annualise, compound, max_drawdown
from .models import DAY, EventKind
from .prices import PriceBook, day_of
from .reconstruct import GAS

MIN_SHARE = 0.5
MIN_USD = 1_000.0
SERVICE_FANIN = 3   # a destination many screened wallets send to is a service (exchange, bridge), not a successor
MAX_SWAPS_AFTER = 3
SUCCESSOR_WINDOW_DAYS = 14


@dataclass
class Migration:
    source: str
    destination: str
    timestamp: int
    usd: float
    share: float
    verified: bool
    stitched: dict[str, float] = field(default_factory=dict)


def detect(reports: list, series: dict, exchanges: dict[str, str] | None = None) -> list[Migration]:
    labelled = set(EXCHANGES) | set(MIXERS) | set(exchanges or {})
    by_addr = {r.address: r for r in reports}
    first_seen = {r.address: min((t.timestamp for t in r.history.transfers), default=None) for r in reports}
    book = PriceBook(series)
    out: list[Migration] = []
    for r in reports:
        res = r.result
        if not res.days:
            continue
        day_idx = {d: i for i, d in enumerate(res.days)}
        swaps = [e.timestamp for e in res.events if e.kind is EventKind.SWAP]
        for e in res.events:
            if e.kind is not EventKind.WITHDRAWAL:
                continue
            usd = sum(-a * (book.price(t, e.timestamp) or 0.0) for t, a in e.legs.items())
            i = day_idx.get(day_of(e.timestamp), 0)
            before = res.equity[i - 1] if i else 0.0
            if before <= 0 or usd / before < MIN_SHARE or usd < MIN_USD:
                continue
            if sum(1 for ts in swaps if ts > e.timestamp) > MAX_SWAPS_AFTER:
                continue
            dests = [t for t in r.history.transfers if t.tx_hash == e.tx_hash and t.amount < 0
                     and t.counterparty and t.counterparty != GAS]
            if not dests:
                continue
            dest = max(dests, key=lambda t: -t.amount * (book.price(t.token, t.timestamp) or 0)).counterparty
            if dest in labelled or dest == r.address:
                continue
            fs = first_seen.get(dest)
            verified = dest in by_addr and fs is not None and fs >= e.timestamp - SUCCESSOR_WINDOW_DAYS * DAY
            m = Migration(r.address, dest, e.timestamp, usd, min(usd / before, 1.0), verified)
            if verified:
                m.stitched = stitch(r, by_addr[dest], e.timestamp)
            out.append(m)
            break
    fanin: dict[str, int] = {}
    for m in out:
        fanin[m.destination] = fanin.get(m.destination, 0) + 1
    return [m for m in out if m.verified or fanin[m.destination] < SERVICE_FANIN]


def stitch(old, new, at: int) -> dict[str, float]:
    """One track record: the old wallet up to the hand-over, the new one after."""
    cut = day_of(at)
    a = [x for d, x, v in zip(old.result.days, old.result.returns, old.result.equity) if d < cut and v > 0]
    b = [x for d, x in zip(new.result.days, new.result.returns) if d > cut]
    rs = a + b
    if len(rs) < 3:
        return {}
    sd = st.pstdev(rs)
    return {"days": len(rs), "cagr": annualise(compound(rs), len(rs)),
            "sharpe": st.fmean(rs) / sd * math.sqrt(365) if sd else 0.0, "max_drawdown": max_drawdown(rs)}


def universe_stats(migrations: list[Migration], reports: list) -> dict[str, float]:
    traders = [r for r in reports if r.metrics.get("swaps", 0) >= 5]
    return {"wallets": len(traders), "migrations": len(migrations),
            "verified": sum(m.verified for m in migrations),
            "rate": len(migrations) / len(traders) if traders else 0.0}
