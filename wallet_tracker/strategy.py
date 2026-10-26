"""Copy-trading strategy: pick leader entities, size them, and test it honestly.

Selection (all must hold for an entity to lead):
  * smart money: eligible, and passing the luck test or reputation tier A/B;
  * probably skilled: every scored member's deflated Sharpe >= `min_dsr`
    (0.8 by default: selection needs "likely", the 0.95 badge means "proven");
  * copyable: a one-day-late, cost-paying copy of the entity has a Sharpe
    of at least `min_copy_sharpe` (ratios of growth rates are unstable when
    returns are large, so the copy is judged on its own risk-adjusted terms);
  * robust: Regime Robustness Score above zero;
  * slow enough to follow: the edge's half-life under copying delay is at
    least `min_half_life_multiple` x our reaction time;
  * tradable: with an execution venue, at least `min_tradable_share` of the
    leader's risk book maps to instruments we can actually hold there, and
    the copy is judged on what the venue copy earns (funding and fees paid);
  * clean: no reputation red flags;
  * optionally identifiable: a named member (ENS, Farcaster, curated label).

Allocation: inverse volatility of each entity's copy returns, capped per
entity, with a cash buffer.

Walk-forward: rewind to `holdout_days` ago, run the whole study on data up
to then, pick and size leaders, then measure what copying them earned
*afterwards* - against ETH, against copying every eligible wallet, and
against naively copying the highest past returns.
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass, field

from .cluster import combine
from .config import Config
from .metrics import annualise, compound, max_drawdown
from .models import DAY, WalletHistory
from .pipeline import Study, is_smart, run_study


@dataclass
class Rules:
    min_dsr: float = 0.8
    min_copy_sharpe: float = 1.0
    reaction_days: float = 1.0          # how late we act; leaders' edges must outlast it
    min_half_life_multiple: float = 2.0  # edge half-life >= this x reaction_days
    min_tradable_share: float = 0.8     # of the leader's risk book we can hold on the venue
    min_rrs: float = 0.0
    allow_flags: bool = False
    require_identity: bool = False
    max_leaders: int = 8
    max_weight: float = 0.25
    cash_buffer: float = 0.10


@dataclass
class Leader:
    entity: str
    label: str
    members: list[str]
    weight: float
    stats: dict[str, float] = field(default_factory=dict)


def _entity_reports(study: Study, members: list[str]):
    return [r for r in study.reports if r.address in members]


def select(study: Study, rules: Rules) -> list[Leader]:
    picks = []
    for e in study.entities:
        rs = _entity_reports(study, e.members)
        scored = [r for r in rs if r.eligible]
        if not e.smart or not scored:
            continue
        if not all(r.metrics.get("dsr", 0.0) >= rules.min_dsr for r in scored):
            continue
        if st.median(r.metrics.get("edge_half_life_days", 0.0) for r in scored) < \
                rules.min_half_life_multiple * rules.reaction_days:
            continue
        if not all(is_smart(r) for r in scored):
            continue
        if not rules.allow_flags and any(r.reputation and r.reputation.flags for r in rs):
            continue
        if study.venue is not None and st.median(r.metrics.get("tradable_share", 0.0) for r in scored) \
                < rules.min_tradable_share:
            continue
        if rules.require_identity and not any(r.identity is not None and r.identity.attested for r in rs):
            continue
        attr = "venue_returns" if study.venue is not None else "copy_returns"
        days, copy = combine(scored, copy=True, attr=attr)
        _, actual = combine(scored, copy=False)
        live = [x for x in copy if x != 0]
        if len(live) < 60:
            continue
        a_cagr = annualise(compound(actual), len(actual))
        c_cagr = annualise(compound(copy), len(copy))
        vol = st.pstdev(live) or 1e-6
        copy_sharpe = st.fmean(live) / vol * math.sqrt(365)
        rrs = st.median(r.metrics.get("regime_robustness", 0.0) for r in scored)
        if copy_sharpe < rules.min_copy_sharpe or rrs <= rules.min_rrs:
            continue
        picks.append(Leader(e.id, e.label, e.members, 1 / vol,
                            {"copy_cagr": c_cagr, "cagr": a_cagr, "copy_sharpe": copy_sharpe, "rrs": rrs,
                             "daily_vol": vol, "reputation": e.reputation}))
    # Strongest copy record first, then size.
    picks.sort(key=lambda p: p.stats["copy_sharpe"], reverse=True)
    picks = picks[:rules.max_leaders]
    allocate(picks, rules)
    return picks


def allocate(picks: list[Leader], rules: Rules) -> None:
    """Inverse-vol weights, capped per entity, scaled to (1 - cash buffer)."""
    if not picks:
        return
    budget = 1.0 - rules.cash_buffer
    raw = {p.entity: p.weight for p in picks}
    w = {k: v / sum(raw.values()) * budget for k, v in raw.items()}
    for _ in range(10):  # water-fill the cap
        over = {k: v for k, v in w.items() if v > rules.max_weight}
        if not over:
            break
        spare = sum(v - rules.max_weight for v in over.values())
        free = {k: v for k, v in w.items() if v < rules.max_weight}
        for k in over:
            w[k] = rules.max_weight
        tot = sum(free.values())
        for k in free:
            w[k] += spare * free[k] / tot if tot else 0
    for p in picks:
        p.weight = w[p.entity]


def portfolio_returns(study: Study, leaders: list[Leader], after: int) -> tuple[list[int], list[float]]:
    """Daily copy returns of the weighted leaders after `after`; uninvested weight earns 0."""
    by_day: dict[int, float] = {}
    for p in leaders:
        days, rs = combine([r for r in study.reports if r.address in p.members], copy=True,
                           attr="venue_returns" if study.venue is not None else "copy_returns")
        for d, x in zip(days, rs):
            if d > after:
                by_day[d] = by_day.get(d, 0.0) + p.weight * x
    days = sorted(by_day)
    return days, [by_day[d] for d in days]


def _stats(rs: list[float]) -> dict[str, float]:
    if len(rs) < 2:
        return {"return": 0.0, "cagr": 0.0, "sharpe": 0.0, "max_drawdown": 0.0}
    sd = st.pstdev(rs)
    return {"return": compound(rs), "cagr": annualise(compound(rs), len(rs)),
            "sharpe": st.fmean(rs) / sd * math.sqrt(365) if sd else 0.0, "max_drawdown": max_drawdown(rs)}


def truncate(h: WalletHistory, cutoff: int) -> WalletHistory:
    return WalletHistory(h.address, [t for t in h.transfers if t.timestamp <= cutoff], h.is_contract,
                         h.label, list(h.deployed_contracts), h.truncated)


def walk_forward(histories: list[WalletHistory], series, cfg: Config, now: int, holdout_days: int,
                 rules: Rules, identities=None, exchanges=None, sector_map=None, venue=None,
                 routing: dict | None = None) -> dict:
    cutoff = now - holdout_days * DAY
    past = run_study([truncate(h, cutoff) for h in histories], series, cfg, cutoff, identities, exchanges,
                     sector_map, venue, routing)
    leaders = select(past, rules)
    full = run_study(histories, series, cfg, now, identities, exchanges, sector_map, venue, routing)
    cut_day = cutoff - cutoff % DAY

    _, ours = portfolio_returns(full, leaders, cut_day)
    # Leverage sized only on the copy portfolio's own past (pre-cutoff history
    # warms up the trailing estimates, results count only after the cutoff).
    warm_days, warm = portfolio_returns(full, leaders, cut_day - 180 * DAY)
    pre = [x for d, x in zip(warm_days, warm) if d <= cut_day]

    attr = "venue_returns" if venue is not None else "copy_returns"

    def equal_basket(addresses: list[str]):
        rs = [r for r in full.reports if r.address in addresses]
        days, x = combine(rs, copy=True, attr=attr) if rs else ([], [])
        return [v for d, v in zip(days, x) if d > cut_day]

    eligible = [r.address for r in past.boards.active]
    naive = [r.address for r in sorted(past.boards.active, key=lambda r: r.metrics["cagr"], reverse=True)
             [:max(len(leaders), 5)]]
    eth_days, eth = full.eth
    return {
        "cutoff": cutoff, "holdout_days": holdout_days,
        "leaders": leaders,
        "strategy": _stats(ours),
        "copy_all_eligible": _stats(equal_basket(eligible)),
        "copy_top_past_returns": _stats(equal_basket(naive)),
        "eth": _stats([x for d, x in zip(eth_days, eth) if d > cut_day]),
        "leverage": _levered(pre, ours),
        "past": past, "full": full,
    }


def funnel(study: Study, rules: Rules) -> list[dict]:
    """Wallets surviving each gate, in order; the last gate is replication.

    Each stage keeps the survivors of the one before it, so the drop at each
    step shows what that gate removes."""
    from .models import WalletClass
    m = lambda r, k, d=0.0: r.metrics.get(k, d)  # noqa: E731
    venue = study.venue is not None
    gates = [
        ("screened", lambda r: True),
        ("real active traders (not bots, contracts, exchanges, holders, dormant)",
         lambda r: r.wallet_class is WalletClass.ACTIVE),
        ("made money in dollars", lambda r: m(r, "pnl_usd") > 0),
        ("trades real markets (illiquid share <= 50%)", lambda r: m(r, "illiquid_share") <= 0.5),
        ("solid record (history, trades, size, no one-hit wonder)", lambda r: r.eligible),
        ("beats the market in USD, ETH and BTC terms", lambda r: m(r, "min_numeraire_sharpe") > 0),
        (f"passes the luck test (DSR >= {rules.min_dsr:.0%})", lambda r: m(r, "dsr") >= rules.min_dsr),
        ("robust across market regimes (RRS > 0)", lambda r: m(r, "regime_robustness") > rules.min_rrs),
        (f"edge survives a {rules.reaction_days:g}-day reaction (half-life >= "
         f"{rules.min_half_life_multiple * rules.reaction_days:g}d)",
         lambda r: m(r, "edge_half_life_days") >= rules.min_half_life_multiple * rules.reaction_days),
    ]
    if venue:
        gates += [
            (f"tradable on {study.venue.name} (>= {rules.min_tradable_share:.0%} of book)",
             lambda r: m(r, "tradable_share") >= rules.min_tradable_share),
            ("replicates faithfully (corr >= 0.6, keeps >= 50% of return, copy Sharpe >= "
             f"{rules.min_copy_sharpe:g})",
             lambda r: m(r, "replication_corr") >= 0.6 and m(r, "replication_capture") >= 0.5
             and m(r, "venue_copy_sharpe") >= rules.min_copy_sharpe),
        ]
    alive = list(study.reports)
    out = []
    for name, ok in gates:
        alive = [r for r in alive if ok(r)]
        out.append({"stage": name, "count": len(alive), "survivors": [r.address for r in alive]})
    return out


def _levered(pre: list[float], post: list[float]) -> list[dict]:
    """Each leverage policy applied with its sizing warmed up on `pre`,
    judged only on `post`."""
    from .leverage import DEFAULT_POLICIES, apply, stress
    out = []
    for pol in DEFAULT_POLICIES:
        res = apply(pre + post, pol)
        rs = res["returns"][len(pre):] if len(res["returns"]) > len(pre) else ([-1.0] if res["liquidated"] else [])
        row = {"policy": pol.name, "avg_leverage": res["avg_leverage"], "liquidated": res["liquidated"],
               **_stats(rs), "stress": stress(pre + post, pol)}
        out.append(row)
    return out
