# -*- coding: utf-8 -*-
"""
NutriDSS - Ingredient Cost Engine (backend/services/ingredient_cost_engine.py)
Single Responsibility:
Recipe -> Ingredients (with real units) -> Converted standard quantities -> Multi-store prices -> Median Cost Breakdown.
Zero ML pricing. 100% Deterministic & Transparent.
"""

import sqlite3
import os
from typing import Dict, List, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database", "nutridss.db")

class IngredientCostEngine:
    """
    Cost engine calculating recipe and ingredient costs strictly from raw ingredients and market prices.
    Converts diverse kitchen units (g, kg, ml, l, quả, thìa cà phê, thìa canh, tép) to standard grams/ml.
    Computes Median reference price and observation range [min, max] across supermarkets (WinMart, GO!, AEON).
    """

    # Unit conversion rates to standard grams (or ml for liquids where 1ml ~ 1g)
    DEFAULT_UNIT_CONVERSIONS = {
        "g": 1.0,
        "gam": 1.0,
        "gram": 1.0,
        "kg": 1000.0,
        "kilogram": 1000.0,
        "ml": 1.0,
        "l": 1000.0,
        "lit": 1000.0,
        "lít": 1000.0,
        "qua": 55.0,        # 1 quả trứng ~ 55g
        "quả": 55.0,
        "trái": 55.0,
        "thia": 5.0,        # 1 thìa cà phê ~ 5g
        "thìa": 5.0,
        "muong": 5.0,
        "muỗng": 5.0,
        "tsp": 5.0,
        "thia_ca_phe": 5.0,
        "thìa cà phê": 5.0,
        "thia_canh": 15.0,  # 1 thìa canh / muỗng canh ~ 15g
        "thìa canh": 15.0,
        "muong_canh": 15.0,
        "muỗng canh": 15.0,
        "tbsp": 15.0,
        "tep": 5.0,         # 1 tép tỏi ~ 5g
        "tép": 5.0,
        "bat": 160.0,       # 1 bát cơm ~ 160g
        "bát": 160.0,
        "chen": 160.0,
        "chén": 160.0
    }

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def convert_to_grams(self, quantity: float, unit: str, food_id: Optional[int] = None) -> float:
        """
        Normalizes any input quantity and unit to standard grams.
        Checks custom food-specific conversion first, then default kitchen unit table.
        """
        if quantity is None:
            return 0.0
        unit_clean = (unit or "g").strip().lower()
        if unit_clean in ["g", "gam", "gram", "ml"]:
            return float(quantity)

        # Check DB unit_conversions table if available
        if food_id:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT conversion_value FROM unit_conversions
                    WHERE (food_id = ? OR food_id IS NULL) AND LOWER(from_unit) = ? AND LOWER(to_unit) = 'g'
                    LIMIT 1
                """, (food_id, unit_clean))
                row = cursor.fetchone()
                conn.close()
                if row and row[0]:
                    return float(quantity) * float(row[0])
            except Exception:
                pass

        factor = self.DEFAULT_UNIT_CONVERSIONS.get(unit_clean, 1.0)
        return float(quantity) * factor

    def get_ingredient_price_info(self, food_id: int) -> Dict[str, Any]:
        """
        Retrieves real store price observations, reference median price, and min/max range.
        Returns prices in both per_100g and per_kg.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Fetch store observations
        cursor.execute("""
            SELECT store_name, store_product_name, price_vnd, quantity_g, normalized_price_per_100g, normalized_price_per_kg
            FROM food_prices
            WHERE food_id = ?
            ORDER BY normalized_price_per_100g ASC
        """, (food_id,))
        obs_rows = cursor.fetchall()
        store_observations = []
        for r in obs_rows:
            store_observations.append({
                "store_name": r[0],
                "product_name": r[1],
                "price_vnd": float(r[2]),
                "quantity_g": float(r[3]),
                "price_per_100g": round(float(r[4]), 1),
                "price_per_kg": round(float(r[5]), 0)
            })

        # 2. Fetch summary statistics
        cursor.execute("""
            SELECT price_min, price_median, price_max, estimated_price_per_100g
            FROM food_price_summary
            WHERE food_id = ?
        """, (food_id,))
        summary_row = cursor.fetchone()
        conn.close()

        if summary_row and summary_row[1] is not None:
            p_min = float(summary_row[0] or summary_row[1])
            p_med = float(summary_row[1])
            p_max = float(summary_row[2] or summary_row[1])
        elif store_observations:
            prices = [obs["price_per_100g"] for obs in store_observations]
            p_min = min(prices)
            p_max = max(prices)
            n = len(prices)
            p_med = prices[n // 2] if n % 2 == 1 else (prices[n // 2 - 1] + prices[n // 2]) / 2.0
        else:
            # Fallback default reasonable grocery price (15k/100g)
            p_min = 1500.0
            p_med = 1500.0
            p_max = 1500.0

        return {
            "price_per_100g_median": round(p_med, 1),
            "price_per_100g_min": round(p_min, 1),
            "price_per_100g_max": round(p_max, 1),
            "price_per_kg_median": round(p_med * 10.0, 0),
            "price_per_kg_min": round(p_min * 10.0, 0),
            "price_per_kg_max": round(p_max * 10.0, 0),
            "store_observations": store_observations
        }

    def calculate_ingredient_cost(self, food_id: int, quantity: float, unit: str = "g") -> Dict[str, Any]:
        """
        Computes the cost for a single ingredient item:
        normalized_g = convert_to_grams(quantity, unit)
        cost = (normalized_g / 100) * price_per_100g_median
        """
        norm_g = self.convert_to_grams(quantity, unit, food_id)
        price_info = self.get_ingredient_price_info(food_id)
        cost_med = (norm_g / 100.0) * price_info["price_per_100g_median"]
        cost_min = (norm_g / 100.0) * price_info["price_per_100g_min"]
        cost_max = (norm_g / 100.0) * price_info["price_per_100g_max"]

        return {
            "food_id": food_id,
            "raw_quantity": quantity,
            "raw_unit": unit,
            "display_quantity": f"{quantity:g}{unit}" if isinstance(quantity, (int, float)) else f"{quantity} {unit}",
            "normalized_quantity_g": round(norm_g, 1),
            "cost_vnd": round(cost_med, 0),
            "cost_min_vnd": round(cost_min, 0),
            "cost_max_vnd": round(cost_max, 0),
            "price_info": price_info
        }

    def calculate_recipe_cost_breakdown(self, recipe_id: int) -> Dict[str, Any]:
        """
        Computes complete Recipe Cost Breakdown:
        Every single ingredient (meat, veg, spices, oils, seasonings) with:
        - raw quantity and unit (e.g. 300g, 10ml, 5g)
        - reference median price and supermarket range
        - subtotal cost (VND)
        - total recipe cost
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Recipe meta
        cursor.execute("""
            SELECT id, name_vi, servings, dish_role, meal_type, image_url
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        rec_meta = cursor.fetchone()
        if not rec_meta:
            conn.close()
            return {"error": f"Recipe ID {recipe_id} not found"}

        # Recipe ingredients
        cursor.execute("""
            SELECT ri.food_id, f.canonical_name_vi, ri.quantity_g, ri.raw_quantity, ri.raw_unit, f.default_unit
            FROM recipe_ingredients ri
            JOIN foods f ON ri.food_id = f.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        ing_rows = cursor.fetchall()
        conn.close()

        ingredients_breakdown = []
        tot_cost_med = 0.0
        tot_cost_min = 0.0
        tot_cost_max = 0.0

        for row in ing_rows:
            fid, name_vi, qty_g, raw_q, raw_u, def_u = row
            quantity = raw_q if (raw_q is not None and raw_q > 0) else qty_g
            unit = raw_u if (raw_u is not None and raw_u != "") else (def_u or "g")

            calc = self.calculate_ingredient_cost(fid, quantity, unit)
            calc["name_vi"] = name_vi

            tot_cost_med += calc["cost_vnd"]
            tot_cost_min += calc["cost_min_vnd"]
            tot_cost_max += calc["cost_max_vnd"]

            ingredients_breakdown.append(calc)

        return {
            "recipe_id": rec_meta[0],
            "recipe_name": rec_meta[1],
            "servings": rec_meta[2] or 1,
            "dish_role": rec_meta[3],
            "meal_type": rec_meta[4],
            "image_url": rec_meta[5],
            "total_cost_vnd": round(tot_cost_med, 0),
            "cost_range": {
                "min_vnd": round(tot_cost_min, 0),
                "max_vnd": round(tot_cost_max, 0)
            },
            "ingredient_count": len(ingredients_breakdown),
            "ingredients": ingredients_breakdown,
            "cost_formula_note": "Chi phí = Σ (Định lượng thực tế / 100g) × Giá trung vị tham chiếu từ AEON, WinMart, GO!"
        }

    def calculate_meal_cost(self, recipe_ids: List[int]) -> Dict[str, Any]:
        """
        Aggregates costs for a meal combination of multiple recipes (e.g. Rice + Main + Soup).
        """
        breakdowns = [self.calculate_recipe_cost_breakdown(rid) for rid in recipe_ids]
        tot_cost = sum(b.get("total_cost_vnd", 0) for b in breakdowns if "error" not in b)
        return {
            "total_meal_cost_vnd": round(tot_cost, 0),
            "dishes": breakdowns
        }
