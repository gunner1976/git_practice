"""Command line interface.

  casingdesign demo                      # write the example well to example_well.json
  casingdesign check WELL.json           # evaluate every string with chosen specs
  casingdesign optimize WELL.json        # find the cheapest passing design per string
  casingdesign ratings OD WEIGHT GRADE   # print API ratings for a pipe item
  casingdesign import EDM.xml            # Landmark EDM/COMPASS/StressCheck export -> well JSON
"""
from __future__ import annotations

import json
from pathlib import Path

import typer

from casingdesign.catalog import Catalog
from casingdesign.design import evaluate_string, optimize_string, optimize_tapered
from casingdesign.examples import onshore_horizontal_well, onshore_liner_well
from casingdesign.well import Well

app = typer.Typer(no_args_is_help=True, add_completion=False)


def _load_well(path: Path) -> Well:
    return Well.model_validate_json(path.read_text())


def _print_summary(result) -> None:
    status = "PASS" if result.passes else "FAIL"
    typer.echo(f"\n{result.string}: {result.spec.label}  [{status}]")
    typer.echo(f"  {'check':<10}{'min DF':>8}{'req':>7}  {'governing case':<22}{'MD ft':>8}")
    for chk, v in result.summary.items():
        flag = "" if v["pass"] else "   <-- FAIL"
        typer.echo(f"  {chk:<10}{v['min_df']:>8.2f}{v['required']:>7.2f}  "
                   f"{v['case']:<22}{v['md']:>8.0f}{flag}")


@app.command()
def demo(out: Path = Path("example_well.json"), liner: bool = False) -> None:
    """Write a built-in example well to JSON so you can edit it (--liner for the
    variant with a frac'd production liner)."""
    well = onshore_liner_well() if liner else onshore_horizontal_well()
    out.write_text(well.model_dump_json(indent=2))
    typer.echo(f"wrote {out}")


@app.command()
def ratings(od: float, weight: float, grade: str, connection: str = "BTC") -> None:
    """API 5C3 performance properties for a catalog pipe item."""
    spec = Catalog.default().spec(od, weight, grade, connection)
    g = spec.geometry
    typer.echo(f"{spec.label}: ID {g.id:.3f} in, wall {g.wall:.3f} in, D/t {g.d_over_t:.2f}")
    typer.echo(f"  burst            {spec.burst:>10,.0f} psi")
    typer.echo(f"  collapse         {spec.collapse:>10,.0f} psi")
    typer.echo(f"  body yield       {spec.body_yield:>10,.0f} lbf")
    typer.echo(f"  joint strength   {spec.joint_strength:>10,.0f} lbf")


@app.command()
def check(well_file: Path,
          spec: list[str] = typer.Option(..., "--spec", "-s",
                                         help="STRING=OD,WEIGHT,GRADE[,CONN], repeatable"),
          json_out: Path | None = typer.Option(None, help="write full results as JSON")) -> None:
    """Evaluate chosen pipe specs against all load cases."""
    well = _load_well(well_file)
    cat = Catalog.default()
    for w in well.warnings():
        typer.echo(f"warning: {w}")
    results = {}
    for item in spec:
        name, rest = item.split("=", 1)
        parts = [p.strip() for p in rest.split(",")]
        od, wt, grade = float(parts[0]), float(parts[1]), parts[2]
        conn = parts[3] if len(parts) > 3 else "BTC"
        r = evaluate_string(well, well.string(name), cat.spec(od, wt, grade, conn))
        _print_summary(r)
        results[name] = {"spec": r.spec.label, "pass": r.passes, "summary": r.summary,
                         "checks": [{"case": c.case, "check": c.check,
                                     "md": c.md.tolist(), "load": c.load.tolist(),
                                     "rating": c.rating.tolist(),
                                     "design_factor": [None if x == float("inf") else x
                                                       for x in c.design_factor.tolist()]}
                                    for c in r.checks]}
    if json_out:
        json_out.write_text(json.dumps(results, indent=1))
        typer.echo(f"\nwrote {json_out}")
    raise typer.Exit(code=0 if all(v["pass"] for v in results.values()) else 1)


@app.command()
def optimize(well_file: Path, string: list[str] = typer.Option(None, "--string"),
             connection: str = "BTC", top: int = 3, tapered: bool = True,
             max_sections: int = 3, min_section: float = 500.0) -> None:
    """Cheapest passing designs for each string (or the named strings), uniform and
    tapered."""
    well = _load_well(well_file)
    cat = Catalog.default()
    targets = [well.string(n) for n in string] if string else well.strings
    for s in targets:
        typer.echo(f"\n{s.name} ({s.od:g} in, {s.hanger_md:.0f}-{s.shoe_md:.0f} ft MD)")
        cands = optimize_string(well, s, cat, connection=connection, max_results=top)
        if not cands:
            typer.echo("  no catalog item passes - consider sectional design or heavier OD")
            continue
        for i, c in enumerate(cands, 1):
            summ = c.result.summary
            dfs = " ".join(f"{k[:4]} {v['min_df']:.2f}" for k, v in summ.items())
            typer.echo(f"  {i}. {c.spec.label:<28} cost idx {c.cost_per_ft:6.1f}/ft   {dfs}")
        if tapered:
            t = optimize_tapered(well, s, cat, connection=connection, max_sections=max_sections,
                                 min_section_length=min_section)
            if t is not None and not t.design.is_uniform:
                summ = t.result.summary
                dfs = " ".join(f"{k[:4]} {v['min_df']:.2f}" for k, v in summ.items())
                saving = 100 * (1 - t.cost_per_ft / cands[0].cost_per_ft) if cands else 0
                typer.echo(f"  tapered: cost idx {t.cost_per_ft:6.1f}/ft ({saving:.1f}% saving)   {dfs}")
                for sec in t.design.sections:
                    typer.echo(f"     {sec.top_md:>7.0f}-{sec.bottom_md:<7.0f} {sec.spec.label}")


@app.command("import")
def import_cmd(edm_file: Path, out: Path = Path("imported_well.json"),
               wellbore: str | None = typer.Option(None, help="wellbore name or id"),
               units: str = typer.Option("feet", help="depth units stored in the file"),
               list_only: bool = typer.Option(False, "--list", help="list wellbores and exit")
               ) -> None:
    """Import a well from a Landmark EDM export; writes well JSON and shows how our
    API 5C3 ratings compare with the ratings stored in the file."""
    from casingdesign.io import import_edm, list_wellbores
    if list_only:
        for wid, wname, well in list_wellbores(edm_file):
            typer.echo(f"{wid:<12} {wname:<40} {well}")
        return
    r = import_edm(edm_file, wellbore=wellbore, source_units=units)
    out.write_text(r.well.model_dump_json(indent=2))
    typer.echo(f"wrote {out}: {r.well.name}, {len(r.well.strings)} strings, "
               f"TD {r.well.trajectory.td:.0f} ft MD")
    for w in r.warnings:
        typer.echo(f"  note: {w}")
    cmp = r.rating_comparison()
    if cmp:
        typer.echo("\nStored (Landmark) vs API 5C3 (ours):")
        typer.echo(f"  {'string':<22}{'pipe':<26}{'burst':>14}{'collapse':>14}{'axial klbf':>16}")
        for c in cmp:
            def pair(a, b, fmt="{:.0f}"):
                return f"{fmt.format(b) if b is not None else '-':>6}/{fmt.format(a):<7}"
            typer.echo(f"  {c['string'][:21]:<22}{c['pipe'][:25]:<26}"
                       f"{pair(c['burst_ours'], c['burst_stored']):>14}"
                       f"{pair(c['collapse_ours'], c['collapse_stored']):>14}"
                       f"{pair(c['axial_ours_klbf'], c['axial_stored_klbf']):>16}")
    if r.specs:
        flags = " ".join(f'-s "{n}={sp.pipe.od},{sp.pipe.nominal_weight},{sp.grade.name},'
                         f'{sp.connection.name}"' for n, sp in r.specs.items())
        typer.echo(f"\nnext: casingdesign check {out} {flags}")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, db: str | None = None) -> None:
    """Run the web application (open http://HOST:PORT in a browser)."""
    import os

    import uvicorn
    if db:
        os.environ["CASINGDESIGN_DB"] = db
    uvicorn.run("casingdesign.web.app:app", host=host, port=port)


if __name__ == "__main__":
    app()
