"""Task 8: TEC-12 AFE rebuild, discrepancy fix, currency and escalation to 2026 in USD and CAD.
Usage: python src/afe_rebuild.py
Outputs: data/processed/afe/{afe_lines.csv, afe_by_day.csv, afe_categories.csv, afe_escalated.csv, summary.json}, figures/08_afe.png
Escalation factors are explicit inputs at the top of this file, with their source in the docstring of docs/08_afe.md.
"""
import json, re, numpy as np, pandas as pd, openpyxl
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "data/processed/afe/"
A = "data/raw/ye2020_reserves/TEC-12 Drilling & Completion Cost Estimate.xlsx"           # 7 Apr 2021 copy, complete SUB column
B = "data/raw/tec12_drill/TEC-12 Rough Drilling & Completion Cost Estimate (2).xlsx"     # 14 Sep 2021 copy, SUB cell AB12 blank
USDCAD = 1.3915                     # 15 Sep 2026 mid-market (tradingeconomics.com, Bank of Canada series), see docs/08_afe.md
USDCAD_GLJ = 1 / 0.79               # GLJ Jan-2022 forecast CAD/USD 0.79 for 2022-2032+ (GLJ jan22.xlsx!FX rates)
# escalation, Nov 2020 (AFE pricing date) -> Sep 2026, cumulative multipliers
ESC = {"low": 1.15, "base": 1.25, "high": 1.40}   # see docs/08_afe.md section 4 for the basis of each
CATEGORY = {  # AFE row -> cost category for escalation and for the TEC-11 comparison
    "Surveys / Pre-Site": "site & civil", "Drilling Pad": "site & civil", "Cellar": "site & civil", "Location and Road": "site & civil",
    "Conductor Hammering": "site & civil", "Rig move": "rig & rig move", "Drilling Rig": "rig & rig move", "Camp": "rig & rig move", "Campers": "rig & rig move",
    "Special Tools": "downhole tools & directional", "Directional": "downhole tools & directional", "Drill bits": "downhole tools & directional", "Drill Pipe": "downhole tools & directional",
    "Mud and": "mud, fluids & disposal", "Drill Cuttings": "mud, fluids & disposal", "Fluid Hauling": "mud, fluids & disposal", "Solids Cleaning": "mud, fluids & disposal", "Trucking": "mud, fluids & disposal",
    "Conductor Casing": "tubulars & wellhead", "Surface Casing": "tubulars & wellhead", "Intermediate Casing": "tubulars & wellhead", "Production Tubing": "tubulars & wellhead", "Wellhead": "tubulars & wellhead", "Tubing packer": "tubulars & wellhead", "Power Tongs": "tubulars & wellhead", "Welding": "tubulars & wellhead",
    "Cement": "cementing", "Wireline": "logging, perforating & completion", "Perforating": "logging, perforating & completion", "Stimulation": "logging, perforating & completion", "Induction": "logging, perforating & completion",
    "Communication": "supervision, engineering & HSE", "Wellsite Geologist": "supervision, engineering & HSE", "Wellsite & RIG": "supervision, engineering & HSE", "Safety": "supervision, engineering & HSE", "Engineering": "supervision, engineering & HSE",
}
def cat(desc):
    for k, v in CATEGORY.items():
        if desc.startswith(k) or k in desc: return v
    return "other"

def read_afe(path):
    wb = openpyxl.load_workbook(path, data_only=True); ws = wb.worksheets[0]
    wf = openpyxl.load_workbook(path, data_only=False).worksheets[0]
    days = [ws.cell(6, c).value for c in range(8, 28)]; stages = [ws.cell(7, c).value for c in range(8, 28)]; dates = [ws.cell(8, c).value for c in range(8, 28)]
    lines = []
    for r in range(11, 49):
        desc = ws.cell(r, 2).value
        if not desc: continue
        vals = [ws.cell(r, c).value for c in range(8, 28)]
        vals = [float(v) if isinstance(v, (int, float)) else 0.0 for v in vals]
        lines.append(dict(row=r, code=str(ws.cell(r, 1).value or "").strip(), description=desc.strip(), vendor=str(ws.cell(r, 7).value or "").strip(),
                          sum_of_days=sum(vals), sub_cell=ws.cell(r, 28).value, sub_formula=wf.cell(r, 28).value, daily=vals))
    daily_tot = [ws.cell(50, c).value for c in range(8, 28)]; cum = [ws.cell(51, c).value for c in range(8, 28)]
    grand_sub = ws.cell(50, 28).value; grand_sub_formula = wf.cell(50, 28).value
    wb.close()
    return dict(days=days, stages=stages, dates=dates, lines=lines, daily_total=daily_tot, cumulative=cum, grand_sub=grand_sub, grand_sub_formula=grand_sub_formula)

a = read_afe(A); b = read_afe(B)
la = pd.DataFrame([{k: v for k, v in l.items() if k != "daily"} for l in a["lines"]]); lb = pd.DataFrame([{k: v for k, v in l.items() if k != "daily"} for l in b["lines"]])
la["sub_cell_B"] = lb.sub_cell.values; la["sub_formula_B"] = lb.sub_formula.values; la["sum_of_days_B"] = lb.sum_of_days.values
la["category"] = la.description.map(cat)
la["usd_2020"] = la.sum_of_days
la.to_csv(OUT + "afe_lines.csv", index=False)
# by day
bd = pd.DataFrame(dict(day=a["days"], stage=a["stages"], date=a["dates"], daily_total_usd=a["daily_total"], cumulative_usd=a["cumulative"]))
bd["stage"] = bd.stage.ffill(); bd.to_csv(OUT + "afe_by_day.csv", index=False)
total = float(la.usd_2020.sum())
disc = dict(version_A_sub_total=float(a["grand_sub"]), version_B_sub_total=float(b["grand_sub"]), cumulative_row_end=float(a["cumulative"][-1]),
            sum_of_all_daily_cells=total, lines_where_B_sub_blank=lb[lb.sub_cell.isna() & (lb.sum_of_days > 0)].description.tolist(),
            B_sub_formulas_not_starting_at_H=lb[lb.sub_formula.astype(str).str.contains(r"=SUM\([IJ]", regex=True)].description.tolist(),
            explanation="Version B (Sep 2021): the SUB formula in AB12 (Drilling Pad Maintenance, 5,000) was deleted, so the SUB column totals 1,567,724 while the daily totals and cumulative row still include the 5,000 and end at 1,572,724. Two other SUB formulas (rows 14, 15) start at column I/J instead of H but lose nothing because H is blank there. Version A (Apr 2021) is internally consistent at 1,572,724.")
# categories and escalation
cats = la.groupby("category").usd_2020.sum().sort_values(ascending=False).reset_index()
cats["share"] = cats.usd_2020 / total
cats.to_csv(OUT + "afe_categories.csv", index=False)
esc = []
for lab, f in ESC.items():
    usd = total * f
    esc.append(dict(case=lab, escalation_factor=f, usd=round(usd), cad_at_spot=round(usd * USDCAD), cad_at_glj_0p79=round(usd * USDCAD_GLJ)))
esc = pd.DataFrame(esc); esc.to_csv(OUT + "afe_escalated.csv", index=False)
# TEC-11 actual vs budget (Tec 11 Summary of Costs, sheet Actual)
wb = openpyxl.load_workbook("data/raw/development_plan/Tec 11 Summary of Costs (Actual and Budgeted).xlsx", read_only=True, data_only=True); ws = wb["Actual"]
t11 = [r for r in ws.iter_rows(min_row=7, max_row=11, min_col=2, max_col=7, values_only=True)]; wb.close()
t11 = pd.DataFrame(t11, columns=["project", "item", "date", "actual_usd", "budget_usd", "over_under"]).dropna(subset=["actual_usd"])
t11_ratio = float(t11[t11.item == "Drilling Costs"].actual_usd.iloc[0] / t11[t11.item == "Drilling Costs"].budget_usd.iloc[0])
summary = dict(afe_total_usd_2020=round(total, 2), discrepancy=disc, days=dict(pre_spud=6, drilling_and_completion=14, first_date=str(a["dates"][0])[:10], last_date=str(a["dates"][-1])[:10]),
               currency="no label in either workbook; USD by evidence (see docs)", usdcad_spot_2026_09_15=USDCAD, usdcad_glj_jan22=round(USDCAD_GLJ, 4),
               afe_2020_in_cad_at_spot=round(total * USDCAD), afe_2020_in_cad_at_glj=round(total * USDCAD_GLJ),
               escalation=esc.to_dict("records"), tec11_drilling_actual_over_budget=round(t11_ratio, 3), tec11=t11.to_dict("records"),
               categories=cats.round(3).to_dict("records"), top_lines=la.sort_values("usd_2020", ascending=False).head(12)[["description", "vendor", "usd_2020"]].round(0).to_dict("records"))
json.dump(summary, open(OUT + "summary.json", "w"), indent=1, default=str)
print(json.dumps(summary, indent=1, default=str)[:5000])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 7), gridspec_kw={"width_ratios": [1.3, 1]})
top = la.sort_values("usd_2020", ascending=True)
ax1.barh(top.description.str[:34], top.usd_2020 / 1e3, color=[plt.cm.tab10(i % 10) for i in pd.factorize(top.category)[0]])
ax1.set_xlabel("USD thousand (Nov 2020 pricing)"); ax1.set_title(f"TEC-12 AFE line items, total USD {total:,.0f} (Apr 2021 workbook; Sep 2021 copy shows 1,567,724 because one SUB cell was cleared)", fontsize=9); ax1.grid(axis="x", alpha=0.3)
bd2 = bd.copy(); bd2["x"] = range(len(bd2))
ax2.bar(bd2.x, bd2.daily_total_usd / 1e3, color="#9ecae1", label="daily spend (USD k)")
ax2b = ax2.twinx(); ax2b.plot(bd2.x, bd2.cumulative_usd / 1e6, color="k", lw=1.5, label="cumulative (USD MM)")
for lab, f, col in [("base +25 %", ESC["base"], "tab:orange"), ("high +40 %", ESC["high"], "tab:red")]:
    ax2b.axhline(total * f / 1e6, color=col, ls="--", lw=1, label=f"escalated {lab}: USD {total*f/1e6:.2f} MM = CAD {total*f*USDCAD/1e6:.2f} MM")
ax2.set_xticks(bd2.x); ax2.set_xticklabels([str(d) for d in bd2.day], fontsize=7); ax2.set_xlabel("operational day (PS = pre-spud)"); ax2.set_ylabel("USD thousand per day"); ax2b.set_ylabel("USD million")
h1, l1 = ax2.get_legend_handles_labels(); h2, l2 = ax2b.get_legend_handles_labels(); ax2.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left")
ax2.set_title("Spend by day and escalation to Sep 2026 (CAD at 1.3915)", fontsize=9)
plt.tight_layout(); plt.savefig("figures/08_afe.png", dpi=140); print("figure written")
