"""
NutriDSS - Rule Engine
Xử lý Ràng buộc cứng (Hard Constraints - Loại bỏ 100% dị ứng)
và Ràng buộc mềm (Soft Constraints - Đánh giá cảnh báo Dinh dưỡng theo Chuẩn WHO)
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any

DB_PATH = "database/nutridss.db"

class RuleEngine:
    @staticmethod
    def get_valid_allergen_codes() -> List[str]:
        """Lấy toàn bộ danh sách mã dị ứng hợp lệ được hỗ trợ trong cơ sở dữ liệu"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT code FROM allergens")
        rows = cursor.fetchall()
        conn.close()
        return [r[0].upper() for r in rows]

    @staticmethod
    def get_user_allergen_ids(user_allergy_codes: List[str]) -> List[int]:
        """
        Lấy danh sách allergen_id bị cấm từ mã code dị ứng.
        Bảo đảm an toàn y tế (Hard Constraint): Bất kỳ mã dị ứng lạ nào chưa được định nghĩa
        đều BẮT BUỘC phải bị từ chối thay vì âm thầm bỏ qua.
        """
        if not user_allergy_codes:
            return []
        
        clean_codes = [c.strip().upper() for c in user_allergy_codes if c and c.strip()]
        if not clean_codes:
            return []

        valid_codes = RuleEngine.get_valid_allergen_codes()
        unknown_codes = [c for c in clean_codes if c not in valid_codes]
        if unknown_codes:
            raise ValueError(
                f"Phát hiện mã dị ứng không xác định hoặc chưa được hỗ trợ: {', '.join(unknown_codes)}. "
                f"Vì lý do an toàn y tế nghiêm ngặt (Hard Constraint), hệ thống không thể xây dựng thực đơn "
                f"khi có chất dị ứng chưa được kiểm chứng trong cơ sở dữ liệu."
            )

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in clean_codes)
        cursor.execute(f"SELECT id FROM allergens WHERE code IN ({placeholders})", clean_codes)
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    @staticmethod
    def filter_hard_constraints(recipes: List[Dict[str, Any]], user_allergy_codes: List[str]) -> List[Dict[str, Any]]:
        """
        Hard Constraint: Loại bỏ hoàn toàn 100% các công thức chứa nguyên liệu dị ứng của người dùng.
        Không cho phép bất kỳ ngoại lệ nào.
        """
        allergen_ids = RuleEngine.get_user_allergen_ids(user_allergy_codes)
        if not allergen_ids:
            return recipes
            
        conn = sqlite3.connect(DB_PATH)
        placeholders = ','.join('?' for _ in allergen_ids)
        # Tìm danh sách food_id chứa allergen
        query = f"SELECT DISTINCT food_id FROM food_allergens WHERE allergen_id IN ({placeholders})"
        forbidden_foods = pd.read_sql_query(query, conn, params=allergen_ids)['food_id'].tolist()
        
        if not forbidden_foods:
            conn.close()
            return recipes
            
        # Tìm danh sách recipe_id chứa forbidden_foods
        placeholders_food = ','.join('?' for _ in forbidden_foods)
        query_recipe = f"SELECT DISTINCT recipe_id FROM recipe_ingredients WHERE food_id IN ({placeholders_food})"
        forbidden_recipes = pd.read_sql_query(query_recipe, conn, params=forbidden_foods)['recipe_id'].tolist()
        conn.close()
        
        valid_recipes = [r for r in recipes if r['id'] not in forbidden_recipes]
        return valid_recipes

    @staticmethod
    def evaluate_health_warnings(meal_item: Dict[str, Any], daily_target_calories: float) -> List[str]:
        """
        Soft Constraint: Cảnh báo sức khỏe chuẩn WHO
        - Natri > 2000mg/ngày (hoặc > 800mg/bữa)
        - Năng lượng bữa ăn vượt 45% tổng calo ngày
        - Đường tự do > 10% năng lượng
        - Chất béo bão hòa cao
        """
        warnings = []
        safe_daily_cal = daily_target_calories if daily_target_calories and daily_target_calories > 0 else 1800.0
        target_meal_cal = safe_daily_cal / 3.0
        
        calories = meal_item.get('calories', 0)
        fat_g = meal_item.get('fat_g', 0)
        sugar_g = meal_item.get('sugar_g', 0)
        sodium_mg = meal_item.get('sodium_mg', 0)
        
        # Cảnh báo Calo
        if calories > target_meal_cal * 1.35:
            warnings.append(f"⚠️ Năng lượng bữa ăn ({calories:.0f} Kcal) cao hơn mức khuyến nghị cho 1 bữa ({target_meal_cal:.0f} Kcal).")
            
        # Cảnh báo Đường tự do (WHO Guideline: < 10% total calories)
        sugar_calories = sugar_g * 4.0
        if calories > 0 and (sugar_calories / calories) > 0.15:
            warnings.append("⚠️ Hàm lượng đường tự do trong món ăn khá cao. Nên tiết chế nếu có mục tiêu kiểm soát cân nặng.")
            
        # Cảnh báo Chất béo
        fat_calories = fat_g * 9.0
        if calories > 0 and (fat_calories / calories) > 0.35:
            warnings.append("⚠️ Tỷ lệ năng lượng từ chất béo tương đối cao. Cân nhắc giảm dầu mỡ khi chế biến.")
            
        # Cảnh báo Natri/Muối (WHO Guideline: < 2000mg/day -> ~700mg/bữa)
        if sodium_mg > 700:
            warnings.append("⚠️ Hàm lượng Natri (Muối) trong khẩu phần khá cao. Nên uống đủ nước và giảm mặn bữa kế tiếp.")
            
        return warnings
