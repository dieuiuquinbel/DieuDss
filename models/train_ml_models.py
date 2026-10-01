import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import json
import datetime
import sklearn

from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

def train_and_evaluate():
    dataset_path = 'data/processed/survey_scenarios_dataset.csv'
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at {dataset_path}")
        return
        
    df_ml = pd.read_csv(dataset_path)
    print(f"[DATA] Loaded {len(df_ml)} scenario samples from {dataset_path}")
    
    feature_cols = ['goal', 'budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']
    X = df_ml[feature_cols]
    y = df_ml['compatibility_rating']

    cat_cols = ['goal']
    num_cols = ['budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']

    num_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    cat_pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(drop='first', handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, num_cols),
            ('cat', cat_pipeline, cat_cols)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Danh sách thuật toán bao gồm DummyRegressor baseline + 5 thuật toán
    models = {
        "Dummy Regressor (Baseline)": DummyRegressor(strategy='mean'),
        "Linear Regression": LinearRegression(),
        "KNN Regressor": KNeighborsRegressor(n_neighbors=5),
        "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
        "ANN (MLPRegressor)": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

    results = []
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in models.items():
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])
        
        # 5-Fold Cross Validation
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=kf, scoring='r2')
        cv_r2_mean = float(np.mean(cv_scores))
        cv_r2_std = float(np.std(cv_scores))

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        
        r2 = float(r2_score(y_test, y_pred))
        mae = float(mean_absolute_error(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        
        results.append({
            "Model": name,
            "CV_R2_Mean": round(cv_r2_mean, 4),
            "CV_R2_Std": round(cv_r2_std, 4),
            "Test_R2": round(r2, 4),
            "Test_MAE": round(mae, 4),
            "Test_RMSE": round(rmse, 4),
            "Pipeline": pipe
        })

    df_results = pd.DataFrame(results)[["Model", "CV_R2_Mean", "CV_R2_Std", "Test_R2", "Test_MAE", "Test_RMSE"]]
    df_results.sort_values(by="Test_R2", ascending=False, inplace=True)
    
    print("\n" + "="*80)
    print(" NUTRIDSS ML MODELS BENCHMARK & CROSS-VALIDATION COMPARISON")
    print("="*80)
    print(df_results.to_string(index=False))
    print("="*80 + "\n")
    
    # Lưu biểu đồ so sánh
    os.makedirs('docs', exist_ok=True)
    try:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        sns.barplot(data=df_results, x='Test_R2', y='Model', ax=axes[0], palette='Blues_r')
        axes[0].set_title('Test R2 Score (Higher is Better)')
        sns.barplot(data=df_results, x='Test_MAE', y='Model', ax=axes[1], palette='Reds_r')
        axes[1].set_title('Test MAE (Lower is Better)')
        sns.barplot(data=df_results, x='Test_RMSE', y='Model', ax=axes[2], palette='Oranges_r')
        axes[2].set_title('Test RMSE (Lower is Better)')
        plt.tight_layout()
        plt.savefig('docs/ml_models_performance_comparison.png', dpi=300)
        plt.close()
        print("[GRAPH] Saved comparison plot to docs/ml_models_performance_comparison.png")
    except Exception as e:
        print(f"[GRAPH WARNING] Plot generation error: {e}")
    
    # Chọn mô hình thực sự tốt nhất (ngoại trừ Dummy)
    valid_candidates = [r for r in results if "Dummy" not in r["Model"]]
    best_model_info = max(valid_candidates, key=lambda x: x["Test_R2"])
    best_pipeline = best_model_info["Pipeline"]
    
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_pipeline, "models/best_recipe_ranker.joblib")
    print(f"[BEST MODEL] Exported '{best_model_info['Model']}' to models/best_recipe_ranker.joblib (Test R2 = {best_model_info['Test_R2']})")

    # Xuất Metadata Model
    metadata = {
        "model_name": best_model_info["Model"],
        "trained_at": datetime.datetime.now().isoformat(),
        "scikit_learn_version": sklearn.__version__,
        "dataset_path": dataset_path,
        "dataset_samples": len(df_ml),
        "features": feature_cols,
        "metrics": {
            "test_r2": best_model_info["Test_R2"],
            "test_mae": best_model_info["Test_MAE"],
            "test_rmse": best_model_info["Test_RMSE"],
            "cv_5fold_r2_mean": best_model_info["CV_R2_Mean"],
            "cv_5fold_r2_std": best_model_info["CV_R2_Std"]
        },
        "all_models_summary": [
            {
                "model": r["Model"],
                "cv_r2_mean": r["CV_R2_Mean"],
                "test_r2": r["Test_R2"],
                "test_mae": r["Test_MAE"],
                "test_rmse": r["Test_RMSE"]
            }
            for r in results
        ]
    }
    with open("models/model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print("[METADATA] Exported model metadata to models/model_metadata.json")

if __name__ == "__main__":
    train_and_evaluate()
