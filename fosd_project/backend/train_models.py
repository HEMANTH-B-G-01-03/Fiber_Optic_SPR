
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    from catboost import CatBoostRegressor
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

FEATURES = ["wavelength_nm", "sensing_length_mm", "analyte_ri", "ag_thickness_nm"]
TARGET = "fom_riu_inv"

df = pd.read_csv("../data/fosd_dataset.csv")
X = df[FEATURES].values
y = df[TARGET].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

results = {}
predictions = {}
models = {}

# Random Forest 
rf = RandomForestRegressor(n_estimators=150, max_depth=10, min_samples_leaf=5, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
predictions["RandomForest"] = rf.predict(X_test)
models["RandomForest"] = rf

# XGBoost 
if HAS_XGB:
    xgb = XGBRegressor(n_estimators=400, max_depth=6, learning_rate=0.05,
                        subsample=0.9, colsample_bytree=0.9, random_state=42)
    xgb.fit(X_train, y_train)
    predictions["XGBoost"] = xgb.predict(X_test)
    models["XGBoost"] = xgb
else:
    print("xgboost not installed in this environment - skipping (will run on user's machine)")

# CatBoost 
if HAS_CATBOOST:
    cb = CatBoostRegressor(iterations=600, depth=8, learning_rate=0.05,
                            loss_function="MAE", random_seed=42, verbose=False)
    cb.fit(X_train, y_train)
    predictions["CatBoost"] = cb.predict(X_test)
    models["CatBoost"] = cb
else:
    print("catboost not installed in this environment - skipping (will run on user's machine)")

# ANN -
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

ann = MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", solver="adam",
                    max_iter=2000, random_state=42, early_stopping=True)
ann.fit(X_train_s, y_train)
predictions["ANN"] = ann.predict(X_test_s)
models["ANN"] = ann

# Metrics 
metrics_rows = []
for name, y_pred in predictions.items():
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    metrics_rows.append({"Model": name, "MAE": mae, "RMSE": rmse, "R2": r2})

metrics_df = pd.DataFrame(metrics_rows).sort_values("MAE")
print(metrics_df)
metrics_df.to_csv("../outputs/model_metrics.csv", index=False)

best_model_name = metrics_df.iloc[0]["Model"]
print(f"\nBest model (lowest MAE): {best_model_name}")

# Trend-matching plots -
n_models = len(predictions)
fig, axes = plt.subplots(1, n_models, figsize=(5 * n_models, 4), sharey=True)
if n_models == 1:
    axes = [axes]

rng_plot = np.random.default_rng(42)
y_test_arr = np.asarray(y_test)
n_sample = min(200, len(y_test_arr))
sample_idx = rng_plot.choice(len(y_test_arr), size=n_sample, replace=False)
order_idx = sample_idx[np.argsort(y_test_arr[sample_idx])]
for ax, (name, y_pred) in zip(axes, predictions.items()):
    ax.plot(y_test_arr[order_idx], label="Actual", color="black", linewidth=1.5)
    ax.plot(np.array(y_pred)[order_idx], label="Predicted", color="tab:red", linewidth=1, alpha=0.8)
    ax.set_title(name)
    ax.set_xlabel("Test sample (sorted by actual FoM)")
    ax.legend(fontsize=8)
axes[0].set_ylabel("FoM (RIU$^{-1}$)")
plt.tight_layout()
plt.savefig("../outputs/trend_matching.png", dpi=150)
plt.close()


for name, model in models.items():
    joblib.dump(model, f"../models/{name}.joblib")
joblib.dump(scaler, "../models/ann_scaler.joblib")

with open("../models/best_model.json", "w") as f:
    json.dump({"best_model": best_model_name, "features": FEATURES, "target": TARGET}, f, indent=2)

print("\nSaved models, scaler, metrics, and trend-matching plot.")
