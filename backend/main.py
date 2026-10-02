"""
NutriDSS - FastAPI Main Application & Web Entrypoint V2
Architecture:
- Secure CORS (Specific Allowed Origins, No Dangerous Wildcard Credentials)
- Rate Limiting Protection (DoS Prevention)
- JWT Authentication & RBAC Authorization (User, Admin)
- Relational 30+ Nutrients Engine & WHO Guidelines
- Real User Feedback Tracking Loop
- Decision Support System (Daily Options, Weekly Planning, Portion Scaling, Smart Replacement)
"""

from fastapi import FastAPI, HTTPException, Depends, Request, status, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional, List, Dict, Any
import os
import json
import sqlite3
import pandas as pd

from backend.core.config import settings
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_optional,
    get_current_user_required
)
from backend.core.rate_limiter import limiter
from backend.schemas.dss_schemas import (
    RegisterRequest,
    LoginRequest,
    ProfileCalculateRequest,
    MealPlanGenerateRequest,
    WeeklyPlanRequest,
    ReplaceItemRequest,
    CustomFoodAnalyzeRequest,
    UserFeedbackRequest,
    PortionScaleRequest,
    SingleMealGenerateRequest,
    SaveMealPlanRequest
)
from backend.services.nutrition_service import NutritionService
from backend.services.recommender_service import RecommenderService
from backend.services.meal_optimizer import MealOptimizer
from backend.services.rule_engine import RuleEngine
from backend.services.ingredient_cost_engine import IngredientCostEngine
from backend.services.recipe_service import RecipeService
from backend.services.food_vision_service import FoodVisionService

app = FastAPI(
    title="NutriDSS - Decision Support System API V2",
    description="Hệ hỗ trợ ra quyết định dinh dưỡng cá nhân hóa dựa trên ML, Chuẩn WHO & Tối ưu hóa ngân sách",
    version="2.0.0"
)

# ---------------------------------------------------------
# 1. SECURITY HARDENED CORS MIDDLEWARE
# ---------------------------------------------------------
# Prohibit allow_origins=["*"] when allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

cost_engine = IngredientCostEngine()
recipe_service = RecipeService()
vision_service = FoodVisionService()
optimizer = MealOptimizer()
recommender = RecommenderService()
DB_PATH = "database/nutridss.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------------
# 2. FRONTEND DASHBOARD
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = "frontend/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>NutriDSS API Service V2 is Running!</h1>"

# ---------------------------------------------------------
# 3. AUTHENTICATION & USER MANAGEMENT API
# ---------------------------------------------------------
@app.post("/api/auth/register", summary="Đăng ký tài khoản người dùng mới")
def register_user(req: RegisterRequest, request: Request):
    limiter.check(request, custom_limit=20)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check existing email or username
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (req.email, req.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email hoặc tên đăng nhập đã tồn tại trong hệ thống."
        )

    pwd_hash = hash_password(req.password)
    cursor.execute("""
        INSERT INTO users (email, username, password_hash, role)
        VALUES (?, ?, ?, 'USER')
    """, (req.email, req.username, pwd_hash))
    user_id = cursor.lastrowid

    # Initialize empty profile
    cursor.execute("""
        INSERT INTO user_profiles (user_id, display_name, health_goal, daily_budget_vnd)
        VALUES (?, ?, 'BALANCED', 70000.0)
    """, (user_id, req.username))
    
    conn.commit()
    conn.close()

    token = create_access_token({"sub": str(user_id), "username": req.username, "role": "USER"})
    return {
        "message": "Đăng ký tài khoản thành công!",
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": req.username, "email": req.email, "role": "USER"}
    }

@app.post("/api/auth/login", summary="Đăng nhập nhận Access Token")
def login_user(req: LoginRequest, request: Request):
    limiter.check(request, custom_limit=30)
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, username, password_hash, role FROM users WHERE username = ? OR email = ?", (req.username, req.username))
    row = cursor.fetchone()
    conn.close()

    if not row or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác."
        )

    token = create_access_token({"sub": str(row["id"]), "username": row["username"], "role": row["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "role": row["role"]
        }
    }

@app.get("/api/auth/me", summary="Lấy thông tin tài khoản hiện tại")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user_required)):
    user_id = int(user["sub"])
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.email, u.username, u.role, p.display_name, p.age, p.gender, 
               p.height_cm, p.weight_kg, p.activity_level, p.health_goal, p.daily_budget_vnd
        FROM users u
        LEFT JOIN user_profiles p ON u.id = p.user_id
        WHERE u.id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin người dùng.")
    return dict(row)

# ---------------------------------------------------------
# 4. PROFILE & NUTRITION TARGETS API
# ---------------------------------------------------------
@app.post("/api/profile/calculate", summary="Tính chỉ số BMI, BMR, TDEE và Lời khuyên mục tiêu sức khỏe")
def calculate_user_targets(req: ProfileCalculateRequest, request: Request):
    limiter.check(request, custom_limit=60)
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
# 5. MEAL PLAN GENERATION API (DAILY & WEEKLY)
# ---------------------------------------------------------
@app.post("/api/meal-plans/generate", summary="Sinh 3 phương án thực đơn ngày (A, B, C)")
def generate_meal_plan(req: MealPlanGenerateRequest, request: Request):
    limiter.check(request, custom_limit=30)
    try:
        res = optimizer.generate_daily_plan_options(
            req.health_goal, 
            req.daily_budget_vnd, 
            req.allergies,
            target_calories=req.target_calories,
            target_protein_g=req.target_protein_g,
            target_carb_g=req.target_carb_g,
            target_fat_g=req.target_fat_g,
            is_vegetarian=bool(req.is_vegetarian),
            meal_structure=req.meal_structure or "STANDARD"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/meal-plans/weekly", summary="Sinh kế hoạch thực đơn 7 ngày đa dạng món ăn")
def generate_weekly_meal_plan(req: WeeklyPlanRequest, request: Request):
    limiter.check(request, custom_limit=20)
    try:
        res = optimizer.generate_weekly_plan(
            goal=req.health_goal,
            daily_budget_vnd=req.daily_budget_vnd,
            user_allergies=req.allergies,
            target_calories=req.target_calories,
            target_protein_g=req.target_protein_g
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/meal-plans/scale-portion", summary="Điều chỉnh tỷ lệ khẩu phần ăn")
def scale_meal_portion(req: PortionScaleRequest):
    all_recipes = recommender.get_all_recipes_with_nutrition_and_cost()
    rec = next((r for r in all_recipes if r["id"] == req.recipe_id), None)
    if not rec:
        raise HTTPException(status_code=404, detail="Không tìm thấy món ăn.")
    scaled = optimizer.scale_meal_portion(rec, req.multiplier)
    return scaled

@app.post("/api/meal-plans/single-meal", summary="Sinh mâm cơm chuẩn Việt cho 1 bữa lẻ (Sáng, Trưa, Tối)")
def generate_single_meal(req: SingleMealGenerateRequest, request: Request):
    limiter.check(request, custom_limit=30)
    try:
        res = optimizer.generate_single_meal(
            meal_type=req.meal_type,
            budget_vnd=req.budget_vnd,
            goal=req.health_goal,
            user_allergies=req.allergies,
            is_vegetarian=bool(req.is_vegetarian),
            structure_mode=req.structure_mode or "STANDARD",
            target_calories=req.target_calories
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/meal-plans/save", summary="Lưu thực đơn vào danh sách của tôi")
def save_meal_plan(req: SaveMealPlanRequest, user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    user_id = int(user["sub"]) if user and "sub" in user else 1
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meal_plans (user_id, plan_name, plan_type, budget_vnd, health_goal, target_calories, total_cost_vnd, total_calories)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        req.plan_name,
        req.plan_type,
        req.budget_vnd,
        req.health_goal,
        req.target_calories,
        req.total_cost_vnd,
        req.total_calories
    ))
    plan_id = cursor.lastrowid

    for it in req.items:
        cursor.execute("""
            INSERT INTO meal_plan_items (meal_plan_id, recipe_id, day_of_week, meal_type, portion_multiplier, selected_by, cost_vnd, calories)
            VALUES (?, ?, ?, ?, ?, 'USER', ?, ?)
        """, (
            plan_id,
            it.recipe_id,
            it.day_of_week or "Hôm nay",
            it.meal_type,
            it.portion_multiplier or 1.0,
            it.cost_vnd or 0.0,
            it.calories or 0.0
        ))

    conn.commit()
    conn.close()
    return {"status": "success", "message": "Đã lưu thực đơn thành công!", "plan_id": plan_id}

@app.get("/api/meal-plans", summary="Lấy danh sách các thực đơn đã lưu")
def get_saved_meal_plans(user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mp.*, COUNT(mpi.id) as item_count
        FROM meal_plans mp
        LEFT JOIN meal_plan_items mpi ON mp.id = mpi.meal_plan_id
        GROUP BY mp.id
        ORDER BY mp.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/api/meal-plans/{plan_id}", summary="Lấy chi tiết thực đơn đã lưu kèm danh sách món, nguyên liệu & cách nấu")
def get_saved_meal_plan_detail(plan_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meal_plans WHERE id = ?", (plan_id,))
    plan_row = cursor.fetchone()
    if not plan_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Không tìm thấy thực đơn.")

    plan_data = dict(plan_row)

    cursor.execute("""
        SELECT mpi.*, r.name_vi, r.image_url, r.dish_role, r.cook_time_min, r.prep_time_min,
               r.description
        FROM meal_plan_items mpi
        LEFT JOIN recipes r ON mpi.recipe_id = r.id
        WHERE mpi.meal_plan_id = ?
        ORDER BY mpi.id ASC
    """, (plan_id,))
    items_rows = cursor.fetchall()
    conn.close()

    items = []
    for row in items_rows:
        it = dict(row)
        recipe_detail = recipe_service.get_recipe_details(it["recipe_id"])
        it["recipe_detail"] = recipe_detail
        items.append(it)

    plan_data["items"] = items
    return plan_data

@app.delete("/api/meal-plans/{plan_id}", summary="Xóa thực đơn đã lưu")
def delete_saved_meal_plan(plan_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meal_plan_items WHERE meal_plan_id = ?", (plan_id,))
    cursor.execute("DELETE FROM meal_plans WHERE id = ?", (plan_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Đã xóa thực đơn thành công."}

@app.post("/api/meal-plans/{plan_id}/apply", summary="Áp dụng thực đơn cho ngày hôm nay")
def apply_saved_meal_plan(plan_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meal_plans WHERE id = ?", (plan_id,))
    plan_row = cursor.fetchone()
    conn.close()
    if not plan_row:
        raise HTTPException(status_code=404, detail="Không tìm thấy thực đơn.")
    return {"status": "success", "message": f"Đã áp dụng thực đơn '{plan_row['plan_name'] or plan_id}' cho hôm nay!"}

# ---------------------------------------------------------
# 6. REPLACEMENT ENGINE API
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
# 7. USER CUSTOM FOOD EVALUATOR API
# ---------------------------------------------------------
@app.post("/api/analyze/custom-food", summary="Đánh giá món tự nhập & tư vấn bù trừ")
def analyze_custom_food(req: CustomFoodAnalyzeRequest, request: Request):
    limiter.check(request, custom_limit=30)
    res = optimizer.evaluate_user_selected_food(
        req.food_name,
        req.calories,
        req.protein_g,
        req.fat_g,
        req.estimated_cost_vnd,
        req.daily_target_calories,
        req.daily_budget_vnd,
        sodium_mg=req.sodium_mg or 400.0,
        free_sugar_g=req.free_sugar_g,
        saturated_fat_g=req.saturated_fat_g
    )
    return res

# ---------------------------------------------------------
# 8. REAL USER FEEDBACK & INTERACTION TRACKING
# ---------------------------------------------------------
@app.post("/api/feedback", summary="Ghi nhận phản hồi và hành vi người dùng (Feedback Loop)")
def record_user_feedback(
    req: UserFeedbackRequest, 
    user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = int(user["sub"]) if user and "sub" in user else None
    
    cursor.execute("""
        INSERT INTO user_interactions (user_id, recipe_id, food_id, event_type, rating, session_id, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, 
        req.recipe_id, 
        req.food_id, 
        req.event_type, 
        req.rating, 
        req.session_id, 
        json.dumps(req.metadata or {}, ensure_ascii=False)
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Đã ghi nhận tương tác '{req.event_type}'."}

def df_to_clean_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Converts a pandas DataFrame to dict records replacing all NaN with None for strict JSON compliance."""
    return [{k: (None if pd.isna(v) else v) for k, v in row.items()} for row in df.to_dict(orient="records")]

# ---------------------------------------------------------
# 9. WHO GUIDELINES & 30+ NUTRIENT CRITERIA APIs
# ---------------------------------------------------------
@app.get("/api/guidelines", summary="Tra cứu danh mục quy chuẩn khuyến nghị dinh dưỡng WHO & Bộ Y Tế")
def get_guidelines():
    conn = get_db_connection()
    df_sources = pd.read_sql_query("SELECT * FROM guideline_sources", conn)
    df_rules = pd.read_sql_query("SELECT * FROM guideline_rules", conn)
    conn.close()
    return {
        "sources": df_to_clean_records(df_sources),
        "rules": df_to_clean_records(df_rules)
    }

@app.get("/api/nutrients", summary="Tra cứu 30+ tiêu chí dinh dưỡng chuẩn hóa")
def get_nutrients_master():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM nutrients ORDER BY id ASC", conn)
    conn.close()
    return df_to_clean_records(df)

# ---------------------------------------------------------
# 10. CATALOG & SEARCH AUTOCOMPLETE APIs
# ---------------------------------------------------------
@app.get("/api/allergens/search", summary="Tìm kiếm thực phẩm dị ứng tự động theo từ khóa")
def search_allergens(q: Optional[str] = None):
    conn = get_db_connection()
    if q:
        query = "SELECT * FROM allergens WHERE name_vi LIKE ? OR code LIKE ?"
        df = pd.read_sql_query(query, conn, params=[f"%{q}%", f"%{q}%"])
    else:
        df = pd.read_sql_query("SELECT * FROM allergens", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/api/foods", summary="Tra cứu danh mục thực phẩm hạt nhân")
def get_foods(q: Optional[str] = None):
    conn = get_db_connection()
    if q:
        query = """
            SELECT DISTINCT f.* FROM foods f
            LEFT JOIN food_aliases a ON f.id = a.food_id
            WHERE f.canonical_name_vi LIKE ? OR a.raw_name LIKE ? OR a.normalized_name LIKE ?
            LIMIT 100
        """
        df = pd.read_sql_query(query, conn, params=[f"%{q}%", f"%{q}%", f"%{q.lower()}%"])
    else:
        df = pd.read_sql_query("SELECT * FROM foods LIMIT 100", conn)
    conn.close()
    return df_to_clean_records(df)

@app.get("/api/recipes", summary="Tra cứu danh mục món ăn & công thức")
def get_recipes(
    q: Optional[str] = None,
    dish_role: Optional[str] = None,
    is_vegetarian: Optional[int] = None,
    limit: Optional[int] = 120
):
    all_recs = recommender.get_all_recipes_with_nutrition_and_cost()
    results = all_recs
    if q:
        q_low = q.lower()
        results = [r for r in results if q_low in r['name_vi'].lower() or q_low in (r.get('tags') or '').lower() or q_low in (r.get('description') or '').lower()]
    if dish_role:
        results = [r for r in results if r.get('dish_role') == dish_role]
    if is_vegetarian is not None:
        results = [r for r in results if int(r.get('is_vegetarian', 0)) == is_vegetarian]
    
    # Ưu tiên các món CURATED_VN_MASTER lên đầu
    results = sorted(
        results,
        key=lambda x: (
            0 if x.get('source_name') == 'CURATED_VN_MASTER' else 1,
            -x.get('calories', 0)
        )
    )
    if limit and limit > 0:
        results = results[:limit]
    return results

@app.get("/api/recipes/{recipe_id}", summary="Lấy chi tiết món ăn kèm các bước nấu và bóc tách chi phí siêu thị")
def get_recipe_detail(recipe_id: int):
    detail = recipe_service.get_recipe_details(recipe_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Không tìm thấy món ăn.")
    
    cb = detail.get("cost_breakdown", {})
    nutr = detail.get("nutrition", {})
    detail["calculated_cost_vnd"] = cb.get("total_cost_vnd", 0)
    detail["calculated_calories"] = nutr.get("calories", 0)
    detail["calculated_protein_g"] = nutr.get("protein_g", 0)
    detail["calculated_carb_g"] = nutr.get("carb_g", 0)
    detail["calculated_fat_g"] = nutr.get("fat_g", 0)
    detail["ingredients"] = [
        {
            "canonical_name_vi": ing.get("name_vi", ""),
            "quantity_g": ing.get("normalized_quantity_g", 0),
            "raw_quantity": ing.get("raw_quantity"),
            "raw_unit": ing.get("raw_unit"),
            "display_quantity": ing.get("display_quantity"),
            "ingredient_cost": ing.get("cost_vnd", 0),
            "price_info": ing.get("price_info", {})
        }
        for ing in cb.get("ingredients", [])
    ]
    return detail

@app.get("/api/recipes/{recipe_id}/cost-breakdown", summary="Bóc tách chi phí nguyên liệu & quan sát siêu thị (AEON, WinMart, GO!)")
def get_recipe_cost_breakdown(recipe_id: int):
    res = cost_engine.calculate_recipe_cost_breakdown(recipe_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

# ---------------------------------------------------------
# 11. FOOD VISION AI (MobileNetV3 / ONNX 103 DISHES)
# ---------------------------------------------------------
@app.get("/api/vision/classes", summary="Danh mục 103 món ăn Việt Nam mô hình AI hỗ trợ nhận diện")
def get_vision_classes():
    return vision_service.labels

@app.post("/api/vision/predict-food", summary="Nhận diện món ăn từ ảnh chụp (MobileNetV3/ONNX)")
async def predict_food_image(file: UploadFile = File(...)):
    if not (file.content_type and file.content_type.startswith("image/")):
        raise HTTPException(status_code=400, detail="Vui lòng tải lên định dạng file ảnh hợp lệ (JPG, PNG, WEBP).")
    
    image_bytes = await file.read()
    pred_res = vision_service.predict(image_bytes)
    if "error" in pred_res:
        raise HTTPException(status_code=400, detail=pred_res["error"])
    
    # Auto-match with Recipe Database
    pred_name = pred_res.get("predicted_label", "")
    matched_recipes = recipe_service.list_recipes(search_query=pred_name)
    if not matched_recipes:
        # Partial keyword match
        first_word = pred_name.split()[0] if pred_name else ""
        matched_recipes = recipe_service.list_recipes(search_query=first_word)
        
    matched_detail = None
    if matched_recipes:
        matched_detail = recipe_service.get_recipe_details(matched_recipes[0]["id"])
        
    return {
        "vision_result": pred_res,
        "matched_recipe": matched_detail
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
