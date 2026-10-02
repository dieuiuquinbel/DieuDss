# -*- coding: utf-8 -*-
"""
NutriDSS - Meal Composer Service (backend/services/meal_composer.py)
Single Responsibility:
Composes authentic Vietnamese meal combinations according to selectable structures:
- STANDARD: 1 Cơm + 1 Mặn + 1 Canh (3 món sinh viên / người đi làm)
- FULL: 1 Cơm + 2 Món Mặn + 1 Canh (4 món gia đình)
- LIGHT: 1 Tinh bột nhẹ + 1 Đạm nạc + 1 Rau củ luộc (Eat-clean)
- VEGETARIAN: 1 Cơm + 1 Đậu hũ + 1 Nấm + 1 Canh chay
Aggregates exact nutrition and deterministic costs via IngredientCostEngine.
"""

from typing import Dict, List, Any, Optional
from backend.services.ingredient_cost_engine import IngredientCostEngine

class MealComposer:
    def __init__(self, cost_engine: Optional[IngredientCostEngine] = None):
        self.cost_engine = cost_engine or IngredientCostEngine()

    def compose_meal(
        self,
        items: List[Dict[str, Any]],
        meal_type: str = "LUNCH",
        structure_mode: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        Combines discrete recipe items into a unified Vietnamese meal set.
        Calculates exact sum of calories, protein, carb, fat, sodium, and supermarket cost.
        """
        if not items:
            return {"error": "Danh sách món ăn trống."}

        tot_cal = sum(it.get("calories", 0) for it in items)
        tot_prot = sum(it.get("protein_g", 0) for it in items)
        tot_carb = sum(it.get("carb_g", 0) for it in items)
        tot_fat = sum(it.get("fat_g", 0) for it in items)
        tot_sod = sum(it.get("sodium_mg", 0) for it in items)
        tot_cost = sum(it.get("estimated_cost_vnd", 0) for it in items)
        avg_score = round(sum(it.get("score", 4.5) for it in items) / len(items), 2)

        name = " + ".join(it.get("name_vi", "") for it in items)

        label_map = {
            "FULL": "Mâm cơm gia đình 4 món (1 cơm + 2 mặn + 1 canh)",
            "LIGHT": "Bữa ăn nhẹ Eat-clean (3 món)",
            "VEGETARIAN": "Mâm cơm chay thanh tịnh",
            "STANDARD": "Mâm cơm chuẩn Việt 3 món"
        }
        structure_label = label_map.get(structure_mode, "Mâm cơm chuẩn Việt")

        # Find main image from main protein or first item
        main_dish = next((i for i in items if i.get("dish_role") in ["MAIN_PROTEIN", "VEG_PROTEIN"]), items[0])
        dish_image = main_dish.get("image_url", "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=80")

        return {
            "id": items[0].get("id", 0),
            "name_vi": name,
            "meal_type": meal_type,
            "calories": round(tot_cal, 1),
            "protein_g": round(tot_prot, 1),
            "carb_g": round(tot_carb, 1),
            "fat_g": round(tot_fat, 1),
            "sodium_mg": round(tot_sod, 1),
            "estimated_cost_vnd": round(tot_cost, 0),
            "score": avg_score,
            "servings": 1,
            "image_url": dish_image,
            "explanation": f"{structure_label}: {name}.",
            "compatibility_label": items[0].get("compatibility_label", "Khuyên dùng"),
            "meal_set": {
                "structure_mode": structure_mode,
                "dish_count": len(items),
                "items": items,
                "staple": items[0] if len(items) > 0 else None,
                "main_dish": items[1] if len(items) > 1 else None,
                "soup_veg": items[-1] if len(items) > 2 else None
            }
        }
