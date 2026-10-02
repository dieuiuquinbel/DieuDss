"""
NutriDSS - ML Model Training, Cross-Validation & Evaluation Pipeline
Fixes ML Methodology Vulnerabilities (Fix.md Sections 36, 37, 38 & P0.1 - P0.4):
1. Uses synthetic baseline dataset with honest provenance labeling.
2. Group-aware train/test split (GroupKFold by user_id) to eliminate cross-scenario data leakage.
3. Model selection strictly performed on Cross-Validation (CV) performance, NOT on the test set.
4. Test set evaluated exactly once as a true final holdout.
5. Baseline DummyRegressor included for rigorous comparative benchmarking.
"""

import os
import sys
import json
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sklearn

from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor


def train_and_evaluate():
    # Prefer explicitly labeled synthetic baseline dataset
    dataset_path = 'data/processed/synthetic_baseline_dataset.csv'
    if not os.path.exists(dataset_path):
        dataset_path = 'data/processed/survey_scenarios_dataset.csv'
        
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset not found at {dataset_path}")
        return
        
    df_ml = pd.read_csv(dataset_path)
    print(f"[DATA] Loaded {len(df_ml)} baseline scenario samples from {dataset_path}")
    
    feature_cols = ['goal', 'budget_vnd', 'calories', 'protein_g', 'carb_g', 'fat_g', 'estimated_cost_vnd', 'cost_ratio']
    X = df_ml[feature_cols]
    y = df_ml['compatibility_rating']
    groups = df_ml['user_id'] if 'user_id' in df_ml.columns else df_ml.index

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

    # 1. GROUP-AWARE SPLIT (P0.3): Split users so same user doesn't leak into train & test
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))
    
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    groups_train = groups.iloc[train_idx]
    
    print(f"[SPLIT] Train samples: {len(X_train)} (unique users: {groups_train.nunique()}), Test samples: {len(X_test)}")

    # 2. MODEL CANDIDATES (including Dummy Regressor baseline)
    models = {
        "Dummy Regressor (Baseline)": DummyRegressor(strategy='mean'),
        "Linear Regression": LinearRegression(),
        "Ridge Regressor": Ridge(alpha=1.0),
        "KNN Regressor": KNeighborsRegressor(n_neighbors=5),
        "Decision Tree": DecisionTreeRegressor(max_depth=6, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, max_depth=4, random_state=42),
        "ANN (MLPRegressor)": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }

    results = []
    gkf = GroupKFold(n_splits=5)

    print("\n[CV] Running 5-Fold GroupKFold Cross-Validation on Training Set...")
    for name, model in models.items():
        pipe = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('regressor', model)
        ])
        
        # Cross-validation evaluated strictly on (X_train, y_train) using GroupKFold
        cv_r2_scores = []
        cv_mae_scores = []
        for cv_tr_idx, cv_val_idx in gkf.split(X_train, y_train, groups_train):
            pipe_cv = Pipeline(steps=[
                ('preprocessor', preprocessor),
                ('regressor', model)
            ])
            pipe_cv.fit(X_train.iloc[cv_tr_idx], y_train.iloc[cv_tr_idx])
            val_preds = pipe_cv.predict(X_train.iloc[cv_val_idx])
            cv_r2_scores.append(r2_score(y_train.iloc[cv_val_idx], val_preds))
            cv_mae_scores.append(mean_absolute_error(y_train.iloc[cv_val_idx], val_preds))
            
        cv_r2_mean = float(np.mean(cv_r2_scores))
        cv_r2_std = float(np.std(cv_r2_scores))
        cv_mae_mean = float(np.mean(cv_mae_scores))

        # Fit model on entire train set
        pipe.fit(X_train, y_train)
        
        results.append({
            "Model": name,
            "CV_R2_Mean": round(cv_r2_mean, 4),
            "CV_R2_Std": round(cv_r2_std, 4),
            "CV_MAE_Mean": round(cv_mae_mean, 4),
            "Pipeline": pipe
        })

    # 3. MODEL SELECTION STRICTLY BY CROSS-VALIDATION (P0.2)
    valid_candidates = [r for r in results if "Dummy" not in r["Model"]]
    best_candidate = max(valid_candidates, key=lambda x: x["CV_R2_Mean"])
    print(f"\n[SELECTION] Best model selected via 5-Fold Group CV: '{best_candidate['Model']}' (CV R2 = {best_candidate['CV_R2_Mean']})")

    # 4. FINAL TEST EVALUATION (Evaluated on Holdout Test Set)
    for r in results:
        pipe = r["Pipeline"]
        y_pred = pipe.predict(X_test)
        r["Test_R2"] = round(float(r2_score(y_test, y_pred)), 4)
        r["Test_MAE"] = round(float(mean_absolute_error(y_test, y_pred)), 4)
        r["Test_RMSE"] = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4)

    df_results = pd.DataFrame(results)[["Model", "CV_R2_Mean", "CV_R2_Std", "CV_MAE_Mean", "Test_R2", "Test_MAE", "Test_RMSE"]]
    df_results.sort_values(by="CV_R2_Mean", ascending=False, inplace=True)
    
    print("\n" + "="*85)
    print(" NUTRIDSS ML MODELS BENCHMARK (GROUP-KFOLD CV & FINAL HOLDOUT TEST)")
    print("="*85)
    print(df_results.to_string(index=False))
    print("="*85 + "\n")
    
    # Save comparison chart
    os.makedirs('docs', exist_ok=True)
    try:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        sns.barplot(data=df_results, x='CV_R2_Mean', y='Model', ax=axes[0], palette='Blues_r')
        axes[0].set_title('CV R2 Mean (Model Selection Metric)')
        sns.barplot(data=df_results, x='Test_MAE', y='Model', ax=axes[1], palette='Reds_r')
        axes[1].set_title('Test MAE (Holdout Evaluation)')
        sns.barplot(data=df_results, x='Test_RMSE', y='Model', ax=axes[2], palette='Oranges_r')
        axes[2].set_title('Test RMSE (Holdout Evaluation)')
        plt.tight_layout()
        plt.savefig('docs/ml_models_performance_comparison.png', dpi=300)
        plt.close()
        print("[GRAPH] Saved comparison plot to docs/ml_models_performance_comparison.png")
    except Exception as e:
        print(f"[GRAPH WARNING] Plot generation error: {e}")
    
    # Export locked best model
    os.makedirs("models", exist_ok=True)
    best_pipeline = best_candidate["Pipeline"]
    joblib.dump(best_pipeline, "models/best_recipe_ranker.joblib")
    print(f"[BEST MODEL] Exported '{best_candidate['Model']}' to models/best_recipe_ranker.joblib")

    # Export Model Metadata with honest documentation
    metadata = {
        "model_name": best_candidate["Model"],
        "model_selection_strategy": "Best 5-Fold GroupKFold Cross-Validation R2 on Train Set",
        "trained_at": datetime.datetime.now().isoformat(),
        "scikit_learn_version": sklearn.__version__,
        "dataset_path": dataset_path,
        "dataset_type": "synthetic_baseline_dataset",
        "dataset_samples": len(df_ml),
        "features": feature_cols,
        "metrics": {
            "cv_5fold_r2_mean": best_candidate["CV_R2_Mean"],
            "cv_5fold_r2_std": best_candidate["CV_R2_Std"],
            "cv_5fold_mae_mean": best_candidate["CV_MAE_Mean"],
            "test_r2": best_candidate["Test_R2"],
            "test_mae": best_candidate["Test_MAE"],
            "test_rmse": best_candidate["Test_RMSE"]
        },
        "evaluation_note": (
            "Model is trained and benchmarked on synthetic baseline scenario data. "
            "Metrics reflect the algorithm's capability to learn heuristic fitness functions. "
            "Real-world recommendation accuracy will be evaluated on production user interaction logs."
        ),
        "all_models_summary": [
            {
                "model": r["Model"],
                "cv_r2_mean": r["CV_R2_Mean"],
                "cv_mae_mean": r["CV_MAE_Mean"],
                "test_r2": r["Test_R2"],
                "test_mae": r["Test_MAE"],
                "test_rmse": r["Test_RMSE"]
            }
            for r in results
        ]
    }
    with open("models/model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    print("[METADATA] Exported updated model metadata to models/model_metadata.json")

if __name__ == "__main__":
    train_and_evaluate()
