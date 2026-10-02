# -*- coding: utf-8 -*-
"""
NutriDSS - Real Supermarket Store Prices & Seasonings Seeder
Populates multi-store price observations (WinMart, GO! Vietnam, AEON EShop)
Calculates exact Median (Giá tham chiếu) and Min/Max ranges for ingredients and seasonings.
"""

import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutridss.db")

# 1. Seasonings and key pantry items to ensure in `foods`
CORE_PANTRY_FOODS = [
    # (id, canonical_name_vi, food_group_id, food_state, default_unit, calories_100g, protein_100g, carb_100g, fat_100g, fiber_100g, sugar_100g, sodium_100g)
    (1504, "Nước mắm cá cơm", 5, "RAW", "ml", 35.0, 7.0, 1.8, 0.0, 0.0, 1.5, 7800.0),
    (1505, "Dầu ăn thực vật", 5, "RAW", "ml", 884.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0),
    (1506, "Muối ăn", 5, "RAW", "g", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 38758.0),
    (1507, "Đường cát trắng (Đường kính)", 5, "RAW", "g", 398.0, 0.0, 99.8, 0.0, 0.0, 99.8, 2.0),
    (1508, "Hạt nêm thịt thăn xương ống", 5, "RAW", "g", 180.0, 12.0, 25.0, 3.5, 0.0, 15.0, 18500.0),
    (1509, "Bột ngọt (Mì chính)", 5, "RAW", "g", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12280.0),
    (1510, "Nước tương (Xì dầu)", 5, "RAW", "ml", 53.0, 8.1, 4.9, 0.1, 0.8, 3.2, 5580.0),
    (1512, "Tiêu đen xay", 5, "RAW", "g", 251.0, 10.4, 64.0, 3.3, 25.3, 0.6, 20.0),
    (1514, "Tỏi củ tươi", 4, "RAW", "g", 149.0, 6.4, 33.1, 0.5, 2.1, 1.0, 17.0),
    (1515, "Hành tím (Hành củ khô)", 4, "RAW", "g", 75.0, 2.5, 16.8, 0.1, 3.2, 7.9, 12.0),
    (1516, "Hành lá tươi", 4, "RAW", "g", 32.0, 1.8, 7.3, 0.2, 2.6, 2.3, 16.0),
    (1517, "Ớt chỉ thiên / ớt tươi", 4, "RAW", "g", 40.0, 1.9, 8.8, 0.4, 1.5, 5.3, 9.0),
    (1518, "Gừng tươi", 4, "RAW", "g", 80.0, 1.8, 17.8, 0.8, 2.0, 1.7, 13.0),
    (1519, "Sả cây tươi", 4, "RAW", "g", 99.0, 1.8, 25.3, 0.5, 4.2, 0.0, 6.0),
    (1520, "Hành tây", 4, "RAW", "g", 40.0, 1.1, 9.3, 0.1, 1.7, 4.2, 4.0),
    (2103, "Lòng bò tươi làm sạch", 2, "RAW", "g", 96.0, 14.5, 0.0, 4.2, 0.0, 0.0, 85.0),
    (410, "Lá lốt tươi", 4, "RAW", "g", 39.0, 4.3, 6.1, 0.5, 2.5, 0.0, 15.0),
    (2151, "Măng chua / Dưa cải muối chua", 4, "RAW", "g", 19.0, 1.2, 3.5, 0.1, 1.5, 1.2, 850.0),
]

# 2. Multi-store Price Observations (AEON, GO!, WinMart, Bách Hóa Xanh / Chợ)
# Tuple: (food_id, store_name, product_name, price_vnd, quantity_g, region)
MULTI_STORE_PRICES = [
    # Lòng bò (2103) - Example directly from user's image 18
    (2103, "AEON EShop", "Lòng bò tươi làm sạch khay 500g", 49000, 500, "Toàn quốc"),      # 98k/kg
    (2103, "WinMart", "Lòng bò sạch MeatDeli khay 500g", 51000, 500, "Toàn quốc"),         # 102k/kg
    (2103, "GO! Vietnam", "Lòng bò tươi loại 1 khay 500g", 52500, 500, "Toàn quốc"),       # 105k/kg

    # Thịt bò thăn (203)
    (203, "WinMart", "Thịt bò thăn Úc MeatDeli 300g", 96000, 300, "Toàn quốc"),            # 320k/kg
    (203, "GO! Vietnam", "Thịt thăn bò tươi 500g", 145000, 500, "Toàn quốc"),              # 290k/kg
    (203, "AEON EShop", "Thịt bò thăn mềm 300g", 93000, 300, "Toàn quốc"),                # 310k/kg

    # Lá lốt tươi (410)
    (410, "WinMart", "Lá lốt tươi WinEco túi 100g", 5500, 100, "Toàn quốc"),               # 55k/kg
    (410, "GO! Vietnam", "Lá lốt sạch túi 100g", 4800, 100, "Toàn quốc"),                  # 48k/kg
    (410, "Bách Hóa Xanh", "Lá lốt tươi bó 100g", 5000, 100, "Toàn quốc"),                 # 50k/kg

    # Muối ăn (1506)
    (1506, "WinMart", "Muối i-ốt Bạc Liêu gói 1kg", 11000, 1000, "Toàn quốc"),             # 11k/kg -> 1.1k/100g -> 5g = 55d
    (1506, "GO! Vietnam", "Muối tinh sấy i-ốt Visalco 1kg", 10000, 1000, "Toàn quốc"),     # 10k/kg -> 1.0k/100g -> 5g = 50d
    (1506, "AEON EShop", "Muối hạt tinh khiết 1kg", 9000, 1000, "Toàn quốc"),              # 9k/kg

    # Đường cát trắng (1507)
    (1507, "WinMart", "Đường tinh luyện Biên Hòa túi 1kg", 27000, 1000, "Toàn quốc"),      # 27k/kg
    (1507, "GO! Vietnam", "Đường trắng cao cấp Lam Sơn 1kg", 25000, 1000, "Toàn quốc"),     # 25k/kg
    (1507, "AEON EShop", "Đường tinh luyện Toàn Phát 1kg", 26000, 1000, "Toàn quốc"),      # 26k/kg

    # Bột ngọt / Mì chính (1509)
    (1509, "WinMart", "Bột ngọt Ajinomoto gói 454g", 28000, 454, "Toàn quốc"),             # 61.6k/kg -> 5g = 308d
    (1509, "GO! Vietnam", "Bột ngọt Ajinomoto gói 400g", 24000, 400, "Toàn quốc"),         # 60k/kg -> 5g = 300d
    (1509, "AEON EShop", "Mì chính Vedan gói 400g", 22000, 400, "Toàn quốc"),             # 55k/kg -> 5g = 275d

    # Hạt nêm (1508)
    (1508, "WinMart", "Hạt nêm Knorr thịt thăn xương ống gói 400g", 36000, 400, "Toàn quốc"), # 90k/kg
    (1508, "GO! Vietnam", "Hạt nêm Knorr gói 400g", 34000, 400, "Toàn quốc"),              # 85k/kg
    (1508, "AEON EShop", "Hạt nêm Maggi xương hầm gói 400g", 32000, 400, "Toàn quốc"),     # 80k/kg

    # Dầu ăn thực vật (1505)
    (1505, "WinMart", "Dầu đậu nành Simply chai 1 Lít", 58000, 1000, "Toàn quốc"),         # 58k/lít -> 10ml = 580d
    (1505, "GO! Vietnam", "Dầu ăn thực vật Tường An Cooking Oil chai 1L", 45000, 1000, "Toàn quốc"), # 45k/lít -> 10ml = 450d
    (1505, "AEON EShop", "Dầu ăn Meizan chai 1 Lít", 42000, 1000, "Toàn quốc"),            # 42k/lít -> 10ml = 420d

    # Nước mắm cá cơm (1504)
    (1504, "WinMart", "Nước mắm Nam Ngư Đệ Nhị chai 900ml", 36000, 900, "Toàn quốc"),      # 40k/lít -> 5ml = 200d
    (1504, "GO! Vietnam", "Nước mắm Nam Ngư chai 750ml", 30000, 750, "Toàn quốc"),         # 40k/lít
    (1504, "AEON EShop", "Nước mắm cá cơm truyền thống 500ml", 25000, 500, "Toàn quốc"),   # 50k/lít

    # Nước tương / Xì dầu (1510)
    (1510, "WinMart", "Nước tương Maggi Đậm Đặc chai 700ml", 28000, 700, "Toàn quốc"),     # 40k/lít
    (1510, "GO! Vietnam", "Nước tương Chinsu tỏi ớt chai 330ml", 15000, 330, "Toàn quốc"),  # 45.4k/lít

    # Tiêu đen xay (1512)
    (1512, "WinMart", "Tiêu đen xay Dh Foods hũ 55g", 24000, 55, "Toàn quốc"),             # 436k/kg
    (1512, "GO! Vietnam", "Tiêu đen xay gói 100g", 38000, 100, "Toàn quốc"),              # 380k/kg
    (1512, "AEON EShop", "Tiêu đen nguyên hạt/xay 100g", 40000, 100, "Toàn quốc"),        # 400k/kg

    # Tỏi củ tươi (1514)
    (1514, "WinMart", "Tỏi Hải Dương túi 300g", 24000, 300, "Toàn quốc"),                  # 80k/kg
    (1514, "GO! Vietnam", "Tỏi củ tươi loại 1 500g", 37000, 500, "Toàn quốc"),             # 74k/kg
    (1514, "Bách Hóa Xanh", "Tỏi củ tươi 300g", 22000, 300, "Toàn quốc"),                 # 73.3k/kg

    # Hành tím khô (1515)
    (1515, "WinMart", "Hành tím Vĩnh Châu túi 300g", 21000, 300, "Toàn quốc"),             # 70k/kg
    (1515, "GO! Vietnam", "Hành tím củ khô 500g", 32000, 500, "Toàn quốc"),               # 64k/kg

    # Hành lá tươi (1516)
    (1516, "WinMart", "Hành lá sạch WinEco bó 100g", 5000, 100, "Toàn quốc"),              # 50k/kg
    (1516, "GO! Vietnam", "Hành lá tươi bó 100g", 4500, 100, "Toàn quốc"),                # 45k/kg

    # Ớt tươi (1517)
    (1517, "WinMart", "Ớt chỉ thiên cay WinEco 100g", 6000, 100, "Toàn quốc"),             # 60k/kg
    (1517, "GO! Vietnam", "Ớt hiểm tươi khay 100g", 5000, 100, "Toàn quốc"),              # 50k/kg

    # Gừng tươi (1518)
    (1518, "WinMart", "Gừng sẻ tươi WinEco 200g", 12000, 200, "Toàn quốc"),                # 60k/kg
    (1518, "GO! Vietnam", "Gừng ta củ tươi 300g", 16000, 300, "Toàn quốc"),               # 53k/kg

    # Dưa cải muối chua (2151)
    (2151, "WinMart", "Dưa cải chua đóng hộp sạch 500g", 18000, 500, "Toàn quốc"),         # 36k/kg
    (2151, "GO! Vietnam", "Dưa muối chua giòn 500g", 16000, 500, "Toàn quốc"),            # 32k/kg

    # Thịt ba chỉ heo (205)
    (205, "WinMart", "Thịt ba chỉ heo MeatDeli 400g", 72000, 400, "Toàn quốc"),            # 180k/kg
    (205, "GO! Vietnam", "Thịt ba chỉ tươi CP 500g", 75000, 500, "Toàn quốc"),             # 150k/kg
    (205, "AEON EShop", "Thịt ba rọi heo tươi 500g", 80000, 500, "Toàn quốc"),            # 160k/kg

    # Trứng gà (204)
    (204, "WinMart", "Trứng gà tươi Ba Huân vỉ 10 quả", 31000, 600, "Toàn quốc"),          # 3.100d/qua (~51.6k/kg)
    (204, "GO! Vietnam", "Trứng gà tươi CP vỉ 10 quả", 28500, 600, "Toàn quốc"),           # 2.850d/qua (~47.5k/kg)
    (204, "AEON EShop", "Trứng gà so sinh thái vỉ 10 quả", 32000, 600, "Toàn quốc"),      # 3.200d/qua (~53.3k/kg)

    # Đậu phụ / Đậu hũ (404)
    (404, "WinMart", "Đậu hũ non làng Mơ hộp 300g", 12000, 300, "Toàn quốc"),             # 40k/kg
    (404, "GO! Vietnam", "Đậu hũ trắng miếng 300g", 10000, 300, "Toàn quốc"),              # 33.3k/kg
    (404, "AEON EShop", "Đậu phụ sạch Ichiban 300g", 11000, 300, "Toàn quốc"),            # 36.7k/kg

    # Nấm bào ngư (2206)
    (2206, "WinMart", "Nấm bào ngư trắng túi 200g", 14000, 200, "Toàn quốc"),             # 70k/kg
    (2206, "GO! Vietnam", "Nấm sò bào ngư tươi khay 250g", 15000, 250, "Toàn quốc"),      # 60k/kg

    # Rau muống (401)
    (401, "WinMart", "Rau muống sạch WinEco túi 500g", 15000, 500, "Toàn quốc"),           # 30k/kg
    (401, "GO! Vietnam", "Rau muống xanh bó 500g", 12000, 500, "Toàn quốc"),              # 24k/kg

    # Cà chua (406)
    (406, "WinMart", "Cà chua WinEco túi 500g", 14000, 500, "Toàn quốc"),                  # 28k/kg
    (406, "GO! Vietnam", "Cà chua tươi loại 1 khay 1kg", 24000, 1000, "Toàn quốc"),        # 24k/kg
]

def seed_prices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure food_prices and food_price_summary tables exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL,
            store_name TEXT NOT NULL,
            store_product_name TEXT NOT NULL,
            price_vnd REAL NOT NULL,
            quantity_g REAL NOT NULL,
            normalized_price_per_100g REAL NOT NULL,
            normalized_price_per_kg REAL NOT NULL,
            region TEXT,
            promotion_flag INTEGER DEFAULT 0,
            source_url TEXT,
            collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_price_summary (
            food_id INTEGER PRIMARY KEY,
            price_min REAL,
            price_median REAL,
            price_max REAL,
            estimated_price_per_100g REAL,
            sample_count INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (food_id) REFERENCES foods(id)
        )
    """)

    # 1. Upsert pantry and seasoning foods into `foods`
    print("[1/3] Inserting/Updating pantry & seasoning foods...")
    for f in CORE_PANTRY_FOODS:
        fid, name, gid, state, unit, cal, prot, carb, fat, fiber, sugar, sod = f
        cursor.execute("SELECT id FROM foods WHERE id = ?", (fid,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE foods 
                SET canonical_name_vi = ?, food_group_id = ?, food_state = ?, default_unit = ?,
                    calories_kcal_100g = ?, protein_g_100g = ?, carb_g_100g = ?, fat_g_100g = ?,
                    fiber_g_100g = ?, sugar_g_100g = ?, sodium_mg_100g = ?
                WHERE id = ?
            """, (name, gid, state, unit, cal, prot, carb, fat, fiber, sugar, sod, fid))
        else:
            cursor.execute("""
                INSERT INTO foods (id, canonical_name_vi, food_group_id, food_state, default_unit,
                                   calories_kcal_100g, protein_g_100g, carb_g_100g, fat_g_100g,
                                   fiber_g_100g, sugar_g_100g, sodium_mg_100g)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fid, name, gid, state, unit, cal, prot, carb, fat, fiber, sugar, sod))

    # 2. Insert multi-store observations into `food_prices`
    print("[2/3] Seeding multi-store price observations (AEON, WinMart, GO!)...")
    for row in MULTI_STORE_PRICES:
        fid, store, prod_name, price, qty, region = row
        p_100g = round((price / qty) * 100.0, 2)
        p_kg = round((price / qty) * 1000.0, 2)
        
        # Check if identical record already exists
        cursor.execute("""
            SELECT id FROM food_prices 
            WHERE food_id = ? AND store_name = ? AND store_product_name = ?
        """, (fid, store, prod_name))
        ex = cursor.fetchone()
        if ex:
            cursor.execute("""
                UPDATE food_prices 
                SET price_vnd = ?, quantity_g = ?, normalized_price_per_100g = ?, normalized_price_per_kg = ?
                WHERE id = ?
            """, (price, qty, p_100g, p_kg, ex[0]))
        else:
            cursor.execute("""
                INSERT INTO food_prices (food_id, store_name, store_product_name, price_vnd, quantity_g,
                                         normalized_price_per_100g, normalized_price_per_kg, region)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (fid, store, prod_name, price, qty, p_100g, p_kg, region))

    # 3. Recalculate `food_price_summary` with exact Median, Min, Max from `food_prices`
    print("[3/3] Calculating reference median, min, max prices...")
    cursor.execute("SELECT DISTINCT food_id FROM food_prices")
    distinct_fids = [r[0] for r in cursor.fetchall()]

    for fid in distinct_fids:
        cursor.execute("SELECT normalized_price_per_100g FROM food_prices WHERE food_id = ?", (fid,))
        prices = sorted([r[0] for r in cursor.fetchall()])
        if prices:
            n = len(prices)
            p_min = prices[0]
            p_max = prices[-1]
            if n % 2 == 1:
                p_med = prices[n // 2]
            else:
                p_med = round((prices[n // 2 - 1] + prices[n // 2]) / 2.0, 2)
            
            cursor.execute("""
                INSERT INTO food_price_summary (food_id, price_min, price_median, price_max, estimated_price_per_100g, sample_count)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(food_id) DO UPDATE SET
                    price_min = excluded.price_min,
                    price_median = excluded.price_median,
                    price_max = excluded.price_max,
                    estimated_price_per_100g = excluded.estimated_price_per_100g,
                    sample_count = excluded.sample_count,
                    updated_at = CURRENT_TIMESTAMP
            """, (fid, p_min, p_med, p_max, p_med, n))

    conn.commit()
    conn.close()
    print("[SUCCESS] Seeding real multi-store prices and seasonings complete!")

if __name__ == "__main__":
    seed_prices()
