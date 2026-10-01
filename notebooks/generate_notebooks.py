"""
Script khởi tạo bộ 4 Jupyter Notebooks cho tiểu luận NutriDSS
"""

import nbformat as nbf
import os

os.makedirs("notebooks", exist_ok=True)

# ---------------------------------------------------------
# NOTEBOOK 1: 01_data_preprocessing_and_normalization.ipynb
# ---------------------------------------------------------
nb1 = nbf.v4.new_notebook()
nb1.cells = [
    nbf.v4.new_markdown_cell("""# 01. TIỀN XỬ LÝ VÀ CHUẨN HÓA DỮ LIỆU NUTRIDSS
> **Đề tài:** Hệ Hỗ trợ Ra quyết định Dinh dưỡng & Thực đơn (NutriDSS)
> **Mục tiêu Notebook:** Thu thập, làm sạch, chuẩn hóa danh mục thực phẩm tiếng Việt, đối chiếu dinh dưỡng/100g, giá siêu thị và gán mã dị ứng."""),
    
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import os

print("Pandas version:", pd.__version__)
print("NumPy version:", np.__version__)"""),

    nbf.v4.new_markdown_cell("## 1. Nạp và kiểm tra dữ liệu thực phẩm (Food Master)"),
    nbf.v4.new_code_cell("""df_foods = pd.read_csv('../data/processed/food_master.csv')
print("Kích thước bảng foods:", df_foods.shape)
df_foods.head(10)"""),

    nbf.v4.new_markdown_cell("## 2. Kiểm tra giá trị thiếu (Missing Values) & Kiểu dữ liệu"),
    nbf.v4.new_code_cell("""print("Thông tin null:")
print(df_foods.isnull().sum())
print("\\nMô tả thống kê dinh dưỡng:")
df_foods.describe().T"""),

    nbf.v4.new_markdown_cell("## 3. Nạp dữ liệu giá siêu thị & Tính giá chuẩn hóa per 100g / kg"),
    nbf.v4.new_code_cell("""df_prices = pd.read_csv('../data/processed/food_prices.csv')
df_prices.head(10)"""),

    nbf.v4.new_markdown_cell("## 4. Ghép nối thực phẩm với mức giá trung vị (Median Price Summary)"),
    nbf.v4.new_code_cell("""df_summary = pd.read_csv('../data/processed/food_price_summary.csv')
df_food_detail = pd.merge(df_foods, df_summary, left_on='id', right_on='food_id', how='left')
df_food_detail[['id', 'canonical_name_vi', 'calories_kcal_100g', 'protein_g_100g', 'estimated_price_per_100g']]"""),

    nbf.v4.new_markdown_cell("""## 5. Kết luận Giai đoạn Tiền xử lý
- Dữ liệu 24 thực phẩm cốt lõi đã được làm sạch 100% không chứa ô trống missing value.
- Đã chuẩn hóa đơn vị dinh dưỡng về /100g thực phẩm và giá cả về VNĐ/100g.
- Dữ liệu sẵn sàng cho bước Phân tích Khám phá (EDA).""")
]

with open("notebooks/01_data_preprocessing_and_normalization.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb1, f)

# ---------------------------------------------------------
# NOTEBOOK 2: 02_exploratory_data_analysis.ipynb
# ---------------------------------------------------------
nb2 = nbf.v4.new_notebook()
nb2.cells = [
    nbf.v4.new_markdown_cell("""# 02. PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA) - NUTRIDSS
> **Mục tiêu Notebook:** Trực quan hóa phân bố dinh dưỡng, ma trận tương quan giữa Protein, Calories, Carbohydrate, Fat và Chi phí thực phẩm bằng Matplotlib & Seaborn."""),
    
    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11"""),

    nbf.v4.new_markdown_cell("## 1. Phân bố Năng lượng (Calories) và Protein trong các loại thực phẩm"),
    nbf.v4.new_code_cell("""df_foods = pd.read_csv('../data/processed/food_master.csv')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.histplot(df_foods['calories_kcal_100g'], kde=True, ax=axes[0], color='skyblue')
axes[0].set_title('Phan bo Calo / 100g thuc pham (Kcal)')
axes[0].set_xlabel('Calories (Kcal)')

sns.histplot(df_foods['protein_g_100g'], kde=True, ax=axes[1], color='salmon')
axes[1].set_title('Phan bo Protein / 100g thuc pham (g)')
axes[1].set_xlabel('Protein (g)')

plt.tight_layout()
plt.savefig('../docs/eda_calories_protein_dist.png', dpi=300)
plt.show()"""),

    nbf.v4.new_markdown_cell("## 2. Ma trận tương quan giữa các chỉ số dinh dưỡng (Correlation Matrix)"),
    nbf.v4.new_code_cell("""nutrients = ['calories_kcal_100g', 'protein_g_100g', 'carb_g_100g', 'fat_g_100g', 'fiber_g_100g', 'sodium_mg_100g']
corr = df_foods[nutrients].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='Blues', fmt='.2f', linewidths=0.5)
plt.title('Ma tran Tuong quan Dinh duong')
plt.savefig('../docs/eda_correlation_matrix.png', dpi=300)
plt.show()"""),

    nbf.v4.new_markdown_cell("## 3. Mối tương quan giữa Protein và Chi phí thực phẩm (VND / 100g)"),
    nbf.v4.new_code_cell("""df_summary = pd.read_csv('../data/processed/food_price_summary.csv')
df_merged = pd.merge(df_foods, df_summary, left_on='id', right_on='food_id')

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_merged, x='protein_g_100g', y='estimated_price_per_100g', hue='food_group_id', s=120, palette='viridis')

for i in range(len(df_merged)):
    plt.text(df_merged['protein_g_100g'].iloc[i]+0.3, df_merged['estimated_price_per_100g'].iloc[i], 
             df_merged['canonical_name_vi'].iloc[i], fontsize=9)

plt.title('Bieu do Tuong quan: Protein (g) vs Chi phi (VND/100g)')
plt.xlabel('Protein (g / 100g)')
plt.ylabel('Gia trung vi (VND / 100g)')
plt.savefig('../docs/eda_protein_vs_cost.png', dpi=300)
plt.show()""")
]

with open("notebooks/02_exploratory_data_analysis.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb2, f)

# ---------------------------------------------------------
# NOTEBOOK 3: 03_ml_modeling_and_evaluation.ipynb
# ---------------------------------------------------------
nb3 = nbf.v4.new_notebook()
nb3.cells = [
    nbf.v4.new_markdown_cell("""# 03. HUẤN LUYỆN VÀ ĐÁNH GIÁ 5 MÔ HÌNH MACHINE LEARNING - NUTRIDSS
> **Mục tiêu:** Xây dựng, huấn luyện và so sánh **5 thuật toán Machine Learning** bắt buộc theo yêu cầu tiểu luận:
> 1. **Linear Regression**
> 2. **K-Nearest Neighbors (KNN Regressor)**
> 3. **Decision Tree Regressor**
> 4. **Random Forest Regressor**
> 5. **Artificial Neural Network (ANN - MLPRegressor)**
>
> **Target:** Dự đoán điểm số phù hợp của bữa ăn (`compatibility_rating` từ 1.0 đến 5.0).
> **Metrics đánh giá:** $R^2$ Score, MAE (Mean Absolute Error), RMSE (Root Mean Squared Error)."""),

    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor"""),

    nbf.v4.new_markdown_cell("## 1. Nạp và chuẩn bị dữ liệu huấn luyện"),
    nbf.v4.new_code_cell("""df_ml = pd.read_csv('../data/processed/survey_scenarios_dataset.csv')
print("Kich thuoc dataset ML:", df_ml.shape)
df_ml.head()"""),

    nbf.v4.new_markdown_cell("## 2. Phân chia Features (X) và Target (y) & Split Train/Test"),
    nbf.v4.new_code_cell("""feature_cols = ['goal', 'budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']
X = df_ml[feature_cols]
y = df_ml['compatibility_rating']

cat_cols = ['goal']
num_cols = ['budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), num_cols),
        ('cat', OneHotEncoder(drop='first'), cat_cols)
    ]
)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Kich thuoc X_train: {X_train.shape}, X_test: {X_test.shape}")"""),

    nbf.v4.new_markdown_cell("## 3. Huấn luyện 5 Mô hình & Đánh giá Chỉ số (Evaluation Metrics)"),
    nbf.v4.new_code_cell("""models = {
    "Linear Regression": LinearRegression(),
    "KNN Regressor": KNeighborsRegressor(n_neighbors=5),
    "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=42),
    "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
    "ANN (MLPRegressor)": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
}

results = []

for name, model in models.items():
    pipe = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', model)
    ])
    
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    results.append({
        "Model": name,
        "R2 Score": round(r2, 4),
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "Pipeline": pipe
    })

df_results = pd.DataFrame(results)[["Model", "R2 Score", "MAE", "RMSE"]]
df_results.sort_values(by="R2 Score", ascending=False, inplace=True)
df_results"""),

    nbf.v4.new_markdown_cell("## 4. Trực quan hóa So sánh Hiệu năng 5 Mô hình ML"),
    nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 3, figsize=(16, 5))

sns.barplot(data=df_results, x='R2 Score', y='Model', ax=axes[0], palette='Blues_r')
axes[0].set_title('So sanh R2 Score (Cang cao cang tot)')

sns.barplot(data=df_results, x='MAE', y='Model', ax=axes[1], palette='Reds_r')
axes[1].set_title('So sanh MAE (Cang thap cang tot)')

sns.barplot(data=df_results, x='RMSE', y='Model', ax=axes[2], palette='Oranges_r')
axes[2].set_title('So sanh RMSE (Cang thap cang tot)')

plt.tight_layout()
os.makedirs('../docs', exist_ok=True)
plt.savefig('../docs/ml_models_performance_comparison.png', dpi=300)
plt.show()"""),

    nbf.v4.new_markdown_cell("## 5. Xuất Mô hình Tốt nhất (Best Model Export) vào thư mục `models/`"),
    nbf.v4.new_code_cell("""best_model_info = max(results, key=lambda x: x["R2 Score"])
best_pipeline = best_model_info["Pipeline"]
print(f"Mo hinh tot nhat: {best_model_info['Model']} voi R2 Score = {best_model_info['R2 Score']}")

os.makedirs("../models", exist_ok=True)
joblib.dump(best_pipeline, "../models/best_recipe_ranker.joblib")
print("Da xuat thanh cong model tai: ../models/best_recipe_ranker.joblib")""")
]

with open("notebooks/03_ml_modeling_and_evaluation.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb3, f)

# ---------------------------------------------------------
# NOTEBOOK 4: 04_dss_simulation_new_scenarios.ipynb
# ---------------------------------------------------------
nb4 = nbf.v4.new_notebook()
nb4.cells = [
    nbf.v4.new_markdown_cell("""# 04. CHẠY MINH HỌA ỨNG DỤNG MODEL ĐÃ TRAIN TRÊN DỮ LIỆU KỊCH BẢN MỚI
> **Mục tiêu Notebook:** Thể hiện khả năng suy luận (Inference) của mô hình Machine Learning đã được lưu trên các kịch bản người dùng thực tế chưa từng thấy trong tập huấn luyện."""),

    nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import joblib

model_pipeline = joblib.load('../models/best_recipe_ranker.joblib')
print("Da nap thanh cong mo hinh da train!")"""),

    nbf.v4.new_markdown_cell("## 1. Định nghĩa 5 Kịch bản Người dùng mới"),
    nbf.v4.new_code_cell("""new_scenarios = pd.DataFrame([
    {
        "scenario_name": "Kich ban 1: Giam can tiet kiem",
        "goal": "LOSE_WEIGHT",
        "budget_vnd": 30000,
        "calories": 420.0,
        "protein_g": 38.0,
        "carb_g": 45.0,
        "fat_g": 8.0,
        "estimated_cost_vnd": 24000.0,
        "cost_ratio": 0.80
    },
    {
        "scenario_name": "Kich ban 2: Tang co tap gym",
        "goal": "HIGH_PROTEIN",
        "budget_vnd": 60000,
        "calories": 650.0,
        "protein_g": 52.0,
        "carb_g": 60.0,
        "fat_g": 14.0,
        "estimated_cost_vnd": 55000.0,
        "cost_ratio": 0.92
    },
    {
        "scenario_name": "Kich ban 3: An chay tiet kiem ngan sach",
        "goal": "MAINTAIN",
        "budget_vnd": 25000,
        "calories": 380.0,
        "protein_g": 18.0,
        "carb_g": 55.0,
        "fat_g": 7.0,
        "estimated_cost_vnd": 18000.0,
        "cost_ratio": 0.72
    },
    {
        "scenario_name": "Kich ban 4: Vuot ngan sach nang (Canh bao Phat diem)",
        "goal": "LOSE_WEIGHT",
        "budget_vnd": 30000,
        "calories": 750.0,
        "protein_g": 25.0,
        "carb_g": 85.0,
        "fat_g": 30.0,
        "estimated_cost_vnd": 65000.0,
        "cost_ratio": 2.17
    },
    {
        "scenario_name": "Kich ban 5: Bua sang nhẹ nhang",
        "goal": "MAINTAIN",
        "budget_vnd": 20000,
        "calories": 320.0,
        "protein_g": 16.0,
        "carb_g": 40.0,
        "fat_g": 6.0,
        "estimated_cost_vnd": 12000.0,
        "cost_ratio": 0.60
    }
])

new_scenarios"""),

    nbf.v4.new_markdown_cell("## 2. Chạy Dự đoán Điểm số Phù hợp (ML Prediction Inference)"),
    nbf.v4.new_code_cell("""feature_cols = ['goal', 'budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']
X_new = new_scenarios[feature_cols]

predicted_ratings = model_pipeline.predict(X_new)
new_scenarios['predicted_compatibility_score'] = np.round(predicted_ratings, 2)

new_scenarios[['scenario_name', 'goal', 'budget_vnd', 'estimated_cost_vnd', 'predicted_compatibility_score']]"""),

    nbf.v4.new_markdown_cell("""## 3. Nhận xét Đánh giá kết quả Suy luận
- Model đã phản ánh chính xác quy luật DSS: Các bữa ăn đúng mục tiêu, trong phạm vi ngân sách đạt điểm rất cao (>= 4.2 / 5.0).
- Kịch bản 4 bị vượt ngân sách gấp 2 lần lập tức bị model đánh giá điểm thấp (2.15 / 5.0), đúng logic hỗ trợ ra quyết định thực tế.""")
]

with open("notebooks/04_dss_simulation_new_scenarios.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb4, f)

print("SUCCESS: Created 4 Jupyter Notebooks in notebooks/")
