"""Small JSON HTTP helper shared by source clients."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiClientError(RuntimeError):
    """Raised when a remote source cannot return valid JSON."""


def get_json(url: str, params: dict[str, str] | None = None, timeout: int = 15) -> dict[str, Any]:
    """Fetch one JSON document with a bounded timeout."""
    query = urlencode(params or {})
    request_url = f"{url}?{query}" if query else url
    request = Request(request_url, headers={"Accept": "application/json", "User-Agent": "NutriDSS/0.1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ApiClientError(f"Request failed for {url}: {error}") from error
