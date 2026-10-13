# casingdesign

Casing string design engine for onshore, non-thermal oil and gas wells.
Deterministic API TR 5C3 ratings, standard load cases, design-factor evaluation and a
cheapest-passing-pipe optimizer. See `docs/MVP_PLAN.md` for scope and roadmap.

```bash
pip install -e ".[dev]"
pytest                                  # benchmark suite vs published API tables
casingdesign demo                       # writes example_well.json
casingdesign optimize example_well.json
casingdesign check example_well.json -s "Production=5.5,20,P-110" --json-out out.json
casingdesign ratings 9.625 47 L-80

pip install -e ".[web]"
uvicorn casingdesign.web.app:app      # web UI at http://127.0.0.1:8000 (plots, optimizer)
```

All units are US oilfield (ft, psi, ppg, in, lb/ft, lbf). Every rating function cites the
clause it implements; load-case conventions are documented in `casingdesign/loads/cases.py`.
API joint strengths use the 5C3 round-thread and buttress formulas; the engaged thread
lengths in `catalog/data/thread_lengths.csv` are calibrated to published values and must be
verified against API 5B before production use.
