"""Who (or what) operates a wallet: human vs automated (bot / AI agent).

On-chain data cannot prove a human is behind a key, and an AI agent and a
conventional algorithm look the same to the chain. What *can* be measured is
behaviour, and people behave differently from software:

* they sleep - a contiguous block of hours with no transactions, every day;
* their activity is clustered in their waking hours (low hour-of-day entropy);
* they type round numbers ("1,000 USDC", "0.5 ETH");
* they act in bursts around news, so gaps between txs are irregular;
* they don't fire dozens of swaps per day (this overrides the rest).

These combine into a human-likeness score in [0, 1], shrunk towards 0.5 when
there are too few transactions to judge. Declared identities (an ENS name, a
verified social account, an on-chain AI-agent registry entry, or a public
label) are kept separate from this score and take precedence when grouping.
"""

from __future__ import annotations

import math
import statistics as st
from collections import Counter
from datetime import datetime, timezone

from .models import EventKind, WalletClass
from .prices import STABLES
from .reconstruct import GAS

HUMAN, AUTOMATED, UNCERTAIN, HFT = "human", "automated", "uncertain", "hft/mev bot"

# Display groups for the human-vs-automated matrix.
GROUPS = ["human (attested)", "human (behavioural)", "uncertain",
          "automated (behavioural)", "AI agent (declared)", "hft/mev bot"]


def _clip(x: float) -> float:
    return max(0.0, min(1.0, x))


def is_round(x: float, sig: int = 2) -> bool:
    if x <= 0:
        return False
    mag = 10 ** (math.floor(math.log10(x)) - sig + 1)
    return abs(x / mag - round(x / mag)) < 1e-6


def longest_quiet_run(hours: Counter, n: int) -> int:
    """Longest circular run of hours with (almost) no activity."""
    thresh = max(0, int(0.01 * n))
    quiet = [hours.get(h, 0) <= thresh for h in range(24)]
    if all(quiet):
        return 24
    best = run = 0
    for q in quiet + quiet:  # wrap around midnight
        run = run + 1 if q else 0
        best = max(best, run)
    return min(best, 23)


def features(hist, events) -> dict[str, float]:
    sent = sorted({t.timestamp for t in hist.transfers if t.counterparty == GAS})
    swaps = [e for e in events if e.kind is EventKind.SWAP]
    if len(sent) < 5:
        sent = sorted(e.timestamp for e in swaps)
    n = len(sent)
    hours = Counter(datetime.fromtimestamp(t, timezone.utc).hour for t in sent)
    probs = [c / n for c in hours.values()] if n else []
    entropy = -sum(p * math.log(p) for p in probs) / math.log(24) if probs else 1.0
    gaps = [b - a for a, b in zip(sent, sent[1:]) if b > a]
    cv = (st.pstdev(gaps) / st.fmean(gaps)) if len(gaps) > 2 and st.fmean(gaps) else 1.0
    entries = [amt for e in swaps for tok, amt in e.sold.items() if tok in STABLES or tok == "eth"]
    weekend = sum(datetime.fromtimestamp(t, timezone.utc).weekday() >= 5 for t in sent) / n if n else 0.0
    return {
        "tx_count": n,
        "hour_entropy": entropy,
        "quiet_hours": longest_quiet_run(hours, n) if n else 0,
        "interval_cv": cv,
        "round_amount_ratio": sum(is_round(a) for a in entries) / len(entries) if entries else 0.0,
        "weekend_share": weekend,
    }


def human_score(f: dict[str, float], swaps_per_active_day: float) -> tuple[float, float]:
    """(score, confidence)."""
    evidence = (0.40 * _clip((f["quiet_hours"] - 1) / 5)
                + 0.20 * _clip((0.97 - f["hour_entropy"]) / 0.12)
                + 0.25 * _clip(f["round_amount_ratio"] / 0.3)
                + 0.15 * _clip((f["interval_cv"] - 0.6) / 0.8))
    if swaps_per_active_day > 20:
        # Nobody clicks "swap" dozens of times a day; machine pace overrides
        # everything else (a bot that runs in one burst looks like it "sleeps").
        evidence *= 0.2
    conf = _clip(f["tx_count"] / 60)
    return 0.5 + (evidence - 0.5) * conf, conf


def operator_label(score: float, wallet_class: WalletClass) -> str:
    if wallet_class is WalletClass.BOT:
        return HFT
    if score >= 0.6:
        return HUMAN
    if score <= 0.4:
        return AUTOMATED
    return UNCERTAIN


def group(operator: str, identity_kind: str | None) -> str:
    if identity_kind == "ai_agent":
        return "AI agent (declared)"
    if operator == HFT:
        return "hft/mev bot"
    if identity_kind in ("person", "fund") and operator != AUTOMATED:
        return "human (attested)"
    return {HUMAN: "human (behavioural)", AUTOMATED: "automated (behavioural)"}.get(operator, "uncertain")
