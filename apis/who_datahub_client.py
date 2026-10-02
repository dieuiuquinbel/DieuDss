"""
NutriDSS - WHO Health & Nutrition Guideline Source Client
Retrieves global nutrition indicators and healthy diet guidelines from WHO endpoints / factsheets.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from .base_client import get_json

# WHO GHO OData API Base
BASE_URL = "https://ghoapi.azureedge.net/api"


def get_who_indicators() -> List[Dict[str, Any]]:
    """Fetch WHO Global Health Observatory indicators catalog."""
    try:
        data = get_json(f"{BASE_URL}/Indicator", cache_ttl_seconds=86400 * 30)
        return data.get("value", []) if isinstance(data, dict) else []
    except Exception:
        return []


def get_nutrition_guidelines_reference() -> Dict[str, Any]:
    """
    Returns the authoritative WHO Healthy Diet Guidelines (Fact Sheet N°394 & 2023 Guidelines).
    """
    return {
        "source": "World Health Organization (WHO) Healthy Diet Guidelines",
        "guidelines": {
            "free_sugars": {
                "max_percentage_calories": 10.0,
                "conditional_recommendation_percent": 5.0,
                "description": "Giảm lượng đường tự do xuống dưới 10% tổng năng lượng ăn vào (tương đương 50g đối với người lớn 2000 kcal)."
            },
            "total_fat": {
                "max_percentage_calories": 30.0,
                "description": "Chất béo không quá 30% tổng năng lượng nạp vào."
            },
            "saturated_fat": {
                "max_percentage_calories": 10.0,
                "description": "Chất béo bão hòa nên dưới 10% tổng năng lượng; thay thế bằng chất béo không bão hòa."
            },
            "trans_fat": {
                "max_percentage_calories": 1.0,
                "description": "Chất béo chuyển hóa dưới 1% tổng năng lượng, loại bỏ hoàn toàn trans fat công nghiệp."
            },
            "sodium": {
                "max_mg_day": 2000.0,
                "description": "Tiêu thụ dưới 2000 mg natri mỗi ngày (tương đương dưới 5g muối)."
            },
            "potassium": {
                "min_mg_day": 3510.0,
                "description": "Tối thiểu 3510 mg kali mỗi ngày để giảm huyết áp và nguy cơ đột quỵ."
            },
            "dietary_fiber": {
                "min_g_day": 25.0,
                "description": "Tối thiểu 25g chất xơ mỗi ngày từ rau xanh, hoa quả tươi và ngũ cốc nguyên hạt."
            }
        }
    }
