"""Log statistics by unit (Tantoyuca marl vs El Abra) from repo LAS-derived CSVs. Writes _logstats.json."""
import pandas as pd, numpy as np, json
R = "/home/user/git_practice/data/processed/petrophysics/"
OUT = "data/processed/presentation/"
def st(s):
    s = pd.Series(s).dropna()
    s = s[(s > -999)]
    if len(s) == 0: return None
    return dict(n=int(len(s)), p10=round(float(s.quantile(.1)), 3), p50=round(float(s.median()), 3), p90=round(float(s.quantile(.9)), 3))
res = {}
# TEC-10 triple combo (MD->mSS from the survey-based mss column)
t = pd.read_csv(R + "TEC10_logs_mss.csv")
md2ss = lambda md: np.interp(md, t.DEPT.values, t.mss.values)
units10 = {"Tantoyuca marl (TEC-12 window at TEC-10) 2,294-2,311 mSS": (2294, 2311),
           "El Abra, producing interval 2,313-2,332 mSS": (2313, 2332),
           "El Abra below, 2,332-2,450 mSS": (2332, 2450)}
res["TEC-10_2018_triple_combo"] = {"file": "data/processed/petrophysics/TEC10_logs_mss.csv (TECOLUTLA-10_LAS_2280.50m-2487.00m_02MAY2018.las; mSS from survey, KB 6.13)", "units": {}}
for u, (a, b) in units10.items():
    q = t[(t.mss >= a) & (t.mss < b)]
    res["TEC-10_2018_triple_combo"]["units"][u] = dict(GR_gapi=st(q.gr), GRGM_gapi=st(q.GRGM), ILD_ohmm=st(q.res_ild[q.res_ild < 1e5]), NPHI_limestone_frac=st(q.nprl), DPHI_limestone_frac=st(q.dprl), RHOB_gcc=st(q.den), PE_b_e=st(q.pe))
# TEC-10 sonic (dipole sonic, MD) and array induction (TEC-10 Logs.LAS)
so = pd.read_csv(R + "las/curves_TEC-10_TECOLUTLA_10_SONICO_DIPOLAR_2487.00m-2280.5m_02MAY2018.csv"); so["mss"] = md2ss(so.MD_M)
ai = pd.read_csv(R + "las/curves_TEC-10_TEC-10_Logs.csv"); ai = ai[(ai.DEPT_M >= t.DEPT.min()) & (ai.DEPT_M <= t.DEPT.max())].copy(); ai["mss"] = md2ss(ai.DEPT_M)
res["TEC-10_sonic_and_array_induction"] = {"file": "data/processed/petrophysics/las/curves_TEC-10_TECOLUTLA_10_SONICO_DIPOLAR_2487.00m-2280.5m_02MAY2018.csv (DTC, DTS); las/curves_TEC-10_TEC-10_Logs.csv (R85O array induction, DTC); MD converted to mSS with the TEC10_logs_mss.csv depth pairs", "units": {}}
for u, (a, b) in units10.items():
    q = so[(so.mss >= a) & (so.mss < b)]; w = ai[(ai.mss >= a) & (ai.mss < b)]
    res["TEC-10_sonic_and_array_induction"]["units"][u] = dict(DTC_us_ft_dipole=st(q.DTC), DTS_us_ft=st(q.DTS), DTC_us_ft_TEC10Logs=st(w.DTC), R85O_ohmm=st(w.R85O))
# TEC-101 (1972), vertical, KB 8.0 -> mSS = MD - 8.0; El Abra top 2,341 mMD (-2,334 mSS logs, -2,333.7 tops table)
p = pd.read_csv(R + "las/curves_TEC-101_BLOQUE_TECOLUTLA_101_CILD_DT_GR_ILD_NEUT_SN_SP_SPHI_1699_2364.csv"); p["mss"] = p.DEPTH_M - 8.0
res["TEC-101_1972"] = {"file": "data/processed/petrophysics/las/curves_TEC-101_BLOQUE_TECOLUTLA_101_CILD_DT_GR_ILD_NEUT_SN_SP_SPHI_1699_2364.csv (KB 8.0 m, vertical; vintage digitised log, scales uncalibrated)", "units": {}}
for u, (a, b) in {"Unit above El Abra (same depths as TEC-12 window and below) 2,294-2,333 mSS": (2294, 2333), "El Abra 2,334-2,356 mSS (log ends 2,364 mMD)": (2334, 2357)}.items():
    q = p[(p.mss >= a) & (p.mss < b)]
    res["TEC-101_1972"]["units"][u] = dict(GR=st(q.GR), ILD_ohmm=st(q.ILD), SPHI_frac=st(q.SPHI), DT_us_ft=st(q.DT))
# TEC-9 (1973) El Abra top 2,296 mSS: top unit 2,296-2,304, tight 2,305-2,311, produced 2,323-2,328
n9 = pd.read_csv(R + "TEC9_logs_mss.csv")
res["TEC-9_1973"] = {"file": "data/processed/petrophysics/TEC9_logs_mss.csv (1973 induction-sonic; no marl at window depth: El Abra top -2,296 mSS)", "units": {}}
for u, (a, b) in {"El Abra top unit 2,296-2,304 mSS (TEC-12 analogue)": (2296, 2304), "El Abra tight 2,305-2,311 mSS": (2305, 2311), "El Abra produced 2,323-2,328 mSS": (2323, 2328), "Above El Abra 2,270-2,296 mSS": (2270, 2296)}.items():
    q = n9[(n9.mss >= a) & (n9.mss < b)]
    dt = q["DT:1"] if "DT:1" in q else None
    res["TEC-9_1973"]["units"][u] = dict(GR=st(q.gr), ILD_ohmm=st(q.res_ild), SPHI_frac=st(q.sphi), DT_us_ft=st(dt))
# TEC-11 lateral sonic 2,563-3,283 mMD
e = pd.read_csv(R + "TEC11_logs_mss.csv"); q = e[(e.DEPT >= 2563) & (e.DEPT <= 3283)]
res["TEC-11_lateral_LWD"] = {"file": "data/processed/petrophysics/TEC11_logs_mss.csv (LWD GR and compressional sonic; no resistivity recorded)",
                             "units": {"Lateral 2,563-3,283 mMD (2,305-2,331 mSS)": dict(GR=st(q.gr), DTC_us_ft=st(q.dtc), SPHI_wyllie_frac=st(q.sphi_wyllie))}}
json.dump(res, open(OUT + "_logstats.json", "w"), indent=1)
print(json.dumps(res, indent=1))
