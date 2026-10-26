"""Copy-trading strategy: pick leader entities, size them, and test it honestly.

Selection (all must hold for an entity to lead):
  * smart money: eligible, and passing the luck test or reputation tier A/B;
  * probably skilled: every scored member's deflated Sharpe >= `min_dsr`
    (0.8 by default: selection needs "likely", the 0.95 badge means "proven");
  * copyable: a one-day-late, cost-paying copy of the entity has a Sharpe
    of at least `min_copy_sharpe` (ratios of growth rates are unstable when
    returns are large, so the copy is judged on its own risk-adjusted terms);
  * robust: Regime Robustness Score above zero;
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
        if not all(is_smart(r) for r in scored):
            continue
        if not rules.allow_flags and any(r.reputation and r.reputation.flags for r in rs):
            continue
        if rules.require_identity and not any(r.identity is not None and r.identity.attested for r in rs):
            continue
        days, copy = combine(scored, copy=True)
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
        days, rs = combine([r for r in study.reports if r.address in p.members], copy=True)
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
                 rules: Rules, identities=None, exchanges=None, sector_map=None) -> dict:
    cutoff = now - holdout_days * DAY
    past = run_study([truncate(h, cutoff) for h in histories], series, cfg, cutoff, identities, exchanges,
                     sector_map)
    leaders = select(past, rules)
    full = run_study(histories, series, cfg, now, identities, exchanges, sector_map)
    cut_day = cutoff - cutoff % DAY

    _, ours = portfolio_returns(full, leaders, cut_day)

    def equal_basket(addresses: list[str]):
        rs = [r for r in full.reports if r.address in addresses]
        days, x = combine(rs, copy=True) if rs else ([], [])
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
        "past": past, "full": full,
    }
