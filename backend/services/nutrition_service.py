"""
NutriDSS - Nutrition Service (Validation & Medical Warning Rules)
"""

class NutritionService:
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
        if height_cm <= 0:
            return {"bmi": 0.0, "status": "Không xác định", "color": "secondary", "badge_class": "bg-secondary"}
            
        height_m = height_cm / 100.0
        bmi = round(weight_kg / (height_m * height_m), 1)
        
        if bmi < 18.5:
            return {
                "bmi": bmi,
                "status": "Thiếu cân (Gầy)",
                "color": "warning",
                "badge_class": "bg-warning text-dark",
                "icon": "bi-exclamation-circle-fill"
            }
        elif 18.5 <= bmi < 23.0:
            return {
                "bmi": bmi,
                "status": "Bình thường (Khỏe mạnh)",
                "color": "success",
                "badge_class": "bg-success text-white",
                "icon": "bi-check-circle-fill"
            }
        elif 23.0 <= bmi < 25.0:
            return {
                "bmi": bmi,
                "status": "Thừa cân",
                "color": "warning",
                "badge_class": "bg-warning text-dark",
                "icon": "bi-exclamation-triangle-fill"
            }
        else: # >= 25.0
            return {
                "bmi": bmi,
                "status": "Béo phì",
                "color": "danger",
                "badge_class": "bg-danger text-white",
                "icon": "bi-x-circle-fill"
            }

    @staticmethod
    def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
        gender_upper = gender.upper()
        if gender_upper in ["MALE", "NAM"]:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        multipliers = {
            "SEDENTARY": 1.2,
            "LIGHTLY_ACTIVE": 1.375,
            "MODERATE": 1.55,
            "VERY_ACTIVE": 1.725,
            "EXTRA_ACTIVE": 1.9
        }
        return bmr * multipliers.get(activity_level.upper(), 1.4)

    @staticmethod
    def calculate_target_calories(tdee: float, health_goal: str) -> float:
        goal_upper = health_goal.upper()
        if goal_upper in ["LOSE_WEIGHT", "GIẢM CÂN"]:
            return max(1200.0, tdee - 500.0)
        elif goal_upper in ["GAIN_WEIGHT", "TĂNG CÂN"]:
            return tdee + 400.0
        elif goal_upper in ["HIGH_PROTEIN", "TĂNG CƠ"]:
            return tdee + 250.0
        elif goal_upper in ["GROWTH", "TĂNG CHIỀU CAO"]:
            return tdee + 300.0
        else:
            return tdee

    @staticmethod
    def calculate_macro_targets(target_calories: float, health_goal: str) -> dict:
        """
        Tính toán phân bổ macronutrient (Protein, Carb, Fat) theo mục tiêu sức khỏe:
        - 1g Protein = 4 kcal
        - 1g Carb = 4 kcal
        - 1g Fat = 9 kcal
        """
        goal_upper = health_goal.upper() if health_goal else "BALANCED"
        
        # Tỷ lệ phần trăm năng lượng theo khuyến nghị dinh dưỡng
        if goal_upper in ["LOSE_WEIGHT", "GIẢM CÂN"]:
            p_ratio, c_ratio, f_ratio = 0.30, 0.40, 0.30
        elif goal_upper in ["GAIN_WEIGHT", "TĂNG CÂN"]:
            p_ratio, c_ratio, f_ratio = 0.20, 0.55, 0.25
        elif goal_upper in ["HIGH_PROTEIN", "TĂNG CƠ"]:
            p_ratio, c_ratio, f_ratio = 0.30, 0.45, 0.25
        elif goal_upper in ["GROWTH", "TĂNG CHIỀU CAO"]:
            p_ratio, c_ratio, f_ratio = 0.25, 0.50, 0.25
        else: # Cân bằng (BALANCED, MAINTAIN, v.v.)
            p_ratio, c_ratio, f_ratio = 0.20, 0.50, 0.30

        prot_cal = target_calories * p_ratio
        carb_cal = target_calories * c_ratio
        fat_cal = target_calories * f_ratio

        return {
            "daily_calories": round(target_calories, 1),
            "target_protein_g": round(prot_cal / 4.0, 1),
            "target_carb_g": round(carb_cal / 4.0, 1),
            "target_fat_g": round(fat_cal / 9.0, 1)
        }

    @staticmethod
    def generate_goal_advice(health_goal: str, target_value: float = 0, current_weight: float = 68.0) -> dict:
        """
        Tạo lời khuyên & Cảnh báo y tế NutriDSS:
        - Chặn số âm: Mục tiêu là độ biến thiên nên tuyệt đối không được là số âm.
        - Chặn vượt quá số cân: Số cân muốn giảm tuyệt đối không được >= trọng lượng hiện tại.
        - Cảnh báo nhẹ màu vàng: Nếu giảm từ 1/3 trọng lượng cơ thể trở lên, cảnh báo cơ thể khó thích nghi.
        """
        goal_upper = health_goal.upper()
        warnings = []
        is_negative = target_value < 0
        val = abs(target_value)

        if is_negative:
            warnings.append({
                "type": "danger",
                "message": f"⛔ **Lỗi nhập liệu:** Mục tiêu không thể là số âm ({target_value}). Mục tiêu thể hiện lượng cân cần thay đổi nên phải là số dương. Hệ thống đã tự động chuyển về {val}."
            })

        # Validation đối với mục tiêu GIẢM CÂN
        if goal_upper in ["LOSE_WEIGHT", "GIẢM CÂN"]:
            if val >= current_weight:
                warnings.append({
                    "type": "danger",
                    "message": f"⛔ **Lỗi nhập liệu phi lý:** Số cân muốn giảm ({val} kg) tuyệt đối không được bằng hoặc vượt quá tổng trọng lượng hiện tại của bạn ({current_weight} kg). Bạn không thể giảm toàn bộ cơ thể về 0 kg!"
                })
                # Điều chỉnh về mức an toàn tối đa 10% trọng lượng
                val = round(current_weight * 0.1, 1)
            elif val >= (current_weight / 3.0):
                one_third = round(current_weight / 3.0, 1)
                warnings.append({
                    "type": "warning",
                    "message": f"⚠️ **Cảnh báo Sức khỏe NutriDSS:** Mục tiêu giảm **{val} kg** (chiếm từ 1/3 trọng lượng cơ thể hiện tại {current_weight} kg trở lên - ngưỡng 1/3 là {one_third} kg) là mức giảm rất lớn. Việc giảm cân quá nhiều trong một đợt có thể khiến cơ thể khó thích nghi, gây sụt giảm trao đổi chất, rối loạn nội tiết, mệt mỏi và mất khối cơ. **Khuyến nghị Y khoa:** Bạn nên chia nhỏ mục tiêu thành từng đợt (3-5 kg hoặc 5-10% thể trọng mỗi đợt) để cơ thể kịp thời thích nghi một cách bền vững."
                })

            weeks = max(1, round(val * 2, 0))
            advice = f"💡 **Lời khuyên NutriDSS:** Để giảm {val} kg an toàn chuẩn WHO, bạn cần khoảng {weeks:.0f} tuần (thâm hụt 500 Kcal/ngày, tốc độ ~0.5 kg/tuần). Tuyệt đối không nhịn ăn đột ngột."

        elif goal_upper in ["GAIN_WEIGHT", "TĂNG CÂN"]:
            if val > 30:
                warnings.append({
                    "type": "warning",
                    "message": f"⚠️ **Cảnh báo Sức khỏe NutriDSS:** Mục tiêu tăng {val} kg là mức tăng rất lớn trong một đợt. Tăng cân quá nhanh có thể gây tích mỡ nội tạng thay vì tăng cơ. Nên duy trì mức tăng 1-2 kg/tháng."
                })
            advice = f"💡 **Lời khuyên NutriDSS:** Để tăng {val} kg lành mạnh, hãy duy trì thặng dư 300 - 400 Kcal/ngày từ đạm tươi và tinh bột hấp thu chậm (khoai lang, yến mạch, gạo lứt)."

        elif goal_upper in ["GROWTH", "TĂNG CHIỀU CAO"]:
            advice = f"💡 **Lời khuyên NutriDSS:** Hỗ trợ dinh dưỡng tăng chiều cao (+{val} cm): Ưu tiên Canxi, Vitamin D3, Protein (cá biển, trứng, sữa, rau xanh sẫm) kết hợp vận động bơi lội/bóng rổ và ngủ trước 23h."
        elif goal_upper in ["HIGH_PROTEIN", "TĂNG CƠ"]:
            advice = "💡 **Lời khuyên NutriDSS:** Duy trì 1.8g - 2.2g Protein/kg trọng lượng cơ thể kết hợp các bài tập kháng lực (Gym/Calisthenics) để kích thích tổng hợp cơ bắp tối đa."
        else:
            advice = "💡 **Lời khuyên NutriDSS:** Duy trì chế độ ăn đa dạng 4 nhóm chất chuẩn WHO để cơ thể luôn tràn đầy năng lượng và cân bằng chuyển hóa."

        return {
            "val": val,
            "advice": advice,
            "warnings": warnings
        }
