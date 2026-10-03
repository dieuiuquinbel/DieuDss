"""
NutriDSS - Meal Optimizer & DSS Decision Engine V2
Implements:
1. Top-K Candidate Bounded Optimization (eliminates O(N^3) combinatorial explosion)
2. Daily Plan Options (Budget Saver, Balanced ML DSS Choice, High Protein)
3. Portion Scaling Adjustment (0.75x, 1.0x, 1.25x, 1.5x)
4. Weekly Planner (7-day plan with variety and meal rotation)
5. Smart Replacement Engine (substitutes meals preserving calorie & budget constraints)
6. User Choice Evaluator & Compensation Engine
"""

import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional

from backend.services.recommender_service import RecommenderService
from backend.services.rule_engine import RuleEngine
from backend.services.ingredient_cost_engine import IngredientCostEngine
from backend.services.meal_composer import MealComposer

DB_PATH = "database/nutridss.db"

class MealOptimizer:
    def __init__(self):
        self.recommender = RecommenderService()
        self.cost_engine = IngredientCostEngine()
        self.composer = MealComposer(self.cost_engine)

    def generate_daily_plan_options(
        self, 
        goal: str, 
        daily_budget_vnd: float, 
        user_allergies: Optional[List[str]] = None,
        target_calories: Optional[float] = None,
        target_protein_g: Optional[float] = None,
        target_carb_g: Optional[float] = None,
        target_fat_g: Optional[float] = None,
        is_vegetarian: bool = False,
        meal_structure: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        Sinh 3 phương án thực đơn cả ngày (Sáng, Trưa, Tối) đúng tinh thần DSS:
        - Mỗi bữa trưa/tối gồm MÂM CƠM VIỆT NAM (1 Tinh bột + 1 Món Mặn/Chay + 1 Món Canh/Rau).
        - Hỗ trợ chế độ Ăn Chay / Ăn Kiêng (tự động thay món mặn bằng đạm thực vật).
        - Ràng buộc cứng Ngân sách: Tối ưu hóa sử dụng ngân sách đầu vào, không để ăn thiếu chất.
        - 3 Phương án:
          + Phương án A (Tiết kiệm ngân sách tối đa)
          + Phương án B (Tối ưu điểm ML & Dinh dưỡng cân bằng cá nhân hóa)
          + Phương án C (Ưu tiên đạm & Đa dạng món)
        """
        all_recipes = self.recommender.get_all_recipes_with_nutrition_and_cost()
        
        # 1. Validate allergies strictly via RuleEngine
        if user_allergies:
            user_allergen_ids = RuleEngine.get_user_allergen_ids(user_allergies)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(user_allergen_ids))
            cursor.execute(f"""
                SELECT DISTINCT ri.recipe_id
                FROM recipe_ingredients ri
                JOIN food_allergens fa ON ri.food_id = fa.food_id
                WHERE fa.allergen_id IN ({placeholders})
            """, user_allergen_ids)
            allergy_recipe_ids = set(row[0] for row in cursor.fetchall())
            conn.close()
            all_recipes = [r for r in all_recipes if r['id'] not in allergy_recipe_ids]

        # Group recipes by dish_role
        staples = [r for r in all_recipes if r.get('dish_role') == 'STAPLE']
        is_veg_mode = is_vegetarian or (meal_structure == "VEGETARIAN")
        if is_veg_mode:
            mains = [r for r in all_recipes if r.get('dish_role') == 'VEG_PROTEIN' or (r.get('dish_role') == 'MAIN_PROTEIN' and r.get('is_vegetarian') == 1)]
            soups = [r for r in all_recipes if r.get('dish_role') == 'SOUP_VEG' and r.get('is_vegetarian') == 1]
            bfs = [r for r in all_recipes if (r.get('dish_role') == 'BREAKFAST' or r.get('meal_type') == 'BREAKFAST') and r.get('is_vegetarian') == 1]
            if not bfs:
                bfs = [r for r in all_recipes if r.get('dish_role') == 'BREAKFAST' or r.get('meal_type') == 'BREAKFAST']
        else:
            mains = [r for r in all_recipes if r.get('dish_role') in ['MAIN_PROTEIN', 'VEG_PROTEIN']]
            soups = [r for r in all_recipes if r.get('dish_role') == 'SOUP_VEG']
            bfs = [r for r in all_recipes if r.get('dish_role') == 'BREAKFAST' or r.get('meal_type') == 'BREAKFAST']

        # Fallback if curated items are filtered out
        if not staples:
            staples = [r for r in all_recipes if 'cơm' in r['name_vi'].lower() or 'gạo' in r['name_vi'].lower()][:3]
        if not mains:
            mains = [r for r in all_recipes if r.get('meal_type') in ['LUNCH', 'DINNER']][:20]
        if not soups:
            soups = [r for r in all_recipes if 'canh' in r['name_vi'].lower() or 'rau' in r['name_vi'].lower()][:15]
        if not bfs:
            bfs = [r for r in all_recipes if r.get('meal_type') == 'BREAKFAST'][:15]

        # Sort mains and soups to have both budget-friendly and high-protein candidates
        mains_sorted_cost = sorted(mains, key=lambda x: x['estimated_cost_vnd'])
        mains_sorted_score = sorted(mains, key=lambda x: -x.get('score', 4.0))
        mains_pool = list({m['id']: m for m in (mains_sorted_cost[:6] + mains_sorted_score[:6])}.values())

        soups_sorted_cost = sorted(soups, key=lambda x: x['estimated_cost_vnd'])
        soups_sorted_score = sorted(soups, key=lambda x: -x.get('score', 4.0))
        soups_pool = list({s['id']: s for s in (soups_sorted_cost[:5] + soups_sorted_score[:5])}.values())

        bfs_sorted = sorted(bfs, key=lambda x: x['estimated_cost_vnd'])
        bfs_pool = list({b['id']: b for b in (bfs_sorted[:5] + sorted(bfs, key=lambda x: -x.get('score', 4.0))[:5])}.values())

        # Helper to construct a dynamic Vietnamese Meal Set combo dict via MealComposer
        def make_meal_set_dynamic(items: List[Dict[str, Any]], mtype="LUNCH", structure_label="Mâm cơm chuẩn Việt"):
            return self.composer.compose_meal(items, meal_type=mtype, structure_mode=meal_structure)

        # Build candidate meal sets based on meal_structure mode
        lunch_sets = []
        din_sets = []

        if meal_structure == "FULL":
            # 1 Cơm + 2 Món Mặn + 1 Canh (4 món gia đình)
            for st in staples[:2]:
                for i, m1 in enumerate(mains_pool[:4]):
                    for m2 in mains_pool[i+1:5]:
                        for sp in soups_pool[:3]:
                            lunch_sets.append(make_meal_set_dynamic([st, m1, m2, sp], "LUNCH", "Mâm cơm gia đình 4 món (1 cơm + 2 mặn + 1 canh)"))
                            din_sets.append(make_meal_set_dynamic([st, m1, m2, sp], "DINNER", "Mâm cơm gia đình 4 món (1 cơm + 2 mặn + 1 canh)"))
        elif meal_structure == "LIGHT":
            # Ăn nhẹ / Eat-clean: 1 Tinh bột nhẹ + 1 Đạm nạc + 1 Rau luộc (3 món nhẹ)
            light_staples = [s for s in staples if 'khoai' in s['name_vi'].lower() or 'lứt' in s['name_vi'].lower() or 'bắp' in s['name_vi'].lower()] or staples[:1]
            lean_mains = [m for m in mains_pool if 'gà' in m['name_vi'].lower() or 'cá rô' in m['name_vi'].lower() or 'trứng' in m['name_vi'].lower() or 'đậu' in m['name_vi'].lower()] or mains_pool[:3]
            light_vegs = [v for v in soups_pool if 'luộc' in v['name_vi'].lower() or 'xanh' in v['name_vi'].lower()] or soups_pool[:2]
            for st in light_staples:
                for m in lean_mains:
                    for sp in light_vegs:
                        lunch_sets.append(make_meal_set_dynamic([st, m, sp], "LUNCH", "Bữa ăn nhẹ Eat-clean"))
                        din_sets.append(make_meal_set_dynamic([st, m, sp], "DINNER", "Bữa ăn nhẹ Eat-clean"))
        elif meal_structure == "VEGETARIAN":
            # Bữa chay: 1 Cơm + 1 Đậu + 1 Nấm + 1 Canh chay
            tofu_items = [m for m in mains_pool if 'đậu' in m['name_vi'].lower()] or mains_pool[:1]
            mush_items = [m for m in mains_pool if 'nấm' in m['name_vi'].lower()] or mains_pool[1:2]
            for st in staples[:2]:
                for tf in tofu_items:
                    for mu in mush_items:
                        for sp in soups_pool[:3]:
                            items = [st, tf, mu, sp] if tf['id'] != mu['id'] else [st, tf, sp]
                            lunch_sets.append(make_meal_set_dynamic(items, "LUNCH", "Mâm cơm chay thanh tịnh"))
                            din_sets.append(make_meal_set_dynamic(items, "DINNER", "Mâm cơm chay thanh tịnh"))
        else:
            # STANDARD (Cá nhân tiêu chuẩn / 1 người: 1 Cơm + 1 Mặn + 1 Canh)
            for st in staples[:2]:
                for m in mains_pool:
                    for sp in soups_pool:
                        lunch_sets.append(make_meal_set_dynamic([st, m, sp], "LUNCH", "Mâm cơm tiêu chuẩn 3 món"))
                        din_sets.append(make_meal_set_dynamic([st, m, sp], "DINNER", "Mâm cơm tiêu chuẩn 3 món"))

        bf_candidates = bfs_pool
        # Include both lowest cost and highest score meal sets
        lunch_sets = list({s['name_vi']: s for s in (sorted(lunch_sets, key=lambda x: x['estimated_cost_vnd'])[:12] + sorted(lunch_sets, key=lambda x: -x['score'])[:12])}.values())
        din_sets = list({s['name_vi']: s for s in (sorted(din_sets, key=lambda x: x['estimated_cost_vnd'])[:12] + sorted(din_sets, key=lambda x: -x['score'])[:12])}.values())

        all_combos = []
        for bf in bf_candidates:
            for l_set in lunch_sets:
                for d_set in din_sets:
                    # Avoid duplicate main dishes in both lunch and dinner
                    l_mains = set(l_set.get("main_recipe_ids", []))
                    d_mains = set(d_set.get("main_recipe_ids", []))
                    if l_mains and d_mains and l_mains.intersection(d_mains) and len(mains) > 1:
                        continue
                    tot_cal = bf['calories'] + l_set['calories'] + d_set['calories']
                    tot_prot = bf['protein_g'] + l_set['protein_g'] + d_set['protein_g']
                    tot_carb = bf['carb_g'] + l_set['carb_g'] + d_set['carb_g']
                    tot_fat = bf['fat_g'] + l_set['fat_g'] + d_set['fat_g']
                    tot_cost = bf['estimated_cost_vnd'] + l_set['estimated_cost_vnd'] + d_set['estimated_cost_vnd']
                    avg_score = round((bf.get('score', 4.5) + l_set['score'] + d_set['score']) / 3.0, 2)
                    all_combos.append({
                        "bf": bf,
                        "lunch": l_set,
                        "din": d_set,
                        "total_calories": tot_cal,
                        "total_protein_g": tot_prot,
                        "total_carb_g": tot_carb,
                        "total_fat_g": tot_fat,
                        "total_cost_vnd": tot_cost,
                        "average_score": avg_score
                    })

        if not all_combos:
            # Fallback if combo is empty
            return {"error": "Không thể ghép mâm cơm phù hợp với các ràng buộc dị ứng hiện tại."}

        # Xử lý RÀNG BUỘC CỨNG NGÂN SÁCH (Budget Hard Constraint)
        min_possible_cost = min(c['total_cost_vnd'] for c in all_combos)
        feasible_combos = [c for c in all_combos if c['total_cost_vnd'] <= daily_budget_vnd]
        
        budget_exceeded = False
        budget_warning_msg = None
        
        if not feasible_combos:
            budget_exceeded = True
            shortfall = min_possible_cost - daily_budget_vnd
            budget_warning_msg = (
                f"⚠️ **Ràng buộc ngân sách không khả thi:** Ngân sách {daily_budget_vnd:,.0f}đ/ngày "
                f"thấp hơn chi phí thực đơn 3 bữa (mâm cơm đủ món) tối thiểu khả thi ({min_possible_cost:,.0f}đ/ngày, thiếu hụt {shortfall:,.0f}đ). "
                f"NutriDSS đã tự động chọn các phương án tiết kiệm nhất có thể và khuyến nghị bạn điều chỉnh ngân sách tối thiểu đạt {min_possible_cost:,.0f}đ."
            )
            candidate_pool = all_combos
        else:
            candidate_pool = feasible_combos

        # Option A: Budget Saver (Tối ưu chi phí trong hạn mức)
        opt_a = min(candidate_pool, key=lambda x: (x['total_cost_vnd'], -x['average_score']))

        # Option B: Balanced & Personalized Best (Dùng tối đa ngân sách để ăn ngon và đủ chất)
        if target_calories and target_calories > 0:
            def balance_personal_score(c):
                cal_dev = abs(c['total_calories'] - target_calories) / target_calories
                cost_ratio = c['total_cost_vnd'] / daily_budget_vnd if daily_budget_vnd > 0 else 1.0
                return c['average_score'] - (1.5 * cal_dev) + (0.5 * cost_ratio)
            opt_b = max(candidate_pool, key=balance_personal_score)
        else:
            opt_b = max(candidate_pool, key=lambda x: (x['total_cost_vnd'], x['average_score']))

        # Option C: High Protein Choice (Tập trung món nhiều đạm nhất)
        opt_c = max(candidate_pool, key=lambda x: (x['total_protein_g'], x['average_score']))

        def build_option(name, desc, combo):
            bf = combo['bf']
            lunch = combo['lunch']
            din = combo['din']
            tot_cal = combo['total_calories']
            tot_prot = combo['total_protein_g']
            tot_cost = combo['total_cost_vnd']
            avg_score = combo['average_score']

            cal_achieve = round((tot_cal / target_calories) * 100, 1) if (target_calories and target_calories > 0) else None
            prot_achieve = round((tot_prot / target_protein_g) * 100, 1) if (target_protein_g and target_protein_g > 0) else None
            savings = round(daily_budget_vnd - tot_cost, 0)

            # Check health warnings for all 3 meals
            daily_warnings = []
            for meal in (bf, lunch, din):
                m_warns = RuleEngine.evaluate_health_warnings(meal, target_calories or 1800.0)
                for w in m_warns:
                    if w not in daily_warnings:
                        daily_warnings.append(w)

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
                "health_warnings": daily_warnings,
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
                build_option("Phương án C - Giàu đạm & Đa dạng", "Ưu tiên hàm lượng protein cao nhất, hỗ trợ phục hồi và phát triển cơ bắp.", opt_c)
            ]
        }

    def generate_single_meal(
        self,
        meal_type: str = "LUNCH",
        budget_vnd: float = 35000.0,
        goal: str = "BALANCED",
        user_allergies: Optional[List[str]] = None,
        is_vegetarian: bool = False,
        structure_mode: str = "STANDARD",
        target_calories: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sinh các phương án mâm cơm chuẩn Việt cho 1 bữa ăn đơn lẻ (Sáng, Trưa hoặc Tối)
        khớp với ngân sách và mục tiêu dinh dưỡng.
        """
        all_recipes = self.recommender.get_all_recipes_with_nutrition_and_cost()
        
        # 1. Filter allergies
        if user_allergies:
            user_allergen_ids = RuleEngine.get_user_allergen_ids(user_allergies)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(user_allergen_ids))
            cursor.execute(f"""
                SELECT DISTINCT ri.recipe_id
                FROM recipe_ingredients ri
                JOIN food_allergens fa ON ri.food_id = fa.food_id
                WHERE fa.allergen_id IN ({placeholders})
            """, user_allergen_ids)
            allergy_recipe_ids = set(row[0] for row in cursor.fetchall())
            conn.close()
            all_recipes = [r for r in all_recipes if r['id'] not in allergy_recipe_ids]

        is_veg_mode = is_vegetarian or (structure_mode == "VEGETARIAN")

        # Case 1: BREAKFAST
        if meal_type.upper() == "BREAKFAST":
            bf_candidates = [r for r in all_recipes if r.get('dish_role') == 'BREAKFAST' or r.get('meal_type') == 'BREAKFAST']
            if is_veg_mode:
                bf_veg = [r for r in bf_candidates if r.get('is_vegetarian') == 1]
                if bf_veg:
                    bf_candidates = bf_veg
            if not bf_candidates:
                bf_candidates = all_recipes[:10]
            
            ranked = self.recommender.rank_recipes(goal, budget_vnd, user_allergies, meal_type="BREAKFAST")
            if not ranked:
                ranked = sorted(bf_candidates, key=lambda x: x.get('estimated_cost_vnd', 0))
            
            opt_a = min(ranked, key=lambda x: x.get('estimated_cost_vnd', 0))
            opt_b = ranked[0]
            opt_c = max(ranked, key=lambda x: x.get('protein_g', 0))

            return {
                "meal_type": "BREAKFAST",
                "budget_target_vnd": float(budget_vnd),
                "structure_mode": structure_mode,
                "options": [
                    {"code": "A", "title": "Phương án A - Tiết kiệm nhất", "meal": opt_a},
                    {"code": "B", "title": "Phương án B - Đề xuất DSS (Khuyên dùng)", "meal": opt_b},
                    {"code": "C", "title": "Phương án C - Giàu đạm / Trọn vị", "meal": opt_c}
                ]
            }

        # Case 2: LUNCH or DINNER (Vietnamese Meal Sets)
        staples = [r for r in all_recipes if r.get('dish_role') == 'STAPLE'] or [r for r in all_recipes if 'cơm' in r['name_vi'].lower()][:3]
        if is_veg_mode:
            mains = [r for r in all_recipes if (r.get('dish_role') in ['VEG_PROTEIN', 'MAIN_PROTEIN'] and r.get('is_vegetarian') == 1)]
            soups = [r for r in all_recipes if r.get('dish_role') == 'SOUP_VEG' and r.get('is_vegetarian') == 1]
        else:
            mains = [r for r in all_recipes if r.get('dish_role') in ['MAIN_PROTEIN', 'VEG_PROTEIN', 'SECOND_MAIN']]
            soups = [r for r in all_recipes if r.get('dish_role') == 'SOUP_VEG']

        # Exclude non-main dishes
        mains = [r for r in mains if r.get('dish_role') not in ['SEASONING', 'SAUCE', 'DESSERT', 'BEVERAGE']]

        if not mains or not staples or not soups:
            return {"error": "Không đủ món ăn thành phần (Cơm, Món mặn, Canh) phù hợp với các ràng buộc dị ứng và dinh dưỡng đã chọn."}

        candidate_sets = []
        if structure_mode == "FULL":
            # 1 Cơm + 2 Món Mặn + 1 Canh
            for st in staples[:2]:
                for i, m1 in enumerate(mains[:6]):
                    for m2 in mains[i+1:7]:
                        for sp in soups[:3]:
                            composed = self.composer.compose_meal([st, m1, m2, sp], meal_type=meal_type, structure_mode="FULL")
                            candidate_sets.append(composed)
        elif structure_mode == "VEGETARIAN":
            # Chay thanh tịnh: Cơm + Đạm thực vật + Canh chay
            veg_mains = [m for m in mains if m.get('is_vegetarian') == 1] or mains
            for st in staples[:2]:
                for m in veg_mains[:6]:
                    for sp in soups[:4]:
                        composed = self.composer.compose_meal([st, m, sp], meal_type=meal_type, structure_mode="VEGETARIAN")
                        candidate_sets.append(composed)
        else:
            # STANDARD & LIGHT: 1 Cơm + 1 Mặn + 1 Canh
            for st in staples[:2]:
                for m in mains[:8]:
                    for sp in soups[:5]:
                        composed = self.composer.compose_meal([st, m, sp], meal_type=meal_type, structure_mode=structure_mode)
                        candidate_sets.append(composed)

        if not candidate_sets:
            return {"error": "Không tìm thấy phương án mâm cơm phù hợp."}

        # Filter within budget if possible, else closest
        budget_matched = [c for c in candidate_sets if c['estimated_cost_vnd'] <= budget_vnd * 1.15]
        pool = budget_matched if budget_matched else candidate_sets

        opt_a = min(pool, key=lambda x: x['estimated_cost_vnd'])
        opt_b = max(pool, key=lambda x: x.get('score', 4.0))
        opt_c = max(pool, key=lambda x: x['protein_g'])

        return {
            "meal_type": meal_type,
            "budget_target_vnd": float(budget_vnd),
            "structure_mode": structure_mode,
            "options": [
                {"code": "A", "title": "Phương án A - Tiết kiệm nhất", "meal": opt_a},
                {"code": "B", "title": "Phương án B - Đề xuất DSS (Khuyên dùng)", "meal": opt_b},
                {"code": "C", "title": "Phương án C - Giàu đạm / Đầy đặn", "meal": opt_c}
            ]
        }

    def replace_meal_item(
        self, 
        current_recipe_id: int, 
        goal: str, 
        budget_vnd: float, 
        user_allergies: Optional[List[str]] = None,
        remaining_budget_vnd: Optional[float] = None,
        target_protein_g: Optional[float] = None,
        target_calories: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Đổi món thông minh: Đề xuất các món cùng bữa ăn và cùng vai trò (dish_role), tương thích ngân sách và dinh dưỡng."""
        all_recipes = self.recommender.get_all_recipes_with_nutrition_and_cost()
        curr_recipe = next((r for r in all_recipes if r['id'] == current_recipe_id), None)
        
        if not curr_recipe:
            raise ValueError(f"Không tìm thấy món ăn với ID {current_recipe_id}")

        meal_type = curr_recipe.get('meal_type', 'LUNCH')
        dish_role = curr_recipe.get('dish_role')
        effective_budget = remaining_budget_vnd if (remaining_budget_vnd and remaining_budget_vnd > 0) else budget_vnd
        
        ranked_candidates = self.recommender.rank_recipes(
            goal=goal, 
            budget_vnd=effective_budget, 
            user_allergies=user_allergies, 
            meal_type=meal_type
        )
        
        # Loại trừ món đang ăn
        alternatives = [r for r in ranked_candidates if r['id'] != current_recipe_id]

        # Prioritize matching dish_role if specified
        if dish_role:
            same_role = [r for r in alternatives if r.get('dish_role') == dish_role]
            diff_role = [r for r in alternatives if r.get('dish_role') != dish_role]
            alternatives = same_role + diff_role

        for alt in alternatives:
            cal_diff = round(alt['calories'] - curr_recipe['calories'], 1)
            prot_diff = round(alt['protein_g'] - curr_recipe['protein_g'], 1)
            cost_diff = round(alt['estimated_cost_vnd'] - curr_recipe['estimated_cost_vnd'], 0)
            
            alt['diff'] = {
                "calories": cal_diff,
                "protein_g": prot_diff,
                "cost_vnd": cost_diff
            }
            alt['is_within_remaining_budget'] = bool(alt['estimated_cost_vnd'] <= effective_budget)
            alt['health_warnings'] = RuleEngine.evaluate_health_warnings(alt, target_calories or 1800.0)

        return alternatives

    def scale_meal_portion(self, recipe: Dict[str, Any], multiplier: float = 1.0) -> Dict[str, Any]:
        """Điều chỉnh khẩu phần ăn (0.75x, 1.0x, 1.25x, 1.5x) mà không sửa database gốc."""
        scaled = dict(recipe)
        multiplier = max(0.5, min(3.0, multiplier))
        scaled["portion_multiplier"] = multiplier
        scaled["calories"] = round(recipe.get("calories", 0) * multiplier, 1)
        scaled["protein_g"] = round(recipe.get("protein_g", 0) * multiplier, 1)
        scaled["carb_g"] = round(recipe.get("carb_g", 0) * multiplier, 1)
        scaled["fat_g"] = round(recipe.get("fat_g", 0) * multiplier, 1)
        scaled["fiber_g"] = round(recipe.get("fiber_g", 0) * multiplier, 1)
        scaled["sugar_g"] = round(recipe.get("sugar_g", 0) * multiplier, 1)
        scaled["sodium_mg"] = round(recipe.get("sodium_mg", 0) * multiplier, 1)
        scaled["estimated_cost_vnd"] = round(recipe.get("estimated_cost_vnd", 0) * multiplier, 0)
        return scaled

    def generate_weekly_plan(
        self,
        goal: str,
        daily_budget_vnd: float,
        user_allergies: Optional[List[str]] = None,
        target_calories: Optional[float] = None,
        target_protein_g: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sinh kế hoạch thực đơn 7 ngày (Thứ 2 -> Chủ nhật) có xoay vòng món, đa dạng nguồn đạm
        và tối ưu chi phí tổng thể.
        """
        days = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        weekly_plan = []
        total_weekly_cost = 0.0
        total_weekly_cal = 0.0

        # Allocate dynamic budget targets: Breakfast 20%, Lunch 45%, Dinner 35%
        bf_target_budget = daily_budget_vnd * 0.20
        lunch_target_budget = daily_budget_vnd * 0.45
        din_target_budget = daily_budget_vnd * 0.35

        bf_pool = self.recommender.rank_recipes(goal, bf_target_budget, user_allergies, meal_type="BREAKFAST")
        if not bf_pool:
            bf_pool = [r for r in self.recommender.get_all_recipes_with_nutrition_and_cost() if r.get("meal_type") == "BREAKFAST"][:10]

        # Generate candidates for lunch & dinner sets
        all_recs = self.recommender.get_all_recipes_with_nutrition_and_cost()
        staples = [r for r in all_recs if r.get("dish_role") == "STAPLE"] or [r for r in all_recs if "cơm" in r["name_vi"].lower()][:2]
        mains = [r for r in all_recs if r.get("dish_role") in ["MAIN_PROTEIN", "VEG_PROTEIN", "SECOND_MAIN"] and r.get("dish_role") not in ["SEASONING", "SAUCE", "DESSERT"]]
        soups = [r for r in all_recs if r.get("dish_role") == "SOUP_VEG"]

        if not bf_pool or not mains or not soups or not staples:
            return {"error": "Không đủ món ăn thành phần để tạo thực đơn 7 ngày theo ràng buộc dị ứng."}

        # Build diverse lunch and dinner sets
        candidate_lunch_sets = []
        candidate_din_sets = []
        for st in staples[:2]:
            for m in mains:
                for sp in soups[:4]:
                    candidate_lunch_sets.append(self.composer.compose_meal([st, m, sp], meal_type="LUNCH", structure_mode="STANDARD"))
                    candidate_din_sets.append(self.composer.compose_meal([st, m, sp], meal_type="DINNER", structure_mode="STANDARD"))

        # Sort candidate sets by score and cost
        sorted_lunch_sets = sorted(candidate_lunch_sets, key=lambda x: (-x.get("score", 4.0), x.get("estimated_cost_vnd", 0)))
        sorted_din_sets = sorted(candidate_din_sets, key=lambda x: (-x.get("score", 4.0), x.get("estimated_cost_vnd", 0)))

        for day_idx, day_name in enumerate(days):
            bf = bf_pool[day_idx % len(bf_pool)]
            lunch = sorted_lunch_sets[(day_idx * 2) % len(sorted_lunch_sets)]
            # Pick dinner with non-overlapping main protein
            lunch_mains = set(lunch.get("main_recipe_ids", []))
            din_candidates = [d for d in sorted_din_sets if not set(d.get("main_recipe_ids", [])).intersection(lunch_mains)]
            din = din_candidates[(day_idx + 1) % len(din_candidates)] if din_candidates else sorted_din_sets[(day_idx + 1) % len(sorted_din_sets)]

            day_cost = bf["estimated_cost_vnd"] + lunch["estimated_cost_vnd"] + din["estimated_cost_vnd"]
            day_cal = bf["calories"] + lunch["calories"] + din["calories"]
            day_prot = bf["protein_g"] + lunch["protein_g"] + din["protein_g"]

            total_weekly_cost += day_cost
            total_weekly_cal += day_cal

            weekly_plan.append({
                "day": day_name,
                "total_calories": round(day_cal, 1),
                "total_protein_g": round(day_prot, 1),
                "total_cost_vnd": round(day_cost, 0),
                "is_within_budget": bool(day_cost <= daily_budget_vnd),
                "meals": {
                    "breakfast": bf,
                    "lunch": lunch,
                    "dinner": din
                }
            })

        return {
            "plan_type": "WEEKLY",
            "days_count": 7,
            "weekly_budget_vnd": float(daily_budget_vnd * 7),
            "total_weekly_cost_vnd": round(total_weekly_cost, 0),
            "average_daily_calories": round(total_weekly_cal / 7.0, 1),
            "days": weekly_plan
        }

    def evaluate_user_selected_food(
        self,
        food_name: str,
        calories: float,
        protein_g: float,
        fat_g: float,
        estimated_cost_vnd: float,
        daily_target_calories: float,
        daily_budget_vnd: float,
        sodium_mg: float = 400.0,
        free_sugar_g: Optional[float] = None,
        saturated_fat_g: Optional[float] = None
    ) -> Dict[str, Any]:
        """Tự thêm món và Phân tích Cảnh báo / Tư vấn bù trừ năng lượng và ngân sách."""
        cal_pct = round((calories / daily_target_calories) * 100, 1) if daily_target_calories > 0 else 0.0
        budget_pct = round((estimated_cost_vnd / daily_budget_vnd) * 100, 1) if daily_budget_vnd > 0 else 0.0
        
        rem_cal = max(0.0, round(daily_target_calories - calories, 1))
        rem_budget = max(0.0, round(daily_budget_vnd - estimated_cost_vnd, 0))

        # Đánh giá cảnh báo chuẩn WHO thông qua RuleEngine
        warnings = RuleEngine.evaluate_health_warnings({
            "name_vi": food_name,
            "calories": calories,
            "protein_g": protein_g,
            "fat_g": fat_g,
            "free_sugar_g": free_sugar_g,
            "saturated_fat_g": saturated_fat_g,
            "sodium_mg": sodium_mg
        }, daily_target_calories)

        # Lời khuyên bù trừ dinh dưỡng cho các bữa còn lại
        advice = []
        if cal_pct > 40.0:
            advice.append(f"Món '{food_name}' chiếm tới {cal_pct}% calo cả ngày. Bữa tiếp theo nên ưu tiên rau xanh, luộc và giảm tinh bột.")
        if budget_pct > 45.0:
            advice.append(f"Chi phí món chiếm {budget_pct}% ngân sách ngày. Hãy chọn thực đơn tiết kiệm cho các bữa còn lại.")
        if not advice:
            advice.append("Món ăn có mức calo và chi phí hợp lý, phù hợp bổ sung vào thực đơn trong ngày.")

        return {
            "food_name": food_name,
            "calories": float(calories),
            "protein_g": float(protein_g),
            "fat_g": float(fat_g),
            "sodium_mg": float(sodium_mg),
            "estimated_cost_vnd": float(estimated_cost_vnd),
            "cal_percent_of_daily_target": float(cal_pct),
            "budget_percent_of_daily_target": float(budget_pct),
            "calorie_percentage_of_daily": float(cal_pct),
            "budget_percentage_of_daily": float(budget_pct),
            "remaining_calories_for_day": float(rem_cal),
            "remaining_budget_vnd": float(rem_budget),
            "health_warnings": warnings,
            "compensation_advice": advice
        }
