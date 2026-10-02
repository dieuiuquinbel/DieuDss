"""
NutriDSS - Pydantic Request & Response Schemas V2
Contains rigorous input validation, bounds, authentication, feedback, and weekly planner schemas.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import re

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=100, description="Email người dùng")
    username: str = Field(..., min_length=3, max_length=50, description="Tên đăng nhập")
    password: str = Field(..., min_length=6, max_length=72, description="Mật khẩu bảo mật")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str):
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Email không đúng định dạng.")
        return v

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Tên đăng nhập hoặc email")
    password: str = Field(..., min_length=1, max_length=72, description="Mật khẩu")

class ProfileCalculateRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100, description="Tên hiển thị người dùng")
    gender: str = Field(..., description="Giới tính: MALE/NAM hoặc FEMALE/NỮ")
    weight_kg: float = Field(..., gt=10.0, le=300.0, description="Cân nặng hiện tại (kg), phải từ 10 - 300 kg")
    height_cm: float = Field(..., gt=50.0, le=250.0, description="Chiều cao (cm), phải từ 50 - 250 cm")
    age: int = Field(..., ge=1, le=120, description="Tuổi, phải từ 1 - 120")
    activity_level: str = Field(..., description="Mức độ vận động (SEDENTARY, LIGHTLY_ACTIVE, MODERATE, VERY_ACTIVE, EXTRA_ACTIVE)")
    health_goal: str = Field(..., description="Mục tiêu sức khỏe (LOSE_WEIGHT, GAIN_WEIGHT, HIGH_PROTEIN, GROWTH, BALANCED)")
    goal_target_value: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Lượng cân tăng/giảm hoặc chiều cao, tuyệt đối không âm (>= 0)")
    allergies: Optional[List[str]] = Field(default=[], description="Danh sách mã dị ứng")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str):
        valid = ["MALE", "FEMALE", "NAM", "NỮ", "NU", "OTHER"]
        if v.upper().strip() not in valid:
            raise ValueError(f"Giới tính không hợp lệ: '{v}'. Chấp nhận: MALE, FEMALE, NAM, NỮ.")
        return v.upper().strip()

    @field_validator("activity_level")
    @classmethod
    def validate_activity_level(cls, v: str):
        valid = ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATE", "VERY_ACTIVE", "EXTRA_ACTIVE"]
        if v.upper().strip() not in valid:
            raise ValueError(f"Mức độ vận động không hợp lệ: '{v}'. Chấp nhận: {', '.join(valid)}.")
        return v.upper().strip()

    @field_validator("health_goal")
    @classmethod
    def validate_health_goal(cls, v: str):
        valid = [
            "LOSE_WEIGHT", "GAIN_WEIGHT", "HIGH_PROTEIN", "GROWTH", "BALANCED", "MAINTAIN",
            "GIẢM CÂN", "TĂNG CÂN", "TĂNG CƠ", "TĂNG CHIỀU CAO", "DUY TRÌ"
        ]
        if v.upper().strip() not in valid:
            raise ValueError(f"Mục tiêu sức khỏe không hợp lệ: '{v}'. Chấp nhận: {', '.join(valid)}.")
        return v.upper().strip()

    @field_validator("goal_target_value", mode="before")
    @classmethod
    def ensure_non_negative_target(cls, v):
        if v is not None:
            return abs(float(v))
        return 0.0

class MealPlanGenerateRequest(BaseModel):
    health_goal: str = Field(..., description="Mục tiêu sức khỏe")
    daily_budget_vnd: float = Field(..., gt=0.0, le=5000000.0, description="Ngân sách ăn hàng ngày phải > 0 VNĐ")
    allergies: Optional[List[str]] = Field(default=[], description="Danh sách mã dị ứng")
    target_calories: Optional[float] = Field(default=None, gt=500.0, le=10000.0, description="Mục tiêu calo từ hồ sơ cá nhân")
    target_protein_g: Optional[float] = Field(default=None, ge=0.0, le=500.0, description="Mục tiêu protein từ hồ sơ")
    target_carb_g: Optional[float] = Field(default=None, ge=0.0, le=1000.0, description="Mục tiêu carb từ hồ sơ")
    target_fat_g: Optional[float] = Field(default=None, ge=0.0, le=500.0, description="Mục tiêu fat từ hồ sơ")
    is_vegetarian: Optional[bool] = Field(default=False, description="Chế độ ăn chay / ăn kiêng thuần thực vật")
    meal_structure: Optional[str] = Field(default="STANDARD", description="Kiểu cấu trúc bữa ăn: LIGHT, STANDARD, FULL, VEGETARIAN, CUSTOM")

    @field_validator("meal_structure")
    @classmethod
    def validate_meal_structure(cls, v: str):
        valid = ["LIGHT", "STANDARD", "FULL", "VEGETARIAN", "CUSTOM"]
        if v.upper().strip() not in valid:
            return "STANDARD"
        return v.upper().strip()

    @field_validator("health_goal")
    @classmethod
    def validate_goal(cls, v: str):
        valid = [
            "LOSE_WEIGHT", "GAIN_WEIGHT", "HIGH_PROTEIN", "GROWTH", "BALANCED", "MAINTAIN",
            "GIẢM CÂN", "TĂNG CÂN", "TĂNG CƠ", "TĂNG CHIỀU CAO", "DUY TRÌ"
        ]
        if v.upper().strip() not in valid:
            raise ValueError(f"Mục tiêu sức khỏe không hợp lệ: '{v}'.")
        return v.upper().strip()

class WeeklyPlanRequest(BaseModel):
    health_goal: str = Field(..., description="Mục tiêu sức khỏe")
    daily_budget_vnd: float = Field(..., gt=0.0, le=5000000.0, description="Ngân sách mỗi ngày")
    allergies: Optional[List[str]] = Field(default=[])
    target_calories: Optional[float] = Field(default=None, gt=500.0, le=10000.0)
    target_protein_g: Optional[float] = Field(default=None, ge=0.0, le=500.0)
    is_vegetarian: Optional[bool] = Field(default=False, description="Chế độ ăn chay cả tuần")

class ReplaceItemRequest(BaseModel):
    current_recipe_id: int = Field(..., gt=0, description="ID công thức món hiện tại cần thay")
    health_goal: str = Field(..., description="Mục tiêu sức khỏe")
    budget_vnd: float = Field(..., gt=0.0, le=5000000.0, description="Ngân sách cho bữa ăn phải > 0")
    allergies: Optional[List[str]] = Field(default=[])
    remaining_budget_vnd: Optional[float] = Field(default=None, ge=0.0, description="Ngân sách còn lại cho bữa này")
    target_calories: Optional[float] = Field(default=None, gt=0.0, description="Mục tiêu calo của bữa")
    target_protein_g: Optional[float] = Field(default=None, ge=0.0, description="Mục tiêu đạm của bữa")

class CustomFoodAnalyzeRequest(BaseModel):
    food_name: str = Field(..., min_length=1, max_length=200, description="Tên món ăn")
    calories: float = Field(..., ge=0.0, le=5000.0, description="Lượng calo (>= 0)")
    protein_g: float = Field(..., ge=0.0, le=500.0, description="Lượng protein (>= 0)")
    fat_g: float = Field(..., ge=0.0, le=500.0, description="Lượng chất béo (>= 0)")
    estimated_cost_vnd: float = Field(..., ge=0.0, le=10000000.0, description="Chi phí ước tính (>= 0)")
    sodium_mg: Optional[float] = Field(default=400.0, ge=0.0, le=10000.0, description="Hàm lượng natri (mg)")
    free_sugar_g: Optional[float] = Field(default=None, ge=0.0, le=500.0, description="Đường tự do (g)")
    saturated_fat_g: Optional[float] = Field(default=None, ge=0.0, le=500.0, description="Chất béo bão hòa (g)")
    daily_target_calories: float = Field(default=1800.0, gt=0.0, le=10000.0, description="Mục tiêu calo ngày")
    daily_budget_vnd: float = Field(default=70000.0, gt=0.0, le=10000000.0, description="Ngân sách ngày")

class UserFeedbackRequest(BaseModel):
    recipe_id: int = Field(..., gt=0, description="ID món ăn")
    food_id: Optional[int] = Field(default=None, description="ID thực phẩm (nếu có)")
    event_type: str = Field(..., description="VIEW, CLICK, ADD, KEEP, REPLACE, REMOVE, FAVORITE, DISLIKE, RATE")
    rating: Optional[float] = Field(default=None, ge=1.0, le=5.0, description="Đánh giá 1-5 sao")
    session_id: Optional[str] = Field(default=None, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(default={})

    @field_validator("event_type")
    @classmethod
    def validate_event(cls, v: str):
        valid = ["VIEW", "CLICK", "ADD", "KEEP", "REPLACE", "REMOVE", "FAVORITE", "DISLIKE", "RATE"]
        if v.upper().strip() not in valid:
            raise ValueError(f"Event type '{v}' không hợp lệ. Chấp nhận: {', '.join(valid)}")
        return v.upper().strip()

class PortionScaleRequest(BaseModel):
    recipe_id: int = Field(..., gt=0)
    multiplier: float = Field(default=1.0, ge=0.5, le=3.0, description="Hệ số khẩu phần (0.5x đến 3.0x)")

class SingleMealGenerateRequest(BaseModel):
    meal_type: str = Field(default="LUNCH", description="BREAKFAST, LUNCH, DINNER")
    budget_vnd: float = Field(default=35000.0, gt=0.0, le=1000000.0, description="Ngân sách cho 1 bữa ăn")
    health_goal: str = Field(default="BALANCED", description="Mục tiêu sức khỏe")
    allergies: Optional[List[str]] = Field(default=[])
    is_vegetarian: Optional[bool] = Field(default=False)
    structure_mode: Optional[str] = Field(default="STANDARD", description="LIGHT, STANDARD, FULL, VEGETARIAN")
    target_calories: Optional[float] = Field(default=None, gt=0.0, le=5000.0)

class MealPlanItemInput(BaseModel):
    recipe_id: int = Field(..., gt=0)
    day_of_week: Optional[str] = Field(default="Hôm nay")
    meal_type: str = Field(default="LUNCH")
    portion_multiplier: Optional[float] = Field(default=1.0)
    cost_vnd: Optional[float] = Field(default=0.0)
    calories: Optional[float] = Field(default=0.0)

class SaveMealPlanRequest(BaseModel):
    plan_name: str = Field(..., min_length=1, max_length=150, description="Tên thực đơn người dùng đặt")
    plan_type: str = Field(default="DAILY", description="DAILY, WEEKLY, SINGLE_MEAL")
    health_goal: str = Field(default="BALANCED")
    budget_vnd: float = Field(default=70000.0, ge=0.0)
    target_calories: Optional[float] = Field(default=1800.0)
    total_cost_vnd: float = Field(default=0.0, ge=0.0)
    total_calories: float = Field(default=0.0, ge=0.0)
    items: List[MealPlanItemInput] = Field(default=[])
