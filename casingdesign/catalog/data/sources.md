# Catalog data sources

- `pipe.csv` — API Spec 5CT casing dimensional data (OD, nominal weight, wall, drift).
  Cross-checked against, and extended from, the Apache-2.0 `welleng` catalogue
  (`welleng/catalog/data/casing.json`, which cites API Spec 5CT by table). Drift = ID minus
  the API drift undersize (1/8 in for OD <= 8-5/8, 5/32 in for 9-5/8 to 13-3/8, 3/16 in
  for OD >= 16).
- `grades.csv` — API Spec 5CT Table E.5 tensile requirements (min/max yield, min UTS).
- `connections.csv` — connection kinds; joint strength computed per API TR 5C3 (see
  `ratings/joints.py`).
- `thread_lengths.csv` — engaged thread lengths for API round threads, calibrated to
  published joint strengths; verify against API 5B before production use.
