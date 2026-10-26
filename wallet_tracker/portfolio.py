"""Daily portfolio reconstruction.

Replays a wallet's events day by day and produces:

* a time-weighted daily return series (external deposits/withdrawals are
  neutralised, so funding a wallet is never counted as performance);
* the same series for a *passive twin* - the wallet's own initial
  allocation (frozen `freeze_days` after it first holds capital), which then
  receives the same deposits and withdrawals but never trades again.
  Comparing the two isolates what the wallet's ongoing active management
  added (or destroyed) versus simply holding its own first picks;
* FIFO-matched closed trades for trade-level statistics;
* daily portfolio weights, used to simulate how a follower copying the
  wallet with a delay would have done.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from .models import DAY, ClosedTrade, Event, EventKind
from .prices import STABLES, PriceBook, day_of

MIN_IMPLIED_USD = 10.0
MIN_CAPITAL_USD = 1_000.0  # below this a day's return is not meaningful (dust, between-trade lulls)


@dataclass
class Lot:
    amount: float
    unit_cost: float | None  # None = cost basis unknown
    opened_at: int


@dataclass
class PortfolioResult:
    days: list[int] = field(default_factory=list)
    equity: list[float] = field(default_factory=list)
    returns: list[float] = field(default_factory=list)          # aligned with days
    passive_returns: list[float] = field(default_factory=list)
    passive_equity: list[float] = field(default_factory=list)
    weights: list[dict[str, float]] = field(default_factory=list)
    token_returns: list[dict[str, float]] = field(default_factory=list)
    closed_trades: list[ClosedTrade] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    net_flows_usd: float = 0.0
    peak_capital_usd: float = 0.0     # highest cumulative net deposits: the money actually put in
    fees_usd: float = 0.0
    swap_volume_usd: float = 0.0
    swaps_total: int = 0
    swaps_priced: int = 0
    unrealized_pnl_usd: float = 0.0
    symbols: dict[str, str] = field(default_factory=dict)

    @property
    def price_coverage(self) -> float:
        return self.swaps_priced / self.swaps_total if self.swaps_total else 1.0

    @property
    def final_equity(self) -> float:
        return self.equity[-1] if self.equity else 0.0


def _value(holdings: dict[str, float], book: PriceBook, ts: int,
           bought: dict[str, float] | None = None) -> tuple[float, dict[str, float]]:
    """USD value per token. Tokens with no market price are valued at the
    wallet's own implied price, but only up to the quantity it actually
    bought - free balances (airdrops, spam) never get a made-up value."""
    vals = {}
    for tok, amt in holdings.items():
        if amt <= 0:
            continue
        p = book.market(tok, ts)
        if p is None:
            p = book.price(tok, ts)
            if p and bought is not None:
                amt = min(amt, max(bought.get(tok, 0.0), 0.0))
        if p and amt > 0:
            vals[tok] = amt * p
    return sum(vals.values()), vals


def _period_return(v_now: float, v_prev: float, flow: float) -> float:
    base = v_prev + flow  # flows assumed to arrive at the start of the day
    if base < MIN_CAPITAL_USD:
        return 0.0
    return (v_now - v_prev - flow) / base


def simulate(events: list[Event], book: PriceBook, end_ts: int, freeze_days: int = 7) -> PortfolioResult:
    res = PortfolioResult(events=events)
    if not events:
        return res

    holdings: dict[str, float] = defaultdict(float)
    passive: dict[str, float] = defaultdict(float)
    lots: dict[str, deque[Lot]] = defaultdict(deque)
    bought: dict[str, float] = defaultdict(float)   # net quantity acquired by swapping
    universe: set[str] = set()
    live_from: int | None = None
    frozen = False

    ev_i = 0
    prev_v = prev_p = 0.0
    prev_px: dict[str, float] = {}
    start = day_of(events[0].timestamp)
    end = max(day_of(end_ts), start)

    for d in range(start, end + DAY, DAY):
        flow = pflow = 0.0
        while ev_i < len(events) and day_of(events[ev_i].timestamp) == d:
            ev = events[ev_i]
            ev_i += 1
            res.symbols.update(ev.symbols)
            universe.update(ev.legs)
            if ev.fee:
                holdings["eth"] -= ev.fee
                res.fees_usd += ev.fee * (book.price("eth", ev.timestamp) or 0.0)

            if ev.kind is EventKind.SWAP:
                _apply_swap(ev, book, holdings, lots, res)
                for tok, amt in ev.legs.items():
                    bought[tok] += amt
            elif ev.kind is EventKind.DEPOSIT:
                v = 0.0
                for tok, amt in ev.legs.items():
                    p = book.price(tok, ev.timestamp)
                    v += amt * (p or 0.0)
                    holdings[tok] += amt
                    lots[tok].append(Lot(amt, p, ev.timestamp))
                flow += v
                if frozen:
                    _add_pro_rata(passive, v, ev.legs, book, ev.timestamp)
                    pflow += v
            elif ev.kind is EventKind.WITHDRAWAL:
                v = 0.0
                for tok, amt in ev.legs.items():
                    v += -amt * (book.price(tok, ev.timestamp) or 0.0)
                    holdings[tok] += amt
                    _consume(lots[tok], -amt)
                flow -= v
                if frozen:
                    # The passive twin hands over the same USD value, pro rata.
                    pv, _ = _value(passive, book, ev.timestamp)
                    if pv > 0:
                        keep = max(0.0, 1.0 - v / pv)
                        for tok in passive:
                            passive[tok] *= keep
                    pflow -= v

        close = d + DAY - 1
        v, vals = _value(holdings, book, close, bought)
        if not frozen:
            # Until the freeze the twin *is* the wallet.
            passive = defaultdict(float, {t: a for t, a in holdings.items() if a > 0})
            pflow = flow
            if live_from is None and v >= MIN_CAPITAL_USD:
                live_from = d
            frozen = live_from is not None and d >= live_from + freeze_days * DAY
        p, _ = _value(passive, book, close)
        res.days.append(d)
        res.equity.append(v)
        res.passive_equity.append(p)
        res.returns.append(_period_return(v, prev_v, flow))
        res.passive_returns.append(_period_return(p, prev_p, pflow))
        res.weights.append({t: x / v for t, x in vals.items()} if v > 0 else {})

        px = {t: book.price(t, close) for t in universe}
        res.token_returns.append({
            t: (0.0 if t in STABLES else px[t] / prev_px[t] - 1.0)
            for t in universe if px.get(t) and prev_px.get(t)
        })
        prev_px = {t: x for t, x in px.items() if x}
        res.net_flows_usd += flow
        res.peak_capital_usd = max(res.peak_capital_usd, res.net_flows_usd)
        prev_v, prev_p = v, p

    for tok, q in lots.items():
        px = book.price(tok, end_ts)
        if px is None:
            continue
        for lot in q:
            if lot.unit_cost is not None:
                res.unrealized_pnl_usd += lot.amount * (px - lot.unit_cost)
    return res


def _add_pro_rata(passive: dict[str, float], usd: float, legs: dict[str, float],
                  book: PriceBook, ts: int) -> None:
    """Invest a deposit's USD value across the twin's existing weights."""
    pv, vals = _value(passive, book, ts)
    if pv <= 0:
        for tok, amt in legs.items():
            passive[tok] += amt
        return
    for tok, x in vals.items():
        passive[tok] += usd * (x / pv) / book.price(tok, ts)


def _consume(q: deque[Lot], amount: float) -> list[tuple[Lot, float]]:
    """Remove `amount` from the front of the lot queue; return (lot, qty) taken."""
    taken = []
    while amount > 1e-12 and q:
        lot = q[0]
        qty = min(lot.amount, amount)
        taken.append((lot, qty))
        lot.amount -= qty
        amount -= qty
        if lot.amount <= 1e-12:
            q.popleft()
    return taken


def _apply_swap(ev: Event, book: PriceBook, holdings, lots, res: PortfolioResult) -> None:
    sold, bought = ev.sold, ev.bought
    sp = {t: book.price(t, ev.timestamp) for t in sold}
    bp = {t: book.price(t, ev.timestamp) for t in bought}
    sold_v = sum(a * sp[t] for t, a in sold.items() if sp[t]) if all(sp.values()) else None
    bought_v = sum(a * bp[t] for t, a in bought.items() if bp[t]) if all(bp.values()) else None

    # Price an unknown side from the known side (single-token sides only), and
    # only from trades big enough that the rate means something.
    if sold_v is not None and bought_v is None and len(bought) == 1 and sold_v >= MIN_IMPLIED_USD:
        (tok, amt), = bought.items()
        book.record_implied(tok, ev.timestamp, sold_v / amt)
        bp[tok], bought_v = sold_v / amt, sold_v
    elif bought_v is not None and sold_v is None and len(sold) == 1 and bought_v >= MIN_IMPLIED_USD:
        (tok, amt), = sold.items()
        book.record_implied(tok, ev.timestamp, bought_v / amt)
        sp[tok], sold_v = bought_v / amt, bought_v

    res.swaps_total += 1
    priced = sold_v is not None and bought_v is not None
    if priced:
        res.swaps_priced += 1
        res.swap_volume_usd += max(sold_v, bought_v)

    for tok, amt in ev.legs.items():
        holdings[tok] += amt

    # Realise sold lots at the value actually received (captures slippage).
    exec_ratio = (bought_v / sold_v) if priced and sold_v else 1.0
    for tok, amt in sold.items():
        proceeds_unit = sp[tok] * exec_ratio if sp.get(tok) else None
        for lot, qty in _consume(lots[tok], amt):
            if tok in STABLES or lot.unit_cost is None or proceeds_unit is None:
                continue
            res.closed_trades.append(ClosedTrade(
                tok, ev.symbols.get(tok, tok[:8]), qty, qty * lot.unit_cost,
                qty * proceeds_unit, lot.opened_at, ev.timestamp))

    # New lots cost what was given up for them.
    for tok, amt in bought.items():
        if priced and bought_v:
            unit = (amt * bp[tok] / bought_v) * sold_v / amt
        else:
            unit = None
        lots[tok].append(Lot(amt, unit, ev.timestamp))
