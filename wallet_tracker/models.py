"""Core data structures shared across the tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

DAY = 86_400


class EventKind(str, Enum):
    SWAP = "swap"              # wallet gave up asset(s) and received asset(s) in one tx
    DEPOSIT = "deposit"        # asset arrived with nothing leaving (external inflow)
    WITHDRAWAL = "withdrawal"  # asset left with nothing arriving (external outflow)
    FEE = "fee"                # only gas was spent (approvals, failed txs, ...)


class WalletClass(str, Enum):
    ACTIVE = "active_manager"   # discretionary, actively managed - the target set
    BUY_HOLD = "buy_hold"       # accumulates and sits
    BOT = "bot_or_mev"          # machine-speed trading, arbitrage, MEV
    EXCHANGE = "exchange_or_entity"
    CONTRACT = "contract"
    DORMANT = "dormant"         # no recent activity
    INSUFFICIENT = "insufficient_data"


@dataclass(frozen=True)
class Transfer:
    """A single asset movement touching the wallet. `amount` is signed:
    positive = into the wallet, negative = out of it."""

    tx_hash: str
    timestamp: int
    block: int
    token: str            # lowercase contract address, or "eth" for native
    symbol: str
    amount: float
    counterparty: str = ""


@dataclass
class Event:
    kind: EventKind
    tx_hash: str
    timestamp: int
    block: int
    legs: dict[str, float]          # token -> signed amount
    symbols: dict[str, str] = field(default_factory=dict)
    fee: float = 0.0                # gas paid, in ETH (positive)

    @property
    def sold(self) -> dict[str, float]:
        return {t: -a for t, a in self.legs.items() if a < 0}

    @property
    def bought(self) -> dict[str, float]:
        return {t: a for t, a in self.legs.items() if a > 0}


@dataclass
class ClosedTrade:
    """A realized round trip (or partial) produced by FIFO lot matching."""

    token: str
    symbol: str
    amount: float
    cost_usd: float
    proceeds_usd: float
    opened_at: int
    closed_at: int

    @property
    def pnl(self) -> float:
        return self.proceeds_usd - self.cost_usd

    @property
    def ret(self) -> float:
        return self.pnl / self.cost_usd if self.cost_usd > 0 else 0.0

    @property
    def holding_days(self) -> float:
        return max(self.closed_at - self.opened_at, 0) / DAY


@dataclass
class WalletHistory:
    address: str
    transfers: list[Transfer]
    is_contract: bool = False
    label: str = ""
    deployed_contracts: list[str] = field(default_factory=list)
    truncated: bool = False          # history exceeded the fetch cap (machine-scale activity)
    tx_targets: dict[str, str] = field(default_factory=dict)  # tx hash -> contract the wallet called


def history_to_json(h: WalletHistory) -> dict:
    return {"address": h.address, "is_contract": h.is_contract, "label": h.label,
            "deployed_contracts": h.deployed_contracts, "truncated": h.truncated, "tx_targets": h.tx_targets,
            "transfers": [[t.tx_hash, t.timestamp, t.block, t.token, t.symbol, t.amount, t.counterparty]
                          for t in h.transfers]}


def history_from_json(d: dict) -> WalletHistory:
    return WalletHistory(d["address"], [Transfer(*row) for row in d["transfers"]], d["is_contract"],
                         d["label"], d["deployed_contracts"], d["truncated"], d.get("tx_targets", {}))
