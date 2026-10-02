# -*- coding: utf-8 -*-
"""
NutriDSS - Recipe Service (backend/services/recipe_service.py)
Single Responsibility:
Querying and managing canonical Vietnamese recipes, cooking steps, nutritional profiles,
and full ingredient cost breakdowns from IngredientCostEngine.
"""

import sqlite3
import os
from typing import Dict, List, Any, Optional
from backend.services.ingredient_cost_engine import IngredientCostEngine

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "database", "nutridss.db")

class RecipeService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.cost_engine = IngredientCostEngine(db_path)

    def get_recipe_details(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves full recipe details including:
        - Meta info (name, meal_type, dish_role, servings, time, difficulty, image)
        - Cooking steps (recipe_steps)
        - Nutrition profile (calories, protein, carb, fat, fiber, sodium)
        - Full Cost Breakdown from IngredientCostEngine
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name_vi, meal_type, servings, prep_time_min, cook_time_min,
                   difficulty, description, source_name, tags, image_url, dish_role, is_vegetarian
            FROM recipes
            WHERE id = ?
        """, (recipe_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        # Fetch cooking steps
        cursor.execute("""
            SELECT step_number, instruction_vi, duration_min
            FROM recipe_steps
            WHERE recipe_id = ?
            ORDER BY step_number ASC
        """, (recipe_id,))
        steps = [
            {"step_number": s[0], "instruction": s[1], "duration_min": s[2]}
            for s in cursor.fetchall()
        ]

        # Calculate Nutrition from ingredients
        cursor.execute("""
            SELECT ri.quantity_g, f.calories_kcal_100g, f.protein_g_100g, f.carb_g_100g,
                   f.fat_g_100g, f.fiber_g_100g, f.sodium_mg_100g
            FROM recipe_ingredients ri
            JOIN foods f ON ri.food_id = f.id
            WHERE ri.recipe_id = ?
        """, (recipe_id,))
        nutr_rows = cursor.fetchall()
        conn.close()

        tot_cal = sum((r[0] / 100.0) * (r[1] or 0) for r in nutr_rows)
        tot_prot = sum((r[0] / 100.0) * (r[2] or 0) for r in nutr_rows)
        tot_carb = sum((r[0] / 100.0) * (r[3] or 0) for r in nutr_rows)
        tot_fat = sum((r[0] / 100.0) * (r[4] or 0) for r in nutr_rows)
        tot_fiber = sum((r[0] / 100.0) * (r[5] or 0) for r in nutr_rows)
        tot_sodium = sum((r[0] / 100.0) * (r[6] or 0) for r in nutr_rows)

        # Full Cost Breakdown
        cost_breakdown = self.cost_engine.calculate_recipe_cost_breakdown(recipe_id)

        return {
            "id": row[0],
            "name_vi": row[1],
            "meal_type": row[2],
            "servings": row[3] or 1,
            "prep_time_min": row[4] or 10,
            "cook_time_min": row[5] or 15,
            "difficulty": row[6] or "EASY",
            "description": row[7],
            "source_name": row[8],
            "tags": row[9],
            "image_url": row[10],
            "dish_role": row[11],
            "is_vegetarian": bool(row[12]),
            "nutrition": {
                "calories": round(tot_cal, 1),
                "protein_g": round(tot_prot, 1),
                "carb_g": round(tot_carb, 1),
                "fat_g": round(tot_fat, 1),
                "fiber_g": round(tot_fiber, 1),
                "sodium_mg": round(tot_sodium, 1)
            },
            "steps": steps,
            "cost_breakdown": cost_breakdown
        }

    def list_recipes(
        self,
        search_query: Optional[str] = None,
        dish_role: Optional[str] = None,
        meal_type: Optional[str] = None,
        is_vegetarian: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lists recipes with basic filters, nutrition and total cost.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT id, name_vi, meal_type, servings, prep_time_min, cook_time_min,
                   difficulty, description, tags, image_url, dish_role, is_vegetarian
            FROM recipes
            WHERE 1=1
        """
        params = []

        if search_query:
            query += " AND name_vi LIKE ?"
            params.append(f"%{search_query.strip()}%")

        if dish_role and dish_role != "ALL":
            query += " AND dish_role = ?"
            params.append(dish_role)

        if meal_type and meal_type != "ALL":
            query += " AND meal_type = ?"
            params.append(meal_type)

        if is_vegetarian is not None:
            query += " AND is_vegetarian = ?"
            params.append(1 if is_vegetarian else 0)

        query += " ORDER BY id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for r in rows:
            rec_id = r[0]
            # Simple quick cost
            cost_info = self.cost_engine.calculate_recipe_cost_breakdown(rec_id)
            results.append({
                "id": rec_id,
                "name_vi": r[1],
                "meal_type": r[2],
                "servings": r[3] or 1,
                "prep_time_min": r[4] or 10,
                "cook_time_min": r[5] or 15,
                "difficulty": r[6] or "EASY",
                "description": r[7],
                "tags": r[8],
                "image_url": r[9],
                "dish_role": r[10],
                "is_vegetarian": bool(r[11]),
                "estimated_cost_vnd": cost_info.get("total_cost_vnd", 0),
                "cost_range": cost_info.get("cost_range", {})
            })

        return results
