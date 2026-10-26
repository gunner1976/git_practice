"""Reputation: can this wallet's record be trusted, and has it lasted?

Six components, each scored 0-1, then weighted into a 0-100 score and a
tier (A/B/C/D). Red flags subtract points and are always listed.

  longevity     wallet age; 3+ years scores fully
  track record  luck-adjusted significance of the Sharpe ratio (DSR, else PSR)
  persistence   beat ETH across rolling 90-day windows, and both halves of the
                record have a positive Sharpe
  robustness    Regime Robustness Score - adds value in every market regime
  provenance    first funded from a KYC'd exchange (1.0), a plain address
                (0.6), or a mixer (0.0)
  identity      self-published or publicly sourced identity (ENS, Farcaster,
                curated label)

Red flags: mixer funding or interaction, deployed contracts (possible token
issuer trading its own token), membership of a large linked cluster (one
operator with many wallets can cherry-pick the best-looking one).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .identity import Identity
from .labels import EXCHANGES, MIXERS
from .models import DAY, EventKind
from .reconstruct import GAS

WEIGHTS = {"longevity": 1.0, "track_record": 1.5, "persistence": 1.5,
           "robustness": 1.0, "provenance": 1.0, "identity": 1.0}


@dataclass
class Reputation:
    score: float
    tier: str
    components: dict[str, float]
    flags: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    first_funder: str = ""


def first_funder(hist, events) -> str:
    swap_txs = {e.tx_hash for e in events if e.kind is EventKind.SWAP}
    for t in sorted(hist.transfers, key=lambda t: (t.block, t.timestamp)):
        if t.amount > 0 and t.counterparty and t.counterparty != GAS and t.tx_hash not in swap_txs:
            return t.counterparty
    return ""


def assess(hist, events, m: dict[str, float], identity: Identity | None, now: int,
           cluster_size: int = 1, extra_exchanges: dict[str, str] | None = None) -> Reputation:
    exchanges = {**EXCHANGES, **(extra_exchanges or {})}
    flags, evidence = [], []
    c: dict[str, float] = {}

    first_ts = min((t.timestamp for t in hist.transfers), default=now)
    age = (now - first_ts) / DAY
    c["longevity"] = min(1.0, age / (3 * 365))
    evidence.append(f"wallet age {age / 365:.1f}y")

    c["track_record"] = m.get("dsr", m.get("psr", 0.0))

    halves = 1.0 if m.get("min_half_sharpe", 0) > 0 else 0.0
    c["persistence"] = 0.6 * m.get("pct_windows_beat_eth", 0.0) + 0.4 * halves
    evidence.append(f"beat ETH in {m.get('pct_windows_beat_eth', 0):.0%} of rolling 90d windows; "
                    f"split-half Sharpe {m.get('sharpe_first_half', 0):.2f} / {m.get('sharpe_second_half', 0):.2f}")

    rrs = m.get("regime_robustness", 0.0)
    c["robustness"] = 1 / (1 + math.exp(-1.5 * rrs))

    funder = first_funder(hist, events)
    if funder in exchanges:
        c["provenance"] = 1.0
        evidence.append(f"first funded from {exchanges[funder]}")
    elif funder in MIXERS:
        c["provenance"] = 0.0
        flags.append(f"first funded via {MIXERS[funder]}")
    else:
        c["provenance"] = 0.6 if funder else 0.3
        evidence.append("first funded from an unlabelled address" if funder else "funding source unknown")

    touched = {t.counterparty for t in hist.transfers} & set(MIXERS)
    if touched and funder not in MIXERS:
        flags.append("interacted with " + ", ".join(sorted(MIXERS[a] for a in touched)))

    if identity and identity.attested:
        c["identity"] = min(1.0, 0.5 * len(identity.sources))
        evidence.append(f"identity: {identity.name or '(unnamed)'} via {', '.join(identity.sources)}")
    else:
        c["identity"] = 0.0

    if m.get("illiquid_share", 0.0) > 0.5:
        flags.append(f"{m['illiquid_share']:.0%} of volume in tokens with no real market")
    if hist.deployed_contracts:
        flags.append(f"deployed {len(hist.deployed_contracts)} contract(s)")
    if cluster_size >= 4:
        flags.append(f"one of {cluster_size} linked wallets")

    raw = sum(WEIGHTS[k] * v for k, v in c.items()) / sum(WEIGHTS.values())
    score = max(0.0, 100 * raw - 15 * len(flags))
    tier = "A" if score >= 75 else "B" if score >= 55 else "C" if score >= 35 else "D"
    return Reputation(score, tier, c, flags, evidence, funder)
