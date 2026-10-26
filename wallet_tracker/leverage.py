"""Levered copy trading: sizing rules, financing and liquidation.

Leverage multiplies a copy portfolio's daily returns (positions are perps,
so financing is the funding already inside those returns, now paid on L x
the notional). It scales return *and* risk; the Sharpe ratio stays about
the same, so leverage never turns a mediocre leader into a good one.

Sizing uses only past copy returns:

  fixed       - constant L;
  vol_target  - L = target annual vol / trailing realised vol;
  kelly       - L = fraction x (trailing mean / trailing variance), the
                growth-optimal bet scaled down (full Kelly is far too
                aggressive when the edge is estimated with error).

Every rule is capped at `max_leverage`. Liquidation is modelled on daily
data with cross margin: when a day's loss takes equity below maintenance
margin (`mm` of notional) the account is closed out and loses everything
at stake. Daily closes miss intraday wicks, so `wick` adds a safety margin:
a day counts as liquidating if L x move <= -(1 - mm x L) x wick.
"""

from __future__ import annotations

import math
import statistics as st
from dataclasses import dataclass

from .metrics import compound, max_drawdown


@dataclass
class Policy:
    name: str
    kind: str = "fixed"          # fixed | vol_target | kelly
    leverage: float = 1.0        # fixed
    target_vol: float = 0.40     # vol_target, annualised
    kelly_fraction: float = 0.5  # kelly
    window: int = 60
    max_leverage: float = 3.0


DEFAULT_POLICIES = [
    Policy("1x (no leverage)"),
    Policy("2x fixed", leverage=2.0),
    Policy("3x fixed", leverage=3.0, max_leverage=3.0),
    Policy("vol target 40%", kind="vol_target", target_vol=0.40),
    Policy("half Kelly", kind="kelly", kelly_fraction=0.5),
]


def _lev(policy: Policy, past: list[float]) -> float:
    if policy.kind == "fixed":
        return min(policy.leverage, policy.max_leverage)
    hist = past[-policy.window:]
    if len(hist) < 20:
        return 1.0
    mu, sd = st.fmean(hist), st.pstdev(hist)
    if sd == 0:
        return 1.0
    if policy.kind == "vol_target":
        lev = policy.target_vol / (sd * math.sqrt(365))
    else:  # kelly on daily returns
        lev = policy.kelly_fraction * mu / sd ** 2
    return max(0.0, min(policy.max_leverage, lev))


def apply(returns: list[float], policy: Policy, mm: float = 0.02, wick: float = 0.8) -> dict:
    """Levered daily returns plus liquidation count and the leverage path."""
    out, levs, liquidations = [], [], 0
    for i, r in enumerate(returns):
        lev = _lev(policy, returns[:i])
        levs.append(lev)
        if lev > 1 and lev * r <= -(1 - mm * lev) * wick:
            liquidations += 1
            out.append(-1.0)       # closed out: everything at stake is gone
            break
        out.append(lev * r)
    rs = out
    sd = st.pstdev(rs) if len(rs) > 2 else 0.0
    total = compound(rs)
    return {"policy": policy.name, "returns": rs, "return": total,
            "cagr": (1 + total) ** (365 / len(rs)) - 1 if rs and total > -1 else -1.0,
            "sharpe": st.fmean(rs) / sd * math.sqrt(365) if sd else 0.0,
            "max_drawdown": max_drawdown(rs), "liquidated": liquidations > 0,
            "avg_leverage": st.fmean(levs) if levs else 0.0, "max_leverage_used": max(levs) if levs else 0.0}


def compare(returns: list[float], policies: list[Policy] | None = None) -> list[dict]:
    return [apply(returns, p) for p in policies or DEFAULT_POLICIES]


def stress(returns: list[float], policy: Policy, shocks=(-0.10, -0.20, -0.30)) -> dict[str, bool]:
    """Would a sudden one-day crash of this size (on top of history) liquidate?"""
    lev = _lev(policy, returns)
    return {f"{int(-s * 100)}% crash": lev > 1 and lev * s <= -(1 - 0.02 * lev) * 0.8 for s in shocks}
