# NutriDSS — Đặc tả phần mở rộng

# 35. DATABASE — THIẾT KẾ CHI TIẾT

Khuyến nghị:

> **MySQL 8 + MySQL Workbench**

---

---

# 36. NHÓM BẢNG USER

## `users`

```text
id
email
password_hash
role_id
status
created_at
updated_at
last_login_at
```

## `roles`

```text
id
name
```

## `user_profiles`

```text
id
user_id
display_name
date_of_birth / age_group
gender
height_cm
weight_kg
activity_level
health_goal
target_calories
target_protein
created_at
updated_at
```

## `user_preferences`

```text
id
user_id
spicy_level
sweet_level
salty_level
preferred_foods
disliked_foods
preferred_cuisines
preferred_meal_types
max_cooking_time
```

Không cần hỗ trợ taxonomy đa ngôn ngữ.

---

---

# 37. BẢNG DỊ ỨNG

## `allergens`

```text
id
name_vi
description
```

## `user_allergies`

```text
id
user_id
allergen_id
created_at
```

## `food_allergens`

```text
id
food_id
allergen_id
source
confidence
```

---

---

# 38. NHÓM BẢNG FOOD

## `food_groups`

```text
id
name_vi
```

## `foods`

```text
id
canonical_name_vi
food_group_id
default_unit
is_active
created_at
updated_at
```

## `food_aliases`

```text
id
food_id
alias_raw
normalized_text
source
confidence
```

## `food_nutrients`

```text
id
food_id
calories_kcal_100g
protein_g_100g
carb_g_100g
fat_g_100g
fiber_g_100g
sugar_g_100g
sodium_mg_100g
calcium_mg_100g
iron_mg_100g
vitamin_a_ug_100g
vitamin_c_mg_100g
```

## `food_sources`

```text
id
food_id
source_name
source_url
source_record_id
license
collected_at
```

---

---

# 39. BẢNG GIÁ

## `food_prices`

```text
id
food_id
store_name
store_product_name
price_vnd
quantity_g
normalized_price_per_100g
normalized_price_per_kg
region
location
promotion_flag
collected_at
source_url
source_type
```

## `food_price_summary`

Có thể là materialized/cache table:

```text
food_id
price_min
price_median
price_max
estimated_price
confidence_level
calculated_at
sample_count
```

Nếu không cần materialized table trong MVP, có thể tính bằng query/service.

---

---

# 40. RECIPE DATABASE

## `recipes`

```text
id
name_vi
description
meal_type
servings
prep_time_min
cook_time_min
difficulty
source_name
source_url
license
created_at
updated_at
```

## `recipe_ingredients`

```text
id
recipe_id
food_id
quantity
unit
notes
```

## `recipe_steps`

```text
id
recipe_id
step_no
instruction
```

## `recipe_tags`

```text
id
recipe_id
tag
```

Ví dụ tag:

```text
nhanh
ít dầu
nhiều protein
bữa sáng
bữa tối
tiết kiệm
```

---

---

# 41. MEAL PLAN

## `meal_plans`

```text
id
user_id
plan_type
start_date
end_date
budget_vnd
target_calories
target_protein
goal
status
created_at
updated_at
```

`plan_type`:

```text
MEAL
DAY
WEEK
MONTH
```

## `meal_plan_days`

```text
id
meal_plan_id
date
```

## `meal_plan_items`

```text
id
meal_plan_day_id
meal_type
recipe_id
food_id
quantity
servings
estimated_cost
calories
protein
carbs
fat
fiber
user_selected
created_at
```

---

---

# 42. USER-SELECTED FOOD

Khi user tự thêm món:

```text
meal_plan_items.user_selected = true
```

Hệ thống phải đánh giá món này cùng các món AI đề xuất.

---

---

# 43. FEEDBACK

## `food_interactions`

```text
id
user_id
food_id
action
rating
created_at
```

## `recipe_interactions`

```text
id
user_id
recipe_id
action
rating
created_at
```

---

---

# 44. MODEL VERSION

## `model_versions`

```text
id
model_name
model_type
version
dataset_version
metrics_json
model_path
trained_at
status
```

Ví dụ:

```text
RandomForest
food_acceptance
v1.0
F1 = 0.xx
```

---

---

# 45. AUDIT / SECURITY

## `audit_logs`

```text
id
user_id
action
object_type
object_id
result
created_at
```

Không log:

- password;
- token;
- dữ liệu nhạy cảm nguyên bản.

---

---

# 46. API DESIGN

## Auth

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/change-password
```

## Profile

```http
GET /api/profile
PUT /api/profile
PUT /api/preferences
PUT /api/allergies
```

## Food

```http
GET /api/foods
GET /api/foods/{id}
GET /api/foods/search?q=
```

## Recipes

```http
GET /api/recipes
GET /api/recipes/{id}
GET /api/recipes/search?q=
```

## Recommendation

```http
POST /api/recommendations/foods
POST /api/recommendations/meals
POST /api/recommendations/replacement
```

## Meal Plan

```http
POST /api/meal-plans/generate
GET /api/meal-plans
GET /api/meal-plans/{id}
POST /api/meal-plans/{id}/add
POST /api/meal-plans/{id}/replace-item
DELETE /api/meal-plans/{id}/items/{item_id}
```

## Analysis

```http
POST /api/analyze/food
POST /api/analyze/recipe
POST /api/analyze/meal-plan
```

---

---

# 47. API `analyze/food`

Input:

```json
{
  "food_id": 125,
  "quantity_g": 200
}
```

Output mẫu:

```json
{
  "food_name": "Ức gà",
  "quantity_g": 200,
  "calories": 330,
  "protein_g": 62,
  "fat_g": 7.2,
  "estimated_cost": 18400,
  "goal_compatibility": "high",
  "warnings": []
}
```

---

---

# 48. API `analyze/meal-plan`

Input:

```json
{
  "meal_plan_id": 1001
}
```

Output:

```json
{
  "total_calories": 1750,
  "target_calories": 1800,
  "protein_g": 92,
  "budget": 68500,
  "budget_limit": 70000,
  "warnings": [
    "Bữa tối có tỷ trọng chất béo tương đối cao."
  ]
}
```

---

---

# 49. WORKFLOW “TÔI MUỐN ĂN GÌ ĐÓ”

```text
Home
 ↓
Nhập:
"ức gà"
 ↓
Search
 ↓
Food / Recipe results
 ↓
User chọn
 ↓
Chọn khẩu phần
 ↓
Add to plan
 ↓
Analyze
 ↓
Recommendation
```

---

---

# 50. WORKFLOW “TẠO THỰC ĐƠN”

Input:

```text
Goal
Budget
Meal count
Preferences
Allergy
Cooking time
```

Pipeline:

```text
User input
 ↓
Calculate target
 ↓
Filter hard constraints
 ↓
Get current price
 ↓
ML score
 ↓
Optimize
 ↓
Generate options
 ↓
Display
```

Giao diện không nên trả duy nhất một phương án.

Nên trả:

```text
Phương án A
Phương án B
Phương án C
```

để người dùng tự chọn.

---

---

# 51. “TOP OPTIONS” THAY VÌ “ONE ANSWER”

Ví dụ:

```text
Bạn có 50.000đ cho bữa trưa

┌──────────────────────────────┐
│ 1. Cơm + ức gà + rau         │
│ 43.000đ                       │
│ 580 kcal                      │
│ Protein: 38g                  │
│ [Chọn] [Xem]                  │
└──────────────────────────────┘

┌──────────────────────────────┐
│ 2. Cơm + thịt lợn nạc + rau │
│ 47.000đ                       │
│ 620 kcal                      │
│ Protein: 34g                  │
│ [Chọn] [Xem]                  │
└──────────────────────────────┘
```

Đây là trải nghiệm DSS đúng nghĩa.

---

---

# 52. TÍNH NĂNG “ĐỔI KHẨU PHẦN”

Trong màn hình recipe:

```text
Khẩu phần:

[-] 1 [+]
```

hoặc:

```text
100g
150g
200g
250g
```

Khi đổi:

```text
Calories
Protein
Cost
```

cập nhật tức thì.

---

---

# 53. TÍNH NĂNG “ĐỔI PHƯƠNG PHÁP NẤU”

Nếu có dữ liệu:

```text
Ức gà
├── Luộc
├── Hấp
├── Áp chảo
└── Nướng
```

Người dùng có thể chọn cách chế biến.

Hệ thống có thể điều chỉnh:

- dầu sử dụng;
- calories;
- cost;
- thời gian.

Không cần xây mô hình quá phức tạp ở MVP; chỉ cần recipe variant.

---

---

# 54. TRANG RECIPE

Hiển thị:

```text
ỨC GÀ ÁP CHẢO

Khẩu phần: 1
Calories: 360 kcal
Protein: 42g
Chi phí: ~22.000đ
Thời gian: 20 phút

Nguyên liệu:
- 200g ức gà
- 10g dầu
-...

Cách làm:
1. ...
2. ...
3. ...

[Nấu món này]
[Thêm vào thực đơn]
[Đổi món]
```

---

---

# 55. DASHBOARD

Trang chủ cần cực đơn giản:

```text
Xin chào!

Mục tiêu:
Giảm cân

Ngân sách hôm nay:
70.000đ

Đã dùng:
42.000đ

Còn:
28.000đ
```

Sau đó:

```text
Gợi ý tiếp theo

🍗 Ức gà + rau
💰 ~24.000đ
🔥 390 kcal
🥩 35g protein

[Chọn]
[Đổi món]
```

---

---

# 56. ONBOARDING

Không bắt user nhập quá nhiều thông tin.

### Bước 1

```text
Bạn muốn làm gì?

○ Giảm cân
○ Tăng cân
○ Duy trì
○ Tăng protein
○ Hỗ trợ dinh dưỡng cho tăng trưởng
○ Ăn cân bằng hơn
```

### Bước 2

```text
Bạn dự tính chi:
○ Một bữa
○ Một ngày
○ Một tuần
○ Một tháng
```

### Bước 3

```text
Khẩu vị
```

### Bước 4

```text
Dị ứng
```

### Bước 5

```text
Thời gian nấu tối đa
```

Sau đó lập thực đơn ngay.

---

---

# 57. CẤU TRÚC BACKEND

```text
backend/
│
├── api/
│   ├── auth.py
│   ├── profile.py
│   ├── foods.py
│   ├── recipes.py
│   ├── recommendations.py
│   ├── meal_plans.py
│   └── analysis.py
│
├── core/
│   ├── config.py
│   ├── database.py
│   └── logging.py
│
├── models/
│
├── schemas/
│
├── services/
│   ├── nutrition_service.py
│   ├── price_service.py
│   ├── recipe_service.py
│   ├── recommendation_service.py
│   ├── meal_plan_service.py
│   └── analysis_service.py
│
├── recommender/
│   ├── rules.py
│   ├── scoring.py
│   └── ml_model.py
│
├── optimizer/
│   └── meal_optimizer.py
│
├── security/
│   ├── auth.py
│   ├── password.py
│   └── permissions.py
│
└── main.py
```

---

---

# 58. CẤU TRÚC DATA PIPELINE

```text
data/
│
├── raw/
│   ├── nutrition/
│   ├── recipes/
│   └── prices/
│
├── interim/
│
├── processed/
│   ├── food_master.csv
│   ├── recipe_master.csv
│   ├── food_price.csv
│   └── interactions.csv
│
└── dictionaries/
    ├── food_aliases_vi.csv
    ├── allergen_mapping.csv
    └── food_group_mapping.csv
```

---

---

# 63. SECURITY

Dữ liệu gồm:

- tài khoản;
- hồ sơ;
- cân nặng/chiều cao;
- dị ứng;
- khẩu vị;
- lịch sử ăn uống.

Phải áp dụng:

- password hashing;
- authentication;
- RBAC;
- input validation;
- parameterized queries;
- audit log;
- HTTPS khi triển khai;
- secret management.

Mật khẩu:

```text
Argon2id
```

Không lưu plaintext password.

---

---

# 64. PHÁP LÝ DỮ LIỆU CÁ NHÂN VIỆT NAM

Tại thời điểm xây dựng đề tài năm 2026, Luật Bảo vệ dữ liệu cá nhân số **91/2025/QH15** có hiệu lực từ **01/01/2026**; Nghị định **356/2025/NĐ-CP** cũng có hiệu lực từ **01/01/2026** và quy định chi tiết một số nội dung liên quan.

Nguồn chính thức:

https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroupid=3

https://vanban.chinhphu.vn/default.aspx?docid=216387&pageid=27160

Trong thiết kế hệ thống:

- thu thập tối thiểu;
- có mục đích;
- hạn chế truy cập;
- bảo vệ dữ liệu;
- không thu thập thông tin tài chính không cần thiết;
- không thu thập thông tin nhạy cảm ngoài phạm vi.

---

---

# 65. KHÔNG LƯU THÔNG TIN KHÔNG CẦN THIẾT

Không cần:

```text
Bank account
Credit card
Bank password
Investment
Loans
Home expenses
```

NutriDSS chỉ cần:

```text
Food budget
Goal
Preferences
Allergies
Profile
Meal history
```

---

---

# 66. KIẾN TRÚC HỆ THỐNG HOÀN CHỈNH

```text
                       USER
                         │
                         ▼
              React / Streamlit
                         │
                         ▼
                     FastAPI
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
      AUTH           USER PROFILE     FOOD/RECIPE
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                DECISION SUPPORT LAYER
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
   RULE ENGINE         ML MODEL        PRICE ENGINE
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                RECOMMENDATION ENGINE
                         │
                         ▼
                  MEAL OPTIMIZER
                         │
                         ▼
                    MEAL PLAN
                         │
                         ▼
                  USER FEEDBACK
                         │
                         └──────────→ PROFILE / ML

EXTERNAL DATA
   │
   ├── Nutrition datasets
   ├── Recipe APIs/datasets
   ├── Public recipe sources
   └── Retail price sources
              │
              ▼
         DATA PIPELINE
              │
              ▼
        MASTER DATABASE
```

---

---

# 67. QUY TẮC ĐỀ XUẤT

Recommendation phải theo thứ tự:

```text
1. Allergy / safety
2. User restrictions
3. Budget
4. Nutrition target
5. Preference
6. ML score
7. Variety
8. Convenience
```

Không được để:

```text
ML score cao
```

vượt qua:

```text
Allergy = true
```

---

---

# 68. QUY TẮC THAY MÓN

Khi đổi món:

```text
Current item
     ↓
Find candidates
     ↓
Same meal type
     ↓
Hard constraints
     ↓
Similar calories
     ↓
Similar protein
     ↓
Budget
     ↓
Preference score
     ↓
Return Top N
```

Mục tiêu là:

> Đổi món nhanh nhưng vẫn giữ chất lượng của cả thực đơn.

---

---

# 69. QUY TẮC TỰ THÊM MÓN

Nếu người dùng thêm món:

```text
User selected food/recipe
        ↓
Add to temporary plan
        ↓
Analyze
        ↓
Recalculate daily totals
        ↓
Return advice
```

Ví dụ:

```text
Tổng trước:
1.400 kcal

Thêm:
Trà sữa 450 kcal

Tổng:
1.850 kcal
```

Nếu mục tiêu ngày:

```text
1.700 kcal
```

hệ thống:

```text
⚠ Tổng năng lượng hiện cao hơn mục tiêu dự kiến.

Gợi ý:
- giảm khẩu phần món khác;
- thay đồ uống ít đường;
- hoặc chấp nhận món này và điều chỉnh các bữa còn lại.
```

---

---

# 70. “USER CHOICE FIRST”

Hệ thống phải luôn cho phép:

```text
AI đề xuất
     ↓
User chọn
     ↓
User chỉnh
     ↓
System re-evaluate
```

Không khóa user vào một thực đơn duy nhất.

---

---

# 71. PRICE DATA + FOOD MASTER

Ví dụ:

```text
FOOD MASTER
food_id = 101
canonical_name = "Thịt gà"
```

Price records:

```text
AEON
Thịt gà 500g
45.000đ

GO!
Thịt gà 1kg
88.000đ

WinMart
Thịt gà 500g
47.000đ
```

Chuẩn hóa:

```text
AEON = 90.000đ/kg
GO! = 88.000đ/kg
WinMart = 94.000đ/kg
```

Estimated:

```text
Median = 90.000đ/kg
```

Đây là giá dùng trong Meal Planner.

---

---

# 72. GIÁ KHUYẾN MẠI

Phải lưu:

```text
promotion_flag
original_price
sale_price
promotion_start
promotion_end
```

Không mặc định:

```text
sale_price
```

là giá thị trường dài hạn.

Meal Planner có thể có hai chế độ:

```text
GIÁ THÔNG THƯỜNG
GIÁ KHUYẾN MẠI HIỆN TẠI
```

MVP có thể chỉ dùng giá ước tính trung vị và hiển thị riêng khuyến mại.

---

---

# 73. RECIPE SOURCE STRATEGY

## Ưu tiên

```text
API
↓
Open dataset
↓
Licensed content
↓
Public source with permitted use
```

Không tự động sao chép hàng loạt:

- ảnh;
- toàn bộ hướng dẫn;
- toàn bộ nội dung bài viết;

khi license/terms không cho phép.

Nếu chỉ cần trải nghiệm người dùng:

```text
Recipe metadata
+
Source URL
+
Nutrition analysis from Food Master
```

là đủ cho MVP.

---

---

# 77. CẤU TRÚC SOURCE CODE

```text
nutrition-dss/
│
├── apis/
│   ├── base_client.py
│   ├── usda_fooddata_client.py
│   ├── themealdb_client.py
│   └── price_catalog_client.py
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── dictionaries/
│
├── notebooks/
│
├── models/
│
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── recommender/
│   ├── optimizer/
│   └── security/
│
├── frontend/
│
├── scraper/
│   ├── aeon/
│   ├── go/
│   ├── recipes/
│   └── common/
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── migrations/
│
├── tests/
├── docs/
├── .env.example
├── requirements.txt
└── README.md
```

`apis/` là lớp gọi nguồn bên ngoài, tách khỏi pipeline xử lý. Mỗi client trả dữ liệu thô; việc mapping tên tiếng Việt và tính giá chuẩn hóa thực hiện ở data pipeline. `price_catalog_client.py` chỉ dùng cho nguồn có API hoặc điều khoản cho phép thu thập tự động.

---

---

# 78. SCRAPER ARCHITECTURE

```text
PriceCollector
      │
      ├── AEONCollector
      ├── GOCollector
      └── OtherCollector

RecipeCollector
      │
      ├── APICollector
      ├── DatasetLoader
      └── PermittedWebCollector
```

Mọi collector phải trả cùng model:

```text
RawFoodPrice
---------------
source
product_name_raw
price
quantity
unit
promotion
location
collected_at
url
```

và:

```text
RawRecipe
------------
name
ingredients
instructions
source
source_url
license
```

---

---

# 82. HƯỚNG PHÁT TRIỂN THỰC TẾ

## 82.1. Tự động cập nhật giá

```text
Scheduler
 ↓
Price Collector
 ↓
Normalize
 ↓
Database
 ↓
Meal Planner
```

## 82.2. Giá theo khu vực

Sau này có thể hỗ trợ:

```text
Hà Nội
TP.HCM
Đà Nẵng
...
```

Nhưng không bắt buộc trong MVP.

## 82.3. Giảm lãng phí thực phẩm

Mức mở rộng rất thực tế:

```text
Cà rốt đã dùng hôm nay
        ↓
Planner cố gắng sử dụng tiếp trong món ngày mai
```

Giảm:

- nguyên liệu thừa;
- chi phí;
- số lần mua.

## 82.4. Tối ưu thời gian nấu

User:

```text
Tối đa 20 phút
```

Optimizer ưu tiên:

```text
recipe.cook_time <= 20
```

## 82.5. Tối ưu mua nguyên liệu

Từ meal plan:

```text
7 ngày
 ↓
Aggregate ingredients
 ↓
Shopping List
```

Ví dụ:

```text
Ức gà: 1.2kg
Trứng: 10 quả
Gạo: 2kg
Cà rốt: 1kg
```

Sau đó ước tính tổng chi phí.

Đây là hướng phát triển rất hữu ích nhưng có thể làm sau MVP.

---

---

# 83. SHOPPING LIST — OPTIONAL

Có thể thêm:

```text
meal plan
   ↓
ingredients aggregation
   ↓
shopping list
   ↓
estimated price
```

Ví dụ:

```text
Mua trong tuần:

Ức gà       1.0kg
Trứng        10 quả
Gạo         1.5kg
Cà rốt       1kg

Tổng dự kiến:
~ 245.000đ
```

---

---

# 88. PROMPT / NHIỆM VỤ CHO AI AGENT

AI Agent phải triển khai theo thứ tự:

```text
PHASE 1
Requirements
→ Use cases
→ Architecture
→ Database schema

PHASE 2
Nutrition Data
→ Recipe Data
→ Price Data
→ Food Master

PHASE 3
Cleaning
→ Vietnamese normalization
→ Unit normalization
→ Price normalization
→ Deduplication

PHASE 4
EDA
→ Nutrition
→ Price
→ Recipe

PHASE 5
ML
→ Baseline
→ KNN
→ Decision Tree
→ Random Forest
→ Evaluation

PHASE 6
DSS
→ Rules
→ Scoring
→ Recommendation

PHASE 7
Meal Planner
→ Meal
→ Day
→ Week
→ Month
→ Portion
→ Replace

PHASE 8
User Choice
→ Search
→ Add food
→ Add recipe
→ Analyze
→ Advice

PHASE 9
Recipe
→ Recipe retrieval
→ Nutrition mapping
→ Cooking instructions/source

PHASE 10
Backend
→ FastAPI
→ MySQL
→ Auth

PHASE 11
Frontend
→ Dashboard
→ Planner
→ Search
→ Analysis

PHASE 12
Security
→ RBAC
→ Validation
→ Password
→ Audit log

PHASE 13
Testing
→ ML
→ Backend
→ Database
→ UX
→ Security

PHASE 14
Documentation
→ README
→ Notebooks
→ Report
```

---

---

# 89. HẠN CHẾ PHẠM VI MÀ AI AGENT KHÔNG ĐƯỢC TỰ Ý MỞ RỘNG

Không tự ý thêm:

- hệ tài chính cá nhân;
- quản lý thu nhập;
- ngân hàng;
- đầu tư;
- vay nợ;
- đa ngôn ngữ;
- chatbot LLM;
- social network;
- marketplace;
- computer vision;
- mobile app;
- deep recommender;
- taxonomy thực phẩm thương mại quá chi tiết.

Chỉ thêm khi người dùng yêu cầu hoặc khi tính năng là cần thiết để hoàn thành yêu cầu hiện tại.

---

---

# 90. KẾT LUẬN KIẾN TRÚC

Kiến trúc chính thức:

```text
            NUTRIDSS
                │
        ┌───────┴────────┐
        │                │
     INPUT             DATA
        │                │
        ▼                ▼
 User Goal          Nutrition
 Budget             Recipe
 Preference         Price
 Allergy            Sources
 Portion
 Cooking Time
        │                │
        └───────┬────────┘
                ▼
        DECISION ENGINE
                │
       ┌────────┼────────┐
       ▼        ▼        ▼
    RULES       ML    OPTIMIZER
       │        │        │
       └────────┼────────┘
                ▼
       RECOMMENDATIONS
                │
      ┌─────────┼───────────┐
      ▼         ▼           ▼
    Choose    Replace     Add Own
      │         │           │
      └─────────┼───────────┘
                ▼
          RE-EVALUATE
                │
                ▼
        MEAL / DAY / WEEK
             / MONTH
                │
                ▼
        Nutrition + Cost
        + Recipe + Advice
```

> **Core value:** NutriDSS biến thông tin dinh dưỡng, giá thực phẩm, sở thích và ngân sách thành các lựa chọn món ăn/thực đơn có thể dùng ngay; người dùng là người quyết định cuối cùng, còn hệ thống cung cấp dữ liệu, phân tích, xếp hạng, cảnh báo và phương án thay thế.
