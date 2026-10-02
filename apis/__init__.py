"""Clients for approved external food-data sources."""

from .base_client import get_json, ApiClientError
from .api_cache import api_cache
from .usda_fooddata_client import search_foods, get_food
from .themealdb_client import search_meals, get_meal
from .openfoodfacts_client import search_products, get_product
from .who_datahub_client import get_nutrition_guidelines_reference, get_who_indicators

__all__ = [
    "get_json",
    "ApiClientError",
    "api_cache",
    "search_foods",
    "get_food",
    "search_meals",
    "get_meal",
    "search_products",
    "get_product",
    "get_nutrition_guidelines_reference",
    "get_who_indicators"
]
