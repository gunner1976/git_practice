"""Plain-text and JSON rendering of leaderboards and wallet reports."""

from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime, timezone

from .analyze import WalletReport
from .metrics import _ann_sharpe, compound, max_drawdown, monthly
from .ranking import Leaderboards


def pct(x: float) -> str:
    return "n/a" if x is None or math.isinf(x) or math.isnan(x) else f"{x * 100:+.1f}%"


def share(x: float) -> str:
    return "n/a" if x is None or math.isinf(x) or math.isnan(x) else f"{x * 100:.0f}%"


def num(x: float, d: int = 2) -> str:
    return "n/a" if x is None or math.isinf(x) or math.isnan(x) else f"{x:.{d}f}"


def short(a: str) -> str:
    return a[:8] + "…" + a[-4:]


def table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    line = lambda cells: "  ".join(c.rjust(w) if i else c.ljust(w)  # noqa: E731
                                   for i, (c, w) in enumerate(zip(cells, widths)))
    return "\n".join([line(headers), line(["-" * w for w in widths])] + [line(r) for r in rows])


def leaderboard_text(lb: Leaderboards, top: int = 20) -> str:
    out = []
    out.append(f"TOP ACTIVELY-MANAGED WALLETS  ({len(lb.active)} eligible; "
               f"Sharpe expected from luck alone across this sample: {lb.luck_sharpe:.2f})")
    rows = []
    for r in lb.active[:top]:
        m = r.metrics
        rep = f"{r.reputation.tier} {r.reputation.score:.0f}" if r.reputation else "-"
        rows.append([str(r.rank), short(r.address), num(r.score, 1), "yes" if m["significant"] else "no",
                     rep, r.group or "-", num(m.get("regime_robustness", float("nan"))),
                     pct(m["cagr"]), num(m["sharpe"]), num(m["sortino"]), pct(-m["max_drawdown"]),
                     share(m["pct_positive_months"]), share(m["win_rate"]), num(m["profit_factor"]),
                     pct(m["active_premium"]), pct(m["alpha_vs_eth"]), pct(m.get("copy_cagr", float("nan"))),
                     num(m["swaps_per_month"], 1)])
    out.append(table(["#", "wallet", "score", "signif", "rep", "operator", "RRS", "CAGR", "Sharpe", "Sortino", "MaxDD", "+months",
                      "win", "PF", "vs hold", "alpha", "copy CAGR", "swaps/mo"], rows))

    out.append("\nBUY-AND-HOLD WALLETS (relative-performance reference)")
    rows = []
    for r in lb.buy_hold[:top]:
        m = r.metrics
        rows.append([short(r.address), pct(m["cagr"]), num(m["sharpe"]), pct(-m["max_drawdown"]),
                     pct(m["alpha_vs_eth"]), pct(m["eth_cagr"]), num(m["swaps_per_month"], 2)])
    out.append(table(["wallet", "CAGR", "Sharpe", "MaxDD", "alpha", "ETH CAGR", "swaps/mo"], rows))

    out.append("\nCOHORTS (medians)")
    rows = [[k, str(v.get("n", 0)), pct(v.get("median_cagr", float("nan"))),
             num(v.get("median_sharpe", float("nan"))), pct(-v.get("median_max_drawdown", float("nan"))),
             pct(v.get("median_alpha_vs_eth", float("nan"))), pct(v.get("median_active_premium", float("nan")))]
            for k, v in lb.cohorts.items()]
    out.append(table(["cohort", "n", "CAGR", "Sharpe", "MaxDD", "alpha", "vs own hold"], rows))

    out.append("\nEXCLUDED")
    kinds = Counter(r.wallet_class.value for r in lb.excluded)
    out.append("  " + ", ".join(f"{k}: {v}" for k, v in kinds.items()))
    for r in lb.excluded[:top]:
        out.append(f"  {short(r.address)}  {r.wallet_class.value:<20} {'; '.join(r.exclusions[:3])}")
    return "\n".join(out)


def study_text(study, top: int = 20) -> str:
    from .regimes import REGIMES
    out = [leaderboard_text(study.boards, top)]

    out.append("\nLINKED-WALLET CLUSTERS (probable single operators)")
    if not study.clusters:
        out.append("  none found")
    for c in study.clusters:
        s = c.stats
        out.append(f"  cluster {c.id}: {len(c.members)} wallets  combined CAGR {pct(s['cagr'])} Sharpe {num(s['sharpe'])}"
                   f"  | copy basket CAGR {pct(s['copy_cagr'])} Sharpe {num(s['copy_sharpe'])}")
        out.append("    " + ", ".join(short(a) for a in c.members))
        for e in c.evidence[:4]:
            out.append(f"    - {e}")

    out.append("\nHUMAN vs AUTOMATED (medians per operator group)")
    rows = [[g, str(v["n"]), num(v["median_human_score"]), pct(v["median_cagr"]), num(v["median_sharpe"]),
             pct(-v["median_max_drawdown"]), num(v["median_regime_robustness"]), pct(v["median_copy_cagr"]),
             str(v["significant"])] for g, v in study.operator_summary.items()]
    out.append(table(["group", "n", "human", "CAGR", "Sharpe", "MaxDD", "RRS", "copy CAGR", "signif"], rows))

    cols = REGIMES + ["stress"]
    out.append("\nOPERATOR x MARKET REGIME (median annualised excess return vs ETH; stress = per crash day)")
    rows = []
    for g, cells in study.operator_regime.items():
        rows.append([g] + [(pct(cells[c]["median_excess"] / (365 if c == "stress" else 1)) if c in cells else "")
                           for c in cols])
    out.append(table(["group"] + cols, rows))

    out.append("\nWALLET x MARKET REGIME (top ranked; annualised excess return vs ETH)")
    rows = [[short(r.address)] + [(pct(r.regimes[c]["ann_excess"] / (365 if c == "stress" else 1))
                                   if r.regimes.get(c, {}).get("days", 0) >= 10 else "") for c in cols]
            for r in study.boards.active[:min(top, 10)]]
    out.append(table(["wallet"] + cols, rows))
    days = {c: sum(1 for v in study.regimes.labels.values() if v == c) for c in REGIMES}
    out.append("  market days per regime: " + ", ".join(f"{c} {n}" for c, n in days.items())
               + f", stress {len(study.regimes.stress)}")

    out.append("\nCAPITAL MAP: ENTITIES (smart money first; sector mix = time-weighted over the record)")
    rows = []
    for e in study.entities[:top]:
        mix = ", ".join(f"{k} {v:.0%}" for k, v in sorted(e.sectors_avg.items(), key=lambda x: -x[1])[:3] if v >= 0.05)
        rows.append([e.label, str(len(e.members)), f"${e.aum_usd:,.0f}", e.group, f"{e.tier} {e.reputation:.0f}",
                     "yes" if e.smart else "", pct(e.cagr), mix])
    out.append(table(["entity", "wallets", "AUM", "operator", "rep", "smart", "CAGR", "top sectors"], rows))

    months = sorted(study.flows_smart)[-6:]
    sectors = sorted({s for m in months for s in study.flows_smart[m]})
    out.append("\nSMART-MONEY NET FLOWS BY SECTOR (USD bought minus sold via swaps, last 6 months)")
    rows = [[sec] + [f"{study.flows_smart[m].get(sec, 0) / 1e6:+.1f}M" for m in months] for sec in sectors]
    out.append(table(["sector"] + months, rows) if rows else "  no smart-money swaps")

    out.append("\nWHALES vs MINNOWS (active traders by capital put in; medians unless noted)")
    rows = [[t, str(v["n"]), pct(v["median_cagr"]), num(v["median_sharpe"]), pct(-v["median_max_drawdown"]),
             num(v["median_regime_robustness"]), share(v["pct_beating_eth"]),
             f"{v['significant']} ({v['significant_rate']:.0%})", pct(v["median_copy_cagr"]),
             f"${v['median_pnl_usd']:,.0f}", f"${v['total_pnl_usd']:,.0f}", share(v["human_share"])]
            for t, v in study.size_summary.items()]
    out.append(table(["size", "n", "CAGR", "Sharpe", "MaxDD", "RRS", "beat ETH", "signif", "copy CAGR",
                      "PnL (median)", "PnL (total)", "human"], rows) if rows else "  no active traders")

    out.append("\nTRADING FREQUENCY (by median holding period) and how fast each edge decays when copied late")
    lags = (0, 1, 2, 3, 5, 7, 14)
    rows = [[t, str(v["n"]), f"{v['median_hold_days']:.1f}d", num(v["median_swaps_per_month"], 1), pct(v["median_cagr"]),
             num(v["median_sharpe"]), f"{v['significant']} ({v['significant_rate']:.0%})",
             f"{v['median_half_life']:.1f}d"] + [num(v[f"copy_sharpe_lag{lag}"]) for lag in lags]
            for t, v in study.frequency_summary.items()]
    out.append(table(["frequency", "n", "hold", "swaps/mo", "CAGR", "Sharpe", "signif", "half-life"]
                     + [f"copy@{lag}d" for lag in lags], rows) if rows else "  no traders")

    tv = study.trade_venues or {}
    if tv.get("summary"):
        out.append("\nWHERE THE MONEY TRADES (by each wallet's main venue, by swap volume)")
        rows = [[v, str(x["primary_users"]), str(x["smart_users"]), pct(x["median_cagr"]), num(x["median_sharpe"]),
                 ", ".join(f"#{rk}" if rk else short(a) for a, rk, _ in x["top"][:3])]
                for v, x in sorted(tv["summary"].items(), key=lambda kv: -kv[1]["primary_users"])]
        out.append(table(["venue", "main users", "smart", "CAGR", "Sharpe", "top ranked users"], rows))
        months = list(tv["smart_share"])[-6:]
        venues = sorted({v for m in months for v in tv["smart_share"][m]})
        if months:
            out.append("  smart-money volume share by venue:")
            out.append(table(["venue"] + months, [[v] + [share(tv["smart_share"][m].get(v, 0.0)) for m in months]
                                                  for v in venues]))

    ms = study.migration_stats
    out.append(f"\nWALLET MIGRATIONS: {ms.get('migrations', 0)} of {ms.get('wallets', 0)} trading wallets "
               f"({ms.get('rate', 0):.1%}) handed their book to another address; {ms.get('verified', 0)} verified")
    for m in study.migrations:
        line = f"  {short(m.source)} -> {short(m.destination)}  {m.share:.0%} of value (${m.usd:,.0f})  " \
               f"{'verified successor' if m.verified else 'destination not screened'}"
        if m.stitched:
            line += f"  | stitched record CAGR {pct(m.stitched['cagr'])} Sharpe {num(m.stitched['sharpe'])}"
        out.append(line)
    return "\n".join(out)


def wallet_text(r: WalletReport) -> str:
    m = r.metrics
    res = r.result
    lines = [f"WALLET {r.address}",
             f"class: {r.wallet_class.value} ({'; '.join(r.reasons)})"]
    if r.exclusions:
        lines.append(f"not eligible: {'; '.join(r.exclusions)}")
    elif r.rank:
        lines.append(f"rank #{r.rank}, score {r.score:.1f}")
    groups = {
        "Returns": [("total return", pct(m["total_return"])), ("CAGR", pct(m["cagr"])),
                    ("final equity", f"${m['final_equity_usd']:,.0f}"),
                    ("realized PnL", f"${m['realized_pnl_usd']:,.0f}"),
                    ("unrealized PnL", f"${m['unrealized_pnl_usd']:,.0f}"), ("fees", f"${m['fees_usd']:,.0f}")],
        "Risk": [("volatility", pct(m["volatility"])), ("max drawdown", pct(-m["max_drawdown"])),
                 ("ulcer index", num(m["ulcer_index"])), ("worst month", pct(m["worst_month"])),
                 ("skew", num(m["skew"])), ("kurtosis", num(m["kurtosis"]))],
        "Risk-adjusted": [("Sharpe", num(m["sharpe"])), ("Sortino", num(m["sortino"])),
                          ("Calmar", num(m["calmar"])), ("PSR (P[Sharpe>0])", share(m["psr"])),
                          ("DSR (luck-adjusted)", share(m.get("dsr", float("nan")))),
                          ("t-stat", num(m["t_stat"]))],
        "Vs ETH": [("alpha", pct(m["alpha_vs_eth"])), ("beta", num(m["beta_vs_eth"])),
                   ("correlation", num(m["corr_vs_eth"])), ("upside capture", num(m["upside_capture"])),
                   ("downside capture", num(m["downside_capture"])), ("ETH CAGR", pct(m["eth_cagr"]))],
        "Vs its own buy-and-hold": [("buy-hold CAGR", pct(m["buy_hold_cagr"])),
                                    ("buy-hold Sharpe", num(m["buy_hold_sharpe"])),
                                    ("buy-hold max DD", pct(-m["buy_hold_max_drawdown"])),
                                    ("active premium", pct(m["active_premium"])),
                                    ("information ratio", num(m["information_ratio"])),
                                    ("P[beats holding]", share(m["active_psr"]))],
        "Trades": [("closed trades", str(int(m["closed_trades"]))), ("win rate", share(m["win_rate"])),
                   ("profit factor", num(m["profit_factor"])), ("payoff ratio", num(m["payoff_ratio"])),
                   ("avg trade return", pct(m["expectancy_per_trade"])),
                   ("median hold", f"{m['median_hold_days']:.1f}d"),
                   ("top trade share of profit", share(m["top_trade_profit_share"]))],
        "Activity": [("history", f"{int(m['history_days'])}d"), ("swaps", str(int(m["swaps"]))),
                     ("swaps / month", num(m["swaps_per_month"], 1)),
                     ("active months", share(m["active_month_ratio"])),
                     ("annual turnover", f"{m['annual_turnover']:.1f}x"),
                     ("days since last swap", num(m["days_since_last_swap"], 0)),
                     ("price coverage", share(m["price_coverage"]))],
        "Followability": [("copy CAGR (lagged, costed)", pct(m.get("copy_cagr", float("nan")))),
                          ("copy Sharpe", num(m.get("copy_sharpe", float("nan")))),
                          ("share of CAGR captured", share(m.get("copy_capture", float("nan"))))],
    }
    for name, items in groups.items():
        lines.append(f"\n{name}")
        lines += [f"  {k:<28}{v:>14}" for k, v in items]

    groups2 = {
        "Long-term": [("years tracked", num(m.get("years_tracked", 0))),
                      ("90d windows beating ETH", share(m.get("pct_windows_beat_eth", 0))),
                      ("90d windows beating own hold", share(m.get("pct_windows_beat_hold", 0))),
                      ("Sharpe 1st / 2nd half", f"{num(m.get('sharpe_first_half', 0))} / "
                                                f"{num(m.get('sharpe_second_half', 0))}"),
                      ("max-DD recovery", "not yet" if math.isinf(m.get("max_dd_recovery_days", 0))
                       else f"{m['max_dd_recovery_days']:.0f}d"),
                      ("time >10% under water", share(m.get("underwater_ratio", 0)))],
        "Market-regime risk": [("Regime Robustness Score", num(m.get("regime_robustness", 0))),
                               ("regimes beating ETH", share(m.get("regimes_beaten", 0))),
                               ("worst-regime excess", pct(m.get("worst_regime_excess", 0))),
                               ("avg excess on crash days", pct(m.get("stress_excess", 0))),
                               ("up / down / stress beta", f"{num(m.get('up_beta', 0))} / "
                                f"{num(m.get('down_beta', 0))} / {num(m.get('stress_beta', 0))}")],
    }
    for name, items in groups2.items():
        lines.append(f"\n{name}")
        lines += [f"  {k:<28}{v:>14}" for k, v in items]
    if r.regimes:
        lines.append("  " + "  ".join(f"{k}: {pct(v['ann_excess'] / (365 if k == 'stress' else 1))} ({v['days']}d)"
                                      for k, v in r.regimes.items()))
    if r.operator:
        o = r.operator
        lines.append("\nOperator")
        lines.append(f"  {'group':<28}{r.group or r.operator_label:>24}")
        lines += [f"  {k:<28}{v:>14}" for k, v in [
            ("human-likeness", f"{o['human_score']:.2f} (conf {o['human_confidence']:.0%})"),
            ("longest quiet stretch", f"{o['quiet_hours']}h/day"),
            ("hour-of-day entropy", num(o["hour_entropy"])),
            ("round-number entries", share(o["round_amount_ratio"])),
            ("gap irregularity (CV)", num(o["interval_cv"]))]]
    if r.identity is not None and getattr(r.identity, "attested", False):
        lines.append(f"  identity: {r.identity.name} ({r.identity.kind or 'kind unknown'}) via "
                     f"{', '.join(r.identity.sources)}")
    if r.reputation is not None:
        rp = r.reputation
        lines.append(f"\nReputation  {rp.tier}  {rp.score:.0f}/100")
        lines.append("  " + ", ".join(f"{k} {v:.2f}" for k, v in rp.components.items()))
        lines += [f"  + {e}" for e in rp.evidence] + [f"  ! {f}" for f in rp.flags]
    if r.cluster_id:
        lines.append(f"  member of linked cluster {r.cluster_id}")

    i0 = next((i for i, v in enumerate(res.equity) if v > 0), 0)
    mo = monthly(res.days[i0:], res.returns[i0:])
    if mo:
        lines.append("\nMonthly returns: " + " ".join(pct(x) for x in mo[-12:]))
    rec = rolling(r, 90)
    lines.append(f"Last 90d: return {pct(rec['return'])}, Sharpe {num(rec['sharpe'])}, "
                 f"max DD {pct(-rec['max_drawdown'])}, current DD {pct(-rec['current_drawdown'])}")
    best = sorted(r.closed_trades, key=lambda t: t.pnl, reverse=True)
    if best:
        lines.append("\nBest trades:  " + ", ".join(f"{t.symbol} {pct(t.ret)} (${t.pnl:,.0f})" for t in best[:5]))
        lines.append("Worst trades: " + ", ".join(f"{t.symbol} {pct(t.ret)} (${t.pnl:,.0f})" for t in best[-5:][::-1]))
    return "\n".join(lines)


def rolling(r: WalletReport, days: int) -> dict[str, float]:
    rs = r.result.returns[-days:]
    g = peak = 1.0
    for x in rs:
        g *= 1 + x
        peak = max(peak, g)
    return {"return": compound(rs), "sharpe": _ann_sharpe(rs), "max_drawdown": max_drawdown(rs),
            "current_drawdown": 1 - g / peak}


def to_json(lb: Leaderboards) -> str:
    def row(r: WalletReport) -> dict:
        m = {k: (None if isinstance(v, float) and (math.isinf(v) or math.isnan(v)) else v)
             for k, v in r.metrics.items()}
        return {"address": r.address, "class": r.wallet_class.value, "rank": r.rank,
                "score": round(r.score, 2), "eligible": r.eligible, "reasons": r.reasons,
                "exclusions": r.exclusions, "metrics": m}
    return json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "luck_sharpe": lb.luck_sharpe, "cohorts": lb.cohorts,
        "active": [row(r) for r in lb.active], "buy_hold": [row(r) for r in lb.buy_hold],
        "excluded": [row(r) for r in lb.excluded]}, indent=2)
