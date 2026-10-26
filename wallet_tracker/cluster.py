"""Group wallets that are probably run by the same operator (an "entity").

Links between screened wallets, each with its evidence:

* transfer   - value moved directly between the two wallets;
* funder     - both were first funded by the same address, and that address
               is not an exchange and funded only a few of the screened wallets;
* co-trading - repeatedly bought the same token within the same hour
               (same operator, or one copying the other);
* migration  - one wallet handed its whole book to a newly started one
               (see migration.py).

Linked wallets are merged with union-find. A cluster's performance is the
value-weighted combination of its members; its copy performance is an
equal-weight basket of copying each member.
"""

from __future__ import annotations

import math
import statistics as st
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from .labels import EXCHANGES
from .metrics import annualise, compound, max_drawdown, PERIODS
from .models import EventKind
from .reconstruct import GAS

COTRADE_WINDOW = 3600
COTRADE_MIN = 5
COTRADE_SHARE = 0.3
FUNDER_MAX_FANOUT = 10


@dataclass
class Cluster:
    id: int
    members: list[str]
    evidence: list[str] = field(default_factory=list)
    days: list[int] = field(default_factory=list)
    returns: list[float] = field(default_factory=list)
    copy_returns: list[float] = field(default_factory=list)
    stats: dict[str, float] = field(default_factory=dict)


class _UF:
    def __init__(self, items):
        self.p = {i: i for i in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.find(a)] = self.find(b)


def _series_stats(rs: list[float]) -> dict[str, float]:
    if len(rs) < 3:
        return {"cagr": 0.0, "sharpe": 0.0, "max_drawdown": 0.0}
    sd = st.pstdev(rs)
    return {"cagr": annualise(compound(rs), len(rs)),
            "sharpe": st.fmean(rs) / sd * math.sqrt(PERIODS) if sd else 0.0,
            "max_drawdown": max_drawdown(rs)}


def combine(reports: list, copy: bool) -> tuple[list[int], list[float]]:
    """Value-weighted (actual) or equal-weighted (copy) daily returns."""
    by_day: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for r in reports:
        res = r.result
        series = r.copy_returns if copy else res.returns
        for i, d in enumerate(res.days):
            w = 1.0 if copy else (res.equity[i - 1] if i else 0.0)
            if (copy and res.equity[i] > 0) or w > 0:
                by_day[d].append((w, series[i]))
    days = sorted(by_day)
    out = []
    for d in days:
        tot = sum(w for w, _ in by_day[d])
        out.append(sum(w * x for w, x in by_day[d]) / tot if tot else 0.0)
    return days, out


def find_clusters(reports: list, histories: dict, funders: dict[str, str],
                  extra_links: list[tuple[str, str, str]] = ()) -> list[Cluster]:
    addrs = [r.address for r in reports]
    aset = set(addrs)
    uf = _UF(addrs)
    why: dict[tuple[str, str], str] = {}

    def link(a, b, reason):
        if a != b:
            uf.union(a, b)
            why.setdefault(tuple(sorted((a, b))), reason)

    for a, b, reason in extra_links:
        if a in aset and b in aset:
            link(a, b, reason)
    for a in addrs:
        for t in histories[a].transfers:
            if t.counterparty in aset and t.counterparty != a and t.counterparty != GAS:
                link(a, t.counterparty, "direct transfer")

    fanout = Counter(f for f in funders.values() if f)
    by_funder = defaultdict(list)
    for a, f in funders.items():
        if f and f not in EXCHANGES and f not in aset and fanout[f] <= FUNDER_MAX_FANOUT:
            by_funder[f].append(a)
    for f, group in by_funder.items():
        for b in group[1:]:
            link(group[0], b, f"common first funder {f[:6]}…{f[-4:]}")

    buys = {r.address: sorted((e.timestamp, t) for e in r.result.events if e.kind is EventKind.SWAP
                              for t in e.bought) for r in reports}
    for i, a in enumerate(addrs):
        for b in addrs[i + 1:]:
            if not buys[a] or not buys[b]:
                continue
            bt = defaultdict(list)
            for ts, tok in buys[b]:
                bt[tok].append(ts)
            hits = sum(any(abs(ts - x) <= COTRADE_WINDOW for x in bt.get(tok, ())) for ts, tok in buys[a])
            if hits >= COTRADE_MIN and hits >= COTRADE_SHARE * min(len(buys[a]), len(buys[b])):
                link(a, b, f"co-trading ({hits} same-token buys within 1h)")

    groups = defaultdict(list)
    for a in addrs:
        groups[uf.find(a)].append(a)
    by_addr = {r.address: r for r in reports}
    clusters = []
    for members in groups.values():
        if len(members) < 2:
            continue
        cl = Cluster(len(clusters) + 1, sorted(members))
        sh = lambda a: f"{a[:6]}…{a[-4:]}"  # noqa: E731
        cl.evidence = sorted({f"{sh(p[0])} ↔ {sh(p[1])}: {w}" for p, w in why.items()
                              if p[0] in members})
        rs = [by_addr[a] for a in members]
        cl.days, cl.returns = combine(rs, copy=False)
        _, cl.copy_returns = combine(rs, copy=True)
        live = next((i for i, d in enumerate(cl.days) if cl.returns[i] != 0), 0)
        s, cs = _series_stats(cl.returns[live:]), _series_stats(cl.copy_returns[live:])
        cl.stats = {**s, **{f"copy_{k}": v for k, v in cs.items()}, "members": len(members)}
        clusters.append(cl)
    return clusters
