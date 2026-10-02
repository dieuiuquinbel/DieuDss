# -*- coding: utf-8 -*-
import pytest
from backend.services.ingredient_cost_engine import IngredientCostEngine
from backend.services.recipe_service import RecipeService
from backend.services.meal_composer import MealComposer

def test_unit_conversions():
    engine = IngredientCostEngine()
    assert engine.convert_to_grams(100, "g") == 100.0
    assert engine.convert_to_grams(1, "kg") == 1000.0
    assert engine.convert_to_grams(10, "ml") == 10.0
    assert engine.convert_to_grams(1, "l") == 1000.0
    assert engine.convert_to_grams(1, "thìa") == 5.0
    assert engine.convert_to_grams(1, "thìa canh") == 15.0
    assert engine.convert_to_grams(2, "tép") == 10.0

def test_recipe_cost_breakdown():
    engine = IngredientCostEngine()
    recipe_service = RecipeService()
    
    recipes = recipe_service.list_recipes(limit=5)
    assert len(recipes) > 0
    
    first_id = recipes[0]["id"]
    breakdown = engine.calculate_recipe_cost_breakdown(first_id)
    assert "total_cost_vnd" in breakdown
    assert breakdown["total_cost_vnd"] > 0
    assert "cost_range" in breakdown
    assert "min_vnd" in breakdown["cost_range"]
    assert "max_vnd" in breakdown["cost_range"]
    assert len(breakdown["ingredients"]) > 0
    
    for ing in breakdown["ingredients"]:
        assert "cost_vnd" in ing
        assert "price_info" in ing
        assert ing["cost_vnd"] >= 0

def test_meal_composer():
    composer = MealComposer()
    mock_items = [
        {"id": 1, "name_vi": "Cơm trắng", "calories": 200, "protein_g": 4, "carb_g": 45, "fat_g": 0.5, "estimated_cost_vnd": 3000, "dish_role": "STAPLE"},
        {"id": 2, "name_vi": "Thịt kho trứng", "calories": 350, "protein_g": 25, "carb_g": 5, "fat_g": 20, "estimated_cost_vnd": 25000, "dish_role": "MAIN_PROTEIN"},
        {"id": 3, "name_vi": "Canh rau cải", "calories": 50, "protein_g": 2, "carb_g": 6, "fat_g": 1, "estimated_cost_vnd": 6000, "dish_role": "SOUP_VEG"}
    ]
    composed = composer.compose_meal(mock_items, meal_type="LUNCH", structure_mode="STANDARD")
    assert composed["calories"] == 600.0
    assert composed["protein_g"] == 31.0
    assert composed["estimated_cost_vnd"] == 34000.0
    assert composed["meal_set"]["dish_count"] == 3
