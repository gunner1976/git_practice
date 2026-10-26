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
        rows.append([str(r.rank), short(r.address), num(r.score, 1), "yes" if m["significant"] else "no",
                     pct(m["cagr"]), num(m["sharpe"]), num(m["sortino"]), pct(-m["max_drawdown"]),
                     share(m["pct_positive_months"]), share(m["win_rate"]), num(m["profit_factor"]),
                     pct(m["active_premium"]), pct(m["alpha_vs_eth"]), pct(m.get("copy_cagr", float("nan"))),
                     num(m["swaps_per_month"], 1)])
    out.append(table(["#", "wallet", "score", "signif", "CAGR", "Sharpe", "Sortino", "MaxDD", "+months",
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
