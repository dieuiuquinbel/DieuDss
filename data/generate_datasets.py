"""
NutriDSS - Raw & Processed Dataset Generator
Tạo bộ dữ liệu chuẩn hóa chính thống từ Viện Dinh Dưỡng VN, USDA, WHO & Giá Siêu Thị VN (AEON, GO!, WinMart)
"""

import os
import sys
import pandas as pd
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Tạo thư mục dữ liệu nếu chưa có
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/dictionaries", exist_ok=True)

# ---------------------------------------------------------
# 1. FOOD GROUPS (Nhóm thực phẩm chuẩn)
# ---------------------------------------------------------
food_groups = [
    {"id": 1, "name_vi": "Thịt & Gia cẩm", "code": "MEAT"},
    {"id": 2, "name_vi": "Hải sản & Cá", "code": "FISH"},
    {"id": 3, "name_vi": "Trứng & Sản phẩm từ trứng", "code": "EGG"},
    {"id": 4, "name_vi": "Sữa & Sản phẩm từ sữa", "code": "DAIRY"},
    {"id": 5, "name_vi": "Rau củ & Quả tươi", "code": "VEG"},
    {"id": 6, "name_vi": "Tinh bột & Hạt ngũ cốc", "code": "CARB"},
    {"id": 7, "name_vi": "Đậu & Hạt dinh dưỡng", "code": "NUT"},
    {"id": 8, "name_vi": "Trái cây", "code": "FRUIT"},
    {"id": 9, "name_vi": "Gia vị & Dầu ăn", "code": "FAT_CONDIMENT"},
    {"id": 10, "name_vi": "Đồ uống & Món tráng miệng", "code": "BEVERAGE"}
]
pd.DataFrame(food_groups).to_csv("data/processed/food_groups.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 2. FOOD MASTER & NUTRIENTS (Dinh dưỡng / 100g edible portion)
# Nguồn: Bảng Thành Phần Thực Phẩm Việt Nam (Viện Dinh Dưỡng) & USDA
# ---------------------------------------------------------
foods_data = [
    # Tinh bột
    {"id": 101, "canonical_name_vi": "Gạo trắng (cơm chín)", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 130, "protein_g_100g": 2.7, "carb_g_100g": 28.2, "fat_g_100g": 0.3, "fiber_g_100g": 0.4, "sugar_g_100g": 0.1, "sodium_mg_100g": 1},
    {"id": 102, "canonical_name_vi": "Gạo lứt (cơm chín)", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 111, "protein_g_100g": 2.6, "carb_g_100g": 23.0, "fat_g_100g": 0.9, "fiber_g_100g": 1.8, "sugar_g_100g": 0.4, "sodium_mg_100g": 2},
    {"id": 103, "canonical_name_vi": "Khoai lang luộc", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 86, "protein_g_100g": 1.6, "carb_g_100g": 20.1, "fat_g_100g": 0.1, "fiber_g_100g": 3.0, "sugar_g_100g": 4.2, "sodium_mg_100g": 55},
    {"id": 104, "canonical_name_vi": "Bún tươi", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 110, "protein_g_100g": 1.7, "carb_g_100g": 25.7, "fat_g_100g": 0.1, "fiber_g_100g": 0.2, "sugar_g_100g": 0.1, "sodium_mg_100g": 22},
    {"id": 105, "canonical_name_vi": "Yến mạch chín", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 71, "protein_g_100g": 2.5, "carb_g_100g": 12.0, "fat_g_100g": 1.5, "fiber_g_100g": 1.7, "sugar_g_100g": 0.5, "sodium_mg_100g": 49},
    {"id": 106, "canonical_name_vi": "Bánh mì phở/ổ", "food_group_id": 6, "default_unit": "g", "calories_kcal_100g": 265, "protein_g_100g": 9.0, "carb_g_100g": 49.0, "fat_g_100g": 3.2, "fiber_g_100g": 2.7, "sugar_g_100g": 5.0, "sodium_mg_100g": 490},

    # Thịt & Trứng
    {"id": 201, "canonical_name_vi": "Ức gà (không da)", "food_group_id": 1, "default_unit": "g", "calories_kcal_100g": 165, "protein_g_100g": 31.0, "carb_g_100g": 0.0, "fat_g_100g": 3.6, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 74},
    {"id": 202, "canonical_name_vi": "Thịt lợn nạc (thăn)", "food_group_id": 1, "default_unit": "g", "calories_kcal_100g": 143, "protein_g_100g": 26.0, "carb_g_100g": 0.0, "fat_g_100g": 3.5, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 57},
    {"id": 203, "canonical_name_vi": "Thịt bò nạc", "food_group_id": 1, "default_unit": "g", "calories_kcal_100g": 250, "protein_g_100g": 26.0, "carb_g_100g": 0.0, "fat_g_100g": 15.0, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 72},
    {"id": 204, "canonical_name_vi": "Trứng gà", "food_group_id": 3, "default_unit": "quả", "calories_kcal_100g": 155, "protein_g_100g": 12.6, "carb_g_100g": 1.1, "fat_g_100g": 10.6, "fiber_g_100g": 0.0, "sugar_g_100g": 0.6, "sodium_mg_100g": 124},
    {"id": 205, "canonical_name_vi": "Thịt lợn ba chỉ", "food_group_id": 1, "default_unit": "g", "calories_kcal_100g": 518, "protein_g_100g": 9.3, "carb_g_100g": 0.0, "fat_g_100g": 53.0, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 32},

    # Hải sản
    {"id": 301, "canonical_name_vi": "Cá rô phi", "food_group_id": 2, "default_unit": "g", "calories_kcal_100g": 128, "protein_g_100g": 26.0, "carb_g_100g": 0.0, "fat_g_100g": 2.7, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 56},
    {"id": 302, "canonical_name_vi": "Tôm đồng/tôm sú", "food_group_id": 2, "default_unit": "g", "calories_kcal_100g": 99, "protein_g_100g": 24.0, "carb_g_100g": 0.2, "fat_g_100g": 0.3, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 111},
    {"id": 303, "canonical_name_vi": "Cá hồi", "food_group_id": 2, "default_unit": "g", "calories_kcal_100g": 208, "protein_g_100g": 20.0, "carb_g_100g": 0.0, "fat_g_100g": 13.0, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 59},
    {"id": 304, "canonical_name_vi": "Cá thu", "food_group_id": 2, "default_unit": "g", "calories_kcal_100g": 205, "protein_g_100g": 19.0, "carb_g_100g": 0.0, "fat_g_100g": 14.0, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 90},

    # Rau củ & Đậu
    {"id": 401, "canonical_name_vi": "Rau muống", "food_group_id": 5, "default_unit": "g", "calories_kcal_100g": 19, "protein_g_100g": 3.2, "carb_g_100g": 2.1, "fat_g_100g": 0.4, "fiber_g_100g": 1.0, "sugar_g_100g": 0.3, "sodium_mg_100g": 113},
    {"id": 402, "canonical_name_vi": "Bông cải xanh (Súp lơ)", "food_group_id": 5, "default_unit": "g", "calories_kcal_100g": 34, "protein_g_100g": 2.8, "carb_g_100g": 6.6, "fat_g_100g": 0.4, "fiber_g_100g": 2.6, "sugar_g_100g": 1.7, "sodium_mg_100g": 33},
    {"id": 403, "canonical_name_vi": "Cà rốt", "food_group_id": 5, "default_unit": "g", "calories_kcal_100g": 41, "protein_g_100g": 0.9, "carb_g_100g": 9.6, "fat_g_100g": 0.2, "fiber_g_100g": 2.8, "sugar_g_100g": 4.7, "sodium_mg_100g": 69},
    {"id": 404, "canonical_name_vi": "Đậu phụ (Tàu hũ)", "food_group_id": 7, "default_unit": "g", "calories_kcal_100g": 76, "protein_g_100g": 8.0, "carb_g_100g": 1.9, "fat_g_100g": 4.8, "fiber_g_100g": 0.3, "sugar_g_100g": 0.4, "sodium_mg_100g": 7},
    {"id": 405, "canonical_name_vi": "Bắp cải", "food_group_id": 5, "default_unit": "g", "calories_kcal_100g": 25, "protein_g_100g": 1.3, "carb_g_100g": 5.8, "fat_g_100g": 0.1, "fiber_g_100g": 2.5, "sugar_g_100g": 3.2, "sodium_mg_100g": 18},
    {"id": 406, "canonical_name_vi": "Cà chua", "food_group_id": 5, "default_unit": "g", "calories_kcal_100g": 18, "protein_g_100g": 0.9, "carb_g_100g": 3.9, "fat_g_100g": 0.2, "fiber_g_100g": 1.2, "sugar_g_100g": 2.6, "sodium_mg_100g": 5},

    # Gia vị / Khác
    {"id": 501, "canonical_name_vi": "Dầu thực vật/dầu ăn", "food_group_id": 9, "default_unit": "ml", "calories_kcal_100g": 884, "protein_g_100g": 0.0, "carb_g_100g": 0.0, "fat_g_100g": 100.0, "fiber_g_100g": 0.0, "sugar_g_100g": 0.0, "sodium_mg_100g": 0},
    {"id": 502, "canonical_name_vi": "Chuối chín", "food_group_id": 8, "default_unit": "quả", "calories_kcal_100g": 89, "protein_g_100g": 1.1, "carb_g_100g": 22.8, "fat_g_100g": 0.3, "fiber_g_100g": 2.6, "sugar_g_100g": 12.2, "sodium_mg_100g": 1},
    {"id": 503, "canonical_name_vi": "Trà sữa trân châu (đường chuẩn)", "food_group_id": 10, "default_unit": "ly", "calories_kcal_100g": 90, "protein_g_100g": 0.6, "carb_g_100g": 16.0, "fat_g_100g": 2.5, "fiber_g_100g": 0.2, "sugar_g_100g": 14.0, "sodium_mg_100g": 35}
]

df_foods = pd.DataFrame(foods_data)
df_foods.to_csv("data/processed/food_master.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 3. FOOD PRICES (Giá siêu thị Việt Nam: AEON, GO!, WinMart)
# ---------------------------------------------------------
prices_data = [
    # Gạo trắng
    {"food_id": 101, "store_name": "GO! Vietnam", "store_product_name": "Gạo ST25 5kg", "price_vnd": 145000, "quantity_g": 5000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    {"food_id": 101, "store_name": "WinMart", "store_product_name": "Gạo Tám Thái 5kg", "price_vnd": 160000, "quantity_g": 5000, "region": "Hà Nội/HCM", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Gạo lứt
    {"food_id": 102, "store_name": "AEON EShop", "store_product_name": "Gạo lứt đỏ 1kg", "price_vnd": 42000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    {"food_id": 102, "store_name": "GO! Vietnam", "store_product_name": "Gạo lứt huyết rồng 1kg", "price_vnd": 38000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": True, "source_url": "https://go-vietnam.vn"},
    # Khoai lang luộc / củ
    {"food_id": 103, "store_name": "GO! Vietnam", "store_product_name": "Khoai lang mật Đà Lạt 1kg", "price_vnd": 28000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    {"food_id": 103, "store_name": "WinMart", "store_product_name": "Khoai lang vàng WinEco 1kg", "price_vnd": 30000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Bún tươi
    {"food_id": 104, "store_name": "WinMart", "store_product_name": "Bún tươi sạch Ba Khánh 500g", "price_vnd": 12000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 104, "store_name": "GO! Vietnam", "store_product_name": "Bún tươi sợi nhỏ gói 500g", "price_vnd": 11000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Yến mạch chín / cán
    {"food_id": 105, "store_name": "AEON EShop", "store_product_name": "Yến mạch Úc nguyên chất 500g", "price_vnd": 42000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    {"food_id": 105, "store_name": "WinMart", "store_product_name": "Yến mạch cán mỏng 400g", "price_vnd": 36000, "quantity_g": 400, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Bánh mì
    {"food_id": 106, "store_name": "WinMart", "store_product_name": "Bánh mì baguette 250g", "price_vnd": 10000, "quantity_g": 250, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 106, "store_name": "GO! Vietnam", "store_product_name": "Bánh mì sandwich gối 275g", "price_vnd": 16000, "quantity_g": 275, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Ức gà
    {"food_id": 201, "store_name": "AEON EShop", "store_product_name": "Ức gà phi lê tươi 500g", "price_vnd": 45000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    {"food_id": 201, "store_name": "WinMart", "store_product_name": "Ức gà CP 500g", "price_vnd": 48000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 201, "store_name": "GO! Vietnam", "store_product_name": "Ức gà tươi khay 500g", "price_vnd": 42000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": True, "source_url": "https://go-vietnam.vn"},
    # Thịt lợn thăn
    {"food_id": 202, "store_name": "WinMart", "store_product_name": "Thịt thăn lợn MeatDeli 400g", "price_vnd": 62000, "quantity_g": 400, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 202, "store_name": "GO! Vietnam", "store_product_name": "Thịt lợn thăn tươi 1kg", "price_vnd": 135000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Thịt bò
    {"food_id": 203, "store_name": "AEON EShop", "store_product_name": "Thịt bò thăn Úc 300g", "price_vnd": 95000, "quantity_g": 300, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    # Trứng gà
    {"food_id": 204, "store_name": "WinMart", "store_product_name": "Trứng gà vỉ 10 quả", "price_vnd": 31000, "quantity_g": 600, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 204, "store_name": "GO! Vietnam", "store_product_name": "Trứng gà Ba Huân 10 quả", "price_vnd": 28500, "quantity_g": 600, "region": "Toàn quốc", "promotion_flag": True, "source_url": "https://go-vietnam.vn"},
    # Thịt lợn ba chỉ
    {"food_id": 205, "store_name": "WinMart", "store_product_name": "Thịt ba chỉ MeatDeli 400g", "price_vnd": 72000, "quantity_g": 400, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 205, "store_name": "GO! Vietnam", "store_product_name": "Thịt ba chỉ heo tươi 500g", "price_vnd": 75000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Cá rô phi
    {"food_id": 301, "store_name": "GO! Vietnam", "store_product_name": "Cá rô phi làm sạch 1kg", "price_vnd": 55000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Tôm đồng
    {"food_id": 302, "store_name": "AEON EShop", "store_product_name": "Tôm thẻ chân trắng 500g", "price_vnd": 98000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    # Cá hồi
    {"food_id": 303, "store_name": "AEON EShop", "store_product_name": "Cá hồi Nauy phi lê tươi 300g", "price_vnd": 165000, "quantity_g": 300, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    {"food_id": 303, "store_name": "WinMart", "store_product_name": "Cá hồi Nauy khay 250g", "price_vnd": 140000, "quantity_g": 250, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Cá thu
    {"food_id": 304, "store_name": "GO! Vietnam", "store_product_name": "Cá thu cắt khúc tươi 500g", "price_vnd": 115000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    {"food_id": 304, "store_name": "AEON EShop", "store_product_name": "Cá thu tươi làm sạch 400g", "price_vnd": 96000, "quantity_g": 400, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    # Rau muống
    {"food_id": 401, "store_name": "WinMart", "store_product_name": "Rau muống sạch WinEco 500g", "price_vnd": 15000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Bông cải xanh
    {"food_id": 402, "store_name": "AEON EShop", "store_product_name": "Súp lơ xanh Đà Lạt 500g", "price_vnd": 24000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://aeoneshop.com"},
    # Cà rốt
    {"food_id": 403, "store_name": "WinMart", "store_product_name": "Cà rốt Đà Lạt WinEco 500g", "price_vnd": 14000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 403, "store_name": "GO! Vietnam", "store_product_name": "Cà rốt tươi loại 1 1kg", "price_vnd": 22000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Đậu phụ
    {"food_id": 404, "store_name": "WinMart", "store_product_name": "Đậu phụ làng Mơ 300g", "price_vnd": 12000, "quantity_g": 300, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Bắp cải
    {"food_id": 405, "store_name": "WinMart", "store_product_name": "Bắp cải trắng WinEco 1kg", "price_vnd": 18000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 405, "store_name": "GO! Vietnam", "store_product_name": "Bắp cải thảo/trắng Đà Lạt 1kg", "price_vnd": 16000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": True, "source_url": "https://go-vietnam.vn"},
    # Cà chua
    {"food_id": 406, "store_name": "WinMart", "store_product_name": "Cà chua WinEco sạch 500g", "price_vnd": 14000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    {"food_id": 406, "store_name": "GO! Vietnam", "store_product_name": "Cà chua tươi khay 1kg", "price_vnd": 24000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Dầu ăn
    {"food_id": 501, "store_name": "GO! Vietnam", "store_product_name": "Dầu ăn Simply 1 Lit", "price_vnd": 58000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://go-vietnam.vn"},
    # Chuối
    {"food_id": 502, "store_name": "WinMart", "store_product_name": "Chuối nải 1kg", "price_vnd": 25000, "quantity_g": 1000, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://winmart.vn"},
    # Trà sữa
    {"food_id": 503, "store_name": "Cửa hàng trà sữa", "store_product_name": "Trà sữa trân châu size M", "price_vnd": 45000, "quantity_g": 500, "region": "Toàn quốc", "promotion_flag": False, "source_url": "https://menu.com"}
]

df_prices = pd.DataFrame(prices_data)
# Tính giá chuẩn hóa VND/100g và VND/kg
df_prices["normalized_price_per_100g"] = (df_prices["price_vnd"] / df_prices["quantity_g"]) * 100
df_prices["normalized_price_per_kg"] = df_prices["normalized_price_per_100g"] * 10
df_prices.to_csv("data/processed/food_prices.csv", index=False, encoding="utf-8-sig")

# Tính giá trung vị (Median Price Summary) cho Planner
price_summary = df_prices.groupby("food_id")["normalized_price_per_100g"].agg(
    price_min='min',
    price_median='median',
    price_max='max',
    sample_count='count'
).reset_index()
price_summary["estimated_price_per_100g"] = price_summary["price_median"]
price_summary.to_csv("data/processed/food_price_summary.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 4. ALLERGENS (Dị ứng & Safety Constraints)
# ---------------------------------------------------------
allergens = [
    {"id": 1, "code": "SEAFOOD", "name_vi": "Hải sản (Tôm, Cua, Cá)", "description": "Dị ứng với tôm, cua, mực, cá biển"},
    {"id": 2, "code": "PEANUT", "name_vi": "Đậu phộng / Lạc", "description": "Dị ứng các loại hạt đậu phộng"},
    {"id": 3, "code": "EGG", "name_vi": "Trứng", "description": "Dị ứng lòng đỏ/lòng trắng trứng gà, vịt"},
    {"id": 4, "code": "LACTOSE", "name_vi": "Sữa & Phô mai (Lactose)", "description": "Bất dung nạp đường lactose trong sữa"},
    {"id": 5, "code": "SOY", "name_vi": "Đậu nành (Soybean)", "description": "Dị ứng sản phẩm chế biến từ đậu nành, đậu phụ"},
    {"id": 6, "code": "GLUTEN", "name_vi": "Gluten / Lúa mì", "description": "Dị ứng gluten trong bánh mì, mì mì phở lúa mì"}
]
pd.DataFrame(allergens).to_csv("data/processed/allergens.csv", index=False, encoding="utf-8-sig")

food_allergens = [
    {"food_id": 301, "allergen_id": 1},  # Cá rô phi -> Seafood
    {"food_id": 302, "allergen_id": 1},  # Tôm -> Seafood
    {"food_id": 303, "allergen_id": 1},  # Cá hồi -> Seafood
    {"food_id": 304, "allergen_id": 1},  # Cá thu -> Seafood
    {"food_id": 204, "allergen_id": 3},  # Trứng gà -> Egg
    {"food_id": 404, "allergen_id": 5},  # Đậu phụ -> Soy
    {"food_id": 106, "allergen_id": 6},  # Bánh mì -> Gluten
    {"food_id": 503, "allergen_id": 4}   # Trà sữa -> Lactose
]
pd.DataFrame(food_allergens).to_csv("data/processed/food_allergens.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 5. RECIPES & INGREDIENTS (Món ăn & Công thức chuẩn)
# ---------------------------------------------------------
recipes = [
    {
        "id": 1001, "name_vi": "Cơm ức gà áp chảo & rau luộc", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "Dễ",
        "description": "Bữa ăn giàu protein, ít chất béo bão hòa thích hợp cho mục tiêu giảm cân và tăng cơ.",
        "source_name": "NutriDSS Chef", "tags": "giảm cân, nhiều protein, ít dầu, nhanh"
    },
    {
        "id": 1002, "name_vi": "Cơm gạo lứt, cá rô phi áp chảo & súp lơ", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 20, "difficulty": "Dễ",
        "description": "Thực đơn cân bằng dinh dưỡng, giàu chất xơ và đạm từ cá giúp tim mạch khỏe mạnh.",
        "source_name": "NutriDSS Chef", "tags": "cân bằng, giàu xơ, cá tươi, tiết kiệm"
    },
    {
        "id": 1003, "name_vi": "Khoai lang luộc & 2 trứng gà luộc", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 15, "difficulty": "Rất dễ",
        "description": "Bữa sáng siêu nhanh, tiết kiệm chi phí nhưng nạp đủ năng lượng bền vững cho buổi sáng.",
        "source_name": "NutriDSS Chef", "tags": "bữa sáng, cực nhanh, giá rẻ, ít calo"
    },
    {
        "id": 1004, "name_vi": "Bún tôm xào rau muống", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 10, "difficulty": "Trung bình",
        "description": "Món ăn ngon miệng kết hợp tôm đồng tươi và rau muống giòn.",
        "source_name": "NutriDSS Chef", "tags": "ngon miệng, hải sản, bún"
    },
    {
        "id": 1005, "name_vi": "Cơm thịt thăn lợn luộc & bắp cải luộc", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "Dễ",
        "description": "Món ăn thanh nhẹ, ít chất béo, dễ chế biến cho gia đình.",
        "source_name": "NutriDSS Chef", "tags": "thịt lợn nạc, thanh nhẹ, gia đình"
    },
    {
        "id": 1006, "name_vi": "Yến mạch nấu trứng gà & chuối chín", "meal_type": "BREAKFAST", "servings": 1,
        "prep_time_min": 5, "cook_time_min": 10, "difficulty": "Dễ",
        "description": "Bữa sáng thơm ngon giàu chất xơ và kali tốt cho tiêu hóa.",
        "source_name": "NutriDSS Chef", "tags": "yến mạch, bữa sáng, tiêu hóa"
    },
    {
        "id": 1007, "name_vi": "Cơm thịt bò xào súp lơ xanh & cà rốt", "meal_type": "LUNCH", "servings": 1,
        "prep_time_min": 15, "cook_time_min": 15, "difficulty": "Trung bình",
        "description": "Bữa ăn đậm đà, bổ bổ máu và sắt cho cơ thể vận động nhiều.",
        "source_name": "NutriDSS Chef", "tags": "thịt bò, tăng cơ, giàu sắt"
    },
    {
        "id": 1008, "name_vi": "Đậu phụ sốt cà chua & cơm gạo lứt", "meal_type": "DINNER", "servings": 1,
        "prep_time_min": 10, "cook_time_min": 15, "difficulty": "Dễ",
        "description": "Món ăn chay thanh tịnh, tiết kiệm ngân sách nhưng vẫn đầy đủ chất đạm thực vật.",
        "source_name": "NutriDSS Chef", "tags": "ăn chay, tiết kiệm, đậu phụ, thanh tịnh"
    }
]

pd.DataFrame(recipes).to_csv("data/processed/recipe_master.csv", index=False, encoding="utf-8-sig")

recipe_ingredients = [
    # Recipe 1001: Cơm ức gà áp chảo & rau luộc
    {"recipe_id": 1001, "food_id": 101, "quantity_g": 150}, # Cơm gạo trắng 150g
    {"recipe_id": 1001, "food_id": 201, "quantity_g": 200}, # Ức gà 200g
    {"recipe_id": 1001, "food_id": 401, "quantity_g": 100}, # Rau muống 100g
    {"recipe_id": 1001, "food_id": 501, "quantity_g": 5},   # Dầu ăn 5ml

    # Recipe 1002: Cơm gạo lứt, cá rô phi & súp lơ
    {"recipe_id": 1002, "food_id": 102, "quantity_g": 150}, # Gạo lứt 150g
    {"recipe_id": 1002, "food_id": 301, "quantity_g": 180}, # Cá rô phi 180g
    {"recipe_id": 1002, "food_id": 402, "quantity_g": 120}, # Súp lơ 120g
    {"recipe_id": 1002, "food_id": 501, "quantity_g": 5},   # Dầu ăn 5ml

    # Recipe 1003: Khoai lang luộc & 2 trứng gà
    {"recipe_id": 1003, "food_id": 103, "quantity_g": 180}, # Khoai lang 180g
    {"recipe_id": 1003, "food_id": 204, "quantity_g": 110}, # 2 quả trứng gà ~110g

    # Recipe 1004: Bún tôm xào rau muống
    {"recipe_id": 1004, "food_id": 104, "quantity_g": 180}, # Bún tươi 180g
    {"recipe_id": 1004, "food_id": 302, "quantity_g": 120}, # Tôm 120g
    {"recipe_id": 1004, "food_id": 401, "quantity_g": 100}, # Rau muống 100g
    {"recipe_id": 1004, "food_id": 501, "quantity_g": 8},   # Dầu 8ml

    # Recipe 1005: Cơm thịt lợn luộc & bắp cải
    {"recipe_id": 1005, "food_id": 101, "quantity_g": 150}, # Cơm 150g
    {"recipe_id": 1005, "food_id": 202, "quantity_g": 150}, # Thịt thăn lợn 150g
    {"recipe_id": 1005, "food_id": 405, "quantity_g": 120}, # Bắp cải 120g

    # Recipe 1006: Yến mạch trứng & chuối
    {"recipe_id": 1006, "food_id": 105, "quantity_g": 60},  # Yến mạch 60g
    {"recipe_id": 1006, "food_id": 204, "quantity_g": 55},  # 1 trứng 55g
    {"recipe_id": 1006, "food_id": 502, "quantity_g": 100}, # Chuối 100g

    # Recipe 1007: Cơm thịt bò súp lơ
    {"recipe_id": 1007, "food_id": 101, "quantity_g": 150}, # Cơm 150g
    {"recipe_id": 1007, "food_id": 203, "quantity_g": 120}, # Thịt bò 120g
    {"recipe_id": 1007, "food_id": 402, "quantity_g": 100}, # Súp lơ 100g
    {"recipe_id": 1007, "food_id": 403, "quantity_g": 50},  # Cà rốt 50g
    {"recipe_id": 1007, "food_id": 501, "quantity_g": 8},   # Dầu 8ml

    # Recipe 1008: Đậu phụ sốt cà chua & gạo lứt
    {"recipe_id": 1008, "food_id": 102, "quantity_g": 150}, # Gạo lứt 150g
    {"recipe_id": 1008, "food_id": 404, "quantity_g": 150}, # Đậu phụ 150g
    {"recipe_id": 1008, "food_id": 406, "quantity_g": 80},  # Cà chua 80g
    {"recipe_id": 1008, "food_id": 501, "quantity_g": 5}    # Dầu 5ml
]

pd.DataFrame(recipe_ingredients).to_csv("data/processed/recipe_ingredients.csv", index=False, encoding="utf-8-sig")

# ---------------------------------------------------------
# 6. ML TRAINING DATASET GENERATOR (Tập khảo sát 300+ kịch bản)
# Để huấn luyện Linear Regression, KNN, Decision Tree, Random Forest, ANN
# Target: compatibility_rating (1.0 đến 5.0)
# ---------------------------------------------------------
np.random.seed(42)
scenarios = []

goals = ["LOSE_WEIGHT", "GAIN_WEIGHT", "MAINTAIN", "HIGH_PROTEIN"]
meal_types = ["BREAKFAST", "LUNCH", "DINNER"]
df_rec_master = pd.DataFrame(recipes)

for i in range(1, 401):
    rec = recipes[i % len(recipes)]
    goal = np.random.choice(goals)
    user_budget = np.random.choice([20000, 30000, 40000, 50000, 70000])
    
    # Tính dinh dưỡng và chi phí công thức ngẫu nhiên
    recipe_ings = [ing for ing in recipe_ingredients if ing["recipe_id"] == rec["id"]]
    cal = 0
    prot = 0
    carb = 0
    fat = 0
    cost = 0
    
    for ing in recipe_ings:
        f = next(item for item in foods_data if item["id"] == ing["food_id"])
        qty = ing["quantity_g"]
        cal += (f["calories_kcal_100g"] / 100.0) * qty
        prot += (f["protein_g_100g"] / 100.0) * qty
        carb += (f["carb_g_100g"] / 100.0) * qty
        fat += (f["fat_g_100g"] / 100.0) * qty
        
        # Lấy giá median
        p_med = df_prices[df_prices["food_id"] == ing["food_id"]]["normalized_price_per_100g"].median()
        cost += (p_med / 100.0) * qty
        
    # Tính điểm giả lập khoa học (Ground Truth cho Survey Rating)
    base_score = 4.0
    
    # Phạt nếu vượt ngân sách
    if cost > user_budget:
        budget_diff = (cost - user_budget) / user_budget
        base_score -= min(2.0, budget_diff * 3.0)
    else:
        base_score += 0.3
        
    # Phạt theo mục tiêu
    if goal == "LOSE_WEIGHT":
        if cal > 550: base_score -= 1.2
        if prot >= 25: base_score += 0.5
    elif goal == "HIGH_PROTEIN":
        if prot >= 30: base_score += 0.8
        elif prot < 20: base_score -= 1.0
    elif goal == "GAIN_WEIGHT":
        if cal < 400: base_score -= 0.8
        else: base_score += 0.4
        
    # Nhiễu ngẫu nhiên khảo sát (+- 0.3)
    rating = round(float(np.clip(base_score + np.random.normal(0, 0.25), 1.0, 5.0)), 2)
    
    scenarios.append({
        "scenario_id": i,
        "user_id": (i % 50) + 1,
        "goal": goal,
        "budget_vnd": user_budget,
        "recipe_id": rec["id"],
        "recipe_name": rec["name_vi"],
        "meal_type": rec["meal_type"],
        "calories": round(cal, 1),
        "protein_g": round(prot, 1),
        "carb_g": round(carb, 1),
        "fat_g": round(fat, 1),
        "estimated_cost_vnd": round(cost, 0),
        "cost_ratio": round(cost / user_budget, 2),
        "compatibility_rating": rating
    })

df_scenarios = pd.DataFrame(scenarios)
df_scenarios.to_csv("data/processed/synthetic_baseline_dataset.csv", index=False, encoding="utf-8-sig")
# Keep survey_scenarios_dataset.csv for backward compatibility
df_scenarios.to_csv("data/processed/survey_scenarios_dataset.csv", index=False, encoding="utf-8-sig")

# Initialize Real User Interaction Feedback Schema (Fix.md Section 19)
df_interactions = pd.DataFrame(columns=[
    "id", "user_id", "recipe_id", "food_id", "event_type", "rating", "session_id", "metadata_json", "created_at"
])
df_interactions.to_csv("data/processed/user_interactions.csv", index=False, encoding="utf-8-sig")

print("[SUCCESS] ĐÃ KHỞI TẠO THÀNH CÔNG BỘ DỮ LIỆU NUTRIDSS CHUẨN HÓA:")
print(f" - Food Master: {len(df_foods)} thực phẩm")
print(f" - Price Records: {len(df_prices)} bản ghi từ AEON, GO!, WinMart")
print(f" - Recipe Master: {len(recipes)} món ăn chuẩn")
print(f" - ML Training Baseline Dataset: {len(df_scenarios)} mẫu kịch bản baseline")
print(" - Real User Interactions Table initialized for online learning.")
