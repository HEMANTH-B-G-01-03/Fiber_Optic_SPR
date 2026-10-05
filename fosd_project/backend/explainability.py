
import json
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

FEATURES = ["wavelength_nm", "sensing_length_mm", "analyte_ri", "ag_thickness_nm"]

with open("../models/best_model.json") as f:
    meta = json.load(f)
best_model_name = meta["best_model"]

df = pd.read_csv("../data/fosd_dataset.csv")
X = df[FEATURES]

model = joblib.load(f"../models/{best_model_name}.joblib")
print(f"Explaining model: {best_model_name}")

if not HAS_SHAP:
    print("shap not installed in this environment - run this script on your machine "
          "(pip install shap) to generate the plots below.")
else:
    # subsample for speed
    X_sample = X.sample(n=min(1500, len(X)), random_state=42)

    if best_model_name in ("RandomForest", "XGBoost", "CatBoost"):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X_sample)
    else:
        # ANN / MLP - use KernelExplainer
        background = X_sample.sample(n=100, random_state=1)
        explainer = shap.KernelExplainer(model.predict, background)
        sv = explainer.shap_values(X_sample.sample(n=200, random_state=2))
        shap_values = shap.Explanation(values=sv, data=X_sample.sample(n=200, random_state=2).values,
                                        feature_names=FEATURES)

    # Global summary (beeswarm) plot
    plt.figure()
    shap.summary_plot(shap_values, X_sample if hasattr(shap_values, "values") is False else None,
                       show=False)
    plt.tight_layout()
    plt.savefig("../outputs/shap_summary.png", dpi=150)
    plt.close()

    # Mean |SHAP| bar chart
    plt.figure()
    shap.summary_plot(shap_values, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig("../outputs/shap_mean_importance.png", dpi=150)
    plt.close()

    # Save mean importance table
    vals = np.abs(shap_values.values).mean(axis=0)
    importance_df = pd.DataFrame({"feature": FEATURES, "mean_abs_shap": vals}).sort_values(
        "mean_abs_shap", ascending=False)
    importance_df.to_csv("../outputs/shap_feature_importance.csv", index=False)
    print(importance_df)

    # Local explanation example (single instance) - waterfall plot 
    plt.figure()
    shap.plots.waterfall(shap_values[0], show=False)
    plt.tight_layout()
    plt.savefig("../outputs/shap_local_waterfall.png", dpi=150)
    plt.close()

    print("Saved SHAP global summary, bar importance, feature importance table, "
          "and a local waterfall explanation.")
