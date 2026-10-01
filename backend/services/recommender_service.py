"""
NutriDSS - Recommender Service
Kết hợp Rule Engine (Allergy Filtering) và Machine Learning Model (Decision Tree Ranker)
để xếp hạng và gợi ý công thức phù hợp nhất cho người dùng.
"""

import sqlite3
import pandas as pd
import numpy as np
import joblib
import os
from typing import List, Dict, Any

from backend.services.rule_engine import RuleEngine

MODEL_PATH = "models/best_recipe_ranker.joblib"
DB_PATH = "database/nutridss.db"

class RecommenderService:
    def __init__(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            self.model = None

    def _get_all_recipes_with_nutrition_and_cost(self) -> List[Dict[str, Any]]:
        """Lấy tất cả công thức cùng thông tin dinh dưỡng và chi phí ước tính"""
        conn = sqlite3.connect(DB_PATH)
        df_recipes = pd.read_sql_query("SELECT * FROM recipes", conn)
        df_ings = pd.read_sql_query("SELECT * FROM recipe_ingredients", conn)
        df_foods = pd.read_sql_query("SELECT * FROM foods", conn)
        df_prices = pd.read_sql_query("SELECT * FROM food_price_summary", conn)
        conn.close()

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

            for _, ing in ings.iterrows():
                f_id = ing['food_id']
                qty = ing['quantity_g']
                
                f_info = df_foods[df_foods['id'] == f_id].iloc[0]
                p_info = df_prices[df_prices['food_id'] == f_id]
                price_100g = p_info['estimated_price_per_100g'].values[0] if len(p_info) > 0 else 5000.0
                
                total_cal += (f_info['calories_kcal_100g'] / 100.0) * qty
                total_prot += (f_info['protein_g_100g'] / 100.0) * qty
                total_carb += (f_info['carb_g_100g'] / 100.0) * qty
                total_fat += (f_info['fat_g_100g'] / 100.0) * qty
                total_fiber += (f_info['fiber_g_100g'] / 100.0) * qty
                total_sugar += (f_info['sugar_g_100g'] / 100.0) * qty
                total_sodium += (f_info['sodium_mg_100g'] / 100.0) * qty
                total_cost += (price_100g / 100.0) * qty

            recipe_list.append({
                "id": rec['id'],
                "name_vi": rec['name_vi'],
                "meal_type": rec['meal_type'],
                "servings": rec['servings'],
                "prep_time_min": rec['prep_time_min'],
                "cook_time_min": rec['cook_time_min'],
                "difficulty": rec['difficulty'],
                "description": rec['description'],
                "tags": rec['tags'],
                "calories": round(total_cal, 1),
                "protein_g": round(total_prot, 1),
                "carb_g": round(total_carb, 1),
                "fat_g": round(total_fat, 1),
                "fiber_g": round(total_fiber, 1),
                "sugar_g": round(total_sugar, 1),
                "sodium_mg": round(total_sodium, 1),
                "estimated_cost_vnd": round(total_cost, 0)
            })

        return recipe_list

    def rank_recipes(self, goal: str, budget_vnd: float, user_allergies: List[str] = None, meal_type: str = None) -> List[Dict[str, Any]]:
        """
        Xếp hạng các món ăn dựa trên ML Score & Rule Constraints
        """
        all_recipes = self._get_all_recipes_with_nutrition_and_cost()

        # 1. Lọc Hard Constraints (Loại bỏ món chứa dị ứng)
        filtered_recipes = RuleEngine.filter_hard_constraints(all_recipes, user_allergies or [])

        # Lọc theo bữa ăn nếu có
        if meal_type:
            filtered_recipes = [r for r in filtered_recipes if r['meal_type'].upper() == meal_type.upper()]

        if not filtered_recipes:
            return []

        # 2. Tạo tính năng dự đoán cho ML Model
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

        # 3. Chạy ML Model suy luận điểm số (Score 1.0 - 5.0)
        if self.model:
            ml_scores = self.model.predict(df_features)
        else:
            ml_scores = [4.0] * len(filtered_recipes)

        # 4. Đính kèm điểm số và phân hạng
        for idx, r in enumerate(filtered_recipes):
            score = round(float(ml_scores[idx]), 2)
            r['score'] = score
            
            if score >= 4.0:
                r['compatibility_label'] = "Rất phù hợp"
            elif score >= 3.0:
                r['compatibility_label'] = "Phù hợp"
            else:
                r['compatibility_label'] = "Cần cân nhắc"

        # Sắp xếp theo score giảm dần
        ranked = sorted(filtered_recipes, key=lambda x: x['score'], reverse=True)
        return ranked
