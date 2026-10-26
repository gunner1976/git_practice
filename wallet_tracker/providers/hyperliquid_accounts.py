"""Hyperliquid perps traders: the venue's public leaderboard and per-account history.

Every account on Hyperliquid is an EVM address, so the same wallet can be
looked up on Ethereum and here. For each account we get the account value
and cumulative PnL history (PnL excludes deposits and withdrawals), which
gives clean trading returns:

    r_i = dPnL_i / (account_value_{i-1} + max(0, net deposit during i))

(deposits made inside an interval count as capital at risk for it, so a
top-up followed by a loss can't produce a loss bigger than the capital).

The all-time history is sampled every few days, so annualisation uses the
real sampling interval. Display names are self-chosen aliases: weak identity
at best. Anything that looks like an email address is masked.
"""

from __future__ import annotations

import math
import re
import statistics as st

from ..metrics import (compound, days_to_proof, evidence_status, expected_max_sharpe, max_drawdown, moments,
                       probabilistic_sharpe)
from .http import Http

URL = "https://api.hyperliquid.xyz/info"
LEADERBOARD = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", re.I)


def mask(name: str | None) -> str:
    return EMAIL.sub("(email hidden)", name or "")


def interp(series: dict[int, float], t: int) -> float:
    """Linear interpolation of a sparse time series at t."""
    ks = sorted(series)
    lo = max((k for k in ks if k <= t), default=ks[0])
    hi = min((k for k in ks if k >= t), default=ks[-1])
    if hi == lo:
        return series[lo]
    return series[lo] + (series[hi] - series[lo]) * (t - lo) / (hi - lo)


def _windows(row) -> dict[str, dict[str, float]]:
    return {w: {k: float(v) for k, v in x.items()} for w, x in row["windowPerformances"]}


class HyperliquidAccounts:
    def __init__(self):
        self.http = Http(min_interval=0.2, cache_ttl=6 * 3600)
        self._lb: dict[str, dict] | None = None

    def leaderboard(self) -> dict[str, dict]:
        if self._lb is None:
            rows = self.http.get_json(LEADERBOARD)["leaderboardRows"]
            self._lb = {r["ethAddress"].lower(): {"account_value": float(r["accountValue"]),
                                                  "alias": mask(r.get("displayName")), **_windows(r)}
                        for r in rows}
        return self._lb

    def candidates(self, min_value: float = 50_000, top: int = 300) -> list[str]:
        """Accounts of meaningful size that traded this month, largest first -
        selected by size, not by PnL, so the screen isn't pre-selected for
        winners (and not by volume, which would mostly pick market makers)."""
        lb = self.leaderboard()
        live = [(a, r) for a, r in lb.items() if r["account_value"] >= min_value and r["month"]["vlm"] > 0]
        live.sort(key=lambda x: x[1]["account_value"], reverse=True)
        return [a for a, _ in live[:top]]

    def history(self, address: str) -> dict:
        data = self.http.post_json(URL, {"type": "portfolio", "user": address})
        windows = dict(data)
        # The all-time series is sampled every few days; the month and week
        # series are much finer. Merge them for the densest history available.
        av_pts: dict[int, float] = {}
        pnl_pts: dict[int, float] = {}
        for name in ("perpAllTime", "perpMonth", "perpWeek"):
            w = windows.get(name) or {}
            for t, v in w.get("accountValueHistory", []):
                av_pts[int(t) // 1000] = float(v)
        # PnL is cumulative from each window's start; re-base finer windows onto
        # the all-time curve by matching the nearest earlier all-time point.
        alltime = {int(t) // 1000: float(v) for t, v in (windows.get("perpAllTime") or {}).get("pnlHistory", [])}
        pnl_pts.update(alltime)
        for name in ("perpMonth", "perpWeek"):
            w = windows.get(name) or {}
            rows = [(int(t) // 1000, float(v)) for t, v in w.get("pnlHistory", [])]
            if not rows or not alltime or rows[0][0] < min(alltime):
                continue
            offset = interp(alltime, rows[0][0]) - rows[0][1]
            for t, v in rows:
                if t not in alltime:
                    pnl_pts[t] = v + offset
        ts = sorted(set(av_pts) & set(pnl_pts))
        w = windows.get("perpAllTime") or windows.get("allTime") or {}
        return {"address": address.lower(), "account_value": [(t, av_pts[t]) for t in ts],
                "pnl": [(t, pnl_pts[t]) for t in ts], "volume": float(w.get("vlm") or 0)}


def _px(series: dict[int, float], t: int) -> float | None:
    """Price at time t from a daily series (nearest earlier day)."""
    if not series:
        return None
    d = t - t % 86_400
    for k in range(4):
        p = series.get(d - k * 86_400)
        if p:
            return p
    return None


def perp_metrics(h: dict, eth: dict[int, float] | None = None, btc: dict[int, float] | None = None) -> dict[str, float]:
    av, pnl = h["account_value"], h["pnl"]
    n = min(len(av), len(pnl))
    rs, gaps = [], []
    for i in range(1, n):
        d_pnl = pnl[i][1] - pnl[i - 1][1]
        deposit = (av[i][1] - av[i - 1][1]) - d_pnl
        base = av[i - 1][1] + max(0.0, deposit)
        if base > 100:
            rs.append(max(d_pnl / base, -1.0))
            gaps.append(max((av[i][0] - av[i - 1][0]) / 86_400, 1e-3))
    if len(rs) < 8:
        return {"intervals": len(rs)}
    times = [av[i][0] for i in range(1, n) if (av[i - 1][1] + max(0.0, (av[i][1] - av[i - 1][1]) - (pnl[i][1] - pnl[i - 1][1]))) > 100]
    span_days = (av[n - 1][0] - av[0][0]) / 86_400
    ppy = 365 / st.median(gaps)
    # Intervals are uneven (coarse history, fine recent data), so estimate
    # daily drift and volatility per unit time, then express the Sharpe per
    # typical interval for the significance test.
    mu = sum(rs) / sum(gaps)
    var = sum((r - mu * g) ** 2 for r, g in zip(rs, gaps)) / sum(gaps)
    daily_sr = mu / math.sqrt(var) if var > 0 else 0.0
    _, _, skew, kurt = moments([r / math.sqrt(g) for r, g in zip(rs, gaps)])
    # Significance is judged in daily units over the record's length: a month
    # of hourly points is not more evidence than a month of daily ones.
    sr = daily_sr
    total = compound(rs)
    avg_value = st.fmean(v for _, v in av[:n]) or 1.0
    market = {}
    for name, series in (("eth", eth), ("btc", btc)):
        if not series:
            continue
        ex, ok_gaps = [], []
        for r, g, t in zip(rs, gaps, times):
            p0, p1 = _px(series, int(t - g * 86_400)), _px(series, t)
            if p0 and p1:
                ex.append((1 + r) / (p1 / p0) - 1)
                ok_gaps.append(g)
        if len(ex) >= 8:
            mu_x = sum(ex) / sum(ok_gaps)
            var_x = sum((x - mu_x * g) ** 2 for x, g in zip(ex, ok_gaps)) / sum(ok_gaps)
            sr_x = mu_x / math.sqrt(var_x) if var_x > 0 else 0.0
            _, _, sk_x, ku_x = moments([x / math.sqrt(g) for x, g in zip(ex, ok_gaps)])
            market[f"excess_total_vs_{name}"] = compound(ex)
            market[f"ir_vs_{name}"] = sr_x * math.sqrt(365)
            market[f"ir_period_vs_{name}"] = sr_x
            market[f"ir_skew_vs_{name}"], market[f"ir_kurt_vs_{name}"] = sk_x, ku_x
            # consistency: share of ~30-day blocks that beat the benchmark
            block, acc, days_acc = [], 1.0, 0.0
            for x, g in zip(ex, ok_gaps):
                acc *= 1 + x
                days_acc += g
                if days_acc >= 30:
                    block.append(acc - 1)
                    acc, days_acc = 1.0, 0.0
            win_n = len(block)
            wins = sum(b > 0 for b in block)
            market[f"pct_months_beat_{name}"] = wins / win_n if win_n else 0.0
    return {
        **market,
        "intervals": len(rs), "effective_days": max(int(span_days), 3), "span_days": span_days,
        "periods_per_year": ppy,
        "total_return": total,
        "cagr": (1 + total) ** (365 / span_days) - 1 if span_days > 30 and total > -1 else 0.0,
        "sharpe": daily_sr * math.sqrt(365), "sharpe_period": sr, "skew": skew, "kurtosis": kurt,
        "psr": probabilistic_sharpe(sr, max(int(span_days), 3), skew, kurt),
        "max_drawdown": max_drawdown(rs),
        "pct_positive": sum(r > 0 for r in rs) / len(rs),
        "pnl_usd": pnl[n - 1][1] - pnl[0][1],
        "account_value": av[n - 1][1],
        "annual_turnover": h["volume"] / avg_value * 365 / max(span_days, 1),
    }


def deflate(rows: list[dict]) -> float:
    """Luck bar across the screened accounts (null variance 1/T); sets 'dsr'."""
    scored = [r for r in rows if "sharpe_period" in r]
    if len(scored) < 2:
        return 0.0
    t_typ = st.median(r["effective_days"] for r in scored)
    star = expected_max_sharpe(1.0 / t_typ, len(scored))
    for r in scored:
        r["dsr"] = probabilistic_sharpe(r["sharpe_period"], r["effective_days"], r["skew"], r["kurtosis"], star)
        # The claim that matters: beating the market, not just making money.
        for name in ("eth", "btc"):
            if f"ir_period_vs_{name}" in r:
                r[f"dsr_vs_{name}"] = probabilistic_sharpe(r[f"ir_period_vs_{name}"], r["effective_days"],
                                                           r[f"ir_skew_vs_{name}"], r[f"ir_kurt_vs_{name}"], star)
        # Evidence clock on the claim that matters - beating ETH - if measured.
        sr_x = r.get("ir_period_vs_eth", r["sharpe_period"])
        sk, ku = r.get("ir_skew_vs_eth", r["skew"]), r.get("ir_kurt_vs_eth", r["kurtosis"])
        need = days_to_proof(sr_x, star, sk, ku)
        r["days_to_proof"] = need
        r["days_remaining"] = max(0.0, need - r["effective_days"]) if need is not None else None
        r["evidence"] = evidence_status(r.get("dsr_vs_eth", r["dsr"]) if "ir_period_vs_eth" in r else r["dsr"],
                                        r["effective_days"], need)
    return star * math.sqrt(365)


def recent_stats(h: dict, days: int, now: int) -> dict[str, float]:
    """Return and max drawdown over the last `days`, deposits excluded."""
    av, pnl = h["account_value"], h["pnl"]
    start = now - days * 86_400
    g = peak = 1.0
    worst = 0.0
    seen = 0
    for i in range(1, min(len(av), len(pnl))):
        if av[i][0] < start:
            continue
        d_pnl = pnl[i][1] - pnl[i - 1][1]
        base = av[i - 1][1] + max(0.0, (av[i][1] - av[i - 1][1]) - d_pnl)
        if base <= 100:
            continue
        g *= 1 + max(d_pnl / base, -1.0)
        peak = max(peak, g)
        worst = min(worst, g / peak - 1)
        seen += 1
    return {"recent_return": g - 1, "recent_drawdown": -worst, "recent_points": seen,
            "off_peak": 1 - g / peak}
