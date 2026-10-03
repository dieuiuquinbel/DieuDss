"""
NutriDSS Database Seeder V2
Seeds comprehensive schema: foods, 30+ nutrients, relational matrix, WHO guidelines, 
recipes with steps, unit conversions, and users.
"""

import sqlite3
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.core.security import hash_password

DB_PATH = "database/nutridss.db"
SCHEMA_PATH = "database/schema.sql"

# 30+ Nutrients definition matching Fix.md Section 6
NUTRIENTS_DATA = [
    (1, "CALORIES", "Energy / Calories", "Năng lượng", "kcal", "MACRO", 2000.0, None),
    (2, "PROTEIN", "Protein", "Chất đạm", "g", "MACRO", 60.0, None),
    (3, "CARB", "Carbohydrate", "Chất bột đường", "g", "MACRO", 260.0, None),
    (4, "FAT_TOTAL", "Total Fat", "Tổng chất béo", "g", "MACRO", 65.0, 70.0),
    (5, "FAT_SATURATED", "Saturated Fat", "Chất béo bão hòa", "g", "MACRO", None, 20.0),
    (6, "FAT_TRANS", "Trans Fat", "Chất béo chuyển hóa", "g", "MACRO", None, 2.0),
    (7, "FIBER", "Dietary Fiber", "Chất xơ", "g", "MACRO", 25.0, None),
    (8, "SUGAR_TOTAL", "Total Sugars", "Tổng lượng đường", "g", "SUGAR_LIPID", None, 50.0),
    (9, "SUGAR_FREE", "Free / Added Sugars", "Đường tự do / thêm", "g", "SUGAR_LIPID", None, 25.0),
    (10, "SODIUM", "Sodium", "Natri", "mg", "SUGAR_LIPID", None, 2000.0),
    (11, "CHOLESTEROL", "Cholesterol", "Cholesterol", "mg", "SUGAR_LIPID", None, 300.0),
    (12, "POTASSIUM", "Potassium", "Kali", "mg", "SUGAR_LIPID", 3510.0, None),
    (13, "CALCIUM", "Calcium", "Canxi", "mg", "MINERAL", 1000.0, 2500.0),
    (14, "IRON", "Iron", "Sắt", "mg", "MINERAL", 14.0, 45.0),
    (15, "MAGNESIUM", "Magnesium", "Magie", "mg", "MINERAL", 370.0, 700.0),
    (16, "PHOSPHORUS", "Phosphorus", "Phốt pho", "mg", "MINERAL", 700.0, 4000.0),
    (17, "ZINC", "Zinc", "Kẽm", "mg", "MINERAL", 11.0, 40.0),
    (18, "VIT_A", "Vitamin A", "Vitamin A", "mcg", "VITAMIN", 800.0, 3000.0),
    (19, "VIT_C", "Vitamin C", "Vitamin C", "mg", "VITAMIN", 90.0, 2000.0),
    (20, "VIT_D", "Vitamin D", "Vitamin D", "mcg", "VITAMIN", 15.0, 100.0),
    (21, "VIT_E", "Vitamin E", "Vitamin E", "mg", "VITAMIN", 15.0, 1000.0),
    (22, "VIT_K", "Vitamin K", "Vitamin K", "mcg", "VITAMIN", 75.0, None),
    (23, "VIT_B1", "Thiamin (B1)", "Vitamin B1", "mg", "VITAMIN", 1.2, None),
    (24, "VIT_B2", "Riboflavin (B2)", "Vitamin B2", "mg", "VITAMIN", 1.3, None),
    (25, "VIT_B3", "Niacin (B3)", "Vitamin B3", "mg", "VITAMIN", 16.0, 35.0),
    (26, "VIT_B6", "Vitamin B6", "Vitamin B6", "mg", "VITAMIN", 1.7, 100.0),
    (27, "VIT_B9", "Folate (B9)", "Axit Folic / B9", "mcg", "VITAMIN", 400.0, 1000.0),
    (28, "VIT_B12", "Vitamin B12", "Vitamin B12", "mcg", "VITAMIN", 2.4, None),
    (29, "OMEGA3", "Omega-3 Fatty Acids", "Axit béo Omega-3", "g", "FATTY_ACID", 1.6, None),
    (30, "OMEGA6", "Omega-6 Fatty Acids", "Axit béo Omega-6", "g", "FATTY_ACID", 14.0, None)
]

# WHO and National Guideline Sources & Rules
GUIDELINE_SOURCES = [
    (1, "World Health Organization", "Healthy Diet Fact Sheet No. 394 & 2023 Guidelines", "2023", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet", "2023-05-01"),
    (2, "Viện Dinh Dưỡng Quốc Gia Việt Nam", "Nhu cầu dinh dưỡng khuyến nghị cho người Việt Nam", "2016-2020", "http://viendinhduong.vn", "2016-12-01")
]

GUIDELINE_RULES = [
    (1, 1, "WHO_SODIUM_MAX", "GENERAL_ADULT", "SODIUM", None, 2000.0, "mg", "DAILY", "Dưới 2000mg Natri mỗi ngày"),
    (2, 1, "WHO_SODIUM_PER_MEAL", "GENERAL_ADULT", "SODIUM", None, 800.0, "mg", "PER_MEAL", "Không quá 800mg Natri trong một bữa ăn đơn lẻ"),
    (3, 1, "WHO_FREE_SUGAR_MAX", "GENERAL_ADULT", "SUGAR_FREE", None, 25.0, "g", "DAILY", "Đường tự do dưới 5-10% tổng năng lượng"),
    (4, 1, "WHO_SAT_FAT_MAX", "GENERAL_ADULT", "FAT_SATURATED", None, 20.0, "g", "DAILY", "Chất béo bão hòa dưới 10% tổng năng lượng"),
    (5, 1, "WHO_TRANS_FAT_MAX", "GENERAL_ADULT", "FAT_TRANS", None, 2.0, "g", "DAILY", "Chất béo chuyển hóa dưới 1% tổng calo"),
    (6, 1, "WHO_FIBER_MIN", "GENERAL_ADULT", "FIBER", 25.0, None, "g", "DAILY", "Tối thiểu 25g chất xơ/ngày từ rau củ quả"),
    (7, 1, "WHO_POTASSIUM_MIN", "GENERAL_ADULT", "POTASSIUM", 3510.0, None, "mg", "DAILY", "Tối thiểu 3510mg Kali/ngày")
]

UNIT_CONVERSIONS = [
    (1, 301, "quả", "g", 55.0, "TCVN 1858:2008 Trứng gia cầm loại trung bình"),
    (2, 101, "chén", "g", 150.0, "Quy chuẩn bát cơm chuẩn gia đình Việt Nam"),
    (3, 102, "chén", "g", 150.0, "Quy chuẩn bát cơm gạo lứt"),
    (4, 104, "bát", "g", 180.0, "Bát bún tươi tiêu chuẩn"),
    (5, 501, "muỗng canh", "g", 14.0, "1 muỗng canh dầu thực vật tương đương 14g"),
    (6, 501, "muỗng cà phê", "g", 5.0, "1 muỗng cà phê dầu ăn tương đương 5g")
]

RECIPE_STEPS = [
    # 1001: Ức gà xào ớt chuông
    (1001, 1, "Rửa sạch ức gà, thái miếng vừa ăn khoảng 2-3cm.", 5),
    (1001, 2, "Ớt chuông rửa sạch, bỏ hạt, thái miếng vuông vừa ăn.", 3),
    (1001, 3, "Phi thơm hành tỏi với 5g dầu ô liu, cho gà vào xào săn khoảng 5 phút.", 5),
    (1001, 4, "Cho ớt chuông vào đảo nhanh trong 3 phút, nêm chút hạt tiêu và nước tương ít natri.", 3),
    # 1002: Cá rô phi áp chảo
    (1002, 1, "Cá rô phi phi lê rửa sạch với nước muối loãng, thấm khô bằng khăn giấy.", 5),
    (1002, 2, "Ướp cá với chút gừng, tỏi và tiêu trong 10 phút.", 10),
    (1002, 3, "Làm nóng chảo chống dính với 5g dầu, áp chảo mỗi mặt 4-5 phút cho vàng đều.", 10),
    # 1003: Salad trứng gà rau củ
    (1003, 1, "Luộc chín 1 quả trứng gà (khoảng 8 phút), ngâm nước lạnh bóc vỏ và cắt múi cau.", 10),
    (1003, 2, "Rau xà lách, cà chua bi rửa sạch để ráo nước, cắt miếng vừa ăn.", 5),
    (1003, 3, "Trộn đều rau củ với 1 muỗng cà phê dầu ô liu, giấm táo và bày trứng lên trên.", 3),
    # 1004: Bún tôm luộc rau cải
    (1004, 1, "Tôm bóc vỏ, bỏ chỉ lưng, rửa sạch và luộc chín tới trong 3 phút.", 5),
    (1004, 2, "Rau cải thìa rửa sạch, luộc trong nước dùng thanh mát.", 4),
    (1004, 3, "Trần bún tươi qua nước sôi, xếp vào bát, cho tôm và rau cải lên, chan nước dùng.", 3)
]

API_SOURCES = [
    (1, "USDA FoodData Central", "https://api.nal.usda.gov/fdc/v1", "NUTRITION", 1, 30),
    (2, "Open Food Facts", "https://world.openfoodfacts.org/api/v2", "PACKAGED_FOOD", 1, 60),
    (3, "TheMealDB", "https://www.themealdb.com/api/json/v1/1", "RECIPES", 1, 60),
    (4, "WHO Health Data Hub", "https://ghoapi.azureedge.net/api", "GUIDELINES", 1, 30)
]

def seed_database():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Execute Schema V2
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("[OK] Schema V2 created.")
    
    # 2. Seed Base CSV Data
    tables_map = [
        ("food_groups", "data/processed/food_groups.csv"),
        ("foods", "data/processed/food_master.csv"),
        ("food_prices", "data/processed/food_prices.csv"),
        ("food_price_summary", "data/processed/food_price_summary.csv"),
        ("allergens", "data/processed/allergens.csv"),
        ("food_allergens", "data/processed/food_allergens.csv"),
        ("recipes", "data/processed/recipe_master.csv"),
        ("recipe_ingredients", "data/processed/recipe_ingredients.csv")
    ]
    
    for table_name, csv_path in tables_map:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Add food_state default if missing in foods
            if table_name == "foods" and "food_state" not in df.columns:
                df["food_state"] = df["canonical_name_vi"].apply(
                    lambda name: "COOKED" if any(w in name.lower() for w in ["chín", "luộc", "hấp", "xào", "nấu", "rán"]) else "RAW"
                )
            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"[OK] Seeded table '{table_name}' with {len(df)} records.")

    # 3. Seed Nutrients Master
    cursor.executemany("""
        INSERT INTO nutrients (id, code, name_en, name_vi, unit, category, daily_recommended, who_upper_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, NUTRIENTS_DATA)
    print(f"[OK] Seeded 30+ nutrients criteria.")

    # 4. Populate Relational Food Nutrients matrix from foods
    df_foods = pd.read_sql_query("SELECT * FROM foods", conn)
    food_nutrients_rows = []
    for _, f in df_foods.iterrows():
        fid = int(f["id"])
        # Map core macros to nutrients table
        food_nutrients_rows.append((fid, 1, float(f.get("calories_kcal_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 2, float(f.get("protein_g_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 3, float(f.get("carb_g_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 4, float(f.get("fat_g_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 7, float(f.get("fiber_g_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 8, float(f.get("sugar_g_100g", 0)), "per_100g_edible", 1, 1.0))
        food_nutrients_rows.append((fid, 10, float(f.get("sodium_mg_100g", 0)), "per_100g_edible", 1, 1.0))

    cursor.executemany("""
        INSERT OR IGNORE INTO food_nutrients (food_id, nutrient_id, value, basis, source_id, confidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """, food_nutrients_rows)
    print(f"[OK] Seeded {len(food_nutrients_rows)} relational food nutrient records.")

    # 5. Seed Guideline Sources & Rules
    cursor.executemany("""
        INSERT INTO guideline_sources (id, organization, title, version, source_url, published_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, GUIDELINE_SOURCES)

    cursor.executemany("""
        INSERT INTO guideline_rules (id, source_id, rule_code, population, nutrient, min_value, max_value, unit, scope, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, GUIDELINE_RULES)
    print(f"[OK] Seeded WHO guidelines and rules.")

    # 6. Seed Unit Conversions
    cursor.executemany("""
        INSERT INTO unit_conversions (id, food_id, from_unit, to_unit, conversion_value, conversion_source)
        VALUES (?, ?, ?, ?, ?, ?)
    """, UNIT_CONVERSIONS)

    # 7. Seed Recipe Steps
    cursor.executemany("""
        INSERT INTO recipe_steps (recipe_id, step_number, instruction_vi, duration_min)
        VALUES (?, ?, ?, ?)
    """, RECIPE_STEPS)

    # 8. Seed API Sources Registry
    cursor.executemany("""
        INSERT INTO api_sources (id, name, base_url, source_type, enabled, rate_limit_per_min)
        VALUES (?, ?, ?, ?, ?, ?)
    """, API_SOURCES)

    # 9. Seed Default Administrative & Demo Accounts (Configurable via Environment Variables)
    admin_pw = os.getenv("NUTRIDSS_ADMIN_PASSWORD")
    demo_pw = os.getenv("NUTRIDSS_DEMO_PASSWORD")
    
    if not admin_pw:
        admin_pw = "NutriDSS@2026"
        print("[SECURITY NOTICE] NUTRIDSS_ADMIN_PASSWORD not set. Using dev default for local development only.")
    if not demo_pw:
        demo_pw = "DemoUser@123"
        print("[SECURITY NOTICE] NUTRIDSS_DEMO_PASSWORD not set. Using dev default for local development only.")

    admin_hash = hash_password(admin_pw)
    demo_hash = hash_password(demo_pw)
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, username, password_hash, role)
        VALUES (1, 'admin@nutridss.vn', 'admin', ?, 'ADMIN')
    """, (admin_hash,))
    cursor.execute("""
        INSERT OR REPLACE INTO users (id, email, username, password_hash, role)
        VALUES (2, 'demo@nutridss.vn', 'demouser', ?, 'USER')
    """, (demo_hash,))
    cursor.execute("""
        INSERT OR REPLACE INTO user_profiles (user_id, display_name, age, gender, height_cm, weight_kg, activity_level, health_goal, daily_budget_vnd)
        VALUES (2, 'Demo User', 26, 'MALE', 172.0, 68.0, 'MODERATE', 'LOSE_WEIGHT', 80000.0)
    """)

    conn.commit()
    conn.close()
    print("[SUCCESS] NutriDSS Database seeding V2 complete!")

if __name__ == "__main__":
    seed_database()
