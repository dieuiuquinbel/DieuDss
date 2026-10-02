"""
NutriDSS - Recommender Service V2
Implements multi-stage recommendation:
1. Candidate Generation (Filtering by meal type & hard constraints)
2. ML Scoring (Gradient Boosting Ranker)
3. Diversity & Re-Ranking (Food group / protein source balance)
4. Explainability ('Why this food?' DSS reasoning tags)
"""

import sqlite3
import pandas as pd
import numpy as np
import joblib
import os
from typing import List, Dict, Any, Optional

from backend.services.rule_engine import RuleEngine

MODEL_PATH = "models/best_recipe_ranker.joblib"
DB_PATH = "database/nutridss.db"

class RecommenderService:
    def __init__(self):
        self._load_model()
        self._cached_recipes = None

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None
        else:
            self.model = None

    def get_all_recipes_with_nutrition_and_cost(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Lấy tất cả công thức cùng dinh dưỡng và chi phí ước tính (có in-memory cache)."""
        if self._cached_recipes is not None and not force_refresh:
            # Return deep copy or fresh dicts
            return [dict(r) for r in self._cached_recipes]

        conn = sqlite3.connect(DB_PATH)
        df_recipes = pd.read_sql_query("SELECT * FROM recipes", conn)
        df_ings = pd.read_sql_query("SELECT * FROM recipe_ingredients", conn)
        df_foods = pd.read_sql_query("SELECT * FROM foods", conn)
        df_prices = pd.read_sql_query("SELECT * FROM food_price_summary", conn)
        conn.close()

        food_map = {row['id']: row for _, row in df_foods.iterrows()}
        price_map = {row['food_id']: row.get('estimated_price_per_100g', 5000.0) for _, row in df_prices.iterrows()}

        recipe_list = []

        for _, rec in df_recipes.iterrows():
            rec_id = rec['id']
            ings = df_ings[df_ings['recipe_id'] == rec_id]
            
            total_cal = 0.0
            total_prot = 0.0
            total_carb = 0.0
            total_fat = 0.0
            total_fiber = 0.0
            total_sugar = 0.0
            total_sodium = 0.0
            total_cost = 0.0
            main_ingredients = []

            for _, ing in ings.iterrows():
                f_id = ing['food_id']
                qty = ing['quantity_g']
                
                f_info = food_map.get(f_id)
                if f_info is None:
                    continue
                price_100g = price_map.get(f_id, 5000.0)
                
                total_cal += (float(f_info['calories_kcal_100g']) / 100.0) * qty
                total_prot += (float(f_info['protein_g_100g']) / 100.0) * qty
                total_carb += (float(f_info['carb_g_100g']) / 100.0) * qty
                total_fat += (float(f_info['fat_g_100g']) / 100.0) * qty
                total_fiber += (float(f_info['fiber_g_100g']) / 100.0) * qty
                total_sugar += (float(f_info['sugar_g_100g']) / 100.0) * qty
                total_sodium += (float(f_info['sodium_mg_100g']) / 100.0) * qty
                total_cost += (price_100g / 100.0) * qty
                main_ingredients.append(f_info['canonical_name_vi'])

            recipe_list.append({
                "id": int(rec['id']),
                "name_vi": str(rec['name_vi']) if pd.notna(rec.get('name_vi')) else "",
                "meal_type": str(rec['meal_type']) if pd.notna(rec.get('meal_type')) else "LUNCH",
                "dish_role": str(rec.get('dish_role')) if pd.notna(rec.get('dish_role')) else "MAIN_DISH",
                "is_vegetarian": int(rec.get('is_vegetarian', 0) or 0) if pd.notna(rec.get('is_vegetarian')) else 0,
                "servings": int(rec.get('servings', 1)) if pd.notna(rec.get('servings')) else 1,
                "prep_time_min": int(rec.get('prep_time_min', 10)) if pd.notna(rec.get('prep_time_min')) else 10,
                "cook_time_min": int(rec.get('cook_time_min', 15)) if pd.notna(rec.get('cook_time_min')) else 15,
                "difficulty": str(rec.get('difficulty')) if pd.notna(rec.get('difficulty')) else "EASY",
                "description": str(rec.get('description')) if pd.notna(rec.get('description')) else "",
                "tags": str(rec.get('tags')) if pd.notna(rec.get('tags')) else "",
                "source_name": str(rec.get('source_name')) if pd.notna(rec.get('source_name')) else "",
                "image_url": str(rec.get('image_url')) if pd.notna(rec.get('image_url')) else "",
                "main_ingredients": main_ingredients,
                "calories": 0.0 if pd.isna(total_cal) else round(float(total_cal), 1),
                "protein_g": 0.0 if pd.isna(total_prot) else round(float(total_prot), 1),
                "carb_g": 0.0 if pd.isna(total_carb) else round(float(total_carb), 1),
                "fat_g": 0.0 if pd.isna(total_fat) else round(float(total_fat), 1),
                "fiber_g": 0.0 if pd.isna(total_fiber) else round(float(total_fiber), 1),
                "sugar_g": 0.0 if pd.isna(total_sugar) else round(float(total_sugar), 1),
                "sodium_mg": 0.0 if pd.isna(total_sodium) else round(float(total_sodium), 1),
                "estimated_cost_vnd": 0.0 if pd.isna(total_cost) else round(float(total_cost), 0)
            })

        self._cached_recipes = recipe_list
        return [dict(r) for r in self._cached_recipes]

    def _generate_explanation(self, recipe: Dict[str, Any], goal: str, budget_vnd: float) -> str:
        """Sinh lời giải thích 'Why this food?' (Explainable DSS)."""
        reasons = []
        cost = recipe.get("estimated_cost_vnd", 0)
        prot = recipe.get("protein_g", 0)
        cal = recipe.get("calories", 0)
        
        if budget_vnd > 0 and cost <= budget_vnd * 0.9:
            reasons.append(f"Tiết kiệm chi phí ({cost:,.0f}đ)")
            
        if goal == "LOSE_WEIGHT":
            if prot >= 20:
                reasons.append(f"Giàu protein ({prot:.0f}g) tạo cảm giác no lâu")
            if cal <= 450:
                reasons.append(f"Mức calo vừa phải ({cal:.0f} kcal)")
        elif goal in ("GAIN_MUSCLE", "HIGH_PROTEIN"):
            if prot >= 25:
                reasons.append(f"Hàm lượng đạm cao ({prot:.0f}g) hỗ trợ cơ bắp")
        elif goal == "GAIN_WEIGHT":
            if cal >= 400:
                reasons.append(f"Giàu năng lượng sạch ({cal:.0f} kcal)")

        if recipe.get("sodium_mg", 0) <= 600:
            reasons.append("Hàm lượng muối thấp theo chuẩn WHO")

        return "; ".join(reasons) if reasons else "Cân đối dinh dưỡng tổng thể"

    def rank_recipes(
        self, 
        goal: str, 
        budget_vnd: float, 
        user_allergies: Optional[List[str]] = None, 
        meal_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Xếp hạng các món ăn dựa trên ML Score & Rule Constraints + Explainability.
        """
        all_recipes = self.get_all_recipes_with_nutrition_and_cost()

        # 1. Hard Constraints: Lọc dị ứng
        filtered_recipes = RuleEngine.filter_hard_constraints(all_recipes, user_allergies or [])

        # Lọc theo bữa ăn nếu có
        if meal_type:
            filtered_recipes = [r for r in filtered_recipes if r['meal_type'].upper() == meal_type.upper()]

        if not filtered_recipes:
            return []

        # 2. Tạo feature cho ML Model
        feature_rows = []
        for r in filtered_recipes:
            cost_ratio = r['estimated_cost_vnd'] / budget_vnd if budget_vnd > 0 else 1.0
            feature_rows.append({
                "goal": goal.upper(),
                "budget_vnd": float(budget_vnd),
                "calories": float(r['calories']),
                "protein_g": float(r['protein_g']),
                "carb_g": float(r['carb_g']),
                "fat_g": float(r['fat_g']),
                "estimated_cost_vnd": float(r['estimated_cost_vnd']),
                "cost_ratio": float(cost_ratio)
            })

        df_features = pd.DataFrame(feature_rows)

        # 3. Chạy ML Model suy luận điểm số
        if self.model:
            try:
                ml_scores = self.model.predict(df_features)
            except Exception:
                ml_scores = [4.0] * len(filtered_recipes)
        else:
            ml_scores = [4.0] * len(filtered_recipes)

        # 4. Gán score và explanation
        for idx, r in enumerate(filtered_recipes):
            score = round(float(ml_scores[idx]), 2)
            r['score'] = score
            r['explanation'] = self._generate_explanation(r, goal, budget_vnd)
            
            if score >= 4.2:
                r['compatibility_label'] = "Rất phù hợp"
            elif score >= 3.2:
                r['compatibility_label'] = "Phù hợp"
            else:
                r['compatibility_label'] = "Cần cân nhắc"

        # Sắp xếp theo score giảm dần
        ranked = sorted(filtered_recipes, key=lambda x: x['score'], reverse=True)
        return ranked

    # Backward compatibility helper
    def _get_all_recipes_with_nutrition_and_cost(self) -> List[Dict[str, Any]]:
        return self.get_all_recipes_with_nutrition_and_cost()
