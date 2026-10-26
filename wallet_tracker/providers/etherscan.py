"""Wallet histories from the Etherscan v2 multichain API.

Needs a free API key (https://etherscan.io/apis) in ETHERSCAN_API_KEY.
"""

from __future__ import annotations

import os
import time
from collections import Counter, defaultdict

from ..labels import EXCHANGES as KNOWN_ENTITIES
from ..models import Transfer, WalletHistory
from ..reconstruct import GAS
from .http import Http

BASE = "https://api.etherscan.io/v2/api"
PAGE = 1_000          # current per-call record cap
BLOCKS_PER_DAY = 7_200

# Aggregator / router entry points; the senders of swaps through them are
# people and bots actually trading.
ROUTERS = {
    "0x66a9893cc07d91d95644aedd05d03f95e1dba8af": "Uniswap Universal Router (v4)",
    "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad": "Uniswap Universal Router",
    "0x111111125421ca6dc452d289314280a0f8842a65": "1inch Router v6",
    "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "0x Exchange Proxy",
}
SWAP_FUNCS = ("execute", "swap", "sell", "fill", "unoswap", "uniswap", "clipper", "transform")


class Etherscan:
    def __init__(self, api_key: str | None = None, chain_id: int = 1, labels: dict[str, str] | None = None,
                 max_pages: int = 15):
        self.api_key = api_key or os.environ.get("ETHERSCAN_API_KEY", "")
        if not self.api_key:
            raise SystemExit("Set ETHERSCAN_API_KEY (free at https://etherscan.io/apis) or use --demo.")
        self.chain_id = chain_id
        self.labels = {**KNOWN_ENTITIES, **{k.lower(): v for k, v in (labels or {}).items()}}
        self.max_pages = max_pages  # per tx type; a wallet beyond this is machine-scale
        self.http = Http(min_interval=0.22, cache_ttl=0)  # free tier: 5 req/s
        self.calls = 0

    def _call(self, **params):
        params = {"chainid": self.chain_id, "apikey": self.api_key, **params}
        for attempt in range(6):
            self.calls += 1
            data = self.http.get_json(BASE, params, cache=False)
            if str(data.get("status")) != "0":
                return data["result"]
            msg = str(data.get("message", "")) + " " + str(data.get("result", ""))
            if "No transactions found" in msg or "No records found" in msg:
                return []
            if "rate limit" in msg.lower() and attempt < 5:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"Etherscan error: {msg.strip()}")

    def _paged(self, action: str, address: str, start_block: int, key) -> tuple[list[dict], bool]:
        """All rows from `start_block`, oldest first; (rows, truncated)."""
        rows, seen, sb = [], set(), start_block
        for _ in range(self.max_pages):
            batch = self._call(module="account", action=action, address=address,
                               startblock=sb, endblock=99_999_999, page=1, offset=PAGE, sort="asc")
            fresh = [r for r in batch if key(r) not in seen]
            for r in fresh:
                seen.add(key(r))
            rows += fresh
            if len(batch) < PAGE or not fresh:
                return rows, False
            sb = int(batch[-1]["blockNumber"])  # re-read the boundary block; dedupe handles overlap
        return rows, True

    def latest_block(self) -> int:
        return int(self._call(module="proxy", action="eth_blockNumber"), 16)

    def is_contract(self, address: str) -> bool:
        code = self._call(module="proxy", action="eth_getCode", address=address, tag="latest")
        return bool(code) and code != "0x"

    def history(self, address: str, start_block: int = 0, check_contract: bool = True) -> WalletHistory:
        a = address.lower()
        out: list[Transfer] = []
        deployed: list[str] = []
        targets: dict[str, str] = {}
        normal, t1 = self._paged("txlist", a, start_block, lambda r: r["hash"])
        internal, t2 = self._paged("txlistinternal", a, start_block,
                                   lambda r: (r["hash"], r.get("traceId", ""), r["value"], r["to"]))
        tokens, t3 = self._paged("tokentx", a, start_block, lambda r: (r["hash"], r.get("logIndex", "")))

        for tx in normal:
            ts, blk, h = int(tx["timeStamp"]), int(tx["blockNumber"]), tx["hash"]
            ok = tx.get("isError", "0") == "0"
            val = int(tx["value"]) / 1e18
            if tx["from"].lower() == a and ok and tx.get("contractAddress") and not tx.get("to"):
                deployed.append(tx["contractAddress"].lower())
            if tx["from"].lower() == a:
                if tx.get("to"):
                    targets[h] = tx["to"].lower()
                gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / 1e18
                out.append(Transfer(h, ts, blk, "eth", "ETH", -gas, GAS))
                if ok and val and (tx["to"] or "").lower() != a:
                    out.append(Transfer(h, ts, blk, "eth", "ETH", -val, (tx["to"] or "").lower()))
            elif ok and val and (tx["to"] or "").lower() == a:
                out.append(Transfer(h, ts, blk, "eth", "ETH", val, tx["from"].lower()))

        for tx in internal:
            if tx.get("isError", "0") != "0":
                continue
            val = int(tx["value"]) / 1e18
            if not val or tx["from"].lower() == tx["to"].lower():
                continue
            sign = 1 if tx["to"].lower() == a else -1
            cp = tx["from"] if sign > 0 else tx["to"]
            out.append(Transfer(tx["hash"], int(tx["timeStamp"]), int(tx["blockNumber"]),
                                "eth", "ETH", sign * val, cp.lower()))

        for tx in tokens:
            frm, to = tx["from"].lower(), tx["to"].lower()
            if frm == to:
                continue
            dec = int(tx.get("tokenDecimal") or 18)
            amt = int(tx["value"]) / 10 ** dec
            sign = 1 if to == a else -1
            out.append(Transfer(tx["hash"], int(tx["timeStamp"]), int(tx["blockNumber"]),
                                tx["contractAddress"].lower(), tx.get("tokenSymbol", "?"),
                                sign * amt, frm if sign > 0 else to))

        return WalletHistory(a, out, is_contract=check_contract and self.is_contract(a),
                             label=self.labels.get(a, ""), deployed_contracts=deployed,
                             truncated=t1 or t2 or t3, tx_targets=targets)

    def tx_targets(self, address: str, start_block: int = 0) -> dict[str, str]:
        """Contracts the wallet called, by tx hash (normal txs only: cheap to backfill)."""
        a = address.lower()
        rows, _ = self._paged("txlist", a, start_block, lambda r: r["hash"])
        return {r["hash"]: r["to"].lower() for r in rows if r["from"].lower() == a and r.get("to")}

    def peek(self, address: str, n: int = 100) -> dict:
        """A cheap look at an address: is it a contract, where has it sent
        value recently, and which contracts has it called."""
        a = address.lower()
        txs = self._call(module="account", action="txlist", address=a, page=1, offset=n, sort="desc")
        toks = self._call(module="account", action="tokentx", address=a, page=1, offset=n, sort="desc")
        sent_to = {r["to"].lower() for r in txs + toks if r["from"].lower() == a and r.get("to")}
        senders = {r["from"].lower() for r in txs + toks if (r.get("to") or "").lower() == a}
        return {"is_contract": self.is_contract(a), "sent_to": sent_to, "senders": senders,
                "called": {r["to"].lower() for r in txs if r["from"].lower() == a and r.get("to")}}

    def discover_swappers(self, days: int = 90, windows: int = 12, min_windows: int = 2,
                          routers: dict[str, str] | None = None, top: int = 300,
                          max_per_sample: int = 6) -> list[str]:
        """Recent DEX traders who keep coming back.

        Samples the latest PAGE swaps through each router at `windows` points
        spread over the last `days`, and keeps senders seen in at least
        `min_windows` separate samples - persistent traders, not one-offs.
        Anyone with more than `max_per_sample` swaps inside one sample (about
        two hours of router traffic) is trading at machine pace and skipped.
        """
        head = self.latest_block()
        seen: dict[str, set[int]] = defaultdict(set)
        count: Counter[str] = Counter()
        burst: Counter[tuple[str, int]] = Counter()
        for router in routers or ROUTERS:
            for w in range(windows):
                end = head - int(w * days / windows * BLOCKS_PER_DAY)
                rows = self._call(module="account", action="txlist", address=router, startblock=0,
                                  endblock=end, page=1, offset=PAGE, sort="desc")
                for r in rows:
                    fn = (r.get("functionName") or "").lower()
                    if r.get("isError", "0") != "0" or not any(k in fn for k in SWAP_FUNCS):
                        continue
                    a = r["from"].lower()
                    seen[a].add(w)
                    count[a] += 1
                    burst[(a, w)] += 1
        ignore = set(self.labels) | {a for (a, _), n in burst.items() if n > max_per_sample}
        ranked = sorted((a for a in seen if len(seen[a]) >= min_windows and a not in ignore),
                        key=lambda a: (len(seen[a]), count[a]), reverse=True)
        return ranked[:top]

    def discover(self, token_contracts: list[str], per_token: int = 1000, top: int = 200) -> list[str]:
        """Seed candidates: addresses most frequently moving the given tokens
        recently. Classification later drops pools, routers, bots and CEXs."""
        counts: Counter[str] = Counter()
        for c in token_contracts:
            rows = self._call(module="account", action="tokentx", contractaddress=c,
                              page=1, offset=per_token, sort="desc")
            for r in rows:
                counts[r["from"].lower()] += 1
                counts[r["to"].lower()] += 1
        ignore = set(self.labels) | {"0x0000000000000000000000000000000000000000"}
        return [a for a, _ in counts.most_common() if a not in ignore][:top]
