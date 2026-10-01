"""
NutriDSS Database Seeder
Nạp toàn bộ dữ liệu CSV từ data/processed/ vào CSDL SQLite nutridss.db
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "database/nutridss.db"
SCHEMA_PATH = "database/schema.sql"

def seed_database():
    # Xóa DB cũ nếu có để khởi tạo sạch
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Đọc schema SQL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    
    # Seed tables
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
            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"[OK] Seeded table '{table_name}' with {len(df)} records.")
            
    conn.commit()
    conn.close()
    print("[SUCCESS] NutriDSS Database seeding complete!")

if __name__ == "__main__":
    seed_database()
