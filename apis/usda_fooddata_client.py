"""Minimal client for USDA FoodData Central search and food details."""

from __future__ import annotations

import os
from typing import Any

from .base_client import get_json

BASE_URL = "https://api.nal.usda.gov/fdc/v1"


def search_foods(query: str, api_key: str | None = None) -> dict[str, Any]:
    """Search USDA foods. Set USDA_FDC_API_KEY outside source control."""
    key = api_key or os.environ.get("USDA_FDC_API_KEY")
    if not key:
        raise ValueError("Set USDA_FDC_API_KEY before calling FoodData Central.")
    return get_json(f"{BASE_URL}/foods/search", {"api_key": key, "query": query})


def get_food(fdc_id: int, api_key: str | None = None) -> dict[str, Any]:
    """Retrieve the nutrient details for one USDA FDC record."""
    key = api_key or os.environ.get("USDA_FDC_API_KEY")
    if not key:
        raise ValueError("Set USDA_FDC_API_KEY before calling FoodData Central.")
    return get_json(f"{BASE_URL}/food/{fdc_id}", {"api_key": key})
