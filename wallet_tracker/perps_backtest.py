"""Backtest the Hyperliquid leader-selection process itself.

At each past cutoff, every account's history is truncated there, the full
screen is re-run on that data alone (luck tests vs ETH and BTC, evidence
clock, recency, kill switch), leaders are picked, and their *subsequent*
returns are measured over the horizon - compared with every screened
account, naive "top past PnL" and "top past return" picks, and ETH.

Survivorship: candidates are sampled by all-time trading volume from the
current leaderboard, which still lists accounts that have since blown up
(their value is ~0) - so dead accounts stay in the test. Accounts that
closed and vanished from the leaderboard entirely are still missing, which
flatters every strategy equally; the comparison between them is the point.

Forward returns are the leaders' own (a perfect, instant copy); the group
proxy test showed a daily copier keeps roughly a third to a half of that.
"""

from __future__ import annotations

import statistics as st

from .metrics import compound, max_drawdown
from .models import DAY
from .providers.hyperliquid_accounts import _px, deflate, perp_metrics, recent_stats


def truncate(h: dict, cutoff: int) -> dict:
    return {**h, "account_value": [p for p in h["account_value"] if p[0] <= cutoff],
            "pnl": [p for p in h["pnl"] if p[0] <= cutoff]}


def forward(h: dict, start: int, end: int) -> list[float]:
    """Interval returns between start and end, deposits excluded."""
    av, pnl = h["account_value"], h["pnl"]
    out = []
    for i in range(1, min(len(av), len(pnl))):
        if not (start < av[i][0] <= end):
            continue
        d_pnl = pnl[i][1] - pnl[i - 1][1]
        base = av[i - 1][1] + max(0.0, (av[i][1] - av[i - 1][1]) - d_pnl)
        if base > 100:
            out.append(max(d_pnl / base, -1.0))
    return out


def screen_at(histories: dict[str, dict], cutoff: int, eth, btc, volume: dict[str, float]) -> list[dict]:
    rows = []
    for a, h in histories.items():
        t = truncate(h, cutoff)
        t["volume"] = volume.get(a, 0.0)
        m = perp_metrics(t, eth, btc)
        if "sharpe_period" not in m or m.get("span_days", 0) < 30:
            continue
        m.update(recent_stats(t, 60, cutoff), address=a)
        for w in (30, 90):
            rs = recent_stats(t, w, cutoff)
            m[f"recent_return_{w}"], m[f"off_peak_{w}"] = rs["recent_return"], rs["off_peak"]
        rows.append(m)
    deflate(rows)
    return rows


STRATEGIES = {
    "proven (beat ETH >=95%, BTC >=80%)":
        lambda r: r.get("dsr_vs_eth", 0) >= 0.95 and r.get("dsr_vs_btc", 0) >= 0.8,
    "proven + on track, still working, not falling":
        lambda r: r.get("evidence") in ("proven", "on track") and r["recent_return"] > 0 and r["off_peak"] < 0.30,
    "proven + steady (max DD < 40%)":
        lambda r: r.get("dsr_vs_eth", 0) >= 0.95 and r["max_drawdown"] < 0.40,
}


def funnel_rule(statuses=("proven", "on track"), recency: int | None = 60, kill: float | None = 0.30,
                max_vol: float | None = None):
    """The funnel with each open fork as a parameter (decision log D15-D18)."""
    def rule(r):
        if r.get("evidence") not in statuses:
            return False
        if recency:
            rec = r["recent_return"] if recency == 60 else r[f"recent_return_{recency}"]
            if rec <= 0:
                return False
        if kill is not None and r["off_peak"] >= kill:
            return False
        if max_vol is not None and r.get("volatility", 0) > max_vol:
            return False
        return True
    return rule


AUDIT = {
    "BASE funnel (proven/on track, 60d recency, 30% kill)": funnel_rule(),
    "D16 no recency gate": funnel_rule(recency=None),
    "D16 recency 30d": funnel_rule(recency=30),
    "D16 recency 90d": funnel_rule(recency=90),
    "D17 no kill switch": funnel_rule(kill=None),
    "D17 kill at 20%": funnel_rule(kill=0.20),
    "D17 kill at 50%": funnel_rule(kill=0.50),
    "D15 + volatility cap 150%/yr": funnel_rule(max_vol=1.5),
    "D15 + volatility cap 100%/yr": funnel_rule(max_vol=1.0),
    "D15 + volatility cap 60%/yr": funnel_rule(max_vol=0.6),
    "D18 + let 'too early' in": funnel_rule(statuses=("proven", "on track", "too early")),
}


def run(histories: dict[str, dict], eth, btc, volume: dict[str, float], cutoffs_days: list[int],
        horizon_days: int, now: int, mm_turnover: float = 5_000, top_n: int = 20,
        strategies: dict | None = None) -> list[dict]:
    results = []
    for back in cutoffs_days:
        cutoff = now - back * DAY
        end = min(cutoff + horizon_days * DAY, now)
        rows = screen_at(histories, cutoff, eth, btc, volume)
        base = [r for r in rows if 5 <= r.get("annual_turnover", 0) <= mm_turnover and r["pnl_usd"] > 0
                and r["max_drawdown"] < 0.95]
        e0, e1 = _px(eth, cutoff), _px(eth, end)
        eth_ret = e1 / e0 - 1 if e0 and e1 else 0.0

        def evaluate(name: str, picks: list[dict]) -> dict:
            fwd = {r["address"]: forward(histories[r["address"]], cutoff, end) for r in picks}
            rets = [compound(x) for x in fwd.values() if x]
            dds = [max_drawdown(x) for x in fwd.values() if x]
            # Equal money in each pick, held: the average of their compounded returns.
            port = st.fmean(rets) if rets else 0.0
            return {"cutoff_days_ago": back, "strategy": name, "picked": len(picks), "with_data": len(rets),
                    "equal_weight_return": port, "median_return": st.median(rets) if rets else 0.0,
                    "beat_eth": sum(r > eth_ret for r in rets) / len(rets) if rets else 0.0,
                    "blew_up": sum(d > 0.5 for d in dds) / len(dds) if dds else 0.0, "eth_return": eth_ret,
                    "picks": [r["address"] for r in picks]}

        for name, rule in (strategies or STRATEGIES).items():
            results.append(evaluate(name, [r for r in base if rule(r)]))
        results.append(evaluate(f"naive: top {top_n} by past PnL",
                                sorted(base, key=lambda r: -r["pnl_usd"])[:top_n]))
        results.append(evaluate(f"naive: top {top_n} by past return",
                                sorted(base, key=lambda r: -r["total_return"])[:top_n]))
        results.append(evaluate("everyone screened (profitable, non-MM)", base))
    return results


def summarise(results: list[dict]) -> dict[str, dict]:
    by: dict[str, list[dict]] = {}
    for r in results:
        by.setdefault(r["strategy"], []).append(r)
    out = {}
    for name, rs in by.items():
        valid = [r for r in rs if r["with_data"]]
        out[name] = {
            "cutoffs": len(rs), "avg_picked": st.fmean(r["picked"] for r in rs),
            "cutoffs_with_picks": len(valid),
            "avg_equal_weight_return": st.fmean(r["equal_weight_return"] for r in valid) if valid else 0.0,
            "avg_median_return": st.fmean(r["median_return"] for r in valid) if valid else 0.0,
            "avg_beat_eth": st.fmean(r["beat_eth"] for r in valid) if valid else 0.0,
            "avg_blew_up": st.fmean(r["blew_up"] for r in valid) if valid else 0.0,
            "avg_eth_return": st.fmean(r["eth_return"] for r in rs),
        }
    return out

