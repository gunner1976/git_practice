"""Eligibility gates, multiple-testing correction and composite scoring."""

from __future__ import annotations

import statistics as st
from dataclasses import dataclass

from .analyze import WalletReport
from .config import Config
from .metrics import expected_max_sharpe, probabilistic_sharpe
from .models import WalletClass


@dataclass
class Leaderboards:
    active: list[WalletReport]          # ranked, eligible active managers
    buy_hold: list[WalletReport]        # ranked holders, for comparison
    excluded: list[WalletReport]
    cohorts: dict[str, dict[str, float]]
    luck_sharpe: float                  # annualised Sharpe expected from luck alone


def _gates(r: WalletReport, cfg: Config) -> list[str]:
    e, m, out = cfg.eligibility, r.metrics, []
    if m["history_days"] < e.min_history_days:
        out.append(f"history {m['history_days']}d < {e.min_history_days}d")
    if m["closed_trades"] < e.min_closed_trades:
        out.append(f"{m['closed_trades']} closed trades < {e.min_closed_trades}")
    if m["avg_equity_usd"] < e.min_avg_equity_usd:
        out.append(f"avg equity ${m['avg_equity_usd']:,.0f} < ${e.min_avg_equity_usd:,.0f}")
    if m["price_coverage"] < e.min_price_coverage:
        out.append(f"price coverage {m['price_coverage']:.0%} < {e.min_price_coverage:.0%}")
    if m["top_trade_profit_share"] > e.max_top_trade_profit_share:
        out.append(f"one trade = {m['top_trade_profit_share']:.0%} of gross profit")
    if m.get("illiquid_share", 0.0) > e.max_illiquid_share:
        out.append(f"{m['illiquid_share']:.0%} of volume in tokens with no real market (manipulation-prone)")
    if e.require_dollar_profit and m.get("pnl_usd", 0.0) <= 0:
        out.append(f"lost money in dollars (${m.get('pnl_usd', 0.0):,.0f}) despite {m['total_return']:+.0%} TWR")
    if m["active_month_ratio"] < e.min_active_month_ratio:
        out.append(f"active in only {m['active_month_ratio']:.0%} of months")
    return out


def _percentiles(values: list[float], higher_is_better: bool) -> list[float]:
    """Average-rank percentile in [0, 1]; robust to outliers by construction."""
    n = len(values)
    if n == 1:
        return [1.0]
    order = sorted(range(n), key=lambda i: values[i] if higher_is_better else -values[i])
    pct = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        p = ((i + j) / 2) / (n - 1)
        for k in range(i, j + 1):
            pct[order[k]] = p
        i = j + 1
    return pct


def _deflate(reports: list[WalletReport], cfg: Config) -> float:
    """Deflated Sharpe ratio: test each Sharpe against the best Sharpe that
    `len(reports)` skill-less wallets would produce by chance. When you
    screen thousands of wallets, some look brilliant purely by luck."""
    if len(reports) < 2:
        sr_star = 0.0
    else:
        # Under the null (no skill) a Sharpe estimate over T days has variance
        # ~1/T, so the luck bar is the expected best of N such draws. Using the
        # cross-sectional spread instead would treat genuine skill differences
        # between wallets as noise and raise the bar for everyone.
        t_typ = st.median(r.metrics["history_days"] for r in reports) or 1
        sr_star = expected_max_sharpe(1.0 / t_typ, len(reports))
    for r in reports:
        m = r.metrics
        m["dsr"] = probabilistic_sharpe(m["sharpe_daily"], int(m["history_days"]),
                                        m["skew"], m["kurtosis"], sr_star)
        m["significant"] = float(m["dsr"] >= cfg.significance_level)
    return sr_star * (365 ** 0.5)


def score(reports: list[WalletReport], cfg: Config) -> None:
    if not reports:
        return
    total = {i: 0.0 for i in range(len(reports))}
    wsum = 0.0
    for metric, (w, hib) in cfg.weights.items():
        if metric not in reports[0].metrics:
            continue
        pct = _percentiles([r.metrics[metric] for r in reports], hib)
        for i, p in enumerate(pct):
            total[i] += w * p
        wsum += w
    for i, r in enumerate(reports):
        r.score = 100 * total[i] / wsum if wsum else 0.0


def _cohort(reports: list[WalletReport]) -> dict[str, float]:
    if not reports:
        return {"n": 0}
    med = lambda k: st.median(r.metrics[k] for r in reports)  # noqa: E731
    return {"n": len(reports), "median_cagr": med("cagr"), "median_sharpe": med("sharpe"),
            "median_max_drawdown": med("max_drawdown"), "median_active_premium": med("active_premium"),
            "median_alpha_vs_eth": med("alpha_vs_eth")}


def build(reports: list[WalletReport], cfg: Config) -> Leaderboards:
    active = [r for r in reports if r.wallet_class is WalletClass.ACTIVE]
    holders = [r for r in reports if r.wallet_class is WalletClass.BUY_HOLD]
    luck = _deflate(active + holders, cfg)

    eligible, excluded = [], []
    for r in reports:
        if r.wallet_class is not WalletClass.ACTIVE:
            r.exclusions = [f"class: {r.wallet_class.value}"] + r.reasons
            excluded.append(r)
            continue
        r.exclusions = _gates(r, cfg)
        r.eligible = not r.exclusions
        (eligible if r.eligible else excluded).append(r)

    score(eligible, cfg)
    # Statistically significant records first, then by composite score.
    eligible.sort(key=lambda r: (r.metrics["significant"], r.score), reverse=True)
    for i, r in enumerate(eligible, 1):
        r.rank = i

    holders.sort(key=lambda r: (r.metrics["sharpe"], r.metrics["cagr"]), reverse=True)
    cohorts = {
        "eligible_active": _cohort(eligible),
        "all_active": _cohort(active),
        "buy_hold": _cohort(holders),
        "bots": _cohort([r for r in reports if r.wallet_class is WalletClass.BOT]),
    }
    return Leaderboards(eligible, holders, excluded, cohorts, luck)
