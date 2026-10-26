"""Turn raw transfers into economic events (swaps, deposits, withdrawals).

All transfers sharing a transaction hash are netted per token. A tx where the
wallet both gave up and received assets is a swap - a trading decision. One-
sided txs are external flows, which must be excluded from performance so that
funding a wallet is never mistaken for profit. Gas is tracked separately as a
cost that *does* count against performance.
"""

from __future__ import annotations

from collections import defaultdict

from .models import Event, EventKind, Transfer

GAS = "gas"
DUST = 1e-12

# Wrapped native tokens are treated as the native asset so that wrap/unwrap
# txs net to nothing instead of looking like trades.
WRAPPED_NATIVE = {
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": "eth",  # WETH (mainnet)
}


def normalise_token(token: str) -> str:
    token = token.lower()
    return WRAPPED_NATIVE.get(token, token)


def build_events(transfers: list[Transfer]) -> list[Event]:
    """Net transfers per tx into chronologically sorted events."""
    by_tx: dict[str, list[Transfer]] = defaultdict(list)
    for t in transfers:
        by_tx[t.tx_hash].append(t)

    events: list[Event] = []
    for tx_hash, group in by_tx.items():
        legs: dict[str, float] = defaultdict(float)
        symbols: dict[str, str] = {}
        fee = 0.0
        for t in group:
            if t.counterparty == GAS:
                fee += -abs(t.amount)
                continue
            tok = normalise_token(t.token)
            legs[tok] += t.amount
            symbols[tok] = "ETH" if tok == "eth" else t.symbol
        legs = {k: v for k, v in legs.items() if abs(v) > DUST}
        first = min(group, key=lambda t: (t.block, t.timestamp))

        if not legs and not fee:
            continue

        has_in = any(v > 0 for v in legs.values())
        has_out = any(v < 0 for v in legs.values())
        if has_in and has_out:
            kind = EventKind.SWAP
        elif has_in:
            kind = EventKind.DEPOSIT
        elif has_out:
            kind = EventKind.WITHDRAWAL
        else:
            kind = EventKind.FEE
        events.append(Event(kind, tx_hash, first.timestamp, first.block, legs, symbols, fee=-fee))

    events.sort(key=lambda e: (e.block, e.timestamp, e.tx_hash))
    return events
