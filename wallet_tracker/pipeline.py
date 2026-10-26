"""Full study: analyse -> rank -> cluster -> reputation -> human/automated matrices."""

from __future__ import annotations

import statistics as st
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .analyze import WalletReport, analyze_wallet
from .cluster import Cluster, combine, find_clusters
from .config import Config
from .identity import Identity
from .metrics import compound
from .models import WalletClass, WalletHistory
from .operator_type import GROUPS, group
from .ranking import Leaderboards, build
from .regimes import REGIMES, MarketRegimes
from .reputation import assess, first_funder

BUY_HOLD_ROW = "buy-and-hold (reference)"
TRADER_CLASSES = {WalletClass.ACTIVE, WalletClass.BOT, WalletClass.DORMANT}


@dataclass
class Study:
    reports: list[WalletReport]
    boards: Leaderboards
    clusters: list[Cluster]
    regimes: MarketRegimes
    # group -> regime -> {"median_excess", "n"}
    operator_regime: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    # group -> "YYYY-Qn" -> {"median_return", "n"}
    operator_quarter: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    operator_summary: dict[str, dict[str, float]] = field(default_factory=dict)
    # group -> (days, equal-weight copy-basket daily returns)
    baskets: dict[str, tuple[list[int], list[float]]] = field(default_factory=dict)
    eth: tuple[list[int], list[float]] = field(default_factory=lambda: ([], []))


def _quarter(day: int) -> str:
    dt = datetime.fromtimestamp(day, timezone.utc)
    return f"{dt.year}-Q{(dt.month - 1) // 3 + 1}"


def run_study(histories: list[WalletHistory], series: dict[str, dict[int, float]], cfg: Config, now: int,
              identities: dict[str, Identity] | None = None, exchanges: dict[str, str] | None = None) -> Study:
    regimes = MarketRegimes(series.get("eth", {}))
    reports = [analyze_wallet(h, series, cfg, now, regimes) for h in histories]
    boards = build(reports, cfg)

    hist_by = {h.address: h for h in histories}
    funders = {r.address: first_funder(r.history, r.events) for r in reports}
    clusters = find_clusters([r for r in reports if r.wallet_class in TRADER_CLASSES | {WalletClass.BUY_HOLD}],
                             hist_by, funders)
    size = {}
    for c in clusters:
        for a in c.members:
            size[a] = len(c.members)
            next(r for r in reports if r.address == a).cluster_id = c.id

    identities = identities or {}
    for r in reports:
        r.identity = identities.get(r.address) or Identity()
        r.reputation = assess(r.history, r.events, r.metrics, r.identity, now,
                              size.get(r.address, 1), exchanges)
        r.group = group(r.operator_label, r.identity.kind or None)

    # Optional reputation gate on the ranked list.
    if cfg.eligibility.min_reputation > 0:
        keep = []
        for r in boards.active:
            if r.reputation.score < cfg.eligibility.min_reputation:
                r.eligible = False
                r.exclusions = [f"reputation {r.reputation.score:.0f} < {cfg.eligibility.min_reputation:.0f}"]
                boards.excluded.append(r)
            else:
                keep.append(r)
        boards.active = keep
        for i, r in enumerate(keep, 1):
            r.rank = i

    study = Study(reports, boards, clusters, regimes)
    _matrices(study)
    eth = series.get("eth", {})
    days = sorted(d for d in eth if d >= min((r.result.days[0] for r in reports if r.result.days), default=now))
    study.eth = (days, [eth[d] / eth[p] - 1 if p in eth else 0.0 for p, d in zip([days[0]] + days, days)])
    return study


def _rows(study: Study) -> dict[str, list[WalletReport]]:
    rows: dict[str, list[WalletReport]] = {g: [] for g in GROUPS}
    rows[BUY_HOLD_ROW] = []
    for r in study.reports:
        if r.wallet_class is WalletClass.BUY_HOLD:
            rows[BUY_HOLD_ROW].append(r)
        elif r.wallet_class in TRADER_CLASSES and r.metrics["history_days"] >= 60:
            rows[r.group].append(r)
    return {g: v for g, v in rows.items() if v}


def _matrices(study: Study) -> None:
    for g, members in _rows(study).items():
        cells = {}
        for reg in REGIMES + ["stress"]:
            vals = [r.regimes[reg]["ann_excess"] for r in members if r.regimes.get(reg, {}).get("days", 0) >= 10]
            if vals:
                cells[reg] = {"median_excess": st.median(vals), "n": len(vals)}
        study.operator_regime[g] = cells

        quarters: dict[str, list[float]] = {}
        for r in members:
            buckets: dict[str, list[float]] = {}
            for d, x, v in zip(r.result.days, r.result.returns, r.result.equity):
                if v > 0:
                    buckets.setdefault(_quarter(d), []).append(x)
            for q, xs in buckets.items():
                if len(xs) >= 45:
                    quarters.setdefault(q, []).append(compound(xs))
        study.operator_quarter[g] = {q: {"median_return": st.median(v), "n": len(v)}
                                     for q, v in sorted(quarters.items())}

        med = lambda k: st.median(r.metrics.get(k, 0.0) for r in members)  # noqa: E731
        study.operator_summary[g] = {
            "n": len(members), "median_cagr": med("cagr"), "median_sharpe": med("sharpe"),
            "median_max_drawdown": med("max_drawdown"), "median_copy_cagr": med("copy_cagr"),
            "median_regime_robustness": med("regime_robustness"),
            "median_human_score": st.median(r.operator["human_score"] for r in members),
            "significant": sum(bool(r.metrics.get("significant")) for r in members),
        }
        study.baskets[g] = combine(members, copy=True)
