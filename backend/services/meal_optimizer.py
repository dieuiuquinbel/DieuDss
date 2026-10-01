"""
NutriDSS - Meal Optimizer & DSS Decision Engine
- Đề xuất 3 Phương án Thực đơn (Option A - Tiết kiệm, Option B - Cân bằng, Option C - Cao đạm)
- Replacement Engine (Tính năng Đổi Món thông minh giữ nguyên calo & ngân sách)
- User Choice Evaluator (Tự thêm món và Phân tích Cảnh báo/Tư vấn điều chỉnh)
"""

from typing import List, Dict, Any
from backend.services.recommender_service import RecommenderService
from backend.services.rule_engine import RuleEngine

class MealOptimizer:
    def __init__(self):
        self.recommender = RecommenderService()

    def generate_daily_plan_options(
        self, 
        goal: str, 
        daily_budget_vnd: float, 
        user_allergies: List[str] = None,
        target_calories: float = None,
        target_protein_g: float = None,
        target_carb_g: float = None,
        target_fat_g: float = None
    ) -> Dict[str, Any]:
        """
        Sinh 3 phương án thực đơn cả ngày (Sáng, Trưa, Tối) đúng tinh thần DSS:
        - Ràng buộc cứng Ngân sách: Tổng chi phí các bữa ăn BẮT BUỘC <= daily_budget_vnd (nếu khả thi).
        - Tối ưu hóa Dinh dưỡng Cá nhân: Điều chỉnh theo target_calories & target_protein_g từ Hồ sơ người dùng.
        - 3 Phương án:
          + Phương án A (Tiết kiệm ngân sách tối đa)
          + Phương án B (Tối ưu điểm ML & Dinh dưỡng cân bằng cá nhân hóa)
          + Phương án C (Ưu tiên đạm & Đa dạng món)
        """
        meal_budget = daily_budget_vnd / 3.0
        
        bf_ranked = self.recommender.rank_recipes(goal, meal_budget, user_allergies, meal_type="BREAKFAST")
        lunch_ranked = self.recommender.rank_recipes(goal, meal_budget, user_allergies, meal_type="LUNCH")
        din_ranked = self.recommender.rank_recipes(goal, meal_budget, user_allergies, meal_type="DINNER")

        # Fallback nếu một trong các bữa không có món phù hợp (ví dụ do dị ứng lọc hết)
        if not bf_ranked or not lunch_ranked or not din_ranked:
            return {"error": "Không tìm thấy món ăn phù hợp với các ràng buộc dị ứng của bạn cho đủ 3 bữa."}

        # Tạo tất cả các tổ hợp (Breakfast, Lunch, Dinner)
        all_combos = []
        for bf in bf_ranked:
            for lunch in lunch_ranked:
                for din in din_ranked:
                    tot_cal = bf['calories'] + lunch['calories'] + din['calories']
                    tot_prot = bf['protein_g'] + lunch['protein_g'] + din['protein_g']
                    tot_carb = bf['carb_g'] + lunch['carb_g'] + din['carb_g']
                    tot_fat = bf['fat_g'] + lunch['fat_g'] + din['fat_g']
                    tot_cost = bf['estimated_cost_vnd'] + lunch['estimated_cost_vnd'] + din['estimated_cost_vnd']
                    avg_score = round((bf['score'] + lunch['score'] + din['score']) / 3.0, 2)
                    all_combos.append({
                        "bf": bf,
                        "lunch": lunch,
                        "din": din,
                        "total_calories": tot_cal,
                        "total_protein_g": tot_prot,
                        "total_carb_g": tot_carb,
                        "total_fat_g": tot_fat,
                        "total_cost_vnd": tot_cost,
                        "average_score": avg_score
                    })

        # Xử lý RÀNG BUỘC CỨNG NGÂN SÁCH (Budget Hard Constraint)
        min_possible_cost = min(c['total_cost_vnd'] for c in all_combos)
        feasible_combos = [c for c in all_combos if c['total_cost_vnd'] <= daily_budget_vnd]
        
        budget_exceeded = False
        budget_warning_msg = None
        
        if not feasible_combos:
            # Ngân sách người dùng đặt quá thấp so với chi phí tối thiểu của 3 món rẻ nhất
            budget_exceeded = True
            shortfall = min_possible_cost - daily_budget_vnd
            budget_warning_msg = (
                f"⚠️ **Ràng buộc ngân sách không khả thi:** Ngân sách {daily_budget_vnd:,.0f}đ/ngày "
                f"thấp hơn chi phí thực đơn 3 bữa tối thiểu khả thi ({min_possible_cost:,.0f}đ/ngày, thiếu hụt {shortfall:,.0f}đ). "
                f"NutriDSS đã tự động chọn các phương án tiết kiệm nhất có thể và khuyến nghị bạn điều chỉnh ngân sách tối thiểu đạt {min_possible_cost:,.0f}đ."
            )
            # Dùng all_combos làm tập ứng viên
            candidate_pool = all_combos
        else:
            # Ràng buộc cứng được đảm bảo: Tất cả phương án đề xuất đều BẮT BUỘC nằm trong ngân sách
            candidate_pool = feasible_combos

        # Option A: Budget Saver (Chi phí thấp nhất)
        opt_a = min(candidate_pool, key=lambda x: (x['total_cost_vnd'], -x['average_score']))

        # Option B: Balanced & Personalized Best (Cân bằng ML Score + Mục tiêu Dinh dưỡng Cá nhân)
        if target_calories and target_calories > 0:
            def balance_personal_score(c):
                cal_dev = abs(c['total_calories'] - target_calories) / target_calories
                cost_ratio = c['total_cost_vnd'] / daily_budget_vnd if daily_budget_vnd > 0 else 1.0
                return c['average_score'] - (1.5 * cal_dev) - (0.3 * cost_ratio)
            opt_b = max(candidate_pool, key=balance_personal_score)
        else:
            opt_b = max(candidate_pool, key=lambda x: (x['average_score'], -x['total_cost_vnd']))

        # Option C: High Protein Choice (Ưu tiên đạm cao nhất)
        opt_c = max(candidate_pool, key=lambda x: (x['total_protein_g'], x['average_score']))

        def build_option(name, desc, combo):
            bf = combo['bf']
            lunch = combo['lunch']
            din = combo['din']
            tot_cal = combo['total_calories']
            tot_prot = combo['total_protein_g']
            tot_cost = combo['total_cost_vnd']
            avg_score = combo['average_score']

            # Đánh giá % đạt mục tiêu dinh dưỡng cá nhân
            cal_achieve = round((tot_cal / target_calories) * 100, 1) if (target_calories and target_calories > 0) else None
            prot_achieve = round((tot_prot / target_protein_g) * 100, 1) if (target_protein_g and target_protein_g > 0) else None
            savings = round(daily_budget_vnd - tot_cost, 0)

            return {
                "option_name": name,
                "description": desc,
                "total_calories": round(float(tot_cal), 1),
                "total_protein_g": round(float(tot_prot), 1),
                "total_carb_g": round(float(combo['total_carb_g']), 1),
                "total_fat_g": round(float(combo['total_fat_g']), 1),
                "total_cost_vnd": round(float(tot_cost), 0),
                "average_score": float(avg_score),
                "is_within_budget": bool(tot_cost <= daily_budget_vnd),
                "budget_savings_vnd": float(savings) if savings > 0 else 0.0,
                "budget_over_vnd": float(abs(savings)) if savings < 0 else 0.0,
                "calorie_achievement_pct": float(cal_achieve) if cal_achieve is not None else None,
                "protein_achievement_pct": float(prot_achieve) if prot_achieve is not None else None,
                "meals": {
                    "breakfast": bf,
                    "lunch": lunch,
                    "dinner": din
                }
            }

        return {
            "daily_budget_target": float(daily_budget_vnd),
            "min_possible_daily_cost": float(min_possible_cost),
            "is_budget_strictly_feasible": bool(not budget_exceeded),
            "budget_warning": budget_warning_msg,
            "target_calories": float(target_calories) if target_calories else None,
            "target_protein_g": float(target_protein_g) if target_protein_g else None,
            "options": [
                build_option("Phương án A - Tiết kiệm ngân sách", "Tối ưu chi phí ăn uống thấp nhất, tuân thủ nghiêm ngặt ngân sách.", opt_a),
                build_option("Phương án B - Đề xuất DSS Cân bằng (Khuyên dùng)", "Phương án tối ưu toàn diện nhất về Dinh dưỡng cá nhân và Điểm số ML.", opt_b),
                build_option("Phương án C - Giàu Protein", "Tăng cường tối đa hàm lượng đạm trong phạm vi ngân sách cho phép.", opt_c)
            ]
        }

    def replace_meal_item(
        self, 
        current_recipe_id: int, 
        goal: str, 
        budget_vnd: float, 
        user_allergies: List[str] = None,
        remaining_budget_vnd: float = None,
        target_protein_g: float = None,
        target_calories: float = None
    ) -> List[Dict[str, Any]]:
        """
        Tính năng "Đổi món" thông minh:
        Tìm các món thay thế cùng bữa giữ tương đương Calo, Protein & Chi phí trong giới hạn ngân sách.
        """
        max_budget = remaining_budget_vnd if remaining_budget_vnd is not None and remaining_budget_vnd > 0 else budget_vnd
        all_ranked = self.recommender.rank_recipes(goal, max_budget, user_allergies)
        
        # Tìm món hiện tại
        current_item = next((r for r in all_ranked if r['id'] == current_recipe_id), None)
        if not current_item:
            # Nếu món hiện tại bị lọc vì dị ứng hoặc không tìm thấy, lấy top món cùng ngân sách
            return all_ranked[:3]
            
        m_type = current_item['meal_type']
        curr_cal = max(current_item['calories'], 1.0)
        curr_prot = max(current_item['protein_g'], 1.0)
        curr_cost = max(current_item['estimated_cost_vnd'], 1.0)
        
        # Lọc các món cùng meal_type ngoại trừ món hiện tại
        candidates = [r for r in all_ranked if r['meal_type'] == m_type and r['id'] != current_recipe_id]
        if not candidates:
            return []

        # Đánh giá đa tiêu chuẩn (Multi-objective score):
        # 1. Chênh lệch calo
        # 2. Chênh lệch protein
        # 3. Phù hợp chi phí (phạt nếu vượt quá ngân sách cho phép)
        # 4. Điểm ML compatibility
        for c in candidates:
            cal_diff = abs(c['calories'] - curr_cal)
            prot_diff = abs(c['protein_g'] - curr_prot)
            cost_diff = c['estimated_cost_vnd'] - curr_cost
            
            # Tỷ lệ sai lệch
            cal_err = cal_diff / curr_cal
            prot_err = prot_diff / curr_prot
            cost_penalty = max(0.0, (c['estimated_cost_vnd'] - max_budget) / max_budget) if max_budget > 0 else 0.0
            
            # Điểm phù hợp (Fit score: càng cao càng tốt)
            fit_score = (c['score'] / 5.0) - (0.35 * cal_err) - (0.25 * prot_err) - (0.40 * cost_penalty)
            
            c['cal_diff'] = float(round(cal_diff, 1))
            c['prot_diff'] = float(round(prot_diff, 1))
            c['cost_diff'] = float(round(cost_diff, 0))
            c['fit_score'] = float(round(fit_score, 3))
            c['is_within_budget'] = bool(c['estimated_cost_vnd'] <= max_budget)
            
        candidates.sort(key=lambda x: (x['is_within_budget'], x['fit_score']), reverse=True)
        return candidates[:3]

    def evaluate_user_selected_food(
        self, 
        food_or_recipe_name: str, 
        calories: float, 
        protein_g: float, 
        fat_g: float, 
        estimated_cost_vnd: float, 
        daily_target_calories: float, 
        daily_budget_vnd: float,
        sodium_mg: float = 400.0
    ) -> Dict[str, Any]:
        """
        Đánh giá món ăn do Người dùng tự nhập vào thực đơn và tư vấn bù trừ năng lượng
        Bảo đảm an toàn: chặn hoàn toàn ZeroDivisionError với calo và ngân sách.
        """
        safe_daily_cal = daily_target_calories if daily_target_calories and daily_target_calories > 0 else 1800.0
        safe_daily_budget = daily_budget_vnd if daily_budget_vnd and daily_budget_vnd > 0 else 70000.0
        safe_sodium = sodium_mg if sodium_mg is not None and sodium_mg >= 0 else 400.0

        warnings = RuleEngine.evaluate_health_warnings(
            {"calories": calories, "fat_g": fat_g, "protein_g": protein_g, "sodium_mg": safe_sodium}, 
            safe_daily_cal
        )
        
        cal_percent = round((calories / safe_daily_cal) * 100, 1)
        cost_percent = round((estimated_cost_vnd / safe_daily_budget) * 100, 1)
        
        advice = []
        if cal_percent > 40:
            advice.append("💡 Món ăn này chiếm tỷ trọng năng lượng lớn (> 40% ngày). Bạn nên giảm bớt phần tinh bột/dầu mỡ ở bữa tiếp theo.")
        else:
            advice.append("✅ Món ăn nằm trong phạm vi năng lượng hợp lý cho 1 bữa.")
            
        if cost_percent > 50:
            advice.append("⚠️ Chi phí món này chiếm hơn 50% ngân sách cả ngày. Hãy chọn món tiết kiệm cho các bữa còn lại.")
            
        return {
            "food_name": food_or_recipe_name,
            "calories": calories,
            "protein_g": protein_g,
            "fat_g": fat_g,
            "sodium_mg": safe_sodium,
            "estimated_cost_vnd": estimated_cost_vnd,
            "daily_target_calories": safe_daily_cal,
            "daily_budget_vnd": safe_daily_budget,
            "cal_percent_of_daily_target": cal_percent,
            "cost_percent_of_daily_budget": cost_percent,
            "warnings": warnings,
            "dss_advice": advice
        }
