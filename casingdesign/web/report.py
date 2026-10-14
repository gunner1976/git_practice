"""Printable HTML design report (print to PDF from the browser)."""
from __future__ import annotations

import html
from datetime import UTC, datetime

from casingdesign.well import Well


def _n(x, d=0):
    return "—" if x is None else f"{x:,.{d}f}"


def render_report(project: dict, well: Well, data: dict) -> str:
    e = html.escape
    f = well.formation
    rows_strings = "".join(
        f"<tr><td>{e(s.name)}</td><td>{e(s.type)}</td><td>{s.od:g}</td><td>{s.hole_size:g}</td>"
        f"<td>{_n(s.hanger_md)}</td><td>{_n(s.shoe_md)}</td><td>{_n(s.toc_md)}</td>"
        f"<td>{s.mud_weight:g}</td><td>{s.cement_lead_ppg:g}/{s.cement_tail_ppg:g}</td></tr>"
        for s in well.strings)
    traj = "".join(f"<tr><td>{_n(st.md)}</td><td>{st.inclination:g}</td><td>{st.azimuth:g}</td>"
                   f"<td>{_n(float(well.trajectory.tvd(st.md)))}</td></tr>"
                   for st in well.trajectory.stations)
    pp = "".join(f"<tr><td>{_n(p.tvd)}</td><td>{p.value:g}</td></tr>" for p in f.pore_pressure.points)
    fg = "".join(f"<tr><td>{_n(p.tvd)}</td><td>{p.value:g}</td></tr>"
                 for p in f.fracture_gradient.points)
    dfs = well.design_factors
    sections = []
    for st in data["strings"]:
        r = st["result"]
        if r is None:
            sections.append(f"<h3>{e(st['string'])}</h3><p class='fail'>No catalog pipe passes.</p>")
            continue
        secs = "".join(
            f"<tr><td>{_n(x['top_md'])}–{_n(x['bottom_md'])}</td><td>{e(x['spec']['label'])}</td>"
            f"<td>{x['spec']['id']:.3f}</td><td>{_n(x['spec']['burst'])}</td>"
            f"<td>{_n(x['spec']['collapse'])}</td><td>{_n(x['spec']['body_yield'])}</td>"
            f"<td>{_n(x['spec']['joint_strength'])}</td></tr>" for x in r["design"]["sections"])
        checks = "".join(
            f"<tr><td>{k}</td><td>{v['min_df']:.2f}</td><td>{v['required']:.2f}</td>"
            f"<td>{e(v['case'])}</td><td>{_n(v['md'])}</td>"
            f"<td class='{'pass' if v['pass'] else 'fail'}'>{'PASS' if v['pass'] else 'FAIL'}</td></tr>"
            for k, v in r["summary"].items())
        cases = "".join(f"<li><b>{e(c['name'])}</b>: {e(c['description'])}</li>" for c in r["cases"])
        status = "PASS" if r["pass"] else "FAIL"
        src = "user selection" if st["overridden"] else "optimizer recommendation"
        sections.append(f"""
<h3>{e(st['string'])} — {st['od']:g}" from {_n(st['top_md'])} to {_n(st['shoe_md'])} ft MD
  <span class="{status.lower()}">{status}</span></h3>
<p class="muted">Pipe: {src}.</p>
<table><thead><tr><th>MD (ft)</th><th>Pipe</th><th>ID (in)</th><th>Burst (psi)</th><th>Collapse (psi)</th>
<th>Body yield (lbf)</th><th>Joint (lbf)</th></tr></thead><tbody>{secs}</tbody></table>
<table><thead><tr><th>Check</th><th>Min DF</th><th>Required</th><th>Governing case</th><th>MD (ft)</th><th></th></tr></thead>
<tbody>{checks}</tbody></table>
<details><summary>Load cases applied ({len(r['cases'])})</summary><ul>{cases}</ul></details>""")
    warn = "".join(f"<li>{e(w)}</li>" for w in data.get("warnings", []))
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Casing design — {e(well.name)}</title>
<style>
body{{font:13px/1.45 system-ui,sans-serif;color:#1c2430;max-width:960px;margin:24px auto;padding:0 16px}}
h1{{font-size:22px;margin:0}} h2{{font-size:16px;margin:26px 0 8px;border-bottom:1px solid #ccd;padding-bottom:4px}}
h3{{font-size:14px;margin:18px 0 4px}} table{{border-collapse:collapse;width:100%;margin:6px 0 10px;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:4px 6px;border-bottom:1px solid #e3e6ea;font-size:12px}} th{{color:#5f6b7a}}
.pass{{color:#1e8e4f;font-weight:600}} .fail{{color:#c0392b;font-weight:600}} .muted{{color:#5f6b7a}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px}} .meta{{color:#5f6b7a;margin:4px 0 0}}
@media print{{ details{{display:none}} h2{{page-break-after:avoid}} }}
</style></head><body>
<h1>Casing design report — {e(well.name)}</h1>
<p class="meta">Project {e(project['id'])} · generated {now} · engine casingdesign (API TR 5C3 ratings; load cases per onshore convention)</p>
<h2>Design basis</h2>
<p>Design factors: burst {dfs.burst}, collapse {dfs.collapse}, tension {dfs.tension}, triaxial {dfs.triaxial}.
Gas gradient {well.gas_gradient_psi_ft} psi/ft. Surface temperature {f.surface_temperature_f:g} °F,
geothermal gradient {f.geothermal_gradient_f_per_100ft:g} °F/100 ft; yield derating
{'on' if well.yield_derating.enabled else 'off'} ({well.yield_derating.slope_per_f * 100:.3f} %/°F above
{well.yield_derating.reference_f:g} °F). {'Sour service.' if f.sour else ''}</p>
<div class="grid"><div><h3>Pore pressure (EMW)</h3><table><thead><tr><th>TVD (ft)</th><th>ppg</th></tr></thead><tbody>{pp}</tbody></table></div>
<div><h3>Fracture gradient (EMW)</h3><table><thead><tr><th>TVD (ft)</th><th>ppg</th></tr></thead><tbody>{fg}</tbody></table></div></div>
<h3>Trajectory</h3><table><thead><tr><th>MD (ft)</th><th>Inc (°)</th><th>Azi (°)</th><th>TVD (ft)</th></tr></thead><tbody>{traj}</tbody></table>
<h3>Casing program</h3><table><thead><tr><th>String</th><th>Type</th><th>OD</th><th>Hole</th><th>Top MD</th><th>Shoe MD</th><th>TOC MD</th><th>Mud ppg</th><th>Cement lead/tail</th></tr></thead><tbody>{rows_strings}</tbody></table>
{'<h2>Warnings</h2><ul>' + warn + '</ul>' if warn else ''}
<h2>Results</h2>{''.join(sections)}
<p class="muted" style="margin-top:30px">Ratings per API TR 5C3 (burst: Barlow with 87.5 % wall; collapse: four-regime with axial-stress correction;
joint strength: API round-thread and buttress formulas; triaxial: von Mises at inner/outer fibre with bending). Load-case conventions
are documented in the engine source. This report is a design aid and does not replace engineering review.</p>
</body></html>"""
