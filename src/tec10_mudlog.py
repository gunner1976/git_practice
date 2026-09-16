"""Parse the Weatherford TEC-10 lithology report (Litologia_Tecolutla_10.pdf) into
2-m/10-m intervals with lithology percentages, description, total gas and calcimetry.

Source: data/processed/drive_text/Litologia_Tecolutla_10.pdf.txt (Drive-connector
text rendering of Drive id 1UTXD3q5c2TSs9RFhF0OVXTpWsB5zmGOe, 7,307,773 bytes).
Depths are mMD below KB. The masterlog header prints KB 5.13 m; the package uses the
directional-survey KB 6.13 m for every TEC-10 subsea depth (decision of 16 Sep 2026, G-46),
applied in src/log_panel.py.

Output: data/processed/tec10/tec10_mudlog_intervals.csv
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data/processed/drive_text/Litologia_Tecolutla_10.pdf.txt"
OUT = ROOT / "data/processed/tec10/tec10_mudlog_intervals.csv"
SKIP = re.compile(r"ANALISIS LITOLOGICO|Compañía:|Weatherford de|^Intervalo$|^\(m\) %|^etría$|^Microsoft|^F\d+ ")
IV = re.compile(r"^(\d{3,4})\s*-\s*(\d{3,4})(?:\s+(.*))?$")
PCT = re.compile(r"^(\d{1,3}|TRZ|Trazas)(\s+(\d{1,3}|TRZ|Trazas))*$", re.I)
GAS = re.compile(r"Gas:\s*([\d.]*)\s*[Uu]nits?", re.I)
CAL = re.compile(r"100\s*%\s*-?\s*(\d{1,3})\s*$")


def main():
    lines = [l.strip() for l in SRC.read_text().splitlines()]
    lines = [l for l in lines if l and not SKIP.search(l)]
    recs, cur, last_top = [], None, -1
    for l in lines:
        m = IV.match(l)
        if m and int(m.group(1)) > last_top and int(m.group(2)) > int(m.group(1)) and int(m.group(2)) - int(m.group(1)) <= 20:
            if cur:
                recs.append(cur)
            cur = {"top_mmd": int(m.group(1)), "base_mmd": int(m.group(2)), "pct": "", "desc": [], "gas_units": None, "calcimetry_pct": None}
            last_top = int(m.group(1))
            rest = (m.group(3) or "").strip()
            if rest:
                if PCT.match(rest):
                    cur["pct"] = rest
                else:
                    pm = re.match(r"^(\d{1,3})\s+(.*)$", rest)
                    if pm:
                        cur["pct"] = pm.group(1); cur["desc"].append(pm.group(2))
                    else:
                        cur["desc"].append(rest)
            continue
        if cur is None:
            continue
        if PCT.match(l) and not cur["desc"]:
            cur["pct"] = (cur["pct"] + " " + l).strip()
            continue
        g = GAS.search(l)
        if g:
            cur["gas_units"] = float(g.group(1)) if g.group(1) else None
            c = CAL.search(l)
            if c:
                cur["calcimetry_pct"] = int(c.group(1))
            continue
        cur["desc"].append(l)
    if cur:
        recs.append(cur)
    df = pd.DataFrame(recs)
    df["desc"] = df["desc"].str.join(" ")
    df["pct"] = df["pct"].str.replace("Trazas", "TRZ", regex=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(len(df), "intervals", df["top_mmd"].min(), "-", df["base_mmd"].max())
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(df[df["top_mmd"] >= 2280][["top_mmd", "base_mmd", "pct", "gas_units", "calcimetry_pct", "desc"]].to_string())


if __name__ == "__main__":
    main()
