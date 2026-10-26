"""Self-published and public identity attestations for wallets.

Only identity a wallet's owner chose to publish, or a public attribution
with a citable source, is used:

* ENS reverse record - the owner set `name.eth` to point back at the address;
* Farcaster verified address - the owner signed a message linking it to their
  account (via the Neynar API, needs NEYNAR_API_KEY);
* an identities file - public labels you curate, each with a source, e.g. a
  fund's published address, an on-chain AI-agent registry entry, or a label
  exported from an analytics platform.

This module never infers who is behind an anonymous wallet. Behavioural
signals (operator_type.py) judge *whether* a wallet looks human-operated, not
*which* human.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from .providers.http import Http

KINDS = {"person", "fund", "entity", "ai_agent"}


@dataclass
class Identity:
    name: str = ""
    kind: str = ""                      # person | fund | entity | ai_agent | "" (unknown)
    sources: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)

    @property
    def attested(self) -> bool:
        return bool(self.sources)

    def merge(self, other: "Identity") -> None:
        self.name = self.name or other.name
        self.kind = self.kind or other.kind
        self.sources += [s for s in other.sources if s not in self.sources]
        self.urls += [u for u in other.urls if u not in self.urls]


def load_file(path: str) -> dict[str, Identity]:
    """JSON: {"0xaddr": {"name": "...", "kind": "fund", "source": "...", "url": "..."}}"""
    with open(path) as fh:
        raw = json.load(fh)
    out = {}
    for addr, rec in raw.items():
        kind = rec.get("kind", "")
        if kind and kind not in KINDS:
            raise ValueError(f"{addr}: kind must be one of {sorted(KINDS)}")
        out[addr.lower()] = Identity(rec.get("name", ""), kind, [rec.get("source", "identities file")],
                                     [rec["url"]] if rec.get("url") else [])
    return out


class EnsLookup:
    URL = "https://api.ensideas.com/ens/resolve/"

    def __init__(self):
        self.http = Http(min_interval=0.2, cache_ttl=7 * 86_400)

    def lookup(self, address: str) -> Identity | None:
        try:
            data = self.http.get_json(self.URL + address)
        except Exception:
            return None
        name = data.get("name")
        # ensideas only returns a name when forward and reverse records agree.
        return Identity(name, "", ["ENS reverse record"], [f"https://app.ens.domains/{name}"]) if name else None


class FarcasterLookup:
    URL = "https://api.neynar.com/v2/farcaster/user/bulk-by-address"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("NEYNAR_API_KEY", "")

    def lookup_many(self, addresses: list[str]) -> dict[str, Identity]:
        if not self.api_key:
            return {}
        import urllib.request
        out: dict[str, Identity] = {}
        for i in range(0, len(addresses), 300):
            chunk = ",".join(addresses[i:i + 300])
            req = urllib.request.Request(f"{self.URL}?addresses={chunk}",
                                         headers={"x-api-key": self.api_key, "accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.load(resp)
            except Exception:
                continue
            for addr, users in data.items():
                if users:
                    u = users[0]
                    out[addr.lower()] = Identity(
                        u.get("display_name") or u.get("username", ""), "person",
                        ["Farcaster verified address"], [f"https://warpcast.com/{u.get('username', '')}"])
        return out


def resolve(addresses: list[str], file_ids: dict[str, Identity] | None = None,
            ens: bool = False, farcaster: bool = False) -> dict[str, Identity]:
    out: dict[str, Identity] = {a: Identity() for a in addresses}
    for a, ident in (file_ids or {}).items():
        if a in out:
            out[a].merge(ident)
    if ens:
        e = EnsLookup()
        for a in addresses:
            rec = e.lookup(a)
            if rec:
                out[a].merge(rec)
    if farcaster:
        for a, rec in FarcasterLookup().lookup_many(addresses).items():
            if a in out:
                out[a].merge(rec)
    return out
