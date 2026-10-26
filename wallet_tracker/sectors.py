"""Token -> sector taxonomy, and what wallets and entities are invested in.

Sectors answer "what is this capital betting on?". Exposure is time-weighted
from daily portfolio weights; flows are the USD bought minus sold per sector
per month, from swaps only, so deposits and withdrawals never count as
conviction.

Tokens are tagged from a curated map, optionally extended by CoinGecko's
public categories (cached for 30 days) and by a user JSON file
({"0xtoken": "Sector"}).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from .models import EventKind
from .providers.http import Http

STABLE = "Stablecoins"
ETH = "ETH & staking"
RWA = "RWA & tokenized treasuries"
OTHER = "Other"

SECTORS = [ETH, "Bitcoin", "DeFi", "Infrastructure", "AI", "Memes", "Gaming & NFT", RWA, STABLE, OTHER]

CURATED = {
    "eth": ETH,
    "0xae7ab96520de3a18e5e111b5eaab095312d7fe84": ETH,      # stETH
    "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0": ETH,      # wstETH
    "0xae78736cd615f374d3085123a210448e74fc6393": ETH,      # rETH
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": "Bitcoin",  # WBTC
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": STABLE,   # USDC
    "0xdac17f958d2ee523a2206206994597c13d831ec7": STABLE,   # USDT
    "0x6b175474e89094c44da98b954eedeac495271d0f": STABLE,   # DAI
    "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984": "DeFi",   # UNI
    "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9": "DeFi",   # AAVE
    "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2": "DeFi",   # MKR
    "0x5a98fcbea516cf06857215779fd812ca3bef1b32": "DeFi",   # LDO
    "0xd533a949740bb3306d119cc777fa900ba034cd52": "DeFi",   # CRV
    "0xc00e94cb662c3520282e6f5717214004a7f26888": "DeFi",   # COMP
    "0x514910771af9ca656af840dff83e8264ecf986ca": "Infrastructure",  # LINK
    "0xc944e90c64b2c07662a292be6244bdf05cda44a7": "Infrastructure",  # GRT
    "0xb50721bcf8d664c30412cfbc6cf7a15145234ad1": "Infrastructure",  # ARB
    "0xaea46a60368a7bd060eec7df8cba43b7ef41ad85": "AI",     # FET
    "0x6de037ef9ad2725eb40118bb1702ebb27e4aeb24": "AI",     # RNDR
    "0x6982508145454ce325ddbe47a25d4ec3d2311933": "Memes",  # PEPE
    "0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce": "Memes",  # SHIB
    "0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3": RWA,      # ONDO
    "0x7712c34205737192402172409a8f7ccef8aa2aec": RWA,      # BUIDL (BlackRock)
    "0x96f6ef951840721adbf46ac996b59e0235cb985c": RWA,      # USDY (Ondo)
    "0x1b19c19393e2d034d8ff31ff34c81252fcbbee92": RWA,      # OUSG (Ondo)
}

# CoinGecko category keyword -> sector, first match wins.
KEYWORDS = [
    ("tokenized treasur", RWA), ("real world asset", RWA), ("rwa", RWA),
    ("stablecoin", STABLE), ("liquid staking", ETH), ("wrapped-bitcoin", "Bitcoin"),
    ("bitcoin", "Bitcoin"), ("meme", "Memes"), ("artificial intelligence", "AI"), ("ai ", "AI"),
    ("gaming", "Gaming & NFT"), ("nft", "Gaming & NFT"), ("metaverse", "Gaming & NFT"),
    ("decentralized finance", "DeFi"), ("defi", "DeFi"), ("decentralized exchange", "DeFi"),
    ("lending", "DeFi"), ("oracle", "Infrastructure"), ("layer 2", "Infrastructure"),
    ("layer 1", "Infrastructure"), ("infrastructure", "Infrastructure"),
]


class SectorMap:
    def __init__(self, extra: dict[str, str] | None = None, online: bool = False):
        self.map = {**CURATED, **{k.lower(): v for k, v in (extra or {}).items()}}
        self.online = online
        self._http = Http(min_interval=4.0, cache_ttl=30 * 86_400) if online else None

    def sector(self, token: str) -> str:
        token = token.lower()
        if token not in self.map and self.online:
            self.map[token] = self._coingecko(token)
        return self.map.get(token, OTHER)

    def _coingecko(self, token: str) -> str:
        try:
            data = self._http.get_json(f"https://api.coingecko.com/api/v3/coins/ethereum/contract/{token}")
        except Exception:
            return OTHER
        cats = " ".join(c.lower() for c in data.get("categories") or [] if c) + " "
        for kw, sector in KEYWORDS:
            if kw in cats:
                return sector
        return OTHER


def exposure(report, smap: SectorMap) -> dict[str, dict[str, float]]:
    """Time-weighted average and latest sector weights."""
    res = report.result
    avg: dict[str, float] = defaultdict(float)
    n = 0
    for w in res.weights:
        if not w:
            continue
        n += 1
        for tok, x in w.items():
            avg[smap.sector(tok)] += x
    latest: dict[str, float] = defaultdict(float)
    for tok, x in (res.weights[-1] if res.weights else {}).items():
        latest[smap.sector(tok)] += x
    return {"average": {k: v / n for k, v in avg.items()} if n else {}, "latest": dict(latest)}


def flows(report, smap: SectorMap, book_price) -> dict[str, dict[str, float]]:
    """{month: {sector: net USD bought}} from swaps. `book_price(token, ts)` prices legs."""
    out: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for e in report.result.events:
        if e.kind is not EventKind.SWAP:
            continue
        month = datetime.fromtimestamp(e.timestamp, timezone.utc).strftime("%Y-%m")
        for tok, amt in e.legs.items():
            p = book_price(tok, e.timestamp)
            if p:
                out[month][smap.sector(tok)] += amt * p
    return {m: dict(v) for m, v in out.items()}
