"""Tiny stdlib HTTP helper with retries, rate limiting and an on-disk cache."""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

CACHE_DIR = os.environ.get("WALLET_TRACKER_CACHE", os.path.expanduser("~/.cache/wallet_tracker"))


class Http:
    def __init__(self, min_interval: float = 0.0, cache_ttl: float = 0.0):
        self.min_interval = min_interval
        self.cache_ttl = cache_ttl
        self._last = 0.0

    def get_json(self, url: str, params: dict | None = None, cache: bool = True):
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        path = None
        if cache and self.cache_ttl > 0:
            safe = url.split("apikey=")[0]  # never key the cache on secrets
            path = os.path.join(CACHE_DIR, hashlib.sha256(safe.encode()).hexdigest() + ".json")
            if os.path.exists(path) and time.time() - os.path.getmtime(path) < self.cache_ttl:
                with open(path) as fh:
                    return json.load(fh)

        delay = 2.0
        for attempt in range(5):
            wait = self.min_interval - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "wallet-tracker/0.1"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.load(resp)
                break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
                if attempt == 4:
                    raise
                time.sleep(delay)
                delay *= 2

        if path:
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(path, "w") as fh:
                json.dump(data, fh)
        return data
