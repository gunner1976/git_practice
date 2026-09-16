"""Realised crude price at Tecolutla from the PEMEX monthly settlements (G-24).

Inputs: data/processed/drive_text/PEMEX_Delivery-Reception_settlements_2020-2022.csv (transcribed
comprobantes), data/processed/drive_text/Oil_Price_History_WTI_monthly_2018-2023.csv (WTI/Brent/LLS
monthly history from Kevin's price file), data/processed/tecolutla_field_monthly.csv (database sales).

Outputs (data/processed/price/): pemex_settlements_monthly.csv, pemex_settlements_summary.json,
figures/17_realised_price.png
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "data/processed/drive_text/PEMEX_Delivery-Reception_settlements_2020-2022.csv"
W = ROOT / "data/processed/drive_text/Oil_Price_History_WTI_monthly_2018-2023.csv"
OUT = ROOT / "data/processed/price"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(S, comment="#")
    w = pd.read_csv(W, comment="#")
    d = s.merge(w, on="month", how="left")
    d["venta_over_wti"] = d.precio_venta_usd_bbl / d.wti_usd_bbl
    d["compra_over_wti"] = d.precio_compra_usd_bbl / d.wti_usd_bbl
    d["compra_over_brent"] = d.precio_compra_usd_bbl / d.brent_usd_bbl
    d["deductions_usd_bbl"] = d.tarifa_pep + d.tarifa_pl + d.tarifa_tri + d.margen_comercial
    d["revenue_usd"] = d.precio_compra_usd_bbl * d.volume_bbl
    f = pd.read_csv(ROOT / "data/processed/tecolutla_field_monthly.csv")
    f["month"] = pd.to_datetime(f["date"]).dt.strftime("%Y-%m")
    d = d.merge(f[["month", "oil_bbl"]].rename(columns={"oil_bbl": "db_sales_bbl"}), on="month", how="left")
    d.to_csv(OUT / "pemex_settlements_monthly.csv", index=False)

    sold = d[(d.volume_bbl > 0) & d.precio_venta_usd_bbl.notna() & (d.precio_venta_usd_bbl > 0)]
    def wavg(col):
        return float((sold[col] * sold.volume_bbl).sum() / sold.volume_bbl.sum())
    summ = {
        "months_with_settlement": int(len(s)), "months_with_deliveries": int((d.volume_bbl > 0).sum()),
        "volume_bbl_2020_2022": float(d[d.month.between("2020-01", "2022-12")].volume_bbl.sum()),
        "revenue_usd_2020_2022": float(d[d.month.between("2020-01", "2022-12")].revenue_usd.sum()),
        "vol_weighted_precio_venta": wavg("precio_venta_usd_bbl"), "vol_weighted_precio_compra": wavg("precio_compra_usd_bbl"),
        "vol_weighted_wti": wavg("wti_usd_bbl"), "vol_weighted_brent": wavg("brent_usd_bbl"),
        "realised_over_wti_volume_weighted": wavg("precio_compra_usd_bbl") / wavg("wti_usd_bbl"),
        "realised_over_wti_median": float(sold.compra_over_wti.median()),
        "realised_over_wti_p10_p90": [float(sold.compra_over_wti.quantile(.1)), float(sold.compra_over_wti.quantile(.9))],
        "venta_over_wti_median": float(sold.venta_over_wti.median()),
        "constante_rendimiento_range": [float(sold.constante_rendimiento.min()), float(sold.constante_rendimiento.max())],
        "fixed_deductions_usd_bbl_range": [float(sold.deductions_usd_bbl.min()), float(sold.deductions_usd_bbl.max())],
        "ajuste_comercial_total_usd": float(d.ajuste_comercial_usd.fillna(0).sum()),
        "by_year": {},
    }
    for y in ["2020", "2021", "2022"]:
        z = sold[sold.month.str.startswith(y)]
        if len(z):
            summ["by_year"][y] = {"volume_bbl": float(z.volume_bbl.sum()), "revenue_usd": float(z.revenue_usd.sum()),
                                  "realised_usd_bbl": float(z.revenue_usd.sum() / z.volume_bbl.sum()),
                                  "wti_vol_weighted": float((z.wti_usd_bbl * z.volume_bbl).sum() / z.volume_bbl.sum()),
                                  "realised_over_wti": float(z.revenue_usd.sum() / (z.wti_usd_bbl * z.volume_bbl).sum()),
                                  "api_mean": float(z.api.mean()), "sulphur_mean": float(z.sulphur_pct.mean())}
    (OUT / "pemex_settlements_summary.json").write_text(json.dumps(summ, indent=1))
    pd.set_option("display.width", 250)
    print(d[["month", "precio_venta_usd_bbl", "precio_compra_usd_bbl", "wti_usd_bbl", "venta_over_wti", "compra_over_wti", "constante_rendimiento", "volume_bbl", "db_sales_bbl", "api"]].round(3).to_string())
    print(json.dumps(summ, indent=1))

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    x = pd.to_datetime(d.month)
    a1.plot(x, d.wti_usd_bbl, color="#888", lw=1.2, label="WTI monthly (Kevin's price file)")
    a1.plot(x, d.brent_usd_bbl, color="#bbb", lw=0.8, ls="--", label="Brent")
    m = d.precio_venta_usd_bbl > 0
    a1.plot(x[m], d.precio_venta_usd_bbl[m], "o-", color="#1f77b4", ms=4, label="PEMEX reference (precio de venta)")
    m2 = d.precio_compra_usd_bbl > 0
    a1.plot(x[m2], d.precio_compra_usd_bbl[m2], "s-", color="#d62728", ms=4, label="realised (precio de compra)")
    a1.set_ylabel("USD/bbl"); a1.legend(fontsize=8); a1.grid(alpha=0.3)
    a2.plot(x[m2], d.compra_over_wti[m2], "s-", color="#d62728", ms=4, label="realised / WTI")
    a2.plot(x[m], d.venta_over_wti[m], "o-", color="#1f77b4", ms=3, alpha=0.6, label="reference / WTI")
    for v, lab, c in [(0.95, "IFR 2020 model 0.95", "#2ca02c"), (0.801, "IFR 2022 models 0.801", "#ff7f0e"), (0.90, "IFR 2023 model 0.90", "#9467bd")]:
        a2.axhline(v, color=c, lw=0.8, ls=":", label=lab)
    a2.axhline(summ["realised_over_wti_volume_weighted"], color="k", lw=1, label=f"volume-weighted realised/WTI {summ['realised_over_wti_volume_weighted']:.2f}")
    a2.set_ylim(0.5, 1.3); a2.set_ylabel("ratio to WTI"); a2.legend(fontsize=7, ncol=2); a2.grid(alpha=0.3)
    fig.suptitle("Tecolutla realised crude price from the PEMEX monthly settlements, 2020–2022\n(comprobantes de entrega-recepción, Ezequiel Ordóñez; formula: compra = venta × C − PEP − PL − MC)")
    fig.tight_layout(); fig.savefig(ROOT / "figures/17_realised_price.png", dpi=150)


if __name__ == "__main__":
    main()
