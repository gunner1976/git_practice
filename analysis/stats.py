"""Veteran vs fresh comparison per task: mean, SD, Welch's t, Mann-Whitney U,
Hedges' g, and Fisher's exact test for binary tasks."""

from __future__ import annotations

import math

import numpy as np
from scipy import stats as st


def _desc(x: list[float]) -> dict:
    a = np.asarray(x, float)
    return {"n": len(a), "mean": float(a.mean()) if len(a) else math.nan, "sd": float(a.std(ddof=1)) if len(a) > 1 else math.nan}


def compare(vet: list[float], fresh: list[float], binary: bool = False) -> dict:
    out = {"veteran": _desc(vet), "fresh": _desc(fresh), "diff": math.nan, "welch_p": math.nan, "mwu_p": math.nan, "hedges_g": math.nan}
    if not vet or not fresh:
        return out
    out["diff"] = out["veteran"]["mean"] - out["fresh"]["mean"]
    v, f = np.asarray(vet, float), np.asarray(fresh, float)
    if len(v) > 1 and len(f) > 1:
        if v.std() + f.std() > 0:
            out["welch_p"] = float(st.ttest_ind(v, f, equal_var=False).pvalue)
            sp = math.sqrt(((len(v) - 1) * v.var(ddof=1) + (len(f) - 1) * f.var(ddof=1)) / (len(v) + len(f) - 2))
            if sp > 0:
                j = 1 - 3 / (4 * (len(v) + len(f)) - 9)
                out["hedges_g"] = float(out["diff"] / sp * j)
        elif v.mean() == f.mean():
            out["welch_p"] = 1.0
    try:
        out["mwu_p"] = float(st.mannwhitneyu(v, f, alternative="two-sided").pvalue)
    except ValueError:
        pass
    if binary:
        table = [[int(v.sum()), int(len(v) - v.sum())], [int(f.sum()), int(len(f) - f.sum())]]
        out["fisher_p"] = float(st.fisher_exact(table).pvalue)
    return out


def by_task(results: list[dict], tasks: list[str]) -> dict[str, dict]:
    out = {}
    for t in tasks:
        vet = [r["score"] for r in results if r["task"] == t and r["group"] == "veteran"]
        fresh = [r["score"] for r in results if r["task"] == t and r["group"] == "fresh"]
        out[t] = compare(vet, fresh, binary=(t == "ring_on_peak"))
    return out
