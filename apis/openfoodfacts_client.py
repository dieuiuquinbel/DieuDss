"""
NutriDSS - Open Food Facts API Client
Fetches packaged foods, ingredient lists, and allergen information.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from .base_client import get_json

BASE_URL = "https://world.openfoodfacts.org/api/v2"


def search_products_by_text(query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
    """Search for packaged foods by text keywords (e.g. 'Coca Cola', 'Bánh mì')."""
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "fields": "code,product_name,product_name_vi,nutriments,ingredients_text,allergens_tags,brands,image_url",
        "page": page,
        "page_size": page_size
    }
    res = get_json(f"{BASE_URL}/search", params=params, cache_ttl_seconds=86400 * 7)
    return res.get("products", []) if isinstance(res, dict) else []


def search_products_by_category(category: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
    """Search for packaged foods by standard OpenFoodFacts category tag."""
    params = {
        "categories_tags_en": category,
        "fields": "code,product_name,product_name_vi,nutriments,ingredients_text,allergens_tags,brands,image_url",
        "page": page,
        "page_size": page_size
    }
    res = get_json(f"{BASE_URL}/search", params=params, cache_ttl_seconds=86400 * 7)
    return res.get("products", []) if isinstance(res, dict) else []


def get_product_by_barcode(barcode: str) -> Optional[Dict[str, Any]]:
    """Retrieve full product details by exact barcode."""
    url = f"{BASE_URL}/product/{barcode}"
    try:
        res = get_json(url, cache_ttl_seconds=86400 * 30)
        if isinstance(res, dict) and res.get("status") == 1:
            return res.get("product")
    except Exception:
        pass
    return None


# Backward-compatibility alias
search_products = search_products_by_text
get_product = get_product_by_barcode
