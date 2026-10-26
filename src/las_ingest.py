"""Parse every Tecolutla LAS file on disk and write a catalogue plus per-file curve CSVs.

Inputs : data/raw/petrophysics/LAS/*.las|*.LAS  (plus data/raw/geology/tec10_image_log/*.las and
         data/raw/colab_out/las/*.las, the gunzipped Colab copies of files too large for the connector;
         name map in data/processed/petrophysics/las/colab_las_name_map.csv)
         data/manifest.csv                     (Drive id, sha256 for each file)
         data/processed/wells/casing_strings.csv (KB per well, for reference only)
Outputs: data/processed/petrophysics/las/las_catalog.csv      one row per file
         data/processed/petrophysics/las/las_curve_index.csv  one row per file x curve (units, depth range, stats)
         data/processed/petrophysics/las/curves_<well>_<file-stem>.csv
             depth + curves, nulls as NaN, original mnemonics; the depth column is named
             "<MNEM>_<unit>" (e.g. DEPT_M) so the depth unit is explicit.
             Files whose bytes are identical to an earlier file (same sha256) are not written
             again; the catalogue row names the file it duplicates.

Headerless "LAS" exports (WellSight) are read as whitespace-delimited columns and their columns
are identified by exact correlation (|r| >= 0.999) against the full TEC-11 LWD LAS; the match is
recorded in header_problems. Nothing is interpolated, depth-shifted or unit-converted.

Run: .venv/bin/python src/las_ingest.py
"""
import csv, hashlib, io, logging, re, warnings
from pathlib import Path

import lasio
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = [ROOT / "data/raw/petrophysics/LAS", ROOT / "data/raw/geology/tec10_image_log",
       ROOT / "data/raw/colab_out/las"]  # last, so Colab copies are flagged duplicate_of earlier files
OUT = ROOT / "data/processed/petrophysics/las"
MANIFEST = ROOT / "data/manifest.csv"
CASING = ROOT / "data/processed/wells/casing_strings.csv"
WELLSIGHT_REF = "Tecolutla 11_LAS_GR_SST_3283 mMD.las"

ELEV_KEYS = ["EKB", "KB", "EDF", "DF", "EGL", "GL", "ELEV", "EREF", "ERED", "EPD", "APD", "DREF",
             "PDAT", "LMF", "DMF", "E??", "EWD"]


def well_from(name: str, header_well: str) -> str:
    s = f"{name} {header_well}".upper().replace("TECOLULTA", "TECOLUTLA")
    if name.upper() == "MYDATA.LAS":
        s = header_well.upper()
    m = re.search(r"(?:TECOLUTLA|TEC)[\s_\-]*0*(101|11|10|9|7|6|5|3|2)(?!\d)", s)
    return f"TEC-{m.group(1)}" if m else "UNKNOWN"


def manifest_by_path():
    rows = {}
    with MANIFEST.open(newline="") as f:
        for r in csv.DictReader(f):
            rows[r["path"]] = r  # last row wins
    return rows


def kb_by_well():
    kb = {}
    if CASING.exists():
        for r in csv.DictReader(CASING.open(newline="")):
            kb.setdefault(r["well"], r.get("kb_m", ""))
    return kb


def hval(sec, key):
    try:
        it = sec[key]
    except (KeyError, IndexError):
        return None
    return it


def read_las(path: Path):
    """Return (las or None, df, problems list)."""
    problems = []
    handler = _ListHandler()
    lg = logging.getLogger("lasio")
    lg.addHandler(handler)
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            las = lasio.read(str(path), ignore_header_errors=True)
            problems += [str(x.message) for x in w]
    finally:
        lg.removeHandler(handler)
    problems += handler.msgs
    df = las.df().copy().reset_index()
    return las, df, problems


class _ListHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.msgs = []

    def emit(self, record):
        self.msgs.append(record.getMessage())


def read_headerless(path: Path, ref_df: pd.DataFrame | None):
    df = pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    df = df.replace(-999.25, np.nan)
    names = ["DEPT"]
    notes = ["no ~V/~W/~C sections: headerless whitespace-delimited ASCII (WellSight export); "
             "NULL -999.25 assumed; depth unit assumed M (values match TEC-11 MD in metres)"]
    if ref_df is not None:
        ref = ref_df.copy()
        ref["_d"] = ref.iloc[:, 0].round(2)
        ref = ref.drop_duplicates("_d").set_index("_d")
        d = df.copy()
        d["_d"] = d[0].round(2)
        d = d.drop_duplicates("_d").set_index("_d")
        j = d.join(ref, how="inner")
        for c in df.columns[1:]:
            best, br = None, 0.0
            for rc in ref.columns[1:]:
                pair = j[[c, rc]].dropna()
                if len(pair) > 50 and pair[c].std() > 0 and pair[rc].std() > 0:
                    r = abs(np.corrcoef(pair[c], pair[rc])[0, 1])
                    if r > br:
                        best, br = rc, r
            if best and br >= 0.999:
                names.append(best)
                notes.append(f"col{c + 1}={best} (r={br:.4f} vs {WELLSIGHT_REF})")
            else:
                names.append(f"COL{c + 1}")
                notes.append(f"col{c + 1} unidentified (best r={br:.3f})")
    else:
        names += [f"COL{c + 1}" for c in df.columns[1:]]
    df.columns = names
    return df, notes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    man = manifest_by_path()
    kbw = kb_by_well()
    files = []
    for d in RAW:
        if d.exists():
            files += sorted(p for p in d.iterdir() if p.suffix.lower() == ".las")
    # reference for headerless files
    ref_path = RAW[0] / WELLSIGHT_REF
    ref_df = lasio.read(str(ref_path)).df().reset_index() if ref_path.exists() else None

    cat, idx = [], []
    seen_sha = {}
    for p in files:
        rel = str(p.relative_to(ROOT))
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        m = man.get(rel, {})
        problems = []
        las = None
        head = raw[:4000].decode("latin-1")
        if "~" not in head:
            df, notes = read_headerless(p, ref_df)
            problems += notes
            version, wrap, dunit, null = "none", "", "M (assumed)", "-999.25 (assumed)"
            hdr_well, comp, srvc, date = "", "", "", ""
            elev = {}
            curves_desc = [(c, "", "") for c in df.columns]
        else:
            try:
                las, df, problems = read_las(p)
            except Exception as e:  # noqa: BLE001
                cat.append({"file": p.name, "path": rel, "header_problems": f"PARSE FAILED: {e}"})
                continue
            W, V = las.well, las.version
            g = lambda k: (str(hval(W, k).value).strip() if hval(W, k) is not None else "")
            version = str(hval(V, "VERS").value) if hval(V, "VERS") is not None else ""
            wrap = str(hval(V, "WRAP").value) if hval(V, "WRAP") is not None else ""
            hdr_well, comp, srvc, date = g("WELL"), g("COMP"), g("SRVC"), g("DATE")
            strt_unit = hval(W, "STRT").unit if hval(W, "STRT") is not None else ""
            idx_unit = las.curves[0].unit if len(las.curves) else ""
            dunit = idx_unit or strt_unit
            if strt_unit and idx_unit and strt_unit.upper() != idx_unit.upper():
                problems.append(f"depth unit conflict: STRT/STOP in '{strt_unit}', index curve in '{idx_unit}'")
            null = g("NULL")
            elev = {}
            for sec in (las.well, las.params):
                for it in sec:
                    if it.mnemonic.upper() in ELEV_KEYS and str(it.value).strip() not in ("",):
                        elev[it.mnemonic] = f"{it.value}{(' ' + it.unit) if it.unit else ''}"
            curves_desc = [(c.mnemonic, c.unit, c.descr.strip()) for c in las.curves]
            # header vs data checks
            try:
                hs, he, hst = float(g("STRT")), float(g("STOP")), float(g("STEP") or 0)
                ds, de = float(df.iloc[0, 0]), float(df.iloc[-1, 0])
                if abs(hs - ds) > 0.01 or abs(he - de) > 0.01:
                    problems.append(f"STRT/STOP {hs}/{he} differ from data {ds}/{de}")
                if hst == 0:
                    problems.append("STEP=0 (irregular sampling)")
                if hs > he:
                    problems.append("depth decreasing (logged up; STRT > STOP)")
            except ValueError:
                problems.append("STRT/STOP/STEP not numeric")
            if not date or date.upper() == "UNKNOWN":
                problems.append("no DATE in header")
            if not srvc or srvc.upper() == "UNKNOWN":
                problems.append("no SRVC in header")
            for warn_kw, msg in (("Matriz utilizada: Arenisca", "remarks state sandstone matrix 2.65 g/cm3"),
                                 ("Matriz utilizada: Carbonatos", "remarks state carbonate matrix 2.71 g/cm3")):
                if warn_kw in raw.decode("latin-1", "ignore"):
                    problems.append(msg)
        well = well_from(p.name, hdr_well)
        if hdr_well and well_from(hdr_well, "") not in (well, "UNKNOWN"):
            problems.append(f"WELL header '{hdr_well}' disagrees with file name")
        # numeric conversion, NaN nulls
        dcol = df.columns[0]
        for c in df.columns:
            if df[c].dtype == object:
                conv = pd.to_numeric(df[c], errors="coerce")
                if conv.notna().sum() >= 0.5 * df[c].notna().sum():
                    df[c] = conv
        try:
            nv = float(str(null).split()[0]) if null and "assumed" not in str(null) else -999.25
            df = df.replace(nv, np.nan)
        except ValueError:
            pass
        all_null = [c for c in df.columns[1:] if df[c].isna().all()]
        if all_null:
            problems.append("curves entirely null: " + ",".join(all_null))
        dup_of = seen_sha.get(sha, "")
        stem = re.sub(r"[^A-Za-z0-9._-]+", "_", p.stem).strip("_")
        out_name = f"curves_{well}_{stem}.csv"
        if not dup_of:
            seen_sha[sha] = p.name
            dfo = df.rename(columns={dcol: f"{dcol}_{(dunit or 'UNK').split()[0].upper()}"})
            dfo.to_csv(OUT / out_name, index=False, float_format="%.5g")
        dvals = pd.to_numeric(df[dcol], errors="coerce")
        cat.append({
            "well": well, "file": p.name, "path": rel, "drive_id": m.get("file_id", ""),
            "drive_modified": m.get("modified_time", ""), "sha256": sha, "size_bytes": len(raw),
            "header_well": hdr_well, "date": date, "company": comp, "service_company": srvc,
            "las_version": version, "wrap": wrap, "depth_unit": dunit,
            "start": dvals.min(), "stop": dvals.max(),
            "step": (las.well["STEP"].value if las is not None and hval(las.well, "STEP") is not None else ""),
            "n_samples": len(df), "null_value": null,
            "elevation_fields": "; ".join(f"{k}={v}" for k, v in elev.items()),
            "kb_m_casing_strings": kbw.get(well, ""),
            "n_curves": len(curves_desc) - 1,
            "curves": " | ".join(f"{mn}[{un}]{(': ' + de) if de else ''}" for mn, un, de in curves_desc[1:]),
            "duplicate_of": dup_of, "curves_csv": "" if dup_of else out_name,
            "header_problems": " ; ".join(dict.fromkeys(problems)),
        })
        for mn, un, de in curves_desc[1:]:
            if mn not in df.columns:
                continue
            s = df[mn]
            ok = s.notna()
            num = pd.api.types.is_numeric_dtype(s)
            idx.append({"well": well, "file": p.name, "mnemonic": mn, "unit": un, "description": de,
                        "n_valid": int(ok.sum()),
                        "top_valid": dvals[ok].min() if ok.any() else np.nan,
                        "base_valid": dvals[ok].max() if ok.any() else np.nan,
                        "min": s.min() if num and ok.any() else "", "max": s.max() if num and ok.any() else "",
                        "median": s.median() if num and ok.any() else "",
                        "duplicate_of": dup_of})
    pd.DataFrame(cat).sort_values(["well", "file"]).to_csv(OUT / "las_catalog.csv", index=False)
    pd.DataFrame(idx).to_csv(OUT / "las_curve_index.csv", index=False, float_format="%.6g")
    print(f"{len(cat)} files catalogued, {len(seen_sha)} unique contents, curve CSVs in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
