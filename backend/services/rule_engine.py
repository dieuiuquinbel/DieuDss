"""
NutriDSS - Guideline-Driven Rule Engine
Layer 1 of DSS Decision Hierarchy:
1. Hard Constraints: Strict, zero-exception filtering (Allergens & Dietary Exclusions)
2. Soft Constraints: Evidence-based health guideline evaluation (WHO 2023 Guidelines & NIN Standards)
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional

DB_PATH = "database/nutridss.db"

class RuleEngine:
    _cached_guidelines = None

    @classmethod
    def load_guideline_rules(cls) -> Dict[str, Dict[str, Any]]:
        """Load WHO & National guideline rules from database table guideline_rules."""
        if cls._cached_guidelines is not None:
            return cls._cached_guidelines

        conn = sqlite3.connect(DB_PATH)
        try:
            df = pd.read_sql_query("SELECT * FROM guideline_rules", conn)
            rules = {}
            for _, r in df.iterrows():
                rules[r["rule_code"]] = {
                    "nutrient": r["nutrient"],
                    "min_value": r["min_value"],
                    "max_value": r["max_value"],
                    "unit": r["unit"],
                    "scope": r["scope"],
                    "description": r["description"]
                }
            cls._cached_guidelines = rules
            return rules
        except Exception:
            # Fallback defaults if table unavailable
            return {
                "WHO_SODIUM_MAX": {"nutrient": "SODIUM", "max_value": 2000.0, "unit": "mg", "scope": "DAILY"},
                "WHO_SODIUM_PER_MEAL": {"nutrient": "SODIUM", "max_value": 800.0, "unit": "mg", "scope": "PER_MEAL"},
                "WHO_FREE_SUGAR_MAX": {"nutrient": "SUGAR_FREE", "max_value": 25.0, "unit": "g", "scope": "DAILY"},
                "WHO_SAT_FAT_MAX": {"nutrient": "FAT_SATURATED", "max_value": 20.0, "unit": "g", "scope": "DAILY"},
                "WHO_FIBER_MIN": {"nutrient": "FIBER", "min_value": 25.0, "unit": "g", "scope": "DAILY"},
            }
        finally:
            conn.close()

    @staticmethod
    def get_valid_allergen_codes() -> List[str]:
        """Fetch all verified allergen codes from database."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM allergens")
        rows = cursor.fetchall()
        conn.close()
        return [r[0].upper() for r in rows]

    @staticmethod
    def get_user_allergen_ids(user_allergy_codes: List[str]) -> List[int]:
        """
        Validate allergen codes and return corresponding database IDs.
        Strict medical safety (Hard Constraint): Unknown allergen codes trigger explicit rejection.
        """
        if not user_allergy_codes:
            return []
        
        clean_codes = [c.strip().upper() for c in user_allergy_codes if c and c.strip()]
        if not clean_codes:
            return []

        valid_codes = RuleEngine.get_valid_allergen_codes()
        unknown_codes = [c for c in clean_codes if c not in valid_codes]
        if unknown_codes:
            raise ValueError(
                f"Phát hiện mã dị ứng không xác định hoặc chưa được hỗ trợ: {', '.join(unknown_codes)}. "
                f"Vì lý do an toàn y tế nghiêm ngặt (Hard Constraint), hệ thống không thể xây dựng thực đơn "
                f"khi có chất dị ứng chưa được kiểm chứng trong cơ sở dữ liệu."
            )

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in clean_codes)
        cursor.execute(f"SELECT id FROM allergens WHERE code IN ({placeholders})", clean_codes)
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    @staticmethod
    def filter_hard_constraints(recipes: List[Dict[str, Any]], user_allergy_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Hard Constraint: Completely eliminate 100% of recipes containing ingredients matching user allergies.
        """
        allergen_ids = RuleEngine.get_user_allergen_ids(user_allergy_codes)
        if not allergen_ids:
            return recipes
            
        conn = sqlite3.connect(DB_PATH)
        placeholders = ','.join('?' for _ in allergen_ids)
        query = f"SELECT DISTINCT food_id FROM food_allergens WHERE allergen_id IN ({placeholders})"
        forbidden_foods = pd.read_sql_query(query, conn, params=allergen_ids)['food_id'].tolist()
        
        if not forbidden_foods:
            conn.close()
            return recipes
            
        placeholders_food = ','.join('?' for _ in forbidden_foods)
        query_recipe = f"SELECT DISTINCT recipe_id FROM recipe_ingredients WHERE food_id IN ({placeholders_food})"
        forbidden_recipes = pd.read_sql_query(query_recipe, conn, params=forbidden_foods)['recipe_id'].tolist()
        conn.close()
        
        valid_recipes = [r for r in recipes if r['id'] not in forbidden_recipes]
        return valid_recipes

    @classmethod
    def evaluate_health_warnings(cls, meal_item: Dict[str, Any], daily_target_calories: float) -> List[str]:
        """
        Soft Constraint: Evaluate against database-backed WHO Guidelines.
        Respects nutrition distinction: Total vs Free Sugar, Total vs Saturated Fat.
        """
        rules = cls.load_guideline_rules()
        warnings = []
        safe_daily_cal = daily_target_calories if daily_target_calories and daily_target_calories > 0 else 1800.0
        target_meal_cal = safe_daily_cal / 3.0
        
        calories = float(meal_item.get('calories', 0))
        fat_g = float(meal_item.get('fat_g', 0))
        sugar_g = float(meal_item.get('sugar_g', 0))
        free_sugar_g = meal_item.get('free_sugar_g')
        sat_fat_g = meal_item.get('saturated_fat_g')
        sodium_mg = float(meal_item.get('sodium_mg', 0))
        
        # 1. Caloric density check
        if calories > target_meal_cal * 1.35:
            warnings.append(
                f"⚠️ Năng lượng bữa ăn ({calories:.0f} Kcal) cao hơn khuyến nghị cho 1 bữa ({target_meal_cal:.0f} Kcal)."
            )
            
        # 2. Free vs Total Sugar evaluation
        if free_sugar_g is not None:
            sugar_cal = free_sugar_g * 4.0
            if calories > 0 and (sugar_cal / calories) > 0.10:
                warnings.append("⚠️ Đường tự do (Added/Free sugar) vượt mức 10% năng lượng bữa ăn theo khuyến cáo WHO.")
        elif calories > 0 and (sugar_g * 4.0 / calories) > 0.15:
            warnings.append("⚠️ Tổng lượng đường trong món ăn khá cao. Nên tiết chế nếu đang kiểm soát cân nặng.")
            
        # 3. Saturated vs Total Fat evaluation
        if sat_fat_g is not None:
            sat_fat_cal = sat_fat_g * 9.0
            if calories > 0 and (sat_fat_cal / calories) > 0.10:
                warnings.append("⚠️ Chất béo bão hòa vượt quá 10% năng lượng bữa ăn theo chuẩn WHO.")
        elif calories > 0 and (fat_g * 9.0 / calories) > 0.35:
            warnings.append("⚠️ Tỷ lệ năng lượng từ tổng chất béo tương đối cao. Cân nhắc giảm dầu mỡ khi chế biến.")
            
        # 4. Sodium evaluation against WHO limit
        sodium_rule = rules.get("WHO_SODIUM_PER_MEAL", {})
        meal_max_sodium = sodium_rule.get("max_value", 700.0)
        if sodium_mg > meal_max_sodium:
            warnings.append(
                f"⚠️ Hàm lượng Natri ({sodium_mg:.0f} mg) vượt ngưỡng khuyến cáo một bữa ({meal_max_sodium:.0f} mg theo chuẩn WHO)."
            )
            
        return warnings
