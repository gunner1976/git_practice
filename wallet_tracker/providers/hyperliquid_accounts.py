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

from ..metrics import compound, expected_max_sharpe, max_drawdown, moments, probabilistic_sharpe
from .http import Http

URL = "https://api.hyperliquid.xyz/info"
LEADERBOARD = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", re.I)


def mask(name: str | None) -> str:
    return EMAIL.sub("(email hidden)", name or "")


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
        w = windows.get("perpAllTime") or windows.get("allTime") or {}
        av = [(int(t) // 1000, float(v)) for t, v in w.get("accountValueHistory", [])]
        pnl = [(int(t) // 1000, float(v)) for t, v in w.get("pnlHistory", [])]
        return {"address": address.lower(), "account_value": av, "pnl": pnl, "volume": float(w.get("vlm") or 0)}


def perp_metrics(h: dict) -> dict[str, float]:
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
    span_days = (av[n - 1][0] - av[0][0]) / 86_400
    ppy = 365 / st.median(gaps)
    mean, sd, skew, kurt = moments(rs)
    sr = mean / sd if sd else 0.0
    total = compound(rs)
    avg_value = st.fmean(v for _, v in av[:n]) or 1.0
    return {
        "intervals": len(rs), "span_days": span_days, "periods_per_year": ppy,
        "total_return": total,
        "cagr": (1 + total) ** (365 / span_days) - 1 if span_days > 30 and total > -1 else 0.0,
        "sharpe": sr * math.sqrt(ppy), "sharpe_period": sr, "skew": skew, "kurtosis": kurt,
        "psr": probabilistic_sharpe(sr, len(rs), skew, kurt),
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
    t_typ = st.median(r["intervals"] for r in scored)
    star = expected_max_sharpe(1.0 / t_typ, len(scored))
    for r in scored:
        r["dsr"] = probabilistic_sharpe(r["sharpe_period"], r["intervals"], r["skew"], r["kurtosis"], star)
    return star * math.sqrt(st.median(r["periods_per_year"] for r in scored))
