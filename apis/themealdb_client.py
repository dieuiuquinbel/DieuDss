"""Minimal client for recipe metadata from TheMealDB."""

from __future__ import annotations

from typing import Any

from .base_client import get_json

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


def search_meals(name: str) -> list[dict[str, Any]]:
    """Return meals whose names match *name* using the educational test key."""
    return get_json(f"{BASE_URL}/search.php", {"s": name}).get("meals") or []


def get_meal(meal_id: int) -> dict[str, Any] | None:
    """Return full metadata for one meal, or None when it does not exist."""
    meals = get_json(f"{BASE_URL}/lookup.php", {"i": str(meal_id)}).get("meals") or []
    return meals[0] if meals else None
