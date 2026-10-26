"""Market regimes and the wallet x regime risk matrix.

Every day is labelled from ETH's own behaviour, the same labels for every
wallet:

* trend  - ETH's trailing 30-day return: bull (> +10%), bear (< -10%), range;
* vol    - ETH's trailing 30-day realised volatility vs its median: high/low;
* stress - ETH's worst 5% of days (crash days), tracked separately.

A wallet's returns are then cut by regime. The *Regime Robustness Score*
asks "does this wallet beat simply holding ETH in every kind of market, not
just the one it happened to trade in?":

    RRS = mean_r(IR_r) - 0.5 * stdev_r(IR_r)

where IR_r is the annualised information ratio of the wallet over ETH inside
regime r (regimes with fewer than MIN_DAYS observations are skipped). A
bull-market-only hero scores poorly; a wallet that adds a little in every
regime scores well.
"""

from __future__ import annotations

import math
import statistics as st

from .models import DAY

TREND_WINDOW = 30
TREND_BAND = 0.10
STRESS_QUANTILE = 0.05
MIN_DAYS = 20
REGIMES = ["bull·low-vol", "bull·high-vol", "range·low-vol", "range·high-vol",
           "bear·low-vol", "bear·high-vol"]


class MarketRegimes:
    def __init__(self, eth: dict[int, float]):
        days = sorted(eth)
        self.labels: dict[int, str] = {}
        self.stress: set[int] = set()
        rets = {d: eth[d] / eth[p] - 1 for p, d in zip(days, days[1:]) if eth[p]}
        vols: dict[int, float] = {}
        for i, d in enumerate(days):
            if i < TREND_WINDOW:
                continue
            window = [rets[x] for x in days[i - TREND_WINDOW + 1:i + 1] if x in rets]
            vols[d] = st.pstdev(window) if len(window) > 2 else 0.0
        vol_med = st.median(vols.values()) if vols else 0.0
        for i, d in enumerate(days):
            if d not in vols:
                continue
            tr = eth[d] / eth[days[i - TREND_WINDOW]] - 1
            trend = "bull" if tr > TREND_BAND else "bear" if tr < -TREND_BAND else "range"
            self.labels[d] = f"{trend}·{'high' if vols[d] > vol_med else 'low'}-vol"
        if rets:
            cut = sorted(rets.values())[max(0, int(len(rets) * STRESS_QUANTILE) - 1)]
            self.stress = {d for d, r in rets.items() if r <= cut}

    def label(self, day: int) -> str | None:
        return self.labels.get(day - day % DAY)


def _ann_ir(excess: list[float]) -> float:
    if len(excess) < 3:
        return 0.0
    sd = st.pstdev(excess)
    return st.fmean(excess) / sd * math.sqrt(365) if sd else 0.0


def regime_matrix(days: list[int], rs: list[float], bench: list[float],
                  regimes: MarketRegimes) -> dict[str, dict[str, float]]:
    cells: dict[str, list[tuple[float, float]]] = {}
    for d, r, b in zip(days, rs, bench):
        lab = regimes.label(d)
        if lab:
            cells.setdefault(lab, []).append((r, b))
        if d in regimes.stress:
            cells.setdefault("stress", []).append((r, b))
    out = {}
    for lab, pairs in cells.items():
        w = [p[0] for p in pairs]
        e = [p[0] - p[1] for p in pairs]
        out[lab] = {
            "days": len(pairs),
            "ann_return": st.fmean(w) * 365,
            "ann_excess": st.fmean(e) * 365,          # vs ETH, arithmetic
            "ir": _ann_ir(e),
            "hit_rate": sum(x > 0 for x in e) / len(e),
            "eth_ann_return": st.fmean(p[1] for p in pairs) * 365,
        }
    return out


def conditional_betas(rs: list[float], bench: list[float], stress_mask: list[bool]) -> dict[str, float]:
    def beta(pairs):
        if len(pairs) < 5:
            return 0.0
        xs, ys = [p[1] for p in pairs], [p[0] for p in pairs]
        mx, my = st.fmean(xs), st.fmean(ys)
        vx = sum((x - mx) ** 2 for x in xs)
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / vx if vx else 0.0
    pairs = list(zip(rs, bench))
    return {
        "up_beta": beta([p for p in pairs if p[1] > 0]),
        "down_beta": beta([p for p in pairs if p[1] < 0]),
        "stress_beta": beta([p for p, s in zip(pairs, stress_mask) if s]),
    }


def robustness(matrix: dict[str, dict[str, float]]) -> dict[str, float]:
    cells = {k: v for k, v in matrix.items() if k != "stress" and v["days"] >= MIN_DAYS}
    if not cells:
        return {"regime_robustness": 0.0, "worst_regime_excess": 0.0, "regimes_beaten": 0.0,
                "regimes_covered": 0, "stress_excess": 0.0}
    irs = [v["ir"] for v in cells.values()]
    rrs = st.fmean(irs) - 0.5 * (st.pstdev(irs) if len(irs) > 1 else 0.0)
    stress = matrix.get("stress", {})
    return {
        "regime_robustness": rrs,
        "worst_regime_excess": min(v["ann_excess"] for v in cells.values()),
        "regimes_beaten": sum(v["ann_excess"] > 0 for v in cells.values()) / len(cells),
        "regimes_covered": len(cells),
        "stress_excess": stress.get("ann_excess", 0.0) / 365 if stress else 0.0,  # avg per crash day
    }
