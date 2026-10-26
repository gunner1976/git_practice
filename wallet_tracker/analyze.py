"""End-to-end analysis of one wallet: events -> portfolio -> metrics -> class."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .classify import classify
from .config import Config
from .metrics import compute, live_window
from .models import DAY, ClosedTrade, Event, WalletClass, WalletHistory
from .operator_type import features as operator_features
from .operator_type import human_score, operator_label
from .portfolio import PortfolioResult, simulate
from .prices import PriceBook, PriceSource
from .reconstruct import build_events, seed_opening_balances
from .regimes import MarketRegimes, conditional_betas, regime_matrix, robustness


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
    copy_returns: list[float] = field(default_factory=list, repr=False)
    benchmark: list[float] = field(default_factory=list, repr=False)
    regimes: dict[str, dict[str, float]] = field(default_factory=dict)
    operator: dict[str, float] = field(default_factory=dict)   # behavioural features + score
    operator_label: str = ""
    group: str = ""                     # human-vs-automated display group
    identity: object = None
    reputation: object = None
    cluster_id: int = 0
    sectors: dict = field(default_factory=dict)   # {"average": {...}, "latest": {...}}
    size_tier: str = ""
    frequency_tier: str = ""
    venue_returns: list[float] = field(default_factory=list, repr=False)
    venue_coins: list[str] = field(default_factory=list)
    venue_mix: dict[str, float] = field(default_factory=dict)   # where it trades, by swap volume
    primary_venue: str = ""
    history: WalletHistory | None = field(default=None, repr=False)

    @property
    def events(self) -> list[Event]:
        return self.result.events

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


LAGS = (0, 1, 2, 3, 5, 7, 14)
FREQUENCY_TIERS = [("intraday (<1d)", 0.0), ("short swing (1–7d)", 1.0), ("swing (1–4w)", 7.0),
                   ("position (1–3m)", 30.0), ("long-term (3m+)", 90.0)]


def frequency_tier(m: dict) -> str:
    """By median holding period of closed trades; wallets that rarely close
    a position are long-term by definition."""
    if m.get("closed_trades", 0) < 3:
        return FREQUENCY_TIERS[-1][0]
    hold = m.get("median_hold_days", 0.0)
    name = FREQUENCY_TIERS[0][0]
    for label, floor in FREQUENCY_TIERS:
        if hold >= floor:
            name = label
    return name


def _sharpe(rs: list[float]) -> float:
    if len(rs) < 3:
        return 0.0
    mean = sum(rs) / len(rs)
    sd = (sum((x - mean) ** 2 for x in rs) / len(rs)) ** 0.5
    return mean / sd * 365 ** 0.5 if sd else 0.0


def lag_profile(res: PortfolioResult, cost_bps: float, i0: int, own_sharpe: float) -> dict[str, float]:
    """Copy Sharpe at increasing reaction delays, and the edge half-life:
    days of delay after which a copier keeps only half of the wallet's own
    Sharpe. Fast edges are gone before a daily copier can act (half-life 0);
    slow, thesis-driven ones last weeks."""
    out = {f"copy_sharpe_lag{lag}": _sharpe(copy_trade_returns(res, lag, cost_bps)[i0:]) for lag in LAGS}
    base = own_sharpe
    if base <= 0 or out["copy_sharpe_lag0"] <= base / 2:
        out["edge_half_life_days"] = 0.0
        return out
    prev_lag, prev = 0, out["copy_sharpe_lag0"]
    for lag in LAGS[1:]:
        cur = out[f"copy_sharpe_lag{lag}"]
        if cur <= base / 2:
            frac = (prev - base / 2) / (prev - cur) if prev != cur else 1.0
            out["edge_half_life_days"] = prev_lag + frac * (lag - prev_lag)
            return out
        prev_lag, prev = lag, cur
    out["edge_half_life_days"] = float(LAGS[-1] * 2)  # still >half at the longest lag tested
    return out


def benchmark_returns(res: PortfolioResult, book: PriceBook, token: str = "eth") -> list[float]:
    out, prev = [], None
    for d in res.days:
        p = book.market(token, d + 86_399)
        out.append(p / prev - 1.0 if p and prev else 0.0)
        prev = p or prev
    return out


def tokens_in(hist: WalletHistory) -> set[str]:
    """Tokens worth pricing: anything the wallet swapped, plus ETH. Tokens that
    only ever arrived unsolicited (airdrop spam) are skipped."""
    swapped = {t for e in build_events(hist.transfers) if e.kind.value == "swap" for t in e.legs}
    return swapped | {"eth"}


def analyze_wallet(hist: WalletHistory, series: dict[str, dict[int, float]], cfg: Config,
                   now: int | None = None, regimes: MarketRegimes | None = None) -> WalletReport:
    now = now or int(time.time())
    events = seed_opening_balances(build_events(hist.transfers))
    book = PriceBook(series)
    res = simulate(events, book, now)
    copy = copy_trade_returns(res, cfg.copy_lag_days, cfg.copy_cost_bps)
    bench = benchmark_returns(res, book)
    m = compute(res, bench, copy, now=now)

    regimes = regimes or MarketRegimes(series.get("eth", {}))
    i0 = live_window(res)
    matrix = regime_matrix(res.days[i0:], res.returns[i0:], bench[i0:], regimes)
    m.update(robustness(matrix))
    m.update(conditional_betas(res.returns[i0:], bench[i0:], [d in regimes.stress for d in res.days[i0:]]))

    m.update(lag_profile(res, cfg.copy_cost_bps, i0, m["sharpe"]))
    freq = frequency_tier(m)

    cls, reasons = classify(hist, m, cfg.classifier)
    feats = operator_features(hist, events)
    score, conf = human_score(feats, m["swaps_per_active_day"])
    feats.update(human_score=score, human_confidence=conf)
    return WalletReport(hist.address, cls, reasons, m, res, copy_returns=copy, benchmark=bench,
                        regimes=matrix, operator=feats, operator_label=operator_label(score, cls),
                        history=hist, frequency_tier=freq)


def fetch_series(source: PriceSource, histories: list[WalletHistory], now: int,
                 max_tokens: int = 1500) -> dict[str, dict[int, float]]:
    """Daily prices for the tokens these wallets swapped.

    With a source that can tell which tokens it prices (DefiLlama), only those
    are fetched, each from its first use, most-traded first up to
    `max_tokens`. Everything else is valued at the price implied by the
    wallet's own swaps."""
    if hasattr(source, "known") and hasattr(source, "daily_prices_ranges"):
        first: dict[str, int] = {}
        uses: dict[str, int] = {}
        for h in histories:
            for e in build_events(h.transfers):
                if e.kind.value != "swap":
                    continue
                for t in e.legs:
                    first[t] = min(first.get(t, e.timestamp), e.timestamp)
                    uses[t] = uses.get(t, 0) + 1
        first.setdefault("eth", min(first.values(), default=now))
        uses["eth"] = 10 ** 9
        priced = source.known(set(first)) | {"eth"}
        keep = sorted(priced, key=lambda t: -uses.get(t, 0))[:max_tokens]
        return source.daily_prices_ranges({t: (first[t] - 2 * DAY, now) for t in keep})
    tokens: set[str] = set()
    start = now
    for h in histories:
        tokens |= tokens_in(h)
        if h.transfers:
            start = min(start, min(t.timestamp for t in h.transfers))
    return source.daily_prices(tokens, start, now)
