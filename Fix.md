# NutriDSS — FIX.md
## Kế hoạch sửa chữa, nâng cấp và hoàn thiện toàn bộ dự án

> **Repository:** `https://github.com/dieuiuquinbel/DieuDss`
>
> **Tên đề tài:** **Xây dựng hệ hỗ trợ quyết định lựa chọn thực phẩm và lập thực đơn dinh dưỡng cá nhân theo ngân sách và mục tiêu sức khỏe**
>
> **Mục tiêu của tài liệu:** tổng hợp toàn bộ các vấn đề đã phát hiện khi rà soát repository hiện tại, đồng thời đưa ra kiến trúc dữ liệu, ML, API, database, bảo mật, UX, pipeline ETL, tiêu chí đánh giá và lộ trình sửa cụ thể để AI Agent có thể dùng làm **master implementation plan**.

---

# 1. MỤC TIÊU CUỐI CÙNG

NutriDSS không nên dừng ở mức:

```text
Người dùng nhập mục tiêu
        ↓
Chọn vài món có sẵn
        ↓
Random / ML score
        ↓
Tạo thực đơn
```

Mục tiêu cuối cùng:

```text
                    USER PROFILE
                         │
        ┌────────────────┼─────────────────┐
        │                │                 │
        ▼                ▼                 ▼
   Goal / BMI       Budget / Time      Taste / Allergy
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                 PERSONAL TARGET ENGINE
                         │
                         ▼
                 FOOD MASTER VI
                         │
        ┌────────────────┼─────────────────────┐
        ▼                ▼                     ▼
    Nutrition          Price                Recipes
        │                │                     │
        └────────────────┼─────────────────────┘
                         ▼
                 DATA QUALITY ENGINE
                         │
                         ▼
                 FEATURE ENGINEERING
                         │
              ┌──────────┼───────────┐
              ▼          ▼           ▼
         RULE ENGINE     ML       OPTIMIZER
              │          │           │
              └──────────┼───────────┘
                         ▼
                DSS RECOMMENDATION
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
     Gợi ý            Đổi món          Tự chọn món
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                  Đánh giá lại plan
                         │
                         ▼
                    USER FEEDBACK
                         │
                         ▼
                 Recommendation Data
```

Trải nghiệm cốt lõi:

1. **Lập thực đơn nhanh**.
2. **Gợi ý theo ngân sách + mục tiêu**.
3. **Đổi món / đổi khẩu phần nếu không thích**.
4. **Tự chọn món rồi để hệ thống tính lại dinh dưỡng + chi phí + mức phù hợp**.

Không mở rộng lan man sang quản lý toàn bộ tài chính cá nhân; ngân sách ở đây chỉ là **ngân sách dành cho thực phẩm/thực đơn**.

---

# 2. TRẠNG THÁI REPOSITORY HIỆN TẠI

Repository đã được push thành công và hiện có:

```text
DieuDss/
├── apis/
├── backend/
├── data/
├── database/
├── docs/
├── frontend/
├── models/
├── notebooks/
├── tests/
├── .env.example
├── .gitignore
├── NutriDSS_FUTURE_SCOPE.md
├── NutriDSS_PROJECT_SPEC.md
├── README.md
└── requirements.txt
```

Nền kiến trúc hiện tại đã có:

- FastAPI backend
- Frontend HTML/Bootstrap
- Rule Engine
- Recommender Service
- Meal Optimizer
- SQLite database
- Dataset generator
- Jupyter notebooks
- ML training script
- Tests
- USDA API client
- TheMealDB API client

Có thể giữ kiến trúc tổng thể này nhưng phải sửa sâu phần **data backbone, ML methodology, guideline layer, security và database**.

---

# 3. CÁC VẤN ĐỀ QUAN TRỌNG NHẤT

## P0 — Phải sửa trước khi tiếp tục mở rộng ML

### P0.1. Training dataset hiện tại chủ yếu là synthetic

File:

```text
data/generate_datasets.py
```

đang tự sinh khoảng 400 scenario records và tạo `compatibility_rating` bằng công thức:

```text
base_score
+ bonus / penalty theo budget
+ bonus / penalty theo goal
+ random noise
```

Sau đó:

```text
synthetic formula
        ↓
synthetic rating
        ↓
ML
        ↓
model học lại synthetic formula
```

Điều này **không phải dữ liệu user behavior thật**.

Dataset hiện tại chỉ nên được ghi nhận là:

```text
synthetic_training_demo
```

hoặc:

```text
synthetic_baseline_dataset
```

Không gọi là `survey_dataset` nếu thực tế chưa có survey người dùng.

---

## P0.2. Không được dùng Test Set để chọn model

`models/train_ml_models.py` đang chọn model bằng `Test_R2`:

```python
best_model_info = max(
    valid_candidates,
    key=lambda x: x["Test_R2"]
)
```

Đây là sai về methodology vì Test Set không còn độc lập.

Pipeline đúng:

```text
RAW
 ↓
TRAIN
 ↓
Cross Validation / Validation
 ↓
Model Selection
 ↓
Hyperparameter Tuning
 ↓
Lock Model
 ↓
FINAL TEST
```

Test Set chỉ dùng **một lần ở cuối**.

---

## P0.3. Có nguy cơ data leakage do split ngẫu nhiên

Dataset có:

- 8 recipes
- nhiều scenario lặp lại
- 50 user giả
- cùng recipe xuất hiện ở nhiều dòng

`train_test_split()` có thể đưa những bản ghi gần như giống nhau vào cả train và test.

Phải dùng ít nhất:

```text
GroupKFold(recipe_id)
```

và tốt hơn cho recommender:

```text
GroupKFold(user_id)
```

Giai đoạn cao hơn:

```text
Train users
Validation users
Test users
```

để đánh giá người dùng hoàn toàn mới.

---

## P0.4. R² > 0.91 chưa thể được diễn giải là recommendation accuracy

Model hiện tại học rating giả.

Vì vậy:

```text
Test R² ≈ 0.91
```

chỉ cho thấy model tái tạo khá tốt hàm điểm synthetic.

Không được viết trong báo cáo:

> AI có độ chính xác 91%.

Không được viết:

> Hệ thống dự đoán đúng 91%.

Phải diễn đạt đúng:

> Mô hình đạt R² ... trên bộ dữ liệu đánh giá synthetic hiện tại.

Sau khi có dữ liệu thật mới báo cáo recommendation metrics thực tế.

---

## P0.5. Food dataset quá nhỏ

Hiện tại `food_master.csv` chỉ có khoảng **23 thực phẩm** và `recipe_master.csv` chỉ có **8 món**.

Mục tiêu mở rộng thực tế:

```text
MVP mở rộng:
1.000+ foods
2.000+ recipes

Mục tiêu nghiên cứu:
5.000–20.000+ canonical foods
20.000–100.000+ usable recipes
```

Không nhất thiết phải đưa toàn bộ dataset khổng lồ vào model; phải lọc, chuẩn hóa và kiểm tra chất lượng trước.

---

# 4. VẤN ĐỀ RECIPE HIỆN TẠI

## 4.1. Recipe chưa có bước nấu thực sự

`recipe_master.csv` có:

```text
name_vi
meal_type
servings
prep_time_min
cook_time_min
difficulty
description
source_name
tags
```

nhưng chưa có `recipe_steps`.

`recipe_ingredients.csv` mới chỉ mô tả nguyên liệu + khối lượng.

Cần thêm:

```text
recipe_steps
------------
id
recipe_id
step_number
instruction_vi
duration_min
temperature_c
equipment
```

---

## 4.2. Recipe hiện tại chủ yếu là recipe nội bộ

Nhiều record dùng:

```text
source_name = NutriDSS Chef
```

Điều này phù hợp cho demo nhưng chưa đủ để tạo recipe knowledge base phong phú.

Nguồn có thể nghiên cứu:

- TheMealDB
- RecipeNLG
- dataset recipe có license phù hợp
- API/website cho phép thu thập tự động
- recipe tự biên soạn có provenance rõ ràng

Không scrape hàng loạt website nếu Terms of Service, robots, copyright hoặc rate limit không cho phép.

---

# 5. DATASET DINH DƯỠNG — KIẾN TRÚC MỚI

Không nên giữ toàn bộ dinh dưỡng trong một bảng cố định vài cột.

Thiết kế:

```text
foods
food_nutrients
nutrients
food_sources
```

## 5.1. `foods`

```text
id
canonical_name_vi
food_group_id
food_state
edible_fraction
default_unit
source_quality
is_active
created_at
updated_at
```

## 5.2. `nutrients`

```text
id
code
name_en
name_vi
unit
category
```

---

# 6. BỘ ÍT NHẤT 30 TIÊU CHÍ DINH DƯỠNG

## Năng lượng và macro

| # | Tiêu chí |
|---:|---|
| 1 | Calories |
| 2 | Protein |
| 3 | Carbohydrate |
| 4 | Total Fat |
| 5 | Saturated Fat |
| 6 | Trans Fat |
| 7 | Fiber |

## Đường, muối, lipid

| # | Tiêu chí |
|---:|---|
| 8 | Total Sugars |
| 9 | Free/Added Sugars |
| 10 | Sodium |
| 11 | Cholesterol |
| 12 | Potassium |

## Khoáng chất

| # | Tiêu chí |
|---:|---|
| 13 | Calcium |
| 14 | Iron |
| 15 | Magnesium |
| 16 | Phosphorus |
| 17 | Zinc |

## Vitamin

| # | Tiêu chí |
|---:|---|
| 18 | Vitamin A |
| 19 | Vitamin C |
| 20 | Vitamin D |
| 21 | Vitamin E |
| 22 | Vitamin K |
| 23 | Vitamin B1 |
| 24 | Vitamin B2 |
| 25 | Vitamin B3 |
| 26 | Vitamin B6 |
| 27 | Folate / Vitamin B9 |
| 28 | Vitamin B12 |

## Fatty acids

| # | Tiêu chí |
|---:|---|
| 29 | Omega-3 |
| 30 | Omega-6 |

### Quy tắc missing value

Không được làm:

```text
missing → 0
```

một cách mù quáng.

Phải phân biệt:

```text
0 = nguồn xác nhận giá trị bằng 0
NULL = nguồn không cung cấp dữ liệu
```

---

# 7. FOOD STATE — BẮT BUỘC BỔ SUNG

Hiện dữ liệu đang trộn:

```text
raw
cooked
boiled
grilled
fried
```

Điều này có thể gây sai lệch lớn về nutrition.

Phải có:

```text
food_state
```

Ví dụ:

```text
Ức gà | RAW
Ức gà | COOKED
Ức gà | GRILLED
Ức gà | BOILED
Gạo trắng | COOKED
Khoai lang | BOILED
```

Nutrition basis khuyến nghị:

```text
per_100g_edible_portion
```

---

# 8. ĐƠN VỊ — PHẢI CHUẨN HÓA

Hiện có:

```text
g
ml
quả
ly
```

trong khi nutrient chủ yếu là `/100g`.

Phải có:

```text
unit_conversions
----------------
food_id
from_unit
to_unit
conversion_value
conversion_source
```

Ví dụ:

```text
1 quả trứng
→ edible_weight_g
```

Dầu ăn:

```text
ml → g
```

phải có conversion phù hợp thay vì giả định 1ml = 1g trong mọi trường hợp.

Calculation nội bộ nên ưu tiên:

```text
gram edible portion
```

---

# 9. CHUẨN HÓA TÊN THỰC PHẨM VỀ TIẾNG VIỆT

Không xóa tên gốc.

Thiết kế:

```text
food_aliases
------------
id
food_id
raw_name
normalized_name
language
source
confidence
```

Ví dụ:

```text
Chicken Breast
Chicken breast boneless skinless
Chicken breast meat
        ↓
food_id = 201
        ↓
Ức gà
```

Luôn giữ:

```text
raw_name
source_name
source_record_id
```

để truy vết.

---

# 10. TAXONOMY PHẢI ĐƠN GIẢN

Không cần tách quá sâu:

```text
black chicken
premium chicken
organic chicken
free-range chicken
...
```

nếu mục tiêu là thực đơn phổ thông.

Nên:

```text
Thịt gà
Ức gà
Đùi gà
```

Khi lấy giá:

```text
canonical item
        ↓
Ức gà phổ thông
```

Mục tiêu là giá đủ ổn định để lập thực đơn.

---

# 11. CÁC NGUỒN DỮ LIỆU NÊN BỔ SUNG

## 11.1. Vietnamese Food Composition Table

Nguồn quan trọng cho thực phẩm Việt Nam.

FAO/INFOODS liệt kê các Vietnamese Food Composition Tables, gồm các phiên bản 2007, 2013 và 2017.

Vai trò:

```text
Vietnam Food Composition
        ↓
Canonical nutrition cho thực phẩm Việt
```

Tham khảo:

- https://www.fao.org/food-composition/tables-and-databases/16/en/

---

## 11.2. USDA FoodData Central

Nguồn nutrition rất lớn và phù hợp cho pipeline.

Có:

- Foundation Foods
- FNDDS
- Branded Foods
- Search API
- Food Details API
- downloadable datasets

API:

- https://fdc.nal.usda.gov/api-guide/

Dataset downloads:

- https://fdc.nal.usda.gov/download-datasets/

Không tải toàn bộ dữ liệu vào model ngay. Pipeline:

```text
USDA
 ↓
filter
 ↓
normalize
 ↓
Vietnamese mapping
 ↓
quality check
 ↓
food master
```

---

## 11.3. Open Food Facts

Phù hợp cho:

- sản phẩm đóng gói
- ingredients
- nutrition
- allergens
- brands

API docs:

- https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/index.md

Nên dùng mạnh cho:

```text
sữa
nước ngọt
ngũ cốc
snack
đồ ăn đóng gói
```

Không coi mọi record là ground truth tuyệt đối.

---

## 11.4. CIQUAL 2025

Dùng để đối chiếu và bổ sung:

- vitamins
- minerals
- fatty acids
- individual sugars

Website:

- https://ciqual.anses.fr/

CIQUAL 2025 công bố 3.484 thực phẩm và 74 thành phần.

---

## 11.5. RecipeNLG

Nguồn recipe corpus lớn:

- https://github.com/Glorf/recipenlg

Có:

- recipe title
- ingredients
- instructions

Phù hợp cho:

```text
ingredient extraction
food matching
recipe retrieval
recipe normalization
```

Phải kiểm tra license/provenance trước khi dùng trong public redistribution.

---

## 11.6. TheMealDB

Đã có client:

```text
apis/themealdb_client.py
```

Dùng cho:

- recipe metadata
- categories
- ingredients
- instructions

Không dùng làm nutrition master.

---

## 11.7. FAOSTAT

Dùng cho:

- food supply
- agriculture
- commodity
- food availability
- country context

Không dùng làm nguồn chính cho calories/100g của từng food.

API:

- https://faostat.fao.org/

---

# 12. WHO — THIẾT KẾ ĐÚNG

WHO nên đóng vai trò:

```text
guideline
health context
population health indicators
```

Không phải:

```text
WHO → calories của từng food
```

WHO GHO/Athena cũ đã được thay thế/chuyển đổi sang hệ thống World Health Data Hub/API mới.

Tạo:

```text
apis/who_datahub_client.py
```

và:

```text
guideline_sources
guideline_rules
```

Không gọi WHO trực tiếp cho từng request tạo thực đơn.

Đúng:

```text
WHO
 ↓
scheduled ETL
 ↓
local guideline cache
 ↓
Rule Engine
```

References:

- https://www.who.int/data/gho/legacy
- https://cms.platform.who.int/api/

---

# 13. GUIDELINE RULE DATABASE

Không nên hard-code toàn bộ rule trong Python.

Tạo:

```text
guideline_sources
-----------------
id
organization
title
version
published_at
source_url
retrieved_at
```

và:

```text
guideline_rules
---------------
id
source_id
rule_code
population
age_min
age_max
sex
nutrient
min_value
max_value
unit
scope
effective_from
effective_to
notes
```

Khi guideline đổi version, chỉ cần thêm version mới.

---

# 14. KHÔNG DÙNG SAI FREE SUGAR

Hiện `food_master` chủ yếu chỉ có:

```text
sugar_g_100g
```

nhưng Rule Engine lại diễn giải thành:

```text
free sugar
```

Đây là semantic mismatch.

Phải tách:

```text
total_sugar_g
added_sugar_g
free_sugar_g
```

Nếu nguồn không có free sugar, không được tuyên bố free sugar vượt ngưỡng.

---

# 15. FAT PHẢI TÁCH

Hiện có:

```text
total_fat
```

nhưng muốn cảnh báo saturated/trans fat phải có:

```text
total_fat
saturated_fat
trans_fat
```

Không suy luận saturated fat từ total fat.

---

# 16. 30 TIÊU CHÍ KHÔNG CÓ NGHĨA 30 TARGET ML

Kiến trúc đúng:

```text
Food Data
   ↓
30+ nutrient dimensions
   ↓
Feature Engineering
   ↓
Rule Engine + ML + Optimization
```

ML có thể dùng ít hơn 30 feature sau feature selection.

30+ tiêu chí là **data backbone**, không phải bắt buộc 30 feature đều phải đưa vào model.

---

# 17. FEATURE ENGINEERING MỚI

Ngoài nutrient:

```text
calories
protein
carb
fat
fiber
...
```

cần thêm:

```text
price_per_100g
cost_per_serving
protein_per_1000_vnd
calories_per_1000_vnd
price_volatility
prep_time
cook_time
servings
meal_type
food_group
ingredient_count
user_preference_score
user_history_score
goal
target_calories
target_protein
target_fat
budget_ratio
nutrition_gap
```

---

# 18. TRAINING DATASET MỚI

Dataset recommendation nên có dạng:

```text
user_id
food_id
recipe_id

age_group
sex
activity_level

goal
target_calories
target_protein
target_carb
target_fat

budget
meal_type

preference_score
history_score

calories
protein
carb
fat
saturated_fat
trans_fat
fiber
total_sugar
free_sugar
sodium
cholesterol
potassium
calcium
iron
magnesium
phosphorus
zinc
vitamin_a
vitamin_c
vitamin_d
vitamin_e
vitamin_k
b1
b2
b3
b6
b9
b12
omega3
omega6

price
cost_per_serving
price_volatility
prep_time
cook_time

accepted
rating
```

---

# 19. REAL USER FEEDBACK

Thay synthetic rating bằng dữ liệu hành vi thật:

```text
user
 ↓
recommendation
 ↓
view
 ↓
click
 ↓
add
 ↓
keep
 ↓
replace
 ↓
remove
 ↓
rating
```

Bảng:

```text
user_interactions
-----------------
id
user_id
recipe_id
food_id
event_type
rating
session_id
created_at
```

Event types:

```text
VIEW
CLICK
ADD
KEEP
REPLACE
REMOVE
FAVORITE
DISLIKE
RATE
```

---

# 20. ONBOARDING USER

Không cần form quá dài.

Thông tin ban đầu:

```text
Mục tiêu
Ngân sách
Độ tuổi
Giới tính
Chiều cao
Cân nặng
Mức vận động
Dị ứng
Món thích
Món không thích
Thời gian nấu tối đa
```

Sau đó học dần từ interaction.

---

# 21. USER PREFERENCE DATABASE

Cần bổ sung:

```text
user_preferences
----------------
user_id
food_id
preference_type
weight
created_at
```

Giá trị:

```text
LIKE
DISLIKE
NEUTRAL
AVOID
```

và:

```text
user_recipe_interactions
```

---

# 22. PERSONALIZATION THỰC SỰ

Hiện tại:

```text
personalized ≈ goal + budget
```

Sau khi sửa:

```text
personalized =
goal
+ nutrition target
+ allergy
+ taste
+ history
+ budget
+ cooking time
+ meal type
+ variety
```

---

# 23. RECOMMENDER ARCHITECTURE

Không nên để:

```text
ML → quyết định món cuối cùng
```

Nên:

```text
Candidate Generation
        ↓
Hard Filter
        ↓
Nutrition Rules
        ↓
ML Ranking
        ↓
Optimization
        ↓
Final recommendation
```

---

# 24. RULE ENGINE

## Hard constraints

Loại:

```text
known allergen
unsupported allergen code
hard budget constraint nếu user yêu cầu strict mode
```

## Soft constraints

Cảnh báo:

```text
high sodium
high free/added sugar
high saturated fat
large calorie share
low fiber
low protein relative to goal
high cost
long cooking time
```

---

# 25. ALLERGEN SYSTEM PHẢI MỞ RỘNG

Hiện có:

```text
SEAFOOD
PEANUT
EGG
LACTOSE
SOY
GLUTEN
```

Không nên gom toàn bộ thành một nhóm quá rộng.

Nên có hierarchy:

```text
allergen_group
allergen_item
food_allergen
```

Ví dụ:

```text
FISH
SHELLFISH
PEANUT
TREE_NUT
MILK
EGG
SOY
WHEAT
```

Nếu người dùng chọn `FISH`, cá bị loại.

Nếu chọn `SHELLFISH`, không tự động loại cá nếu dữ liệu không xác nhận mối quan hệ.

---

# 26. HEALTH GOAL

Không nên để hệ thống hứa:

```text
Tăng chiều cao +5cm
```

Nên định nghĩa:

```text
GROWTH_SUPPORT
```

và tối ưu:

```text
protein adequacy
calcium
vitamin D
overall energy adequacy
micronutrient diversity
```

Đặc biệt nếu hỗ trợ trẻ em:

```text
adult rules ≠ pediatric rules
```

Không dùng cùng logic BMI/macro cho mọi độ tuổi.

---

# 27. BMI / BMR / TDEE

`NutritionService` đang dùng công thức fixed.

Phải:

- ghi rõ công thức;
- ghi nguồn;
- phân biệt population;
- không dùng một bộ ngưỡng cho mọi nhóm.

BMI là chỉ số sàng lọc, không phải chẩn đoán.

Hệ thống phải có disclaimer:

> NutriDSS là hệ hỗ trợ ra quyết định dinh dưỡng, không thay thế chẩn đoán hoặc tư vấn của bác sĩ/chuyên gia dinh dưỡng.

---

# 28. BUDGET ENGINE

Hiện đang chia:

```text
daily_budget / 3
```

làm ngân sách cho ba bữa như nhau.

Không phù hợp trong mọi tình huống.

Có thể cấu hình:

```text
breakfast = 25%
lunch = 35%
dinner = 40%
```

hoặc để optimizer tự phân bổ.

---

# 29. BUDGET HARD CONSTRAINT PHẢI NHẤT QUÁN

Hiện nếu không có combination thỏa budget, code chuyển sang toàn bộ `all_combos` và vẫn trả món vượt budget.

Nếu budget không khả thi, phải trả:

```text
status = INFEASIBLE
minimum_required_budget = X
```

UI:

```text
Không có thực đơn đáp ứng ngân sách.
Ngân sách tối thiểu ước tính: X

[Giữ ngân sách]
[Tăng ngân sách]
```

Không âm thầm vượt budget.

---

# 30. OPTIMIZER V2

Hiện optimizer brute-force:

```text
Breakfast × Lunch × Dinner
```

Với 500 món mỗi nhóm:

```text
500 × 500 × 500
= 125,000,000 combinations
```

Không phù hợp.

Dùng:

```text
Top-K candidate generation
        ↓
Hard filtering
        ↓
Beam Search
```

hoặc:

```text
OR-Tools CP-SAT / optimization
```

Objective:

```text
minimize:
nutrition_gap
+ budget_gap
+ preference_penalty
+ preparation_time_penalty
+ repetition_penalty
```

Constraints:

```text
budget <= budget_limit
protein >= target_min
calories within acceptable range
allergy = 0
```

---

# 31. SMART REPLACEMENT

Flow:

```text
Current Recipe
      ↓
get target nutrition
      ↓
candidate recipes
      ↓
same meal type
      ↓
allergy filter
      ↓
budget filter
      ↓
nutrition similarity
      ↓
preference score
      ↓
top 3
```

`ReplaceItemRequest` hiện có `target_protein_g`, `target_calories` nhưng cần bảo đảm hai trường này thực sự tham gia ranking.

---

# 32. CUSTOM FOOD FLOW

Không nên bắt user nhập mọi nutrition.

Flow mới:

```text
[Tìm kiếm món]
       ↓
Phở bò
       ↓
Nutrition + Price + Recipe
       ↓
[Thêm vào thực đơn]
       ↓
DSS kiểm tra
       ↓
Calories
Protein
Sugar
Sodium
Fat
Cost
Goal fit
Allergy
       ↓
Khuyến nghị
```

Chỉ cho nhập tay khi hệ thống không tìm thấy dữ liệu.

---

# 33. UI/UX

Frontend hiện đã có các tab chính:

- Tổng quan & Hồ sơ
- Lập thực đơn
- Đổi món
- Tự thêm món
- Dinh dưỡng & giá

Đây là hướng đúng.

Nâng cấp thành:

## Trang Onboarding

```text
Mục tiêu
Budget
Body profile
Allergy
Taste
Cooking time
```

## Daily Dashboard

```text
Calories target
Protein target
Budget
Meals
Progress
```

## Recommendation Card

```text
Tên món
Calories
Protein
Cost
Cooking time
Compatibility
Why recommended
```

## Replace

```text
Món hiện tại
↓
3 món thay thế
```

## Search

```text
Search food / recipe
↓
Add
↓
Analyze
```

## Weekly Plan

```text
Monday → Sunday
```

---

# 34. WHY THIS FOOD?

DSS nên giải thích ngắn gọn:

```text
Đề xuất món này vì:
✓ phù hợp ngân sách
✓ protein phù hợp mục tiêu
✓ không có allergen đã khai báo
✓ thời gian nấu phù hợp
✓ người dùng từng thích món tương tự
```

Không cần LLM để tạo explanation ở MVP; có thể sinh explanation từ feature/rule.

---

# 35. MODEL EXPLAINABILITY

Với Tree/Random Forest:

```text
feature_importances_
```

Có thể dùng SHAP ở giai đoạn nâng cao.

UI có thể hiện:

```text
Budget fit        +++
Protein fit       +++
Preference fit    ++
Calorie fit       +++
Cooking time      ++
```

---

# 36. MODEL CANDIDATES

Giữ đúng yêu cầu tiểu luận:

```text
Linear Regression
KNN
Decision Tree
Random Forest
MLP
```

Có thể bổ sung:

```text
Gradient Boosting
HistGradientBoosting
XGBoost / LightGBM
```

nếu môi trường cho phép.

Không cần deep learning lớn nếu dữ liệu thực tế chưa đủ.

---

# 37. MODEL EVALUATION

Nếu target là rating:

```text
MAE
RMSE
R²
```

Nếu target acceptance:

```text
Accuracy
Precision
Recall
F1
ROC-AUC
PR-AUC
```

Nếu recommendation:

```text
Precision@K
Recall@K
MAP@K
NDCG@K
Hit Rate@K
```

Nếu meal planner:

```text
budget feasibility
nutrition gap
constraint violation rate
```

Không chỉ báo cáo R².

---

# 38. DATA SPLIT

Recommendation nên ưu tiên user-based split:

```text
70% users → train
15% users → validation
15% users → test
```

Không split ngẫu nhiên row khi row phụ thuộc cùng user.

---

# 39. DATABASE V2 — MYSQL

Khuyến nghị:

```text
MySQL 8
+
SQLAlchemy
+
Alembic
```

SQLite giữ cho:

```text
unit test
quick prototype
```

không phải database production chính.

---

# 40. DATABASE SCHEMA V2

## Users

```text
users
-----
id
email
password_hash
status
created_at
updated_at

roles
-----
id
name

user_roles
----------
user_id
role_id
```

## Profile

```text
user_profiles
-------------
user_id
display_name
birth_year / age
sex
height_cm
weight_kg
activity_level
```

## Preferences

```text
user_preferences
-----------------
user_id
food_id
preference_type
weight

user_allergies
--------------
user_id
allergen_id
severity
```

## Food

```text
foods
-----
id
canonical_name_vi
food_group_id
food_state
default_unit

food_aliases
------------
id
food_id
raw_name
normalized_name
language
source
confidence
```

## Nutrient

```text
nutrients
---------
id
code
name_vi
unit

food_nutrients
--------------
food_id
nutrient_id
value
basis
source_id
confidence
```

## Sources

```text
data_sources
------------
id
organization
dataset
version
source_url
license
retrieved_at
```

## Prices

```text
stores
------
id
name
region
source_url

food_prices
-----------
id
food_id
store_id
product_name_raw
price_vnd
quantity
unit
normalized_price_per_100g
promotion_flag
region
product_url
collected_at
```

## Recipes

```text
recipes
-------
id
name_vi
source_id
meal_type
servings
prep_time
cook_time
difficulty

recipe_ingredients
-------------------
recipe_id
food_id
quantity_g

recipe_steps
------------
recipe_id
step_number
instruction_vi
duration_min
```

## Planning

```text
meal_plans
----------
id
user_id
plan_type
start_date
end_date
budget_vnd
goal
created_at

meal_plan_items
---------------
meal_plan_id
recipe_id
date
meal_type
serving
selected_by
```

## Feedback

```text
user_interactions
-----------------
id
user_id
recipe_id
event_type
rating
session_id
created_at
```

## Guidelines

```text
guideline_sources
-----------------
id
organization
title
version
source_url
published_at

 guideline_rules
---------------
id
source_id
rule_code
population
nutrient
min_value
max_value
unit
scope
effective_from
effective_to
```

## ML

```text
model_versions
--------------
id
model_name
version
dataset_version
metric_json
artifact_path
trained_at
is_active
```

## Audit

```text
audit_logs
----------
id
user_id
action
target_type
target_id
metadata_json
created_at
```

---

# 41. API V2

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh

GET  /api/profile
PUT  /api/profile

GET  /api/foods
GET  /api/foods/search
GET  /api/foods/{id}

GET  /api/recipes
GET  /api/recipes/search
GET  /api/recipes/{id}

POST /api/plans
POST /api/plans/generate
PUT  /api/plans/{id}
POST /api/plans/{id}/replace-item
POST /api/plans/{id}/add-food

POST /api/analyze/food
POST /api/analyze/recipe

POST /api/feedback
POST /api/favorites

GET /api/guidelines
GET /api/nutrition-summary
```

---

# 42. SECURITY V2

Backend hiện đang có:

```python
allow_origins=["*"]
allow_credentials=True
```

Không phù hợp production.

Phải chuyển sang allowed origins cụ thể.

## Authentication

- password hashing
- access token/session
- refresh token nếu cần
- không lưu plaintext password

## Authorization

User A không được truy cập dữ liệu của User B.

## Input validation

Tiếp tục dùng Pydantic nhưng bổ sung:

- max length
- numeric range
- enum
- reject unexpected values
- output escaping

---

# 43. XSS

Frontend đã có `escapeHtml()` ở một số flow nhưng phải thống nhất.

Ưu tiên:

```text
textContent
```

hơn:

```text
innerHTML
```

khi không cần HTML.

---

# 44. SQL INJECTION

Tiếp tục dùng parameter binding:

```python
cursor.execute(query, params)
```

Không dùng raw string interpolation với user input.

---

# 45. SECRETS

Giữ:

```text
.env
```

trong `.gitignore`.

Không commit:

- USDA API key
- database password
- JWT secret
- cloud credentials
- scraper credentials

Chỉ commit:

```text
.env.example
```

---

# 46. RATE LIMITING

API public phải giới hạn:

```text
/search
/analyze
/plans/generate
/auth/login
```

Tránh abuse và resource exhaustion.

---

# 47. DATA PRIVACY

Thông tin có thể bao gồm:

```text
height
weight
age
health goal
allergy
food preferences
```

Phải:

- lưu tối thiểu;
- hash password;
- hạn chế log;
- không log raw health payload nếu không cần;
- phân quyền;
- hỗ trợ xóa tài khoản/dữ liệu khi triển khai thật.

---

# 48. DATA PROVENANCE

Mỗi nutrition/price/recipe record nên truy được:

```text
source
source_record_id
source_version
retrieved_at
source_url
license
transform_version
```

Ví dụ:

```text
food_id = 201
nutrient = protein
value = 31
gram basis = 100g
source = USDA
source_record_id = ...
dataset_version = ...
transform_version = v2
```

---

# 49. PRICE PIPELINE

Hiện tại giá trong `data/generate_datasets.py` đang hard-code.

Phải chuyển sang:

```text
scraper/API client
        ↓
raw_prices
        ↓
normalize quantity/unit
        ↓
map canonical food
        ↓
deduplicate
        ↓
validate
        ↓
price_history
```

---

# 50. GIÁ SIÊU THỊ

Nguồn mục tiêu:

```text
AEON EShop
GO!
WinMart
```

Có thể nghiên cứu thêm:

```text
Co.op Online
Bách Hóa Xanh
Lotte Mart
```

nhưng từng nguồn phải kiểm tra:

- API
- Terms of Service
- robots
- rate limit
- dữ liệu có public hay không

Không vượt CAPTCHA/login/anti-bot.

---

# 51. PRICE NORMALIZATION

Ví dụ:

```text
Ức gà 500g = 45.000đ
```

chuẩn hóa:

```text
90.000đ/kg
9.000đ/100g
```

Công thức:

```text
price_per_100g = price / quantity_g * 100
```

Nếu package theo quả/hộp, cần conversion hợp lý.

---

# 52. PRICE CONFIDENCE

Tạo:

```text
price_confidence
```

Giá trị:

```text
LOW
MEDIUM
HIGH
```

Dựa trên:

- số nguồn
- số ngày quan sát
- độ mới
- variance
- data quality

Một record đơn lẻ → `LOW`.

---

# 53. DATA QUALITY ENGINE

Thêm:

```text
data_quality/
├── nutrition_validator.py
├── price_validator.py
├── recipe_validator.py
├── duplicate_detector.py
└── quality_report.py
```

Kiểm tra:

```text
calories >= 0
protein >= 0
fat >= 0
sodium >= 0
price > 0
quantity > 0
```

và:

```text
source != NULL
unit != NULL
canonical mapping exists
```

---

# 54. DUPLICATE DETECTION

Food duplicate:

```text
Chicken Breast
Chicken Breast Boneless
Chicken breast meat
```

Recipe duplicate:

```text
Cơm gà
Chicken rice
Rice with chicken
```

Phải có:

```text
normalized_name
canonical_food_id
canonical_recipe_id
```

Có thể dùng:

- normalization
- fuzzy matching
- token similarity
- embeddings ở giai đoạn nâng cao.

---

# 55. DỊCH SANG TIẾNG VIỆT

Không dịch thủ công toàn bộ record.

Pipeline:

```text
raw English
      ↓
normalization
      ↓
dictionary lookup
      ↓
translation model/API nếu cần
      ↓
human / rule review
      ↓
canonical Vietnamese
```

Nhớ rằng:

```text
translation != canonicalization
```

Ví dụ:

```text
Chicken breast, roasted
        ↓
Ức gà | ROASTED
```

không được xóa trạng thái chế biến.

---

# 56. DATA DICTIONARIES

Tạo:

```text
data/dictionaries/
├── food_alias_vi.csv
├── food_group_mapping.csv
├── nutrient_mapping.csv
├── allergen_mapping.csv
├── unit_mapping.csv
├── preparation_state_mapping.csv
└── recipe_tag_mapping.csv
```

---

# 57. NOTEBOOK PLAN

Nâng notebooks thành:

```text
01_source_inventory.ipynb
02_raw_data_ingestion.ipynb
03_data_quality.ipynb
04_food_normalization_vi.ipynb
05_nutrient_harmonization.ipynb
06_price_normalization.ipynb
07_recipe_normalization.ipynb
08_eda_food.ipynb
09_eda_price.ipynb
10_feature_engineering.ipynb
11_ml_baseline.ipynb
12_ml_model_comparison.ipynb
13_ml_validation.ipynb
14_recommendation_evaluation.ipynb
15_meal_optimization.ipynb
16_final_demo.ipynb
```

---

# 58. NOTEBOOK REQUIREMENT CHO TIỂU LUẬN

Mỗi notebook phải có:

```text
1. Mục tiêu
2. Nguồn dữ liệu
3. Import
4. Load dữ liệu
5. Kiểm tra dữ liệu
6. Cleaning
7. Transform
8. Visualization
9. Modeling
10. Evaluation
11. Kết luận
```

Notebook phải có output và diễn giải, không chỉ là tập code.

---

# 59. EDA

## Nutrition

- calorie distribution
- protein distribution
- macro correlations
- food group distribution
- missingness

## Price

- average price by food group
- price range
- price volatility
- retailer comparison
- price/protein
- price/calorie

## Recipe

- cooking time
- recipe complexity
- calories
- cost
- macro distribution

## User

- preference distribution
- goal distribution
- budget distribution

---

# 60. ML V2 — KHÔNG VỘI DEEP LEARNING

Stage:

```text
Baseline
↓
Linear Regression
↓
KNN
↓
Decision Tree
↓
Random Forest
↓
Gradient Boosting
↓
MLP
```

Sau đó mới cân nhắc:

```text
XGBoost
LightGBM
ranking model
```

Không cần neural network lớn nếu dataset thật chưa đủ lớn/chất lượng chưa cao.

---

# 61. RECOMMENDER MODEL

Chia thành:

## Candidate generation

```text
nutrition filter
budget filter
allergy filter
meal type
```

## Ranking

```text
ML ranker
```

## Re-ranking

```text
preference
diversity
variety
convenience
```

---

# 62. DIVERSITY

Nếu top 3 đều là ức gà thì recommendation nghèo.

Phải cân bằng:

```text
food_group diversity
recipe diversity
protein source diversity
meal variety
```

---

# 63. WEEKLY PLANNER

Sau daily:

```text
Monday
Tuesday
...
Sunday
```

Constraint:

```text
avoid repetition
protein variety
vegetable variety
budget
nutrition adequacy
```

---

# 64. MONTHLY PLANNER

Chỉ làm ở mức cao hơn.

Có thể xây từ:

```text
weekly planner × 4
```

thêm:

```text
meal rotation
budget average
shopping list
```

---

# 65. SHOPPING LIST

Từ meal plan:

```text
recipe ingredients
        ↓
aggregate
        ↓
shopping list
```

Ví dụ:

```text
Ức gà: 1.2 kg
Gạo: 1.5 kg
Cà chua: 0.5 kg
```

Sau đó tính package purchase cost theo giá hiện tại.

---

# 66. PORTION ADJUSTMENT

Cho phép:

```text
Ít
Vừa
Nhiều
```

hoặc multiplier:

```text
0.75x
1.00x
1.25x
1.50x
```

Recalculate:

```text
calories
protein
cost
```

Không sửa dữ liệu recipe gốc.

---

# 67. USER-SELECTED MEAL

Flow:

```text
Search "phở bò"
→ add
```

System:

```text
calculate
→ analyze
→ warn
→ suggest compensation
```

Ví dụ nếu tổng day có quá nhiều đường:

```text
bữa sau giảm đồ uống có đường
```

Không chẩn đoán bệnh.

---

# 68. COMPENSATION ENGINE

Nếu user thêm món nhiều calo:

```text
chosen meal
        ↓
calculate remaining nutrition budget
        ↓
re-optimize remaining meals
```

Không xóa món đã chọn.

---

# 69. USER CHOICE FIRST

Nguyên tắc UX:

```text
AI suggests
User chooses
System recalculates
```

Không tự động thay món user đã chọn nếu chưa xác nhận.

---

# 70. API CACHE

Không gọi nguồn ngoài ở mỗi request.

Dùng:

```text
Redis
```

hoặc local cache cho MVP.

Cache cho:

- USDA
- WHO
- recipe APIs
- price sources

---

# 71. API RETRY

`base_client.py` đã có timeout/exception.

Bổ sung:

```text
retry
exponential backoff
status handling
cache
logging
```

Không retry vô hạn.

---

# 72. API SOURCE REGISTRY

Tạo:

```text
api_sources
-----------
id
name
base_url
source_type
enabled
rate_limit
last_success
last_failure
```

---

# 73. INGESTION SCHEDULER

Có thể chạy:

```text
daily
weekly
monthly
```

Ví dụ:

```text
Price → daily
USDA → weekly/monthly
WHO guideline → weekly/monthly
Recipe → weekly
```

---

# 74. DATA VERSIONING

Mỗi processed dataset cần:

```text
dataset_version
created_at
source_versions
transform_version
row_count
hash
```

Ví dụ:

```text
nutrition_v2026_10
price_v2026_10_01
recipe_v2026_10
```

---

# 75. MODEL VERSIONING

Mỗi model:

```text
model_version
dataset_version
features
metrics
training_date
hyperparameters
artifact_hash
```

Không chỉ lưu một file:

```text
best_recipe_ranker.joblib
```

---

# 76. REPOSITORY STRUCTURE V2

```text
DieuDss/
│
├── README.md
├── Fix.md
├── NutriDSS_PROJECT_SPEC.md
├── NutriDSS_FUTURE_SCOPE.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── apis/
│   ├── base_client.py
│   ├── usda_fooddata_client.py
│   ├── themealdb_client.py
│   ├── openfoodfacts_client.py
│   ├── who_datahub_client.py
│   └── faostat_client.py
│
├── ingestion/
│   ├── nutrition_ingest.py
│   ├── recipe_ingest.py
│   ├── price_ingest.py
│   ├── guideline_ingest.py
│   └── pipeline.py
│
├── data/
│   ├── raw/
│   ├── normalized/
│   ├── feature_store/
│   ├── dictionaries/
│   └── quality_reports/
│
├── database/
│   ├── migrations/
│   ├── schema.sql
│   ├── seed.py
│   └── README.md
│
├── backend/
│   ├── main.py
│   ├── api/
│   ├── schemas/
│   ├── services/
│   ├── recommender/
│   ├── optimizer/
│   ├── security/
│   └── repositories/
│
├── models/
│   ├── train/
│   ├── artifacts/
│   ├── metadata/
│   └── evaluation/
│
├── notebooks/
├── frontend/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── data/
│   └── security/
│
└── docs/
    ├── architecture/
    ├── data/
    ├── ml/
    ├── database/
    └── report/
```

---

# 77. MVP MỨC 2

Mức 2 đủ mạnh cho tiểu luận:

```text
Food Master
+
Nutrition
+
Price
+
Recipe
+
Allergy
+
Budget
+
ML
+
Rule Engine
+
Daily Plan
+
Replacement
+
Custom Food
```

Dataset mục tiêu:

```text
1.000+ foods
2.000+ recipes
10+ nutrient groups
```

---

# 78. MỨC 3 ĐƯỢC CẮT GỌN

Không cần:

- đa ngôn ngữ
- multi-country taxonomy phức tạp
- mobile app riêng
- LLM fine-tuning lớn
- computer vision nhận diện món từ ảnh
- microservices cloud phức tạp
- real-time supermarket integration toàn bộ thị trường

Tập trung:

```text
UX
Data quality
Nutrition
Recommendation
Budget
Price
Recipe
Security
```

---

# 79. HƯỚNG NÂNG CAO CÓ GIÁ TRỊ

## Explainable DSS

```text
Why this meal?
```

## Recommendation feedback loop

```text
user feedback
→ training data
```

## Price-aware recommendation

```text
nutrition + current price
```

## Smart substitution

```text
similar nutrition profile
```

## Remaining-budget optimization

```text
chosen meal
→ optimize remaining meals
```

---

# 80. TEST PLAN

Hiện đã có test suite tốt ở mức prototype.

Bổ sung:

## Data tests

```text
No negative nutrition
No duplicate canonical ID
Every recipe ingredient exists
Every food has source
Price units valid
```

## Rule tests

```text
allergy hard exclusion
unknown allergy rejection
budget infeasible
nutrient warnings
```

## Model tests

```text
model loads
feature columns match
prediction finite
output range valid
```

## API tests

```text
200
400
401
403
404
422
500
```

---

# 81. SECURITY TEST PLAN

Bổ sung:

```text
authentication bypass
IDOR
XSS
SQL injection
rate limit
malformed JSON
oversized input
invalid enum
unknown allergen
```

Test đặc biệt:

```text
User A request /plans/UserB
```

phải bị chặn.

---

# 82. DOCUMENTATION SOURCES

## WHO

Healthy diet:

https://www.who.int/vietnam/news/fact-sheets/detail/healthy-diet

WHO GHO legacy / migration:

https://www.who.int/data/gho/legacy

WHO API platform:

https://cms.platform.who.int/api/

## USDA

API:

https://fdc.nal.usda.gov/api-guide/

Datasets:

https://fdc.nal.usda.gov/download-datasets/

## FAO

Food composition:

https://www.fao.org/food-composition/tables-and-databases/16/en/

FAOSTAT:

https://faostat.fao.org/

## CIQUAL

https://ciqual.anses.fr/

## Open Food Facts

https://github.com/openfoodfacts/openfoodfacts-server/blob/main/docs/api/index.md

## RecipeNLG

https://github.com/Glorf/recipenlg

## TheMealDB

https://www.themealdb.com/api.php

---

# 83. LỘ TRÌNH IMPLEMENTATION

```text
STEP 01
Audit hiện tại
        ↓
STEP 02
Fix synthetic ML dataset naming
        ↓
STEP 03
Xây food master 30+ nutrients
        ↓
STEP 04
Chuẩn hóa raw/cooked/unit
        ↓
STEP 05
Bổ sung recipe corpus + steps
        ↓
STEP 06
Bổ sung price history
        ↓
STEP 07
WHO + guideline layer
        ↓
STEP 08
Data quality
        ↓
STEP 09
Feature engineering
        ↓
STEP 10
ML evaluation chuẩn
        ↓
STEP 11
User feedback
        ↓
STEP 12
Recommendation V2
        ↓
STEP 13
Optimizer V2
        ↓
STEP 14
MySQL + Auth
        ↓
STEP 15
Security + testing
        ↓
STEP 16
UX final
        ↓
STEP 17
Notebook + report
        ↓
FINAL NUTRIDSS
```

---

# 84. TASK LIST CHO AI AGENT

## TASK GROUP A — DATA

```text
A01 Create nutrient master
A02 Create food master v2
A03 Create food alias mapping
A04 Add food states
A05 Add unit normalization
A06 USDA ingestion
A07 OpenFoodFacts ingestion
A08 CIQUAL ingestion
A09 Vietnamese Food Table ingestion
A10 Data quality report
```

## TASK GROUP B — RECIPE

```text
B01 Recipe schema v2
B02 RecipeNLG ingestion
B03 TheMealDB ingestion
B04 Recipe normalization
B05 Recipe steps
B06 Recipe-food matching
```

## TASK GROUP C — PRICE

```text
C01 Store schema
C02 Price raw schema
C03 Price normalization
C04 Price history
C05 Price confidence
C06 Permitted retailer source clients
```

## TASK GROUP D — GUIDELINE

```text
D01 WHO API client
D02 Guideline source table
D03 Guideline rules
D04 Versioning
D05 Rule engine refactor
```

## TASK GROUP E — ML

```text
E01 Synthetic dataset relabel
E02 Real feedback dataset schema
E03 Group split
E04 Baselines
E05 Cross validation
E06 Hyperparameter tuning
E07 Ranking model
E08 Recommendation metrics
E09 Explainability
```

## TASK GROUP F — DSS

```text
F01 Candidate generator
F02 Hard filters
F03 Soft rules
F04 Ranking
F05 Replacement
F06 Portion scaling
F07 Remaining budget optimization
F08 Weekly planner
```

## TASK GROUP G — BACKEND

```text
G01 Repository pattern
G02 MySQL
G03 SQLAlchemy
G04 Alembic
G05 Auth
G06 RBAC
G07 Rate limit
G08 Error handling
```

## TASK GROUP H — FRONTEND

```text
H01 Onboarding
H02 Daily plan
H03 Recommendation cards
H04 Replacement UI
H05 Search
H06 Custom food
H07 Weekly planner
H08 Explainability UI
```

## TASK GROUP I — SECURITY

```text
I01 Secret management
I02 XSS audit
I03 SQL injection audit
I04 IDOR audit
I05 Auth tests
I06 Permission tests
I07 Audit logs
```

## TASK GROUP J — ACADEMIC

```text
J01 Notebook rewrite
J02 EDA
J03 Model comparison
J04 Evaluation tables
J05 Architecture diagrams
J06 Final report
J07 Demo script
```

---

# 85. TIÊU CHÍ HOÀN THÀNH

## Data

- [ ] 5.000+ canonical foods hoặc ít nhất 1.000+ cho MVP
- [ ] 30+ nutrient definitions
- [ ] food state
- [ ] unit normalization
- [ ] Vietnamese canonical naming
- [ ] source provenance
- [ ] 20.000+ usable recipes ở mức mở rộng
- [ ] recipe instructions
- [ ] price history
- [ ] allergen mapping

## ML

- [ ] synthetic data chỉ dùng baseline/demo
- [ ] real feedback dataset
- [ ] group-based split
- [ ] cross-validation
- [ ] final holdout test
- [ ] recommendation metrics
- [ ] explainability

## DSS

- [ ] budget constraint
- [ ] allergy hard constraint
- [ ] nutrition soft constraint
- [ ] goal fit
- [ ] replacement
- [ ] custom food
- [ ] portion adjustment
- [ ] weekly planner

## API

- [ ] USDA
- [ ] WHO
- [ ] FAOSTAT
- [ ] Open Food Facts
- [ ] recipe API
- [ ] cache
- [ ] retries
- [ ] rate limit

## Security

- [ ] password hashing
- [ ] authentication
- [ ] authorization
- [ ] IDOR protection
- [ ] XSS prevention
- [ ] SQL injection protection
- [ ] secret management
- [ ] audit logs

## Report

- [ ] problem definition
- [ ] data collection
- [ ] preprocessing
- [ ] EDA
- [ ] feature engineering
- [ ] ML comparison
- [ ] evaluation
- [ ] DSS architecture
- [ ] UI demo
- [ ] limitations
- [ ] future work

---

# 86. NHỮNG ĐIỀU AI AGENT KHÔNG ĐƯỢC LÀM

1. Không tạo dataset giả rồi gọi đó là dữ liệu thật.
2. Không tuyên bố model có accuracy cao nếu chỉ có synthetic data.
3. Không dùng Test Set để chọn model.
4. Không điền missing nutrient = 0 nếu nguồn không cung cấp.
5. Không suy luận free sugar từ total sugar.
6. Không suy luận saturated fat từ total fat.
7. Không coi mọi fish/shellfish là cùng một allergen nếu source không xác nhận.
8. Không dùng WHO API như food nutrition database.
9. Không scrape website vượt CAPTCHA/login/rate limit/ToS.
10. Không commit API key hoặc password.
11. Không gọi API ngoài mỗi request nếu local cache/database đã có dữ liệu.
12. Không dùng brute-force combination khi dataset lớn.
13. Không cho user A truy cập dữ liệu user B.
14. Không biến hệ thống thành hệ chẩn đoán y khoa.
15. Không tự thay đổi món user đã chọn nếu chưa được user xác nhận.

---

# 87. KẾT LUẬN KIẾN TRÚC

NutriDSS cuối cùng nên được coi là:

```text
Nutrition Data Platform
        +
Price Data Platform
        +
Recipe Knowledge Base
        +
Guideline Engine
        +
ML Recommendation Engine
        +
Optimization Engine
        +
DSS UX
```

Không phải chỉ là:

```text
FastAPI + Decision Tree
```

Ba lớp quyết định quan trọng nhất:

```text
LAYER 1 — RULES
An toàn / dị ứng / constraints

LAYER 2 — ML
Preference / ranking / personalization

LAYER 3 — OPTIMIZER
Ghép món thành kế hoạch tối ưu
```

---

# 88. FINAL IMPLEMENTATION PRINCIPLE

Không chạy theo mục tiêu:

```text
"model càng phức tạp càng tốt"
```

Mà theo:

```text
Nguồn dữ liệu đáng tin
        ↓
Chuẩn hóa tốt
        ↓
Dữ liệu có provenance
        ↓
Rules đúng
        ↓
ML có evaluation đúng
        ↓
Optimization rõ ràng
        ↓
UX nhanh
        ↓
Security tốt
```

**DATA QUALITY > MODEL COMPLEXITY**.

Một model rất phức tạp trên dữ liệu giả vẫn không tạo ra recommendation đáng tin. Một pipeline dữ liệu sạch + provenance + rules rõ ràng + model vừa phải + optimizer đúng sẽ tạo ra một DSS thuyết phục hơn nhiều.

---

# 89. MASTER PRIORITY

Nếu thời gian hạn chế, làm theo thứ tự:

```text
1. Data quality
2. Nutrition master
3. Recipe
4. Price
5. Rule Engine
6. ML
7. Optimizer
8. UX
9. Security
```

Không ưu tiên trước:

```text
microservices
mobile app
LLM fine-tuning
multilingual
computer vision
cloud orchestration
```

trước khi Data Backbone hoàn thiện.

---

# 90. DEFINITION OF DONE

NutriDSS được coi là hoàn thiện khi:

```text
User nhập:
- mục tiêu
- thông tin cơ thể
- ngân sách
- dị ứng
- sở thích
- thời gian nấu

             ↓

System:
- tính target
- lọc allergy
- đọc nutrition
- đọc giá
- đọc recipe
- kiểm tra guidelines
- ranking
- optimization

             ↓

User nhận:
- 3 phương án
- calories
- protein
- nutrients
- cost
- cooking time
- warnings
- explanations

             ↓

User:
- chọn
- đổi món
- đổi khẩu phần
- thêm món tự chọn

             ↓

System:
- tính lại
- cảnh báo
- re-optimize phần còn lại

             ↓

User feedback:
- thích
- không thích
- favorite
- replace
- rating

             ↓

Feedback được lưu
             ↓
Recommendation dataset tăng dần
             ↓
Model có thể retrain
```

Vòng lặp hoàn chỉnh:

```text
DATA
 → DSS
 → USER
 → FEEDBACK
 → DATA
```

---

# 91. GHI CHÚ KHI TRIỂN KHAI DATA THỰC TẾ

## 91.1. Không trộn tất cả nguồn thành một “siêu dataset”

Mỗi nguồn phải có vai trò riêng:

| Nguồn | Vai trò |
|---|---|
| Vietnamese Food Composition | Nutrition thực phẩm Việt |
| USDA FDC | Nutrition rộng + branded foods |
| Open Food Facts | Product + ingredients + allergens |
| CIQUAL | Bổ sung/đối chiếu nutrients |
| RecipeNLG | Recipe corpus |
| TheMealDB | Recipe API/demo |
| FAOSTAT | Food/agriculture/supply context |
| WHO | Guideline/health indicators |
| AEON/GO!/WinMart | Price observations |
| User interaction | Target personalization |

## 91.2. Dữ liệu phải có provenance

Không có source → không đưa thẳng vào canonical production set.

## 91.3. Không ép dataset thiếu dữ liệu

Nếu chỉ có calories và protein thì giữ missing cho các nutrients chưa có; downstream phải biết missingness.

## 91.4. Không dùng scraping bất hợp lệ

Chỉ lấy dữ liệu public/API và tuân thủ điều khoản nguồn. Không vượt CAPTCHA, login, rate limit hoặc cơ chế anti-bot.

---

# 92. TASK EXECUTION RULE CHO AI AGENT

Khi Agent bắt đầu sửa repo, phải theo nguyên tắc:

```text
Read Fix.md
        ↓
Inspect current files
        ↓
Make smallest coherent change
        ↓
Run tests
        ↓
Update docs
        ↓
Commit with clear message
```

Không tự tiện tạo thêm framework phức tạp nếu không cần.

Không thay đổi schema/database mà không cập nhật:

```text
schema.sql
seed
models
services
tests
README
```

Mỗi task phải bảo đảm không phá các task trước.

---

# 93. COMMIT ROADMAP GỢI Ý

```text
chore: audit and clean current data pipeline

feat: add nutrient master and food source mapping

feat: add food normalization and Vietnamese aliases

feat: add food state and unit conversion

feat: add USDA ingestion pipeline

feat: add Open Food Facts ingestion

feat: add CIQUAL and Vietnam food composition mapping

feat: add recipe ingestion and recipe steps

feat: add price history pipeline

feat: add WHO guideline integration

refactor: migrate rule engine to guideline-driven rules

refactor: rebuild ML dataset and evaluation pipeline

feat: add group-based recommendation validation

feat: add user preference and interaction tracking

feat: add personalized recommender v2

feat: add optimization engine v2

feat: add MySQL persistence layer

feat: add authentication and authorization

security: harden XSS, IDOR, rate limits and secrets

feat: improve meal planner UX

test: add data, ML and security test suites

docs: update thesis notebooks and architecture
```

---

# 94. KẾT LUẬN CUỐI

Repository hiện tại đã có **khung phần mềm tốt** nhưng cần chuyển trọng tâm từ:

```text
Prototype + synthetic ML
```

sang:

```text
Real data backbone
        +
Reliable nutrition knowledge
        +
Recipe knowledge base
        +
Real price observations
        +
Guideline layer
        +
Real user feedback
        +
Proper ML validation
        +
Constraint optimization
```

Đây là con đường để NutriDSS trở thành một **hệ hỗ trợ ra quyết định có Machine Learning thực chất**, đồng thời vẫn giữ được mục tiêu ban đầu của đề tài: **nhanh, tiện lợi, hiện đại, cá nhân hóa theo ngân sách và mục tiêu sức khỏe**.
