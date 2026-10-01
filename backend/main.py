"""
NutriDSS - FastAPI Main Application & Web Entrypoint
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List
import os
import sqlite3
import pandas as pd

from backend.schemas.dss_schemas import (
    ProfileCalculateRequest,
    MealPlanGenerateRequest,
    ReplaceItemRequest,
    CustomFoodAnalyzeRequest
)
from backend.services.nutrition_service import NutritionService
from backend.services.recommender_service import RecommenderService
from backend.services.meal_optimizer import MealOptimizer

app = FastAPI(
    title="NutriDSS - Decision Support System API",
    description="Hệ hỗ trợ ra quyết định dinh dưỡng cá nhân hóa dựa trên ML & Tối ưu hóa ngân sách",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

optimizer = MealOptimizer()
recommender = RecommenderService()
DB_PATH = "database/nutridss.db"

# ---------------------------------------------------------
# 1. FRONTEND DASHBOARD ROUTE
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = "frontend/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NutriDSS API Service is Running!</h1>"

# ---------------------------------------------------------
# 2. PROFILE & NUTRITION TARGETS API
# ---------------------------------------------------------
@app.post("/api/profile/calculate", summary="Tính chỉ số BMI, BMR, TDEE và Lời khuyên mục tiêu sức khỏe")
def calculate_user_targets(req: ProfileCalculateRequest):
    bmi_info = NutritionService.calculate_bmi(req.weight_kg, req.height_cm)
    bmr = NutritionService.calculate_bmr(req.gender, req.weight_kg, req.height_cm, req.age)
    tdee = NutritionService.calculate_tdee(bmr, req.activity_level)
    target_cal = NutritionService.calculate_target_calories(tdee, req.health_goal)
    macros = NutritionService.calculate_macro_targets(target_cal, req.health_goal)
    
    advice_res = NutritionService.generate_goal_advice(
        req.health_goal, 
        req.goal_target_value or 0, 
        req.weight_kg
    )
    
    return {
        "display_name": req.display_name,
        "bmi_info": bmi_info,
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "target_calories": macros["daily_calories"],
        "target_protein_g": macros["target_protein_g"],
        "target_carb_g": macros["target_carb_g"],
        "target_fat_g": macros["target_fat_g"],
        "goal_advice": advice_res["advice"],
        "goal_warnings": advice_res["warnings"],
        "allergies": req.allergies or []
    }

# ---------------------------------------------------------
# 3. MEAL PLAN GENERATION API
# ---------------------------------------------------------
@app.post("/api/meal-plans/generate", summary="Sinh 3 phương án thực đơn ngày (A, B, C)")
def generate_meal_plan(req: MealPlanGenerateRequest):
    try:
        res = optimizer.generate_daily_plan_options(
            req.health_goal, 
            req.daily_budget_vnd, 
            req.allergies,
            target_calories=req.target_calories,
            target_protein_g=req.target_protein_g,
            target_carb_g=req.target_carb_g,
            target_fat_g=req.target_fat_g
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

# ---------------------------------------------------------
# 4. REPLACEMENT ENGINE API
# ---------------------------------------------------------
@app.post("/api/meal-plans/replace-item", summary="Đổi món thông minh")
def replace_recipe_item(req: ReplaceItemRequest):
    try:
        replacements = optimizer.replace_meal_item(
            req.current_recipe_id, 
            req.health_goal, 
            req.budget_vnd, 
            req.allergies,
            remaining_budget_vnd=req.remaining_budget_vnd,
            target_protein_g=req.target_protein_g,
            target_calories=req.target_calories
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"current_recipe_id": req.current_recipe_id, "replacement_options": replacements}

# ---------------------------------------------------------
# 5. USER CUSTOM FOOD EVALUATOR API
# ---------------------------------------------------------
@app.post("/api/analyze/custom-food", summary="Đánh giá món tự nhập & tư vấn bù trừ")
def analyze_custom_food(req: CustomFoodAnalyzeRequest):
    res = optimizer.evaluate_user_selected_food(
        req.food_name,
        req.calories,
        req.protein_g,
        req.fat_g,
        req.estimated_cost_vnd,
        req.daily_target_calories,
        req.daily_budget_vnd,
        sodium_mg=req.sodium_mg or 400.0
    )
    return res

# ---------------------------------------------------------
# 6. FOOD & ALLERGEN SEARCH AUTOCOMPLETE API
# ---------------------------------------------------------
@app.get("/api/allergens/search", summary="Tìm kiếm thực phẩm dị ứng tự động theo từ khóa")
def search_allergens(q: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if q:
        query = "SELECT * FROM allergens WHERE name_vi LIKE ? OR code LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{q}%", f"%{q}%"])
    else:
        df = pd.read_sql_query("SELECT * FROM allergens", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/foods", summary="Tra cứu danh mục thực phẩm hạt nhân")
def get_foods(q: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if q:
        query = "SELECT * FROM foods WHERE canonical_name_vi LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{q}%"])
    else:
        df = pd.read_sql_query("SELECT * FROM foods", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/recipes", summary="Tra cứu danh mục món ăn & công thức")
def get_recipes(q: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    if q:
        query = "SELECT * FROM recipes WHERE name_vi LIKE ? OR tags LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{q}%", f"%{q}%"])
    else:
        df = pd.read_sql_query("SELECT * FROM recipes", conn)
    conn.close()
    return df.to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
