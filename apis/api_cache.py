"""
NutriDSS - API Cache & Resilience Helper
Caches external JSON responses locally with TTL to prevent rate limit hits and network latency.
"""

from __future__ import annotations

import os
import time
import json
import hashlib
from typing import Any, Optional

CACHE_DIR = "data/api_cache"

class ApiCache:
    def __init__(self, cache_dir: str = CACHE_DIR, default_ttl_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl_seconds
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_key(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> str:
        serialized = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Optional[Any]:
        cache_file = os.path.join(self.cache_dir, f"{self._get_key(endpoint, params)}.json")
        if not os.path.exists(cache_file):
            return None
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() > data.get("expires_at", 0):
                os.remove(cache_file)
                return None
            return data.get("payload")
        except Exception:
            return None

    def set(self, endpoint: str, payload: Any, params: Optional[dict[str, Any]] = None, ttl_seconds: Optional[int] = None) -> None:
        cache_file = os.path.join(self.cache_dir, f"{self._get_key(endpoint, params)}.json")
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        record = {
            "endpoint": endpoint,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "payload": payload
        }
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False)
        except Exception:
            pass

api_cache = ApiCache()
