"""
NutriDSS - Unit & Integration Testing Suite
Kiểm thử tự động cho toàn bộ hệ thống (Nutrition Service, Rule Engine, Recommender, Optimizer & FastAPI Endpoints)
"""

import pytest
import os
import sqlite3
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.nutrition_service import NutritionService
from backend.services.rule_engine import RuleEngine
from backend.services.recommender_service import RecommenderService
from backend.services.meal_optimizer import MealOptimizer

client = TestClient(app)

# 1. Test Nutrition Calculations
def test_nutrition_calculations():
    bmr_male = NutritionService.calculate_bmr("MALE", 70.0, 175.0, 25)
    assert bmr_male > 1600.0, "BMR cho nam 70kg 175cm 25t phải > 1600 kcal"
    
    tdee = NutritionService.calculate_tdee(bmr_male, "MODERATE")
    assert tdee > bmr_male, "TDEE phải lớn hơn BMR"
    
    target_lose = NutritionService.calculate_target_calories(tdee, "LOSE_WEIGHT")
    assert target_lose == tdee - 500.0, "Giảm cân thâm hụt 500 kcal"

# 2. Test Rule Engine Hard Constraints (Allergy Filter)
def test_rule_engine_hard_constraints():
    recommender = RecommenderService()
    all_recipes = recommender._get_all_recipes_with_nutrition_and_cost()
    
    # Giả định dị ứng SEAFOOD
    filtered = RuleEngine.filter_hard_constraints(all_recipes, ["SEAFOOD"])
    
    # Kiểm tra không món nào trong filtered chứa tôm/cá
    forbidden_ids = [1002, 1004] # Cá rô phi, Bún tôm
    for r in filtered:
        assert r['id'] not in forbidden_ids, f"Món dị ứng ID {r['id']} chưa bị loại trừ!"

# 3. Test Recommender Ranking
def test_recommender_ranking():
    recommender = RecommenderService()
    ranked = recommender.rank_recipes("LOSE_WEIGHT", 30000.0)
    assert len(ranked) > 0, "Phải gợi ý danh sách món ăn"
    assert "score" in ranked[0], "Mỗi món ăn phải có điểm ML Score"
    assert ranked[0]['score'] >= ranked[-1]['score'], "Danh sách phải sắp xếp theo điểm score giảm dần"

# 4. Test Meal Optimizer 3 Options
def test_meal_optimizer_options():
    optimizer = MealOptimizer()
    res = optimizer.generate_daily_plan_options("LOSE_WEIGHT", 70000.0)
    assert "options" in res, "Phải có kết quả options"
    assert len(res["options"]) == 3, "Phải trả về đúng 3 phương án A, B, C"

# 5. Test FastAPI Integration Endpoints
def test_api_endpoints():
    # Test Root GET
    res_root = client.get("/")
    assert res_root.status_code == 200
    
    # Test Foods GET
    res_foods = client.get("/api/foods")
    assert res_foods.status_code == 200
    assert len(res_foods.json()) > 0
    
    # Test Generate Meal Plan POST
    res_gen = client.post("/api/meal-plans/generate", json={
        "health_goal": "LOSE_WEIGHT",
        "daily_budget_vnd": 70000.0,
        "allergies": []
    })
    assert res_gen.status_code == 200
    assert "options" in res_gen.json()

# 6. Test Weight Goal Medical Validation Rules
def test_goal_validation_rules():
    # Test 6.1: Negative goal target value is converted to positive
    advice_neg = NutritionService.generate_goal_advice("LOSE_WEIGHT", -5.0, 68.0)
    assert advice_neg["val"] == 5.0, "Mục tiêu âm phải được chuyển thành số dương"
    assert any(w["type"] == "danger" for w in advice_neg["warnings"])

    # Test 6.2: Goal target >= 1/3 body weight produces yellow warning (warning type)
    advice_one_third = NutritionService.generate_goal_advice("LOSE_WEIGHT", 25.0, 68.0)
    assert any(w["type"] == "warning" and "1/3" in w["message"] for w in advice_one_third["warnings"]), \
        "Phải có cảnh báo màu vàng khi muốn giảm >= 1/3 trọng lượng cơ thể"

    # Test 6.3: Goal target >= current weight produces hard error/adjustment
    advice_exceed = NutritionService.generate_goal_advice("LOSE_WEIGHT", 75.0, 68.0)
    assert any(w["type"] == "danger" and "vượt quá" in w["message"] for w in advice_exceed["warnings"]), \
        "Không được phép giảm vượt quá hoặc bằng số cân hiện tại"
    assert advice_exceed["val"] < 68.0, "Giá trị phải được điều chỉnh về mức an toàn"

# 7. Test Macro Targets & Profile Calculation API
def test_profile_macro_targets_api():
    res = client.post("/api/profile/calculate", json={
        "display_name": "Nguyen Van A",
        "gender": "MALE",
        "weight_kg": 72.0,
        "height_cm": 174.0,
        "age": 28,
        "activity_level": "MODERATE",
        "health_goal": "LOSE_WEIGHT"
    })
    assert res.status_code == 200, f"Profile calculate API lỗi: {res.text}"
    data = res.json()
    assert "target_calories" in data
    assert "target_protein_g" in data
    assert "target_carb_g" in data
    assert "target_fat_g" in data
    assert data["target_protein_g"] > 0
    assert data["target_carb_g"] > 0
    assert data["target_fat_g"] > 0

# 8. Test Unknown Allergen Hard Constraint
def test_unknown_allergen_hard_constraint():
    with pytest.raises(ValueError) as excinfo:
        RuleEngine.get_user_allergen_ids(["NOT_A_REAL_ALLERGEN"])
    assert "không xác định" in str(excinfo.value)

    # Qua API phải trả về 400
    res = client.post("/api/meal-plans/generate", json={
        "health_goal": "LOSE_WEIGHT",
        "daily_budget_vnd": 70000.0,
        "allergies": ["NOT_A_REAL_ALLERGEN"]
    })
    assert res.status_code == 400, "Phải từ chối mã dị ứng lạ với mã lỗi 400"

# 9. Test Budget Constraint & Unfeasible Budget Warning
def test_budget_constraints():
    optimizer = MealOptimizer()
    
    # Ngân sách 10.000đ/ngày (thấp hơn chi phí thực tế tối thiểu 3 bữa ~14.192đ)
    res_low = optimizer.generate_daily_plan_options("LOSE_WEIGHT", 10000.0)
    assert res_low["is_budget_strictly_feasible"] is False
    assert res_low["budget_warning"] is not None
    assert "10,000" in res_low["budget_warning"]

    # Ngân sách 70.000đ/ngày (khả thi)
    res_ok = optimizer.generate_daily_plan_options("LOSE_WEIGHT", 70000.0)
    assert res_ok["is_budget_strictly_feasible"] is True
    assert all(opt["is_within_budget"] for opt in res_ok["options"])

# 10. Test Custom Food Analyze Zero Division & Sodium
def test_custom_food_analysis():
    # Trường hợp hợp lệ
    res_valid = client.post("/api/analyze/custom-food", json={
        "food_name": "Trà sữa trân châu",
        "calories": 450.0,
        "protein_g": 3.0,
        "fat_g": 12.0,
        "estimated_cost_vnd": 45000.0,
        "sodium_mg": 350.0,
        "daily_target_calories": 2000.0,
        "daily_budget_vnd": 80000.0
    })
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["cal_percent_of_daily_target"] == 22.5
    assert data["sodium_mg"] == 350.0

    # Chặn daily_target_calories <= 0 bằng schema validation
    res_zero = client.post("/api/analyze/custom-food", json={
        "food_name": "Test Zero",
        "calories": 200.0,
        "protein_g": 10.0,
        "fat_g": 5.0,
        "estimated_cost_vnd": 20000.0,
        "daily_target_calories": 0.0,
        "daily_budget_vnd": 50000.0
    })
    assert res_zero.status_code == 422, "Phải chặn calo mục tiêu <= 0 để tránh ZeroDivisionError"

# 11. Test 100% Price Coverage (No Fallback)
def test_all_foods_have_prices():
    conn = sqlite3.connect("database/nutridss.db")
    import pandas as pd
    df_f = pd.read_sql_query("SELECT id, canonical_name_vi FROM foods", conn)
    df_p = pd.read_sql_query("SELECT food_id, estimated_price_per_100g FROM food_price_summary", conn)
    conn.close()
    
    missing = df_f[~df_f['id'].isin(df_p['food_id'])]
    assert len(missing) == 0, f"Còn {len(missing)} thực phẩm bị thiếu giá: {missing['canonical_name_vi'].tolist()}"

# 12. Test User Registration, Password Hashing & Authentication
def test_auth_and_security():
    # Register test user
    test_email = "testuser_v2@nutridss.vn"
    res_reg = client.post("/api/auth/register", json={
        "email": test_email,
        "username": "testuser_v2",
        "password": "SecurePassword@123"
    })
    # Accept 200 or 400 if user already registered in previous run
    assert res_reg.status_code in (200, 400)
    
    # Login with wrong password
    res_wrong = client.post("/api/auth/login", json={
        "username": "testuser_v2",
        "password": "WrongPassword!"
    })
    assert res_wrong.status_code == 401
    
    # Login with correct password
    res_ok = client.post("/api/auth/login", json={
        "username": "testuser_v2",
        "password": "SecurePassword@123"
    })
    assert res_ok.status_code == 200
    token = res_ok.json()["access_token"]
    
    # Access protected profile
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "testuser_v2"

# 13. Test Weekly Meal Plan Generation
def test_weekly_meal_plan_api():
    res = client.post("/api/meal-plans/weekly", json={
        "health_goal": "LOSE_WEIGHT",
        "daily_budget_vnd": 75000.0,
        "allergies": []
    })
    assert res.status_code == 200
    data = res.json()
    assert data["days_count"] == 7
    assert len(data["days"]) == 7
    assert data["weekly_budget_vnd"] == 75000.0 * 7

# 14. Test Portion Scaling
def test_portion_scaling_api():
    res = client.post("/api/meal-plans/scale-portion", json={
        "recipe_id": 1001,
        "multiplier": 1.5
    })
    assert res.status_code == 200
    scaled = res.json()
    assert scaled["portion_multiplier"] == 1.5
    assert scaled["calories"] > 0

# 15. Test Real User Feedback Tracking
def test_user_feedback_api():
    res = client.post("/api/feedback", json={
        "recipe_id": 1001,
        "event_type": "FAVORITE",
        "rating": 5.0,
        "session_id": "sess_test_123"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "success"

# 16. Test 30+ Nutrients & WHO Guidelines APIs
def test_guidelines_and_nutrients_api():
    res_g = client.get("/api/guidelines")
    assert res_g.status_code == 200
    assert len(res_g.json()["rules"]) >= 5

    res_n = client.get("/api/nutrients")
    assert res_n.status_code == 200
    assert len(res_n.json()) >= 30, "Phải có đủ bộ 30+ tiêu chí dinh dưỡng theo Fix.md"
