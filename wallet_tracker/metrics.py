"""Performance, risk, skill-significance, trade and activity metrics."""

from __future__ import annotations

import math
import statistics as st
import time
from collections import defaultdict
from datetime import datetime, timezone

from .models import DAY, EventKind
from .portfolio import MIN_CAPITAL_USD, PortfolioResult

PERIODS = 365  # crypto trades every day
EULER_GAMMA = 0.5772156649


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    return st.NormalDist().inv_cdf(min(max(p, 1e-12), 1 - 1e-12))


def compound(rs: list[float]) -> float:
    g = 1.0
    for r in rs:
        g *= 1.0 + r
    return g - 1.0


def max_drawdown(rs: list[float]) -> float:
    peak = g = 1.0
    worst = 0.0
    for r in rs:
        g *= 1.0 + r
        peak = max(peak, g)
        worst = min(worst, g / peak - 1.0)
    return -worst


def ulcer_index(rs: list[float]) -> float:
    peak = g = 1.0
    sq = []
    for r in rs:
        g *= 1.0 + r
        peak = max(peak, g)
        sq.append((100 * (g / peak - 1.0)) ** 2)
    return math.sqrt(sum(sq) / len(sq)) if sq else 0.0


def moments(rs: list[float]) -> tuple[float, float, float, float]:
    """mean, stdev, skew, (non-excess) kurtosis."""
    n = len(rs)
    if n < 3:
        return (st.fmean(rs) if rs else 0.0), 0.0, 0.0, 3.0
    m = st.fmean(rs)
    sd = st.pstdev(rs, m)
    if sd == 0:
        return m, 0.0, 0.0, 3.0
    skew = sum((r - m) ** 3 for r in rs) / n / sd ** 3
    kurt = sum((r - m) ** 4 for r in rs) / n / sd ** 4
    return m, sd, skew, kurt


def probabilistic_sharpe(sr: float, n: int, skew: float, kurt: float, sr_star: float = 0.0) -> float:
    """P(true Sharpe > sr_star) given an observed per-period Sharpe `sr`
    (Bailey & Lopez de Prado, 2012). Penalises short, skewed, fat-tailed
    track records - exactly where lucky wallets hide."""
    if n < 3:
        return 0.0
    denom = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if denom <= 0:
        return 0.0
    return norm_cdf((sr - sr_star) * math.sqrt(n - 1) / math.sqrt(denom))


def expected_max_sharpe(sr_variance: float, n_trials: int) -> float:
    """Sharpe the best of `n_trials` skill-less strategies would show by luck."""
    if n_trials < 2 or sr_variance <= 0:
        return 0.0
    return math.sqrt(sr_variance) * (
        (1 - EULER_GAMMA) * norm_ppf(1 - 1 / n_trials)
        + EULER_GAMMA * norm_ppf(1 - 1 / (n_trials * math.e)))


def ols_beta(y: list[float], x: list[float]) -> tuple[float, float, float]:
    """alpha (per period), beta, correlation."""
    if len(y) < 3:
        return 0.0, 0.0, 0.0
    mx, my = st.fmean(x), st.fmean(y)
    vx = sum((a - mx) ** 2 for a in x)
    vy = sum((b - my) ** 2 for b in y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if vx == 0:
        return my, 0.0, 0.0
    beta = cov / vx
    corr = cov / math.sqrt(vx * vy) if vy > 0 else 0.0
    return my - beta * mx, beta, corr


def capture(y: list[float], x: list[float], up: bool) -> float:
    pairs = [(a, b) for a, b in zip(x, y) if (a > 0 if up else a < 0)]
    if not pairs:
        return 0.0
    bx = compound([a for a, _ in pairs])
    by = compound([b for _, b in pairs])
    return by / bx if bx else 0.0


def annualise(total: float, days: int) -> float:
    if days <= 0 or total <= -1:
        return -1.0 if total <= -1 else 0.0
    return (1 + total) ** (PERIODS / days) - 1


def monthly(days: list[int], rs: list[float]) -> list[float]:
    buckets: dict[tuple[int, int], list[float]] = defaultdict(list)
    for d, r in zip(days, rs):
        dt = datetime.fromtimestamp(d, timezone.utc)
        buckets[(dt.year, dt.month)].append(r)
    return [compound(v) for _, v in sorted(buckets.items())]


def live_window(res: PortfolioResult) -> int:
    """Index of the first day the wallet held meaningful capital."""
    for i, v in enumerate(res.equity):
        if v >= MIN_CAPITAL_USD:
            return i
    return len(res.equity)


def compute(res: PortfolioResult, benchmark: list[float], copy_returns: list[float] | None = None,
            now: int | None = None) -> dict[str, float]:
    now = now or int(time.time())
    i0 = live_window(res)
    days, rs = res.days[i0:], res.returns[i0:]
    prs, bench = res.passive_returns[i0:], benchmark[i0:]
    n = len(rs)
    m: dict[str, float] = {}

    # --- returns & risk -------------------------------------------------
    total = compound(rs)
    mean, sd, skew, kurt = moments(rs)
    downside = math.sqrt(st.fmean([min(r, 0.0) ** 2 for r in rs])) if rs else 0.0
    sr = mean / sd if sd else 0.0
    mdd = max_drawdown(rs)
    m["history_days"] = n
    m["total_return"] = total
    m["cagr"] = annualise(total, n)
    m["volatility"] = sd * math.sqrt(PERIODS)
    m["sharpe"] = sr * math.sqrt(PERIODS)
    m["sortino"] = mean / downside * math.sqrt(PERIODS) if downside else 0.0
    m["max_drawdown"] = mdd
    m["calmar"] = m["cagr"] / mdd if mdd > 0 else 0.0
    m["ulcer_index"] = ulcer_index(rs)
    m["skew"] = skew
    m["kurtosis"] = kurt
    m["sharpe_daily"] = sr
    m["psr"] = probabilistic_sharpe(sr, n, skew, kurt)
    m["t_stat"] = sr * math.sqrt(n) if n else 0.0

    mo = monthly(days, rs)
    m["months"] = len(mo)
    m["pct_positive_months"] = sum(r > 0 for r in mo) / len(mo) if mo else 0.0
    m["worst_month"] = min(mo) if mo else 0.0
    m["best_month"] = max(mo) if mo else 0.0

    # --- vs. benchmark (ETH) and vs. its own buy-and-hold twin ----------
    alpha, beta, corr = ols_beta(rs, bench)
    m["alpha_vs_eth"] = alpha * PERIODS
    m["beta_vs_eth"] = beta
    m["corr_vs_eth"] = corr
    m["upside_capture"] = capture(rs, bench, True)
    m["downside_capture"] = capture(rs, bench, False)
    m["eth_cagr"] = annualise(compound(bench), n)

    m["buy_hold_total_return"] = compound(prs)
    m["buy_hold_cagr"] = annualise(m["buy_hold_total_return"], n)
    m["buy_hold_sharpe"] = _ann_sharpe(prs)
    m["buy_hold_max_drawdown"] = max_drawdown(prs)
    m["active_premium"] = m["cagr"] - m["buy_hold_cagr"]
    ex = [a - b for a, b in zip(rs, prs)]
    m["information_ratio"] = _ann_sharpe(ex)
    m["active_psr"] = probabilistic_sharpe(*_sr_moments(ex))

    # --- trade-level -----------------------------------------------------
    trades = res.closed_trades
    wins = [t.pnl for t in trades if t.pnl > 0]
    losses = [-t.pnl for t in trades if t.pnl < 0]
    m["closed_trades"] = len(trades)
    m["win_rate"] = len(wins) / len(trades) if trades else 0.0
    m["profit_factor"] = sum(wins) / sum(losses) if losses else (10.0 if wins else 0.0)
    m["payoff_ratio"] = (st.fmean(wins) / st.fmean(losses)) if wins and losses else 0.0
    m["expectancy_per_trade"] = st.fmean([t.ret for t in trades]) if trades else 0.0
    m["median_hold_days"] = st.median([t.holding_days for t in trades]) if trades else 0.0
    m["realized_pnl_usd"] = sum(t.pnl for t in trades)
    m["unrealized_pnl_usd"] = res.unrealized_pnl_usd
    gross = sum(wins)
    m["top_trade_profit_share"] = max(wins) / gross if gross else 1.0

    # --- activity / management style -------------------------------------
    swaps = [e for e in res.events if e.kind is EventKind.SWAP]
    swap_days = {e.timestamp // DAY for e in swaps}
    months_active = {datetime.fromtimestamp(e.timestamp, timezone.utc).strftime("%Y-%m") for e in swaps}
    eq = [e for e in res.equity[i0:] if e > 0]
    avg_eq = st.fmean(eq) if eq else 0.0
    gaps = [b.timestamp - a.timestamp for a, b in zip(swaps, swaps[1:])]
    m["swaps"] = len(swaps)
    m["swap_days"] = len(swap_days)
    m["swaps_per_month"] = len(swaps) / max(n / 30.4, 1.0)
    m["swaps_per_active_day"] = len(swaps) / len(swap_days) if swap_days else 0.0
    m["active_month_ratio"] = len(months_active) / max(m["months"], 1)
    m["median_secs_between_swaps"] = st.median(gaps) if gaps else float("inf")
    m["same_block_swap_ratio"] = (sum(1 for a, b in zip(swaps, swaps[1:]) if a.block == b.block)
                                  / len(gaps)) if gaps else 0.0
    m["annual_turnover"] = (res.swap_volume_usd / avg_eq) * PERIODS / max(n, 1) if avg_eq else 0.0
    m["days_since_last_swap"] = (now - swaps[-1].timestamp) / DAY if swaps else float("inf")
    m["avg_equity_usd"] = avg_eq
    m["final_equity_usd"] = res.final_equity
    m["swap_volume_usd"] = res.swap_volume_usd
    m["fees_usd"] = res.fees_usd
    m["price_coverage"] = res.price_coverage

    # --- followability ---------------------------------------------------
    if copy_returns is not None:
        cr = copy_returns[i0:]
        m["copy_cagr"] = annualise(compound(cr), len(cr))
        m["copy_sharpe"] = _ann_sharpe(cr)
        m["copy_capture"] = (m["copy_cagr"] / m["cagr"]) if m["cagr"] > 0 else 0.0
    return m


def _sr_moments(rs: list[float]) -> tuple[float, int, float, float]:
    mean, sd, skew, kurt = moments(rs)
    return (mean / sd if sd else 0.0), len(rs), skew, kurt


def _ann_sharpe(rs: list[float]) -> float:
    return _sr_moments(rs)[0] * math.sqrt(PERIODS)
