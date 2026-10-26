"""Route every position the leader holds to the best way we can hold it.

Our tradable basket rarely matches a leader's. Instead of treating anything
off-venue as cash, each token is routed, in order of fidelity:

  1. perp   - the same asset as a listed perp (Hyperliquid), funding paid;
  2. spot   - buy the token itself on a DEX, if its pool is deep enough;
              cost = pool fee + price impact, which grows with our trade
              size relative to pool liquidity;
  3. proxy  - the most correlated instrument we *can* hold (estimated only
              from prices before the day in question - no hindsight),
              sized by its beta; captures the leader's market bet even when
              the token-specific move is lost;
  4. cash   - nothing suitable.

`routed_copy` replays the leader's daily weights through the router and
reports how much of the book went each way, so the replication gate can
judge the whole routed copy rather than a yes/no on one venue.
"""

from __future__ import annotations

import statistics as st
from dataclasses import dataclass, field

from .models import DAY
from .prices import STABLES, PriceBook, day_of
from .providers.http import Http


@dataclass
class Route:
    kind: str                 # perp | spot | proxy
    instrument: str
    target: str               # token whose price drives the position (itself, or the proxy)
    beta: float = 1.0
    cost_bps: float = 10.0
    funding: float = 0.0      # per day, longs pay
    liquidity: float = 0.0    # spot pools: USD depth for price impact


class PerpRouter:
    """Adapts a perp venue (Hyperliquid / StaticVenue) to the router interface."""

    def __init__(self, venue):
        self.venue, self.name = venue, venue.name

    def route(self, token: str, symbol: str, price: float | None, day: int) -> Route | None:
        c = self.venue.coin_for(token, symbol, price)
        if c and self.venue.listed_on(c, day):
            return Route("perp", f"{c}-PERP", token, 1.0, self.venue.cost_bps, self.venue.funding_daily(c, day))
        return None


class Dexscreener:
    URL = "https://api.dexscreener.com/tokens/v1/{chain}/{addrs}"

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain
        self.http = Http(min_interval=0.25, cache_ttl=12 * 3600)
        self.liq: dict[str, float] = {}

    def prefetch(self, tokens: set[str]) -> None:
        todo = sorted(t for t in tokens if t.startswith("0x") and t not in self.liq and t not in STABLES)
        for i in range(0, len(todo), 30):
            chunk = todo[i:i + 30]
            try:
                pairs = self.http.get_json(self.URL.format(chain=self.chain, addrs=",".join(chunk)))
            except Exception:
                pairs = []
            for t in chunk:
                self.liq.setdefault(t, 0.0)
            for p in pairs or []:
                for side in ("baseToken", "quoteToken"):
                    a = (p.get(side) or {}).get("address", "").lower()
                    if a in self.liq:
                        self.liq[a] = max(self.liq[a], float((p.get("liquidity") or {}).get("usd") or 0))

    def liquidity(self, token: str) -> float:
        if token not in self.liq:
            self.prefetch({token})
        return self.liq.get(token, 0.0)


class SpotRouter:
    """Buy the token itself on a DEX when its deepest pool is deep enough."""

    def __init__(self, liquidity_source, min_liquidity: float = 250_000, fee_bps: float = 40.0):
        self.src, self.min_liq, self.fee = liquidity_source, min_liquidity, fee_bps
        self.name = "DEX spot"

    def route(self, token, symbol, price, day):
        if token == "eth" or token in STABLES:
            return None
        liq = self.src.liquidity(token)
        if liq >= self.min_liq:
            return Route("spot", f"{symbol or token[:8]} spot", token, 1.0, self.fee, 0.0, liq)
        return None


class ProxyRouter:
    """Hold the most correlated routable instrument, beta-sized, using only
    the `window` days of prices before the day being copied."""

    def __init__(self, base, book: PriceBook, candidates: dict[str, str], window: int = 90,
                 min_corr: float = 0.5, max_beta: float = 2.0):
        self.base, self.book, self.window = base, book, window
        self.candidates = candidates          # token -> symbol, all routable through `base`
        self.min_corr, self.max_beta = min_corr, max_beta
        self.name = "proxy"
        self._cache: dict[tuple[str, int], Route | None] = {}

    def _rets(self, token: str, end: int) -> dict[int, float]:
        out, prev = {}, None
        for i in range(self.window, -1, -1):
            d = end - i * DAY
            p = self.book.market(token, d)
            if p and prev:
                out[d] = p / prev - 1
            prev = p
        return out

    def route(self, token, symbol, price, day):
        key = (token, day_of(day) // (30 * DAY))       # re-estimate monthly
        if key in self._cache:
            return self._cache[key]
        best = None
        own = self._rets(token, day_of(day) - DAY)
        if len(own) >= 30:
            for cand, csym in self.candidates.items():
                if cand == token:
                    continue
                other = self._rets(cand, day_of(day) - DAY)
                common = sorted(own.keys() & other.keys())
                if len(common) < 30:
                    continue
                x = [other[d] for d in common]
                y = [own[d] for d in common]
                sx, sy = st.pstdev(x), st.pstdev(y)
                if not sx or not sy:
                    continue
                mx, my = st.fmean(x), st.fmean(y)
                cov = sum((a - mx) * (b - my) for a, b in zip(x, y)) / len(x)
                corr = cov / (sx * sy)
                if corr >= self.min_corr and (best is None or corr > best[0]):
                    best = (corr, cand, csym, max(0.0, min(self.max_beta, cov / sx ** 2)))
        route = None
        if best:
            inner = self.base.route(best[1], best[2], self.book.price(best[1], day), day)
            if inner:
                route = Route("proxy", f"{inner.instrument} x{best[3]:.2f} (corr {best[0]:.2f})", best[1],
                              best[3], inner.cost_bps, inner.funding, inner.liquidity)
        self._cache[key] = route
        return route


@dataclass
class Router:
    """Try each route in order; the first that can hold the token wins."""
    routes: list
    name: str = "routed"
    capital: float = 100_000.0     # copy portfolio size, for spot price impact
    stats: dict = field(default_factory=dict)

    def route(self, token, symbol, price, day) -> Route | None:
        for r in self.routes:
            got = r.route(token, symbol, price, day)
            if got:
                return got
        return None


def routed_copy(res, router: Router, book: PriceBook, lag_days: int) -> tuple[list[float], dict]:
    """Daily returns of copying the wallet through `router`, plus the share of
    the leader's risk book routed each way (time-averaged)."""
    def ret(token: str, day: int) -> float:
        p, q = book.price(token, day + DAY - 1), book.price(token, day - 1)
        return p / q - 1 if p and q else 0.0

    out: list[float] = []
    held: dict[str, tuple[float, Route]] = {}
    mix = {"perp": [], "spot": [], "proxy": [], "cash": []}
    instruments: set[str] = set()
    for t, day in enumerate(res.days):
        r = sum(w * (rt.beta * ret(rt.target, day) - rt.funding) for w, rt in held.values())
        src = t - lag_days
        full = res.weights[src] if src >= 0 else {}
        risk = {k: v for k, v in full.items() if k not in STABLES}
        target: dict[str, tuple[float, Route]] = {}
        for tok, w in risk.items():
            rt = router.route(tok, res.symbols.get(tok, ""), book.price(tok, day), day)
            if rt:
                target[tok] = (w, rt)
                instruments.add(rt.instrument.split(" (")[0])
        if risk:
            tot = sum(risk.values())
            for kind in ("perp", "spot", "proxy"):
                mix[kind].append(sum(w for w, rt in target.values() if rt.kind == kind) / tot)
            mix["cash"].append(1 - sum(w for w, _ in target.values()) / tot)
        cost = 0.0
        for tok in set(target) | set(held):
            w_new, rt = target.get(tok, (0.0, held.get(tok, (0, None))[1]))
            dw = abs(w_new - held.get(tok, (0.0, None))[0])
            if not dw or rt is None:
                continue
            cost += dw * rt.cost_bps / 1e4
            if rt.liquidity:  # constant-product impact ~ 2 x trade / pool depth
                cost += dw * min(0.5, 2 * dw * router.capital / rt.liquidity)
        out.append(r - cost)
        held = target
    shares = {k: (st.fmean(v) if v else (1.0 if k == "cash" else 0.0)) for k, v in mix.items()}
    return out, {"route_shares": shares, "tradable_share": shares["perp"] + shares["spot"] + shares["proxy"],
                 "direct_share": shares["perp"] + shares["spot"], "coins": sorted(instruments)}


def build_router(perp_venue, book: PriceBook, symbols: dict[str, str], liquidity_source=None,
                 proxy: bool = True, capital: float = 100_000.0, min_liquidity: float = 250_000) -> Router:
    perp = PerpRouter(perp_venue)
    routes = [perp]
    if liquidity_source is not None:
        routes.append(SpotRouter(liquidity_source, min_liquidity))
    if proxy:
        # Proxy candidates: priced tokens that the perp venue can hold.
        cands = {}
        for tok in book._series:
            if tok in STABLES:
                continue
            p = book.market(tok, max(book._days[tok]) if book._days.get(tok) else 0)
            if tok == "eth" or perp.venue.coin_for(tok, symbols.get(tok, ""), p):
                cands[tok] = symbols.get(tok, "ETH" if tok == "eth" else "")
        routes.append(ProxyRouter(perp, book, cands))
    names = " + ".join(["perps"] + (["DEX spot"] if liquidity_source is not None else []) + (["proxies"] if proxy else []))
    return Router(routes, name=f"{perp_venue.name}: {names}", capital=capital)

