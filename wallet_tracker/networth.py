"""Aggregated value and leverage profile of an address (or an entity).

An address's wealth is spread across places we see differently, so the
total is built from components, each with what it covers:

  hyperliquid perps   account value (margin + unrealised PnL)          exact
  hyperliquid spot    token balances x spot marks (USDC at 1)          exact
  ethereum            ETH balance + token holdings rebuilt from history,
                      valued at current prices; lending receipts/debt
                      tokens (Aave aTokens, variableDebt) flagged       good
  arbitrum            native ETH balance (free API tier)               partial
  not visible         centralised exchanges; Base/Optimism need a paid
                      Etherscan plan; most LP/vault positions          none

Leverage is reported as *effective* leverage - total position notional over
equity - not the per-position maximum an exchange allows. Against the perps
account alone, and against the address's total visible wealth (idle spot
USDC is real collateral capacity). Liquidation distance is the notional-
weighted distance from mark to liquidation price. With fills, average and
peak leverage over recent weeks, and return per unit of leverage: the same
return earned at 1x shows far more skill than at 10x.
"""

from __future__ import annotations

import statistics as st
import time

from .models import DAY
from .providers.http import Http

URL = "https://api.hyperliquid.xyz/info"
STABLE_SPOT = {"USDC", "USDT", "USDE", "USDHL", "USDT0"}


class Hyperliquid:
    def __init__(self):
        self.http = Http(min_interval=0.25, cache_ttl=0)
        self._spot_marks: dict[str, float] | None = None
        self._mids: dict[str, float] | None = None

    def perps(self, address: str) -> dict:
        return self.http.post_json(URL, {"type": "clearinghouseState", "user": address}, cache=False)

    def spot(self, address: str) -> list[dict]:
        d = self.http.post_json(URL, {"type": "spotClearinghouseState", "user": address}, cache=False)
        return d.get("balances", [])

    def spot_marks(self) -> dict[str, float]:
        if self._spot_marks is None:
            meta, ctxs = self.http.post_json(URL, {"type": "spotMetaAndAssetCtxs"}, cache=False)
            names = {t["index"]: t["name"] for t in meta["tokens"]}
            marks = {}
            for pair, ctx in zip(meta["universe"], ctxs):
                base, quote = pair["tokens"]
                if names.get(quote) == "USDC" and ctx.get("markPx"):
                    marks.setdefault(names.get(base, ""), float(ctx["markPx"]))
            self._spot_marks = marks
        return self._spot_marks

    def mids(self) -> dict[str, float]:
        if self._mids is None:
            self._mids = {k: float(v) for k, v in self.http.post_json(URL, {"type": "allMids"}, cache=False).items()
                          if not k.startswith("@")}
        return self._mids


def leverage_profile(state: dict, mids: dict[str, float], total_wealth: float) -> dict:
    ms = state["marginSummary"]
    equity = float(ms["accountValue"])
    gross = float(ms["totalNtlPos"])
    longs = shorts = 0.0
    dist_w = dist_n = 0.0
    positions = []
    for ap in state.get("assetPositions", []):
        p = ap["position"]
        notional = float(p["positionValue"])
        side = 1 if float(p["szi"]) > 0 else -1
        if side > 0:
            longs += notional
        else:
            shorts += notional
        mark = mids.get(p["coin"])
        liq = p.get("liquidationPx")
        dist = abs(mark - float(liq)) / mark if mark and liq not in (None, "") else None
        if dist is not None:
            dist_w += dist * notional
            dist_n += notional
        positions.append({"coin": p["coin"], "side": "long" if side > 0 else "short", "notional": notional,
                          "max_leverage_setting": p["leverage"]["value"], "margin": p["leverage"]["type"],
                          "liq_distance": dist, "unrealized": float(p["unrealizedPnl"])})
    return {
        "perps_equity": equity, "gross_notional": gross, "net_notional": longs - shorts,
        "leverage_vs_perps_equity": gross / equity if equity > 0 else 0.0,
        "leverage_vs_total_wealth": gross / total_wealth if total_wealth > 0 else 0.0,
        "net_leverage_vs_total_wealth": (longs - shorts) / total_wealth if total_wealth > 0 else 0.0,
        "liq_distance_weighted": dist_w / dist_n if dist_n else None,
        "positions": sorted(positions, key=lambda x: -x["notional"]),
    }


def historical_leverage(address: str, days: int = 45) -> dict[str, float]:
    """Average and peak effective leverage over recent days, rebuilt from fills."""
    from .consensus import HyperliquidBooks, reconstruct
    from .providers.hyperliquid_accounts import HyperliquidAccounts, interp, recent_stats
    hb, hl = HyperliquidBooks(), HyperliquidAccounts()
    now = int(time.time())
    end = now - now % DAY - DAY
    grid = [end - i * DAY for i in range(days)][::-1]
    book = hb.book(address)
    fills = hb.fills(address, (grid[0] - 2 * DAY) * 1000)
    coins = {f["coin"] for f in fills} | set(book.weights)
    closes = {c: hb.closes(c, grid[0] - 3 * DAY, end + DAY) for c in coins}
    h = hl.history(address)
    av = dict(h["account_value"])
    if not av:
        return {}
    av_d = {d: interp(av, d + DAY - 1) for d in grid}
    books = reconstruct(fills, av_d, closes, grid, DAY, {c: x["size"] for c, x in book.detail.items()})
    gross = [sum(abs(x) for x in b.values()) for b in books]
    rec = recent_stats(h, days, now)
    avg = st.fmean(gross) if gross else 0.0
    return {"avg_leverage": avg, "peak_leverage": max(gross) if gross else 0.0,
            "days": days, "return": rec["recent_return"],
            "return_per_unit_leverage": rec["recent_return"] / avg if avg > 0.05 else None}


def ethereum_component(address: str, provider, price_source, cfg, now: int) -> dict:
    """Current holdings rebuilt from history and valued at today's prices."""
    from .analyze import analyze_wallet, fetch_series
    h = provider.history(address)
    series = fetch_series(price_source, [h], now)
    r = analyze_wallet(h, series, cfg, now)
    res = r.result
    w = res.weights[-1] if res.weights else {}
    holdings = {res.symbols.get(t, t[:8]): x * res.final_equity for t, x in w.items()}
    lending = {k: v for k, v in holdings.items() if k.lower().startswith(("a", "variabledebt", "stabledebt"))
               and any(s in k.lower() for s in ("eth", "usd", "dai", "btc", "debt"))}
    return {"value": res.final_equity, "holdings": dict(sorted(holdings.items(), key=lambda kv: -kv[1])[:8]),
            "lending_tokens": lending, "native_eth": None}


def networth(address: str, provider=None, price_source=None, cfg=None, with_history: bool = True) -> dict:
    a = address.lower()
    hl = Hyperliquid()
    comps: dict[str, float] = {}
    notes: dict[str, str] = {}
    state = hl.perps(a)
    comps["hyperliquid perps"] = float(state["marginSummary"]["accountValue"])
    marks, mids = hl.spot_marks(), hl.mids()
    spot_v, spot_lines = 0.0, []
    for b in hl.spot(a):
        q = float(b["total"])
        px = 1.0 if b["coin"] in STABLE_SPOT else (marks.get(b["coin"]) or mids.get(b["coin"]) or 0.0)
        if q * px >= 1:
            spot_v += q * px
            spot_lines.append(f"{b['coin']} ${q * px:,.0f}")
    comps["hyperliquid spot"] = spot_v
    notes["hyperliquid spot"] = ", ".join(spot_lines[:6])
    eth = None
    if provider is not None:
        try:
            eth = ethereum_component(a, provider, price_source, cfg, int(time.time()))
            comps["ethereum"] = eth["value"]
            notes["ethereum"] = ", ".join(f"{k} ${v:,.0f}" for k, v in list(eth["holdings"].items())[:6])
            if eth["lending_tokens"]:
                notes["ethereum"] += "  | lending/debt tokens: " + ", ".join(eth["lending_tokens"])
        except Exception as exc:  # history fetch can fail for very active addresses
            notes["ethereum"] = f"unavailable ({exc})"
        try:
            wei = provider._call(module="account", action="balance", address=a, tag="latest", chainid=42161)
            comps["arbitrum (ETH only)"] = int(wei) / 1e18 * mids.get("ETH", 0.0)
        except Exception:
            pass
    total = sum(comps.values())
    lev = leverage_profile(state, mids, total)
    hist = historical_leverage(a) if with_history and lev["gross_notional"] > 0 else {}
    return {"address": a, "components": comps, "notes": notes, "total": total, "leverage": lev,
            "history": hist, "not_visible": "centralised exchanges; Base/Optimism (paid API); most LP/vault positions"}
