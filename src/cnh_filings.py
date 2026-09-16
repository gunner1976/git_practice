"""CNH production filings 2020-2022 and the CNH-filed TEC-12 forecast profile (G-22, G-32, G-53).

Sources (data/processed/drive_text/, connector text renderings, and one raw zip):
  Anexo_III.8.III_Consolidado_Anual_Produccion_2020.pdf.txt   Tonalli annual filing 2020
  Anexo_III.8.III_Consolidado_Anual_Produccion_2021.pdf.txt   Tonalli annual filing 2021
  Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt                  Jul-Oct 2022 monthly report (net monthly volumes)
  data/raw/cnh_reports/Nov-22/CNH_DGM_VHP.xlsx                Nov-2022 per-well VHP format (from the Drive zip)
  Tabla_Produccion_2021_and_2022_CNH_forecast.xlsx.txt        CNH Plan-de-Desarrollo forecast tables

Outputs (data/processed/cnh/): cnh_production_filings_2020_2022.csv, cnh_vs_database_monthly.csv,
  cnh_filed_tec12_profile.csv, cnh_filings_summary.json
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DT = ROOT / "data/processed/drive_text"
OUT = ROOT / "data/processed/cnh"
MONTHS = {m: i + 1 for i, m in enumerate(["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])}
ROW = re.compile(r"^(?:CNH-R01-L03A?-?A24/2016 )?(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre) ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)")


def annual(path: Path, year: int, origin: str, source: str):
    rows = []
    for line in path.read_text().splitlines():
        m = ROW.match(line.strip())
        if m:
            api = float(m.group(4))
            rows.append(dict(month=f"{year}-{MONTHS[m.group(1)]:02d}", oil_bbl=float(m.group(2)), water_bbl=float(m.group(3)),
                             api=api if api > 0 else None, gas_mmcf=float(m.group(5)), origin=origin,
                             destination="BSB Ezequiel Ordonez PEMEX (truck)", source=source))
    assert len(rows) == 12, (path, len(rows))
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = annual(DT / "Anexo_III.8.III_Consolidado_Anual_Produccion_2020.pdf.txt", 2020, "Pozos Tecolutla 2 y Tecolutla 10 (monthly column is gross oil; filing net total 16,132.29 bbl)",
                  "Anexo III.8.III Consolidado Anual de Produccion de hidrocarburos 2020.pdf (Drive 17UZUZ-68OHV5EfE3Hl9IJc0MdlhMi55C)")
    rows += annual(DT / "Anexo_III.8.III_Consolidado_Anual_Produccion_2021.pdf.txt", 2021, "Pozo Tecolutla 10",
                   "Anexo III.8.III Consolidado Anual de Produccion 2021.pdf (Drive 1YS4wmTuUVcqnpGveGFqbhQRUZ5q3mmx7)")
    t = (DT / "Tabla_Informe_Mensual_CNH_Nov2022.xlsx.txt").read_text()
    oil = re.search(r"Aceite: Aprobado [\d ]+; Reportado ([\d ]+)", t).group(1).split()
    wat = re.search(r"Agua: Aprobado [\d ]+; Reportado ([\d ]+)", t).group(1).split()
    gas = re.search(r"Gas \(mmpc\): Aprobado [\d. ]+; Reportado ([\d. ]+)", t).group(1).split()
    for i, mo in enumerate(["2022-07", "2022-08", "2022-09", "2022-10"]):
        rows.append(dict(month=mo, oil_bbl=float(oil[i]), water_bbl=float(wat[i]), api=None, gas_mmcf=float(gas[i]),
                         origin="field (reported net monthly production, Informe Mensual obligacion 4.1)", destination="CAB Poza Rica 100 %",
                         source="Tabla Informe Mensual de actividades e inversiones, Nov 2022 (Drive 1wDcqX4kqn-QhdLG81zcSpsLd_MFS0gLl)"))
    ws = openpyxl.load_workbook(ROOT / "data/raw/cnh_reports/Nov-22/CNH_DGM_VHP.xlsx", data_only=True, read_only=True)["CNH_DGM_01_PM"]
    for r in ws.iter_rows(values_only=True):
        if r and r[0] == "CNH-R01-L03-A24/2016":
            rows.append(dict(month="2022-11", oil_bbl=float(r[9]), water_bbl=float(r[14]), api=float(r[10]), gas_mmcf=float(r[15]),
                             origin=f"{r[4]}, {r[6]} producing days; gross {r[8]} bbl; {r[11]} % S; salt {r[12]} lb/Mbbl; gas flared (approved)",
                             destination="CAB Poza Rica, 916 bbl delivered to PEMEX in 4 truck days",
                             source="Anexo I. Formatos mensuales Tonalli Nov-22.zip / CNH_DGM_VHP.xlsx (Drive 1z3aNg5UAOlPMqLBlId4WeAthavWKvuLi)"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "cnh_production_filings_2020_2022.csv", index=False)
    f = pd.read_csv(ROOT / "data/processed/tecolutla_field_monthly.csv")
    f["month"] = pd.to_datetime(f["date"]).dt.strftime("%Y-%m")
    cmp = df.merge(f[["month", "oil_bbl"]].rename(columns={"oil_bbl": "db_oil_bbl"}), on="month", how="left")
    cmp["diff_pct"] = ((cmp.oil_bbl - cmp.db_oil_bbl) / cmp.db_oil_bbl * 100).round(1)
    cmp.to_csv(OUT / "cnh_vs_database_monthly.csv", index=False)

    ft = (DT / "Tabla_Produccion_2021_and_2022_CNH_forecast.xlsx.txt").read_text()
    p21 = [float(x) for x in re.search(r"Tecolutla-12DES Aceite \(bbl/d\) INCREMENTAL: ([\d. ]+)", ft).group(1).split()]
    p22 = [float(x) for x in re.search(r"Tecolutla-12DES INCREMENTAL starts in Mes 5 \(([\d. ]+)\)", ft).group(1).split()]
    filed = pd.DataFrame({"month_on_prod": range(1, 13),
                          "tec12des_oil_bpd_filed_2021": [np.nan if v == 0 else v for v in p21],
                          "tec12des_oil_bpd_filed_2022": [np.nan] * 4 + p22})
    filed.to_csv(OUT / "cnh_filed_tec12_profile.csv", index=False)
    y20, y21 = df[df.month.str.startswith("2020")], df[df.month.str.startswith("2021")]
    summ = {"2020": {"gross_oil_monthly_sum_bbl": round(y20.oil_bbl.sum(), 2), "net_oil_filing_total_bbl": 16132.29, "gross_liquid_filing_total_bbl": 63864.56,
                     "water_bbl": round(y20.water_bbl.sum(), 2), "gas_mmcf": round(y20.gas_mmcf.sum(), 3), "api_avg": round(y20.api.mean(), 2)},
            "2021": {"oil_bbl": round(y21.oil_bbl.sum(), 2), "gross_liquid_filing_total_bbl": 91229.323, "water_bbl": round(y21.water_bbl.sum(), 3),
                     "gas_mmcf": round(y21.gas_mmcf.sum(), 3), "gor_scf_bbl": round(y21.gas_mmcf.sum() * 1e6 / y21.oil_bbl.sum()), "api_avg": round(y21.api.mean(), 2)},
            "2022_jul_oct_net_oil_bbl": float(df[df.month.between("2022-07", "2022-10")].oil_bbl.sum()),
            "2022_11_tec10_net_oil_bbl": float(df[df.month == "2022-11"].oil_bbl.iloc[0]),
            "filed_tec12_first_month_bpd": p21[2], "filed_profile_equals": "IFR Aug-2020 TEC-12 curve month-average (qi 342 bbl/d, b 1.7, Di 3.507/yr); see forecast/tec12_profiles_monthly.csv ifr_2020_bpd"}
    (OUT / "cnh_filings_summary.json").write_text(json.dumps(summ, indent=1))
    pd.set_option("display.width", 200)
    print(cmp[["month", "oil_bbl", "db_oil_bbl", "diff_pct", "water_bbl", "gas_mmcf", "api"]].to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
