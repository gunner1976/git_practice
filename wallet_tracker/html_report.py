"""Self-contained HTML report: copy-trade curves (individual, clustered, by
operator group), regime and operator matrices, and the ranked table.

Charts are rendered server-side as static SVG so the page is complete
without JavaScript; a small script adds crosshair and cell tooltips.
"""

from __future__ import annotations

import html
import json
import math
from datetime import datetime, timezone

from .pipeline import BUY_HOLD_ROW, Study
from .regimes import REGIMES

HUMAN_GROUPS = {"human (attested)", "human (behavioural)"}
AUTO_GROUPS = {"automated (behavioural)", "AI agent (declared)"}
COLS = REGIMES + ["stress"]


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def pct(x: float, d: int = 0) -> str:
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x * 100:+.{d}f}%"


def short(a: str) -> str:
    return a[:6] + "…" + a[-4:]


def date(d: int) -> str:
    return datetime.fromtimestamp(d, timezone.utc).strftime("%Y-%m-%d")


def growth(days: list[int], rs: list[float], start: int | None = None, step: int = 3) -> list[tuple[int, float]]:
    """Growth of $1 from `start` (default: first non-zero return), sampled every `step` days."""
    pts, g, started = [], 1.0, False
    for i, (d, r) in enumerate(zip(days, rs)):
        if not started:
            if (start is not None and d >= start) or (start is None and r != 0):
                started = True
                pts.append((d, 1.0))
            continue
        g *= 1 + r
        if i % step == 0 or i == len(days) - 1:
            pts.append((d, max(g, 1e-4)))
    return pts


# ---------------------------------------------------------------- line charts
NICE = [m * 10 ** e for e in range(-3, 6) for m in (1, 2, 5)]


def line_svg(cid: str, series: list[dict], width: int = 720, height: int = 300,
             end_labels: bool = True, compact: bool = False) -> str:
    series = [s for s in series if len(s["pts"]) >= 2]
    if not series:
        return '<p class="empty">Not enough history to draw this chart.</p>'
    ml, mr, mt, mb = (40, 12, 10, 22) if compact else (48, 112 if end_labels else 16, 14, 28)
    x0 = min(p[0] for s in series for p in s["pts"])
    x1 = max(p[0] for s in series for p in s["pts"])
    lo = min(p[1] for s in series for p in s["pts"])
    hi = max(p[1] for s in series for p in s["pts"])
    lo, hi = min(lo, 1.0) * 0.92, max(hi, 1.0) * 1.08
    ly0, ly1 = math.log10(lo), math.log10(hi)
    pw, ph = width - ml - mr, height - mt - mb
    X = lambda d: ml + (d - x0) / max(x1 - x0, 1) * pw  # noqa: E731
    Y = lambda v: mt + (ly1 - math.log10(v)) / max(ly1 - ly0, 1e-9) * ph  # noqa: E731

    ticks = [t for t in NICE if lo <= t <= hi]
    if len(ticks) > 6:
        ticks = [t for t in ticks if str(t).lstrip("0.").startswith(("1", "5"))] or ticks[::2]
    out = [f'<svg class="chart" id="{cid}" viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="{esc(", ".join(s["label"] for s in series))}; growth of $1, log scale">']
    for t in ticks:
        y = Y(t)
        cls = "base" if t == 1 else "gl"
        out.append(f'<line class="{cls}" x1="{ml}" x2="{ml + pw}" y1="{y:.1f}" y2="{y:.1f}"/>')
        lab = f"{t:g}×"
        out.append(f'<text class="tick" x="{ml - 6}" y="{y + 3.5:.1f}" text-anchor="end">{lab}</text>')
    # x ticks: start of quarters
    seen = set()
    for s in series[:1]:
        for d, _ in s["pts"]:
            dt = datetime.fromtimestamp(d, timezone.utc)
            q = (dt.year, (dt.month - 1) // 3)
            if q in seen:
                continue
            seen.add(q)
            if len(seen) == 1:
                continue
            x = X(d)
            label = dt.strftime("%b %y") if not compact else dt.strftime("%b")
            out.append(f'<text class="tick" x="{x:.1f}" y="{height - 6}" text-anchor="middle">{label}</text>')
    for s in series:
        path = " ".join(f"{'M' if i == 0 else 'L'}{X(d):.1f},{Y(v):.1f}" for i, (d, v) in enumerate(s["pts"]))
        dash = ' stroke-dasharray="5 4"' if s.get("dashed") else ""
        out.append(f'<path class="ln {s["cls"]}" d="{path}"{dash}/>')
    if end_labels:
        ends = sorted(((Y(s["pts"][-1][1]), s) for s in series), key=lambda e: e[0])
        placed = []
        for y, s in ends:
            y = max(y, placed[-1] + 15) if placed else y
            placed.append(y)
            lx = ml + pw + 8
            last = s["pts"][-1]
            out.append(f'<circle class="dot {s["cls"]}" cx="{X(last[0]):.1f}" cy="{Y(last[1]):.1f}" r="4"/>')
            out.append(f'<text class="endlab" x="{lx}" y="{y + 4:.1f}">{esc(s.get("short", s["label"]))} '
                       f'<tspan class="endval">{last[1]:.2f}×</tspan></text>')
    out.append(f'<line class="xhair" x1="0" x2="0" y1="{mt}" y2="{mt + ph}" visibility="hidden"/>')
    out.append(f'<rect class="hit" x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="transparent"/>')
    out.append("</svg>")
    data = {"x0": x0, "x1": x1, "ml": ml, "pw": pw, "w": width,
            "series": [{"label": s["label"], "cls": s["cls"], "pts": [[d, round(v, 4)] for d, v in s["pts"]]}
                       for s in series]}
    out.append(f'<script type="application/json" data-for="{cid}">{json.dumps(data)}</script>')
    return "".join(out)


def legend(items: list[tuple[str, str, bool]]) -> str:
    return '<div class="legend">' + "".join(
        f'<span class="key"><svg width="22" height="10" aria-hidden="true"><line class="ln {c}" x1="1" x2="21" '
        f'y1="5" y2="5"{" stroke-dasharray=\"5 4\"" if dashed else ""}/></svg>{esc(lbl)}</span>'
        for lbl, c, dashed in items) + "</div>"


# --------------------------------------------------------------- heatmaps
def heat(rows: list[tuple[str, list[float | None], list[str]]], cols: list[str], scale: float,
         fmt=pct, row_head: str = "") -> str:
    out = ['<div class="scroll"><table class="heat"><thead><tr>',
           f'<th scope="col">{esc(row_head)}</th>']
    out += [f'<th scope="col">{esc(c)}</th>' for c in cols]
    out.append("</tr></thead><tbody>")
    for name, vals, tips in rows:
        out.append(f'<tr><th scope="row">{esc(name)}</th>')
        for v, tip in zip(vals, tips):
            if v is None:
                out.append('<td class="na" data-tip="no data">·</td>')
                continue
            t = max(-1.0, min(1.0, v / scale)) if scale else 0.0
            sign = "pos" if t >= 0 else "neg"
            strong = " strong" if abs(t) > 0.55 else ""
            out.append(f'<td class="cell {sign}{strong}" style="--t:{abs(t):.3f}" data-tip="{esc(tip)}">'
                       f'{fmt(v)}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def scale_for(values: list[float]) -> float:
    vals = sorted(abs(v) for v in values if v is not None)
    if not vals:
        return 1.0
    return max(vals[int(0.9 * (len(vals) - 1))], 1e-6)


# ---------------------------------------------------------------- page
def tier_chip(rep) -> str:
    if rep is None:
        return "–"
    return f'<span class="chip tier-{rep.tier}" title="reputation {rep.score:.0f}/100">{rep.tier} {rep.score:.0f}</span>'


def render_html(study: Study, demo: bool = False, fragment: bool = False) -> str:
    lb = study.boards
    eth_days, eth_rs = study.eth
    start = min((p[0] for r in lb.active for p in growth(r.result.days, r.result.returns)[:1]), default=None)

    def basket(groups: set[str]):
        members = [r for r in study.reports if r.group in groups and r in lb.active]
        from .cluster import combine
        return combine(members, copy=True) if members else ([], [])

    hd, hr = basket(HUMAN_GROUPS)
    ad, ar = basket(AUTO_GROUPS)
    bd, br = study.baskets.get(BUY_HOLD_ROW, ([], []))
    n_h = sum(1 for r in lb.active if r.group in HUMAN_GROUPS)
    n_a = sum(1 for r in lb.active if r.group in AUTO_GROUPS)
    s_op = [
        {"label": f"Human copy basket ({n_h})", "short": "Human", "cls": "s1", "pts": growth(hd, hr, start)},
        {"label": f"Automated copy basket ({n_a})", "short": "Automated", "cls": "s2", "pts": growth(ad, ar, start)},
        {"label": "Buy-and-hold wallets", "short": "Buy & hold", "cls": "s3", "pts": growth(bd, br, start)},
        {"label": "ETH", "cls": "bench", "pts": growth(eth_days, eth_rs, start), "dashed": True},
    ]

    top = lb.active[:6]
    multiples = []
    for r in top:
        a = growth(r.result.days, r.result.returns)
        st0 = a[0][0] if a else None
        c = growth(r.result.days, r.copy_returns, st0)
        e = growth(eth_days, eth_rs, st0)
        m = r.metrics
        multiples.append(
            f'<figure class="mini"><figcaption><span class="mono">#{r.rank} {short(r.address)}</span>'
            f'{tier_chip(r.reputation)}<span class="grp">{esc(r.group)}</span></figcaption>'
            + line_svg(f"w{r.rank}", [{"label": "Wallet", "cls": "s1", "pts": a},
                                     {"label": "Copy (1 day late, 30 bps)", "cls": "s2", "pts": c},
                                     {"label": "ETH", "cls": "bench", "pts": e, "dashed": True}],
                       360, 190, end_labels=False, compact=True)
            + f'<p class="mini-stats">CAGR {pct(m["cagr"])} · copy {pct(m.get("copy_cagr"))} · '
              f'captured {m.get("copy_capture", 0) * 100:.0f}% · RRS {m.get("regime_robustness", 0):.2f}</p></figure>')

    cl_html = []
    for cl in study.clusters:
        a = growth(cl.days, cl.returns)
        st0 = a[0][0] if a else None
        cl_html.append(
            f'<figure class="mini"><figcaption><span class="mono">Cluster {cl.id}</span>'
            f'<span class="grp">{len(cl.members)} linked wallets</span></figcaption>'
            + line_svg(f"c{cl.id}", [{"label": "Combined wallets", "cls": "s1", "pts": a},
                                    {"label": "Copy basket", "cls": "s2", "pts": growth(cl.days, cl.copy_returns, st0)},
                                    {"label": "ETH", "cls": "bench", "pts": growth(eth_days, eth_rs, st0),
                                     "dashed": True}], 360, 190, end_labels=False, compact=True)
            + f'<p class="mini-stats">CAGR {pct(cl.stats["cagr"])} · copy {pct(cl.stats["copy_cagr"])} · '
              f'Sharpe {cl.stats["sharpe"]:.2f} → {cl.stats["copy_sharpe"]:.2f}</p>'
            + '<ul class="evidence">' + "".join(f"<li>{esc(e)}</li>" for e in cl.evidence[:4]) + "</ul>"
            + '<p class="members mono">' + " ".join(short(m) for m in cl.members) + "</p></figure>")

    # Operator x regime
    vals = [c["median_excess"] / (365 if k == "stress" else 1)
            for cells in study.operator_regime.values() for k, c in cells.items()]
    sc = scale_for(vals)
    op_rows = []
    for g, cells in study.operator_regime.items():
        v = [(cells[c]["median_excess"] / (365 if c == "stress" else 1)) if c in cells else None for c in COLS]
        tips = [f"{g} · {c}: median {pct(x, 1)} vs ETH across {cells[c]['n']} wallets" if c in cells else ""
                for c, x in zip(COLS, v)]
        op_rows.append((g, v, tips))

    quarters = sorted({q for cells in study.operator_quarter.values() for q in cells})
    qvals = [c["median_return"] for cells in study.operator_quarter.values() for c in cells.values()]
    q_rows = [(g, [cells[q]["median_return"] if q in cells else None for q in quarters],
               [f"{g} · {q}: median quarterly return {pct(cells[q]['median_return'], 1)} ({cells[q]['n']} wallets)"
                if q in cells else "" for q in quarters]) for g, cells in study.operator_quarter.items()]

    w_rows = []
    wvals = []
    for r in lb.active[:12]:
        v = [(r.regimes[c]["ann_excess"] / (365 if c == "stress" else 1))
             if r.regimes.get(c, {}).get("days", 0) >= 10 else None for c in COLS]
        wvals += [x for x in v if x is not None]
        w_rows.append((f"#{r.rank} {short(r.address)}", v,
                       [f"{c}: {pct(x, 1)} vs ETH over {r.regimes[c]['days']} days" if x is not None else ""
                        for c, x in zip(COLS, v)]))

    summary_rows = "".join(
        f"<tr><th scope='row'>{esc(g)}</th><td>{v['n']}</td><td>{v['median_human_score']:.2f}</td>"
        f"<td>{pct(v['median_cagr'])}</td><td>{v['median_sharpe']:.2f}</td><td>{pct(-v['median_max_drawdown'])}</td>"
        f"<td>{v['median_regime_robustness']:.2f}</td><td>{pct(v['median_copy_cagr'])}</td><td>{v['significant']}</td></tr>"
        for g, v in study.operator_summary.items())

    rank_rows = "".join(
        f"<tr><td>{r.rank}</td><td class='mono'>{short(r.address)}</td><td>{r.score:.0f}</td>"
        f"<td>{'<span class=\"chip sig\">significant</span>' if r.metrics.get('significant') else '–'}</td>"
        f"<td>{tier_chip(r.reputation)}</td><td>{esc(r.group)}</td>"
        f"<td>{esc(r.identity.name) if r.identity is not None and r.identity.attested else '–'}</td>"
        f"<td>{pct(r.metrics['cagr'])}</td><td>{r.metrics['sharpe']:.2f}</td><td>{pct(-r.metrics['max_drawdown'])}</td>"
        f"<td>{r.metrics.get('regime_robustness', 0):.2f}</td><td>{r.metrics.get('pct_windows_beat_eth', 0) * 100:.0f}%</td>"
        f"<td>{pct(r.metrics.get('copy_cagr'))}</td>"
        f"<td class='flags'>{esc('; '.join(r.reputation.flags)) if r.reputation and r.reputation.flags else ''}</td></tr>"
        for r in lb.active[:25])

    m_sig = sum(1 for r in lb.active if r.metrics.get("significant"))
    span = f"{date(eth_days[0])} to {date(eth_days[-1])}" if eth_days else ""
    tiles = [("Wallets screened", len(study.reports)), ("Eligible active traders", len(lb.active)),
             ("Pass the luck test", m_sig), ("Linked clusters", len(study.clusters)),
             ("Sharpe expected from luck", f"{lb.luck_sharpe:.2f}")]
    demo_note = ('<p class="note"><strong>Synthetic demo data.</strong> Wallets, prices and identities '
                 '(e.g. demo-trader-1.eth) are generated by the built-in simulator, not real accounts.</p>'
                 if demo else "")

    body = f"""
<header class="top">
  <p class="eyebrow">On-chain trader study · {esc(span)}</p>
  <h1>Wallet Edge Report</h1>
  <p class="lede">Which wallets keep an edge across market regimes, how credible they are, whether a human or software runs
  them, and what a follower who copies them one day late would actually have earned.</p>
  {demo_note}
  <div class="tiles">{"".join(f'<div class="tile"><span class="tv">{esc(v)}</span><span class="tl">{esc(k)}</span></div>' for k, v in tiles)}</div>
</header>

<section>
  <h2>Copy-trade performance by operator</h2>
  <p class="sub">Equal-weight baskets copying every eligible wallet in each group, one day late, after 30 bps per trade. Growth of $1, log scale.</p>
  {legend([(s["label"], s["cls"], bool(s.get("dashed"))) for s in s_op])}
  <div class="chartbox">{line_svg("ops", s_op)}</div>
</section>

<section>
  <h2>Top wallets: actual vs copied</h2>
  <p class="sub">The gap between the two lines is the part of the edge a follower can't capture (speed, execution, size).</p>
  {legend([("Wallet", "s1", False), ("Copy (1 day late, 30 bps)", "s2", False), ("ETH", "bench", True)])}
  <div class="grid">{"".join(multiples) or '<p class="empty">No eligible wallets.</p>'}</div>
</section>

<section>
  <h2>Linked-wallet clusters</h2>
  <p class="sub">Wallets tied together by direct transfers, a shared first funder or repeated same-hour trades: probably one operator.
  Combined performance is value-weighted; the copy basket follows every member equally.</p>
  <div class="grid">{"".join(cl_html) or '<p class="empty">No linked wallets found in this sample.</p>'}</div>
</section>

<section>
  <h2>Human vs automated, by market regime</h2>
  <p class="sub">Median annualised return over ETH inside each regime. Stress = ETH's worst 5% of days, shown per day.
  Regimes come from ETH's trailing 30-day trend (±10%) and volatility (above or below median).</p>
  {heat(op_rows, COLS, sc, row_head="Operator group")}
  <h3>Over time</h3>
  <p class="sub">Median quarterly return of each group's wallets, so you can track whether software or people are pulling ahead.</p>
  {heat(q_rows, quarters, scale_for(qvals), row_head="Operator group")}
  <div class="scroll"><table class="data">
    <thead><tr><th scope="col">Group</th><th scope="col">Wallets</th><th scope="col">Human score</th><th scope="col">CAGR</th>
    <th scope="col">Sharpe</th><th scope="col">Max DD</th><th scope="col">RRS</th><th scope="col">Copy CAGR</th><th scope="col">Significant</th></tr></thead>
    <tbody>{summary_rows}</tbody></table></div>
</section>

<section>
  <h2>Regime risk matrix: top wallets</h2>
  <p class="sub">Annualised excess return over ETH per regime. A wallet that is blue across the row adds value in every
  market, which is what the Regime Robustness Score (RRS) rewards.</p>
  {heat(w_rows, COLS, scale_for(wvals), row_head="Wallet")}
</section>

<section>
  <h2>Ranked active traders</h2>
  <p class="sub">Significant = Sharpe beats the best result this many skill-less wallets would show by luck (deflated Sharpe ≥ 95%).
  Reputation tiers: A ≥ 75, B ≥ 55, C ≥ 35, D below.</p>
  <div class="scroll"><table class="data rank">
    <thead><tr><th scope="col">#</th><th scope="col">Wallet</th><th scope="col">Score</th><th scope="col">Luck test</th>
    <th scope="col">Reputation</th><th scope="col">Operator</th><th scope="col">Identity</th><th scope="col">CAGR</th>
    <th scope="col">Sharpe</th><th scope="col">Max DD</th><th scope="col">RRS</th><th scope="col">90d beats ETH</th>
    <th scope="col">Copy CAGR</th><th scope="col">Flags</th></tr></thead>
    <tbody>{rank_rows}</tbody></table></div>
  <p class="foot">Identity shows only self-published or publicly sourced attestations. Operator groups are behavioural
  estimates, not proof. Past performance, even luck-adjusted, does not guarantee future returns.</p>
</section>
<div class="tip" id="tip" hidden></div>
"""
    page = f"<title>Wallet Edge Report</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n{FONTS}\n<style>{CSS}</style>\n<main>{body}</main>\n<script>{JS}</script>\n"
    if fragment:
        return page
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            f"</head><body>\n{page}</body></html>\n")


FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=Schibsted+Grotesk:wght@600;700&display=swap">')

CSS = """
/* Layout: one reading column of stacked study sections; charts full-width, small multiples in a wrapping grid. */
:root {
  --bg: #f4f6f8; --surface: #ffffff; --ink: #10161c; --ink-2: #47515c; --muted: #77818c;
  --grid: #e2e6ea; --axis: #c2c9d0; --line: rgba(16,22,28,0.10);
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --bench: #77818c;
  --div-pos: #1c5cab; --div-neg: #c53a39; --div-mid: #eef0f2;
  --good: #0ca30c; --warn: #fab219; --serious: #ec835a; --crit: #d03b3b;
  --f-display: "Schibsted Grotesk", "Helvetica Neue", Arial, sans-serif;
  --f-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e1215; --surface: #161b20; --ink: #edf1f4; --ink-2: #b6bfc8; --muted: #8a949e;
  --grid: #252b31; --axis: #39424a; --line: rgba(255,255,255,0.10);
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --bench: #8a949e;
  --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #262c33; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0e1215; --surface: #161b20; --ink: #edf1f4; --ink-2: #b6bfc8; --muted: #8a949e;
  --grid: #252b31; --axis: #39424a; --line: rgba(255,255,255,0.10);
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --bench: #8a949e;
  --div-pos: #3987e5; --div-neg: #e66767; --div-mid: #262c33; color-scheme: dark; }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); }
main { max-width: 1080px; margin: 0 auto; padding-block: 28px 56px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: flex; flex-direction: column; gap: 44px; }
h1, h2, h3 { font-family: var(--f-display); text-wrap: balance; margin: 0; letter-spacing: -0.01em; }
h1 { font-size: clamp(30px, 5vw, 44px); line-height: 1.05; }
h2 { font-size: 22px; }
h3 { font-size: 16px; margin-top: 22px; }
section { display: flex; flex-direction: column; gap: 10px; min-width: 0; }
.eyebrow { margin: 0; font: 500 12px var(--f-mono); letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }
.lede { margin: 0; max-width: 64ch; color: var(--ink-2); font-size: 17px; }
.sub { margin: 0; max-width: 72ch; color: var(--ink-2); }
.note { margin: 0; padding: 10px 14px; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); max-width: 72ch; }
.top { display: flex; flex-direction: column; gap: 14px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1px; background: var(--line);
  border: 1px solid var(--line); border-radius: 8px; overflow: hidden; margin-top: 6px; }
.tile { background: var(--surface); padding: 14px 16px; display: flex; flex-direction: column; gap: 2px; }
.tv { font: 600 26px var(--f-display); }
.tl { font-size: 12px; color: var(--muted); letter-spacing: 0.02em; }
.chartbox { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 12px 8px 4px; overflow-x: auto; }
.chartbox svg.chart { min-width: 560px; }
@media (max-width: 600px) { .tile:last-child:nth-child(odd) { grid-column: 1 / -1; } }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 14px; }
.mini { margin: 0; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 12px;
  display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.mini figcaption { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: 13px; }
.grp { color: var(--muted); font-size: 12px; }
.mini-stats, .members { margin: 0; font-size: 12px; color: var(--ink-2); font-variant-numeric: tabular-nums; }
.evidence { margin: 0; padding-left: 18px; font-size: 12px; color: var(--ink-2); }
.mono { font-family: var(--f-mono); font-size: 12.5px; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 13px; color: var(--ink-2); }
.key { display: inline-flex; align-items: center; gap: 6px; }
svg.chart { width: 100%; height: auto; display: block; overflow: visible; }
.chart .gl { stroke: var(--grid); stroke-width: 1; }
.chart .base { stroke: var(--axis); stroke-width: 1; }
.chart .tick { fill: var(--muted); font: 11px var(--f-body); font-variant-numeric: tabular-nums; }
.ln { fill: none; stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.ln.s1 { stroke: var(--s1); } .ln.s2 { stroke: var(--s2); } .ln.s3 { stroke: var(--s3); } .ln.bench { stroke: var(--bench); stroke-width: 1.5; }
.dot { stroke: var(--surface); stroke-width: 2; }
.dot.s1 { fill: var(--s1); } .dot.s2 { fill: var(--s2); } .dot.s3 { fill: var(--s3); } .dot.bench { fill: var(--bench); }
.endlab { fill: var(--ink-2); font: 12px var(--f-body); }
.endval { fill: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }
.xhair { stroke: var(--axis); stroke-width: 1; }
.scroll { overflow-x: auto; min-width: 0; }
table { border-collapse: collapse; font-variant-numeric: tabular-nums; }
table.heat { border-collapse: separate; border-spacing: 2px; font-size: 12.5px; }
.heat th { font-weight: 500; color: var(--ink-2); text-align: left; padding: 4px 10px 4px 0; white-space: nowrap; }
.heat thead th { font-size: 11.5px; color: var(--muted); text-align: center; padding: 0 4px 4px; }
.heat td { min-width: 76px; text-align: center; padding: 7px 6px; border-radius: 4px; color: var(--ink); }
.heat td.pos { background: color-mix(in oklab, var(--div-mid), var(--div-pos) calc(var(--t) * 100%)); }
.heat td.neg { background: color-mix(in oklab, var(--div-mid), var(--div-neg) calc(var(--t) * 100%)); }
.heat td.strong { color: #ffffff; }
.heat td.na { color: var(--muted); background: transparent; }
table.data { width: 100%; font-size: 13px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }
.data th, .data td { padding: 8px 10px; text-align: right; border-bottom: 1px solid var(--line); white-space: nowrap; }
.data th:first-child, .data td:first-child { text-align: left; }
.data thead th { font-size: 11.5px; font-weight: 500; color: var(--muted); letter-spacing: 0.02em; }
.data tbody th { font-weight: 500; text-align: left; }
.rank td:nth-child(2), .rank td:nth-child(6), .rank td:nth-child(7), .rank td.flags { text-align: left; }
.flags { color: var(--crit); font-size: 12px; white-space: normal; min-width: 140px; }
.chip { display: inline-block; padding: 1px 7px; border-radius: 10px; font: 600 11.5px var(--f-body); border: 1px solid var(--line); }
.tier-A { background: color-mix(in oklab, var(--surface), var(--good) 22%); }
.tier-B { background: color-mix(in oklab, var(--surface), var(--warn) 18%); }
.tier-C { background: color-mix(in oklab, var(--surface), var(--serious) 24%); }
.tier-D { background: color-mix(in oklab, var(--surface), var(--crit) 22%); }
.chip.sig { background: color-mix(in oklab, var(--surface), var(--s1) 18%); font-weight: 500; }
.foot { margin: 0; font-size: 12.5px; color: var(--muted); max-width: 80ch; }
.empty { color: var(--muted); margin: 0; }
.tip { position: fixed; z-index: 20; pointer-events: none; background: var(--surface); color: var(--ink);
  border: 1px solid var(--line); border-radius: 6px; padding: 8px 10px; font-size: 12.5px; max-width: 280px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12); font-variant-numeric: tabular-nums; }
.tip b { font-weight: 600; } .tip .sw { display: inline-block; width: 10px; height: 2px; margin-right: 6px; vertical-align: middle; }
"""

JS = """
(function () {
  const tip = document.getElementById('tip');
  const fmtDate = d => new Date(d * 1000).toISOString().slice(0, 10);
  function place(e) {
    const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
    let x = e.clientX + pad, y = e.clientY + pad;
    if (x + w > innerWidth - 8) x = e.clientX - w - pad;
    if (y + h > innerHeight - 8) y = e.clientY - h - pad;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  document.querySelectorAll('script[data-for]').forEach(s => {
    const svg = document.getElementById(s.dataset.for);
    if (!svg) return;
    const D = JSON.parse(s.textContent);
    const hit = svg.querySelector('.hit'), xh = svg.querySelector('.xhair');
    hit.addEventListener('pointermove', e => {
      const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
      const p = pt.matrixTransform(svg.getScreenCTM().inverse());
      const day = D.x0 + (p.x - D.ml) / D.pw * (D.x1 - D.x0);
      let rows = '', snap = null;
      D.series.forEach(se => {
        let best = se.pts[0];
        for (const q of se.pts) if (Math.abs(q[0] - day) < Math.abs(best[0] - day)) best = q;
        if (snap === null) snap = best[0];
        rows += `<div><span class="sw" style="background:var(--${se.cls})"></span>${se.label}: <b>${best[1].toFixed(2)}×</b></div>`;
      });
      const x = D.ml + (snap - D.x0) / (D.x1 - D.x0) * D.pw;
      xh.setAttribute('x1', x); xh.setAttribute('x2', x); xh.setAttribute('visibility', 'visible');
      tip.innerHTML = `<div>${fmtDate(snap)}</div>${rows}`; tip.hidden = false; place(e);
    });
    hit.addEventListener('pointerleave', () => { tip.hidden = true; xh.setAttribute('visibility', 'hidden'); });
  });
  document.querySelectorAll('td[data-tip]').forEach(td => {
    if (!td.dataset.tip) return;
    td.addEventListener('pointermove', e => { tip.textContent = td.dataset.tip; tip.hidden = false; place(e); });
    td.addEventListener('pointerleave', () => { tip.hidden = true; });
  });
})();
"""
