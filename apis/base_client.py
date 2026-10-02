"""
NutriDSS - Resilient HTTP Client with Caching & Exponential Backoff
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .api_cache import api_cache


class ApiClientError(RuntimeError):
    """Raised when a remote source cannot return valid JSON."""


def get_json(
    url: str, 
    params: Optional[dict[str, Any]] = None, 
    timeout: int = 15, 
    use_cache: bool = False,
    cache_ttl_seconds: Optional[int] = None,
    max_retries: int = 2
) -> Any:
    """Fetch JSON document with bounded timeout, retry logic, and local caching."""
    if use_cache:
        cached = api_cache.get(url, params)
        if cached is not None:
            return cached

    query = urlencode({k: str(v) for k, v in (params or {}).items()})
    request_url = f"{url}?{query}" if query else url
    headers = {
        "Accept": "application/json", 
        "User-Agent": "NutriDSS-AcademicResearch/1.0 (contact: nutridss@academic.org)"
    }
    request = Request(request_url, headers=headers)

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            with urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
                if use_cache:
                    api_cache.set(url, payload, params, ttl_seconds=cache_ttl_seconds)
                return payload
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            last_error = error
            if attempt < max_retries:
                time.sleep(1.0 * (2 ** attempt))  # Exponential backoff: 1s, 2s...

    raise ApiClientError(f"Request failed for {url} after {max_retries + 1} attempts: {last_error}") from last_error
