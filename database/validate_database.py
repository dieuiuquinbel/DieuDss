"""
NutriDSS - Database Contract Validation Tool (database/validate_database.py)
Ensures database schema matches application expectations at startup or CI.
Fails loudly if required tables or columns are missing.
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), "nutridss.db")

REQUIRED_TABLE_COLUMNS = {
    "foods": ["id", "canonical_name_vi", "calories_kcal_100g", "protein_g_100g", "fat_g_100g", "carb_g_100g"],
    "nutrients": ["id", "code", "name_vi", "unit", "category"],
    "food_nutrients": ["food_id", "nutrient_id", "value"],
    "food_prices": ["id", "food_id", "store_name", "price_vnd", "quantity_g", "normalized_price_per_100g"],
    "food_price_summary": ["food_id", "price_median", "estimated_price_per_100g"],
    "allergens": ["id", "code", "name_vi"],
    "food_allergens": ["food_id", "allergen_id"],
    "recipes": ["id", "name_vi", "meal_type", "dish_role", "is_vegetarian"],
    "recipe_ingredients": ["recipe_id", "food_id", "raw_quantity", "raw_unit", "quantity_g"],
    "recipe_steps": ["recipe_id", "step_number", "instruction_vi"],
    "guideline_sources": ["id", "organization", "title"],
    "guideline_rules": ["id", "rule_code", "nutrient", "scope"],
    "users": ["id", "email", "username", "password_hash", "role"],
    "user_profiles": ["user_id", "health_goal", "daily_budget_vnd"],
    "meal_plans": ["id", "user_id", "plan_name", "budget_vnd", "health_goal", "total_cost_vnd", "total_calories"],
    "meals": ["id", "meal_plan_id", "day_of_week", "meal_type", "structure_type"],
    "meal_items": ["id", "meal_id", "recipe_id", "dish_role"],
    "user_interactions": ["id", "user_id", "recipe_id", "event_type"]
}

def validate_database(db_path: str = DB_PATH) -> bool:
    if not os.path.exists(db_path):
        print(f"[FAIL] Database file does not exist: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    errors = []

    # Get list of existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = set(row[0] for row in cursor.fetchall())

    for table, required_cols in REQUIRED_TABLE_COLUMNS.items():
        if table not in existing_tables:
            errors.append(f"Missing TABLE: '{table}'")
            continue

        cursor.execute(f"PRAGMA table_info({table})")
        columns = set(row[1] for row in cursor.fetchall())

        for col in required_cols:
            if col not in columns:
                errors.append(f"Table '{table}' is MISSING column: '{col}'")

    conn.close()

    if errors:
        print("=" * 60)
        print("[ERROR] DATABASE SCHEMA DRIFT DETECTED:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 60)
        return False

    print("[SUCCESS] All required tables and columns are strictly valid according to NutriDSS V3 Contract.")
    return True

if __name__ == "__main__":
    is_valid = validate_database()
    sys.exit(0 if is_valid else 1)
