"""Where the money trades: label each swap with the venue it went through.

The venue is the contract the wallet called for the swap (a DEX router,
aggregator or Telegram trading-bot router). CoW Protocol trades are signed
off-chain and settled by solvers, so they're recognised by the settlement
contract appearing as the counterparty instead. Anything else is "direct /
other" (pool calls, private routers, smart-account execution).

Per venue the study reports how many wallets use it as their main venue, its
share of all and of smart-money swap volume by month (a trend: is the best
money moving between venues?), the median record of its main users, and the
top wallets that trade there.

Labels are best-effort; extend with --venue-labels file.json.
"""

from __future__ import annotations

import statistics as st
from collections import defaultdict
from datetime import datetime, timezone

from .models import EventKind
from .prices import PriceBook

COW_SETTLEMENT = "0x9008d19f58aabd9ed0d60971565aa8510560ab41"

VENUES = {
    "0x66a9893cc07d91d95644aedd05d03f95e1dba8af": "Uniswap",
    "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad": "Uniswap",
    "0x7a250d5630b4cf539739df2c5dacb4c659f2488d": "Uniswap",
    "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap",
    "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "Uniswap",
    "0x111111125421ca6dc452d289314280a0f8842a65": "1inch",
    "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch",
    "0x1111111254fb6c44bac0bed2854e76f90643097d": "1inch",
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "0x / Matcha",
    "0xdef171fe48cf0115b1d80b88dc8eab59176fee57": "ParaSwap",
    "0x6a000f20005980200259b80c5102003040001068": "ParaSwap",
    "0xcf5540fffcdc3d510b18bfca6d2b9987b0772559": "Odos",
    "0x6131b5fae19ea4f9d964eac0408e4408b66337b5": "KyberSwap",
    "0x881d40237659c251811cec9c364ef91dc08d300c": "MetaMask Swaps",
    "0xba12222222228d8ba445958a75a0704d566bf2c8": "Balancer",
    "0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49": "Banana Gun (Telegram bot)",
    "0x80a64c6d7f12c47b7c66c5b4e20e72bc1fcd5d9e": "Maestro (Telegram bot)",
    COW_SETTLEMENT: "CoW Protocol",
}
OTHER = "direct / other"


def label_swaps(report, book: PriceBook, labels: dict[str, str] | None = None) -> dict[str, dict[str, float]]:
    """{month: {venue: USD volume}} for one wallet's swaps."""
    names = {**VENUES, **{k.lower(): v for k, v in (labels or {}).items()}}
    hist = report.history
    cps: dict[str, set[str]] = defaultdict(set)
    for t in hist.transfers:
        cps[t.tx_hash].add(t.counterparty)
    out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for e in report.result.events:
        if e.kind is not EventKind.SWAP:
            continue
        venue = names.get(hist.tx_targets.get(e.tx_hash, ""))
        if venue is None:
            venue = "CoW Protocol" if COW_SETTLEMENT in cps[e.tx_hash] else OTHER
        usd = max(sum(a * (book.price(t, e.timestamp) or 0) for t, a in e.bought.items()),
                  sum(a * (book.price(t, e.timestamp) or 0) for t, a in e.sold.items()))
        month = datetime.fromtimestamp(e.timestamp, timezone.utc).strftime("%Y-%m")
        out[month][venue] += usd
    return {m: dict(v) for m, v in out.items()}


def venue_activity(reports: list, book: PriceBook, is_smart, labels: dict[str, str] | None = None) -> dict:
    """Per-venue usage, smart-money share trend and top wallets."""
    monthly_all: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    monthly_smart: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    users: dict[str, list] = defaultdict(list)
    for r in reports:
        if r.history is None or not any(e.kind is EventKind.SWAP for e in r.result.events):
            continue
        by_month = label_swaps(r, book, labels)
        totals: dict[str, float] = defaultdict(float)
        for month, vs in by_month.items():
            for v, usd in vs.items():
                totals[v] += usd
                monthly_all[month][v] += usd
                if is_smart(r):
                    monthly_smart[month][v] += usd
        if totals:
            r.venue_mix = {k: v / sum(totals.values()) for k, v in totals.items()}
            r.primary_venue = max(totals, key=totals.get)
            users[r.primary_venue].append(r)
    summary = {}
    for venue, rs in users.items():
        ranked = sorted([r for r in rs if r.eligible], key=lambda r: r.score, reverse=True)
        summary[venue] = {
            "primary_users": len(rs),
            "smart_users": sum(bool(is_smart(r)) for r in rs),
            "median_cagr": st.median(r.metrics.get("cagr", 0.0) for r in rs),
            "median_sharpe": st.median(r.metrics.get("sharpe", 0.0) for r in rs),
            "top": [(r.address, r.rank, r.score) for r in ranked[:5]],
        }
    share = {}
    for month, vs in monthly_smart.items():
        tot = sum(vs.values())
        share[month] = {v: x / tot for v, x in vs.items()} if tot else {}
    return {"summary": summary, "smart_share": dict(sorted(share.items())),
            "monthly_all": {m: dict(v) for m, v in sorted(monthly_all.items())},
            "monthly_smart": {m: dict(v) for m, v in sorted(monthly_smart.items())}}
