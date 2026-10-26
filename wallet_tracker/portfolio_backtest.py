"""Portfolio-level backtest of the whole copy strategy, as one account.

Every `rebalance_days` the Hyperliquid screen is re-run on data available at
that date only, leaders are chosen with the funnel the fork audit supports
(proven or on track, still profitable over the last 30 days), and money is
split across the top K. Between rebalances the account earns the leaders'
daily returns, with optional risk controls:

  weighting      equal, or inverse volatility;
  live stop      a leader that falls `stop` below its peak since we added it
                 goes to cash until the next rebalance (D17's live role);
  vol target     the whole book is scaled so trailing 30-day volatility
                 matches `target_vol` (capped at `max_scale`) - the portfolio-
                 level answer to the ~30% blow-up rate selection can't remove;
  copy capture   kappa x leader returns: 1.0 = perfect instant copy; the
                 group fidelity test suggests a daily copier keeps ~0.35-0.5.

Baselines over the same dates: naive top-K by past PnL, everyone profitable,
and holding ETH.
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass

from .metrics import compound, max_drawdown
from .models import DAY
from .perps_backtest import funnel_rule, screen_at
from .providers.hyperliquid_accounts import _px, interp


@dataclass
class Variant:
    name: str
    select: str = "funnel"          # funnel | naive_pnl | everyone
    k: int = 10
    weighting: str = "equal"        # equal | inverse_vol
    stop: float | None = None
    target_vol: float | None = None
    max_scale: float = 1.0
    kappa: float = 1.0


def daily_returns(h: dict, days: list[int]) -> dict[int, float]:
    """Leader's own daily returns (PnL change over prior equity), deposits excluded."""
    av, pnl = dict(h["account_value"]), dict(h["pnl"])
    if not av or not pnl:
        return {}
    first, last = min(av), max(av)
    out = {}
    for d in days:
        if d - DAY < first or d > last:
            continue
        a0 = interp(av, d - 1)
        if a0 <= 100:
            continue
        out[d] = max((interp(pnl, d + DAY - 1) - interp(pnl, d - 1)) / a0, -1.0)
    return out


def _stats(rs: list[float]) -> dict[str, float]:
    if len(rs) < 2:
        return {}
    sd = st.pstdev(rs)
    months = [compound(rs[i:i + 30]) for i in range(0, len(rs), 30)]
    total = compound(rs)
    return {"return": total, "cagr": (1 + total) ** (365 / len(rs)) - 1 if total > -1 else -1.0,
            "sharpe": st.fmean(rs) / sd * math.sqrt(365) if sd else 0.0, "max_drawdown": max_drawdown(rs),
            "worst_month": min(months), "pct_positive_months": sum(m > 0 for m in months) / len(months),
            "volatility": sd * math.sqrt(365)}


def run(histories: dict[str, dict], eth, btc, volume, start_days_ago: int, rebalance_days: int, now: int,
        variants: list[Variant], mm_turnover: float = 5_000) -> dict[str, dict]:
    end = now - now % DAY - DAY
    start = end - start_days_ago * DAY
    days = [start + i * DAY for i in range((end - start) // DAY + 1)]
    rebalances = days[::rebalance_days]
    rule = funnel_rule(recency=30, kill=None)

    # Leader returns are reused across variants; compute once per account.
    ret_cache: dict[str, dict[int, float]] = {}

    def rets(a: str) -> dict[int, float]:
        if a not in ret_cache:
            ret_cache[a] = daily_returns(histories[a], days)
        return ret_cache[a]

    picks_at: dict[int, dict[str, list[dict]]] = {}
    for t in rebalances:
        rows = screen_at(histories, t, eth, btc, volume)
        base = [r for r in rows if 5 <= r.get("annual_turnover", 0) <= mm_turnover and r["pnl_usd"] > 0
                and r["max_drawdown"] < 0.95]
        funnel = sorted([r for r in base if rule(r)],
                        key=lambda r: -min(r.get("dsr_vs_eth", 0), r.get("dsr_vs_btc", 0)))
        picks_at[t] = {"funnel": funnel, "naive_pnl": sorted(base, key=lambda r: -r["pnl_usd"]), "everyone": base}

    out = {}
    for v in variants:
        series, held_counts = [], []
        weights: dict[str, float] = {}
        peak: dict[str, float] = {}
        level: dict[str, float] = {}
        raw_hist: list[float] = []
        for d in days:
            if d in picks_at:
                pool = picks_at[d][v.select]
                chosen = pool if v.select == "everyone" else pool[:v.k]
                if v.weighting == "inverse_vol" and chosen:
                    inv = {r["address"]: 1 / max(r.get("volatility", 1.0), 0.05) for r in chosen}
                    tot = sum(inv.values())
                    weights = {a: x / tot for a, x in inv.items()}
                else:
                    weights = {r["address"]: 1 / len(chosen) for r in chosen} if chosen else {}
                peak = {a: 1.0 for a in weights}
                level = {a: 1.0 for a in weights}
            # Day's return on the current book (stopped leaders sit in cash).
            raw = 0.0
            for a, w in weights.items():
                if w == 0:
                    continue
                r = rets(a).get(d, 0.0)
                raw += w * r
                level[a] *= 1 + r
                peak[a] = max(peak[a], level[a])
                if v.stop is not None and level[a] / peak[a] - 1 <= -v.stop:
                    weights[a] = 0.0       # live stop: out until the next rebalance
            scale = 1.0
            if v.target_vol and len(raw_hist) >= 20:
                vol = st.pstdev(raw_hist[-30:]) * math.sqrt(365)
                scale = min(v.max_scale, v.target_vol / vol) if vol > 0 else v.max_scale
            raw_hist.append(raw)
            series.append(max(v.kappa * scale * raw, -1.0))
            held_counts.append(sum(1 for w in weights.values() if w > 0))
        out[v.name] = {"days": days, "returns": series, **_stats(series),
                       "avg_leaders": st.fmean(held_counts) if held_counts else 0.0}
    e = [(_px(eth, d) / _px(eth, d - DAY) - 1) if _px(eth, d) and _px(eth, d - DAY) else 0.0 for d in days]
    out["hold ETH"] = {"days": days, "returns": e, **_stats(e), "avg_leaders": 0.0}
    return out


def default_variants(kappa: float = 1.0) -> list[Variant]:
    sfx = "" if kappa == 1.0 else f" [copy keeps {kappa:.0%}]"
    return [
        Variant(f"funnel top10, equal{sfx}", kappa=kappa),
        Variant(f"funnel top10, inverse-vol{sfx}", weighting="inverse_vol", kappa=kappa),
        Variant(f"funnel top10, equal, stop 25%{sfx}", stop=0.25, kappa=kappa),
        Variant(f"funnel top10, equal, stop 25%, vol target 30%{sfx}", stop=0.25, target_vol=0.30, kappa=kappa),
        Variant(f"funnel top20, inverse-vol, stop 25%, vol target 30%{sfx}", k=20, weighting="inverse_vol",
                stop=0.25, target_vol=0.30, kappa=kappa),
        Variant(f"funnel top5, equal, stop 25%, vol target 30%{sfx}", k=5, stop=0.25, target_vol=0.30, kappa=kappa),
        Variant(f"naive top20 by past PnL{sfx}", select="naive_pnl", k=20, kappa=kappa),
        Variant(f"everyone profitable{sfx}", select="everyone", kappa=kappa),
    ]
