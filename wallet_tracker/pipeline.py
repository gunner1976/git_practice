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
from .migration import Migration, detect as detect_migrations, universe_stats
from .prices import PriceBook
from .reputation import assess, first_funder
from .sectors import SectorMap, exposure, flows

BUY_HOLD_ROW = "buy-and-hold (reference)"

# Size tiers by capital put in (peak cumulative net deposits), not by
# balance: a minnow that compounds into a whale stays a minnow here, so
# skill can't masquerade as size.
SIZE_TIERS = [("minnow (<$50k)", 0), ("fish ($50k–250k)", 50_000), ("dolphin ($250k–1M)", 250_000),
              ("shark ($1M–10M)", 1_000_000), ("whale ($10M+)", 10_000_000)]


def size_tier(avg_equity: float) -> str:
    name = SIZE_TIERS[0][0]
    for label, floor in SIZE_TIERS:
        if avg_equity >= floor:
            name = label
    return name
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
    migrations: list[Migration] = field(default_factory=list)
    migration_stats: dict[str, float] = field(default_factory=dict)
    entities: list["Entity"] = field(default_factory=list)
    # month -> sector -> net USD bought, for "smart money" and for all traders
    flows_smart: dict[str, dict[str, float]] = field(default_factory=dict)
    flows_all: dict[str, dict[str, float]] = field(default_factory=dict)
    size_summary: dict[str, dict[str, float]] = field(default_factory=dict)
    size_regime: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    size_baskets: dict[str, tuple[list[int], list[float]]] = field(default_factory=dict)
    venue: object = None
    frequency_summary: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass
class Entity:
    """A cluster of linked wallets, or a single unlinked wallet."""
    id: str
    label: str
    members: list[str]
    aum_usd: float
    sectors: dict[str, float]          # latest value-weighted sector mix
    sectors_avg: dict[str, float]      # time-weighted mix over the record
    group: str
    reputation: float
    tier: str
    cagr: float
    sharpe: float
    smart: bool


def _quarter(day: int) -> str:
    dt = datetime.fromtimestamp(day, timezone.utc)
    return f"{dt.year}-Q{(dt.month - 1) // 3 + 1}"


def is_smart(r: WalletReport) -> bool:
    """Eligible and either luck-tested or reputable: the cohort whose flows we follow."""
    return r.eligible and (bool(r.metrics.get("significant")) or
                           (r.reputation is not None and r.reputation.tier in ("A", "B")))


def run_study(histories: list[WalletHistory], series: dict[str, dict[int, float]], cfg: Config, now: int,
              identities: dict[str, Identity] | None = None, exchanges: dict[str, str] | None = None,
              sector_map: SectorMap | None = None, venue=None) -> Study:
    regimes = MarketRegimes(series.get("eth", {}))
    reports = [analyze_wallet(h, series, cfg, now, regimes) for h in histories]
    if venue is not None:
        _venue_fidelity(reports, venue, PriceBook(series), cfg)
    boards = build(reports, cfg)

    hist_by = {h.address: h for h in histories}
    funders = {r.address: first_funder(r.history, r.events) for r in reports}
    traders = [r for r in reports if r.wallet_class in TRADER_CLASSES | {WalletClass.BUY_HOLD}]
    migrations = detect_migrations(traders, series, exchanges)
    clusters = find_clusters(traders, hist_by, funders,
                             [(m.source, m.destination, "verified migration (whole book handed over)")
                              for m in migrations if m.verified])
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
    study.venue = venue
    study.migrations, study.migration_stats = migrations, universe_stats(migrations, traders)
    _matrices(study)
    _capital_map(study, sector_map or SectorMap(), PriceBook(series))
    _size_cohorts(study)
    _frequency_cohorts(study)
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


def _capital_map(study: Study, smap: SectorMap, book: PriceBook) -> None:
    """Sector exposure per wallet and entity, and sector flows by month."""
    by_addr = {r.address: r for r in study.reports}
    for r in study.reports:
        r.sectors = exposure(r, smap)

    def add(dst, src):
        for month, secs in src.items():
            for sec, usd in secs.items():
                dst.setdefault(month, {}).setdefault(sec, 0.0)
                dst[month][sec] += usd

    for r in study.reports:
        if r.wallet_class not in TRADER_CLASSES:
            continue
        f = flows(r, smap, book.price)
        add(study.flows_all, f)
        if is_smart(r):
            add(study.flows_smart, f)

    groups = [(f"cluster-{c.id}", c.members) for c in study.clusters]
    clustered = {a for c in study.clusters for a in c.members}
    groups += [(r.address, [r.address]) for r in study.reports
               if r.address not in clustered and r.wallet_class in TRADER_CLASSES]
    for eid, members in groups:
        rs = [by_addr[a] for a in members]
        aum = sum(r.result.final_equity for r in rs)
        latest: dict[str, float] = {}
        avg: dict[str, float] = {}
        for r in rs:
            w = r.result.final_equity / aum if aum else 1 / len(rs)
            for k, v in r.sectors["latest"].items():
                latest[k] = latest.get(k, 0.0) + w * v
            for k, v in r.sectors["average"].items():
                avg[k] = avg.get(k, 0.0) + v / len(rs)
        named = next((r.identity.name for r in rs if r.identity is not None and r.identity.name), "")
        label = named or (f"Cluster {eid.split('-')[1]}" if eid.startswith("cluster") else eid[:6] + "…" + eid[-4:])
        best = max(rs, key=lambda r: r.reputation.score)
        cl = next((c for c in study.clusters if f"cluster-{c.id}" == eid), None)
        stats = cl.stats if cl else best.metrics
        groups_seen = [r.group for r in rs]
        study.entities.append(Entity(
            eid, label, members, aum, latest, avg, max(set(groups_seen), key=groups_seen.count),
            best.reputation.score, best.reputation.tier, stats["cagr"], stats["sharpe"],
            any(is_smart(r) for r in rs)))
    study.entities.sort(key=lambda e: (e.smart, e.reputation), reverse=True)


def _size_cohorts(study: Study) -> None:
    """Whales vs minnows: the same metrics, cut by how much money a wallet runs."""
    for r in study.reports:
        r.size_tier = size_tier(r.metrics.get("capital_in_usd", 0.0))
    traders = [r for r in study.reports if r.wallet_class is WalletClass.ACTIVE
               and r.metrics["history_days"] >= 60 and r.metrics.get("closed_trades", 0) >= 5]
    for label, _ in SIZE_TIERS:
        members = [r for r in traders if r.size_tier == label]
        if not members:
            continue
        med = lambda k: st.median(r.metrics.get(k, 0.0) for r in members)  # noqa: E731
        sig = sum(bool(r.metrics.get("significant")) for r in members)
        study.size_summary[label] = {
            "n": len(members), "median_cagr": med("cagr"), "median_sharpe": med("sharpe"),
            "median_max_drawdown": med("max_drawdown"), "median_regime_robustness": med("regime_robustness"),
            "median_copy_cagr": med("copy_cagr"), "significant": sig, "significant_rate": sig / len(members),
            "pct_beating_eth": sum(r.metrics.get("alpha_vs_eth", 0) > 0 for r in members) / len(members),
            "median_pnl_usd": med("pnl_usd"), "total_pnl_usd": sum(r.metrics.get("pnl_usd", 0.0) for r in members),
            "human_share": sum(r.operator.get("human_score", 0.5) >= 0.6 for r in members) / len(members),
        }
        cells = {}
        for reg in REGIMES + ["stress"]:
            vals = [r.regimes[reg]["ann_excess"] for r in members if r.regimes.get(reg, {}).get("days", 0) >= 10]
            if vals:
                cells[reg] = {"median_excess": st.median(vals), "n": len(vals)}
        study.size_regime[label] = cells
        study.size_baskets[label] = combine(members, copy=True)


def _frequency_cohorts(study: Study) -> None:
    """How fast each kind of trader's edge decays when copied late."""
    from .analyze import FREQUENCY_TIERS, LAGS
    traders = [r for r in study.reports if r.wallet_class in (WalletClass.ACTIVE, WalletClass.BOT)
               and r.metrics["history_days"] >= 60]
    for label, _ in FREQUENCY_TIERS:
        members = [r for r in traders if r.frequency_tier == label]
        if not members:
            continue
        med = lambda k: st.median(r.metrics.get(k, 0.0) for r in members)  # noqa: E731
        sig = sum(bool(r.metrics.get("significant")) for r in members)
        row = {"n": len(members), "median_cagr": med("cagr"), "median_sharpe": med("sharpe"),
               "median_hold_days": med("median_hold_days"), "median_swaps_per_month": med("swaps_per_month"),
               "significant": sig, "significant_rate": sig / len(members),
               "median_half_life": med("edge_half_life_days"),
               "human_share": sum(r.operator.get("human_score", 0.5) >= 0.6 for r in members) / len(members)}
        for lag in LAGS:
            row[f"copy_sharpe_lag{lag}"] = med(f"copy_sharpe_lag{lag}")
        study.frequency_summary[label] = row


def _venue_fidelity(reports: list[WalletReport], venue, book: PriceBook, cfg: Config) -> None:
    """Copy each trader on the execution venue and measure what survives."""
    import math
    from .metrics import live_window
    from .venue import venue_copy
    for r in reports:
        if r.wallet_class not in TRADER_CLASSES | {WalletClass.BUY_HOLD}:
            continue
        rs, info = venue_copy(r.result, venue, book, cfg.copy_lag_days)
        r.venue_returns, r.venue_coins = rs, info["coins"]
        i0 = live_window(r.result)
        v, c = rs[i0:], r.copy_returns[i0:]
        m = r.metrics
        m["tradable_share"] = info["tradable_share"]
        sd = st.pstdev(v) if len(v) > 2 else 0.0
        m["venue_copy_sharpe"] = st.fmean(v) / sd * math.sqrt(365) if sd else 0.0
        m["venue_copy_cagr"] = annualise_safe(v)
        diff = [a - b for a, b in zip(v, c)]
        m["venue_tracking_error"] = st.pstdev(diff) * math.sqrt(365) if len(diff) > 2 else 0.0
        sv, sc = st.pstdev(v) if len(v) > 2 else 0, st.pstdev(c) if len(c) > 2 else 0
        m["venue_fidelity"] = (sum((a - st.fmean(v)) * (b - st.fmean(c)) for a, b in zip(v, c)) / len(v) / (sv * sc)
                               if sv and sc else 0.0)


def annualise_safe(rs: list[float]) -> float:
    from .metrics import annualise
    return annualise(compound(rs), len(rs)) if rs else 0.0
