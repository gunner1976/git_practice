"""End-to-end analysis of one wallet: events -> portfolio -> metrics -> class."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .classify import classify
from .config import Config
from .metrics import compute
from .models import ClosedTrade, WalletClass, WalletHistory
from .portfolio import PortfolioResult, simulate
from .prices import PriceBook, PriceSource
from .reconstruct import build_events, normalise_token


@dataclass
class WalletReport:
    address: str
    wallet_class: WalletClass
    reasons: list[str]
    metrics: dict[str, float]
    result: PortfolioResult = field(repr=False)
    eligible: bool = False
    exclusions: list[str] = field(default_factory=list)
    score: float = 0.0
    rank: int = 0

    @property
    def closed_trades(self) -> list[ClosedTrade]:
        return self.result.closed_trades


def copy_trade_returns(res: PortfolioResult, lag_days: int, cost_bps: float) -> list[float]:
    """Daily returns of a follower who mirrors the wallet's portfolio weights
    `lag_days` after the wallet's close, paying `cost_bps` on every unit
    traded. A large gap between this and the wallet's own returns means the
    edge is in speed/execution and can't be copied."""
    out: list[float] = []
    held: dict[str, float] = {}
    for t, tok_ret in enumerate(res.token_returns):
        r = sum(w * tok_ret.get(tok, 0.0) for tok, w in held.items())
        src = t - lag_days
        target = res.weights[src] if src >= 0 else {}
        traded = sum(abs(target.get(k, 0.0) - held.get(k, 0.0)) for k in set(target) | set(held))
        # Cash in/out of the market (empty <-> invested) is a one-sided trade.
        cost = (traded / 2 if held and target else traded) * cost_bps / 1e4
        out.append(r - cost)
        held = target
    return out


def benchmark_returns(res: PortfolioResult, book: PriceBook, token: str = "eth") -> list[float]:
    out, prev = [], None
    for d in res.days:
        p = book.market(token, d + 86_399)
        out.append(p / prev - 1.0 if p and prev else 0.0)
        prev = p or prev
    return out


def tokens_in(hist: WalletHistory) -> set[str]:
    return {normalise_token(t.token) for t in hist.transfers} | {"eth"}


def analyze_wallet(hist: WalletHistory, series: dict[str, dict[int, float]], cfg: Config,
                   now: int | None = None) -> WalletReport:
    now = now or int(time.time())
    events = build_events(hist.transfers)
    book = PriceBook(series)
    res = simulate(events, book, now)
    copy = copy_trade_returns(res, cfg.copy_lag_days, cfg.copy_cost_bps)
    m = compute(res, benchmark_returns(res, book), copy, now=now)
    cls, reasons = classify(hist, m, cfg.classifier)
    return WalletReport(hist.address, cls, reasons, m, res)


def fetch_series(source: PriceSource, histories: list[WalletHistory], now: int) -> dict[str, dict[int, float]]:
    tokens: set[str] = set()
    start = now
    for h in histories:
        tokens |= tokens_in(h)
        if h.transfers:
            start = min(start, min(t.timestamp for t in h.transfers))
    return source.daily_prices(tokens, start, now)
