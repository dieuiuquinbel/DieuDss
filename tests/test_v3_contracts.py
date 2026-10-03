"""
NutriDSS V3 Architecture & Contract Acceptance Tests
Verifies:
1. Single database contract validation.
2. Single Cost Engine consistency and NO fake pricing fallback.
3. Role-based Vietnamese Meal Set composer (staple, main1, main2, soup).
4. FULL structure generation with 4 dishes.
5. Weekly planner with composed meal sets.
6. Security & Authorization (user isolation, no default user_id=1 fallback).
"""

import pytest
import sqlite3
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient

from database.validate_database import validate_database
from backend.services.ingredient_cost_engine import IngredientCostEngine
from backend.services.recommender_service import RecommenderService
from backend.services.meal_composer import MealComposer
from backend.services.meal_optimizer import MealOptimizer
from backend.main import app

client = TestClient(app)

def test_database_contract_validity():
    """Verify that the database adheres 100% to NutriDSS V3 schema contract."""
    is_valid = validate_database()
    assert is_valid is True, "Database schema contract validation failed!"

def test_single_cost_engine_and_no_fake_fallback():
    """Verify that IngredientCostEngine returns UNKNOWN for missing price, not 1500 or 5000."""
    cost_engine = IngredientCostEngine()
    
    # Non-existent food ID 9999999
    price_info = cost_engine.get_ingredient_price_info(9999999)
    assert price_info["price_status"] == "UNKNOWN"
    assert price_info["price_per_100g_median"] is None
    assert price_info["price_per_100g_min"] is None
    assert price_info["price_per_100g_max"] is None

    # Calculate ingredient cost for missing price
    cost_calc = cost_engine.calculate_ingredient_cost(9999999, 100.0, "g")
    assert cost_calc["cost_status"] == "INSUFFICIENT_DATA"
    assert cost_calc["cost_vnd"] is None

def test_recommender_uses_single_cost_engine():
    """Verify RecommenderService gets exact cost from IngredientCostEngine without drift."""
    cost_engine = IngredientCostEngine()
    recommender = RecommenderService(cost_engine=cost_engine)
    recipes = recommender.get_all_recipes_with_nutrition_and_cost()
    assert len(recipes) > 0

    first_rec = recipes[0]
    expected_cost = cost_engine.calculate_recipe_cost_breakdown(first_rec["id"])
    assert first_rec["estimated_cost_vnd"] == expected_cost["estimated_cost_vnd"]

def test_meal_composer_role_mapping():
    """Verify MealComposer classifies roles and generates deterministic combo IDs."""
    composer = MealComposer()
    mock_items = [
        {"id": 1, "name_vi": "Cơm trắng", "dish_role": "STAPLE", "calories": 200, "estimated_cost_vnd": 3000},
        {"id": 2, "name_vi": "Thịt kho tàu", "dish_role": "MAIN_PROTEIN", "calories": 350, "estimated_cost_vnd": 25000},
        {"id": 3, "name_vi": "Đậu phụ sốt cà", "dish_role": "SECOND_MAIN", "calories": 150, "estimated_cost_vnd": 10000},
        {"id": 4, "name_vi": "Canh cải ngọt", "dish_role": "SOUP_VEG", "calories": 40, "estimated_cost_vnd": 6000}
    ]
    composed = composer.compose_meal(mock_items, meal_type="LUNCH", structure_mode="FULL")
    assert "error" not in composed
    assert composed["meal_set"]["staple"]["name_vi"] == "Cơm trắng"
    assert composed["meal_set"]["main_dish"]["name_vi"] == "Thịt kho tàu"
    assert composed["meal_set"]["second_main"]["name_vi"] == "Đậu phụ sốt cà"
    assert composed["meal_set"]["soup_veg"]["name_vi"] == "Canh cải ngọt"
    assert composed["main_recipe_ids"] == [2, 3]
    assert composed["id"].startswith("meal_lunch_")

def test_generate_single_meal_full_structure():
    """Verify generate_single_meal creates 4-dish meal sets when structure_mode is FULL."""
    optimizer = MealOptimizer()
    res = optimizer.generate_single_meal(
        meal_type="LUNCH",
        budget_vnd=80000.0,
        goal="BALANCED",
        structure_mode="FULL"
    )
    assert "error" not in res
    assert "options" in res
    assert len(res["options"]) > 0

    first_opt = res["options"][0]["meal"]
    # FULL structure must have 4 dishes in its meal_set items
    assert first_opt["meal_set"]["structure_mode"] == "FULL"
    assert first_opt["meal_set"]["dish_count"] == 4
    assert first_opt["meal_set"]["second_main"] is not None

def test_generate_weekly_plan_composed_sets():
    """Verify weekly planner returns 7 days with composed lunch & dinner meal sets."""
    optimizer = MealOptimizer()
    res = optimizer.generate_weekly_plan(
        goal="BALANCED",
        daily_budget_vnd=85000.0
    )
    assert "error" not in res
    assert res["days_count"] == 7
    assert len(res["days"]) == 7

    monday = res["days"][0]
    lunch = monday["meals"]["lunch"]
    dinner = monday["meals"]["dinner"]
    # Lunch and dinner must be composed Meal Sets, not single dishes
    assert "meal_set" in lunch
    assert "meal_set" in dinner
    assert len(lunch["meal_set"]["items"]) >= 3
    assert len(dinner["meal_set"]["items"]) >= 3

def test_security_unauthenticated_access_rejected():
    """Verify that saving or viewing private meal plans without token is rejected with 401/403."""
    # Attempt to get saved meal plans without Authorization header
    resp = client.get("/api/meal-plans")
    assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"

    # Attempt to save meal plan without token
    save_payload = {
        "plan_name": "Test Plan",
        "plan_type": "DAILY",
        "budget_vnd": 70000,
        "health_goal": "BALANCED",
        "items": []
    }
    resp = client.post("/api/meal-plans/save", json=save_payload)
    assert resp.status_code in [401, 403], f"Expected 401/403, got {resp.status_code}"
