"""Wallet histories from the Etherscan v2 multichain API.

Needs a free API key (https://etherscan.io/apis) in ETHERSCAN_API_KEY.
"""

from __future__ import annotations

import os
from collections import Counter

from ..labels import EXCHANGES as KNOWN_ENTITIES
from ..models import Transfer, WalletHistory
from ..reconstruct import GAS
from .http import Http

BASE = "https://api.etherscan.io/v2/api"
PAGE = 10_000



class Etherscan:
    def __init__(self, api_key: str | None = None, chain_id: int = 1, labels: dict[str, str] | None = None):
        self.api_key = api_key or os.environ.get("ETHERSCAN_API_KEY", "")
        if not self.api_key:
            raise SystemExit("Set ETHERSCAN_API_KEY (free at https://etherscan.io/apis) or use --demo.")
        self.chain_id = chain_id
        self.labels = {**KNOWN_ENTITIES, **{k.lower(): v for k, v in (labels or {}).items()}}
        self.http = Http(min_interval=0.22, cache_ttl=0)  # free tier: 5 req/s

    def _call(self, **params):
        params = {"chainid": self.chain_id, "apikey": self.api_key, **params}
        data = self.http.get_json(BASE, params, cache=False)
        if str(data.get("status")) == "0":
            msg = str(data.get("message", "")) + " " + str(data.get("result", ""))
            if "No transactions found" in msg or "No records found" in msg:
                return []
            raise RuntimeError(f"Etherscan error: {msg.strip()}")
        return data["result"]

    def _paged(self, action: str, address: str, start_block: int, key) -> list[dict]:
        rows, seen, sb = [], set(), start_block
        while True:
            batch = self._call(module="account", action=action, address=address,
                               startblock=sb, endblock=99_999_999, page=1, offset=PAGE, sort="asc")
            fresh = [r for r in batch if key(r) not in seen]
            for r in fresh:
                seen.add(key(r))
            rows += fresh
            if len(batch) < PAGE or not fresh:
                return rows
            sb = int(batch[-1]["blockNumber"])  # re-read the boundary block; dedupe handles overlap

    def latest_block(self) -> int:
        return int(self._call(module="proxy", action="eth_blockNumber"), 16)

    def is_contract(self, address: str) -> bool:
        code = self._call(module="proxy", action="eth_getCode", address=address, tag="latest")
        return bool(code) and code != "0x"

    def history(self, address: str, start_block: int = 0, check_contract: bool = True) -> WalletHistory:
        a = address.lower()
        out: list[Transfer] = []
        deployed: list[str] = []

        for tx in self._paged("txlist", a, start_block, lambda r: r["hash"]):
            ts, blk, h = int(tx["timeStamp"]), int(tx["blockNumber"]), tx["hash"]
            ok = tx.get("isError", "0") == "0"
            val = int(tx["value"]) / 1e18
            if tx["from"].lower() == a and ok and tx.get("contractAddress") and not tx.get("to"):
                deployed.append(tx["contractAddress"].lower())
            if tx["from"].lower() == a:
                gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / 1e18
                out.append(Transfer(h, ts, blk, "eth", "ETH", -gas, GAS))
                if ok and val and (tx["to"] or "").lower() != a:
                    out.append(Transfer(h, ts, blk, "eth", "ETH", -val, (tx["to"] or "").lower()))
            elif ok and val and (tx["to"] or "").lower() == a:
                out.append(Transfer(h, ts, blk, "eth", "ETH", val, tx["from"].lower()))

        for tx in self._paged("txlistinternal", a, start_block,
                              lambda r: (r["hash"], r.get("traceId", ""), r["value"], r["to"])):
            if tx.get("isError", "0") != "0":
                continue
            val = int(tx["value"]) / 1e18
            if not val or tx["from"].lower() == tx["to"].lower():
                continue
            sign = 1 if tx["to"].lower() == a else -1
            cp = tx["from"] if sign > 0 else tx["to"]
            out.append(Transfer(tx["hash"], int(tx["timeStamp"]), int(tx["blockNumber"]),
                                "eth", "ETH", sign * val, cp.lower()))

        for tx in self._paged("tokentx", a, start_block, lambda r: (r["hash"], r.get("logIndex", ""))):
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
                             label=self.labels.get(a, ""), deployed_contracts=deployed)

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
