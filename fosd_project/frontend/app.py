
import json
import sys
import os
import numpy as np
import pandas as pd
import joblib
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from tmm_simulator import (resonance_wavelength, resonance_sweep, fwhm_only,AG_THICKNESS_RANGE_NM, SENSING_LENGTH_RANGE_MM, ANALYTE_RI_RANGE)
from optimizer import recommend_parameters

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

BASE = os.path.join(os.path.dirname(__file__), "..")
FEATURES = ["wavelength_nm", "sensing_length_mm", "analyte_ri", "ag_thickness_nm"]

st.set_page_config(page_title="FOSD Sensor Intelligence Platform", layout="wide")


@st.cache_resource
def load_model():
    with open(os.path.join(BASE, "models", "best_model.json")) as f:
        meta = json.load(f)
    model = joblib.load(os.path.join(BASE, "models", f"{meta['best_model']}.joblib"))
    scaler = None
    if meta["best_model"] == "ANN":
        scaler = joblib.load(os.path.join(BASE, "models", "ann_scaler.joblib"))
    return model, meta, scaler


@st.cache_data
def load_data():
    return pd.read_csv(os.path.join(BASE, "data", "fosd_dataset.csv"))


@st.cache_data
def load_metrics():
    return pd.read_csv(os.path.join(BASE, "outputs", "model_metrics.csv"))


model, meta, scaler = load_model()
df = load_data()
metrics_df = load_metrics()


def predict_fom(wavelength, L, ri, thickness):
    X = np.array([[wavelength, L, ri, thickness]])
    if scaler is not None:
        X = scaler.transform(X)
    return float(model.predict(X)[0])



st.sidebar.title("FOSD Sensor Intelligence Platform")
page = st.sidebar.radio("Go to", [
    "Overview", "Live FoM Predictor", "Model Comparison",
    "Explainable AI (SHAP)", "Parameter Recommendation"
])
st.sidebar.markdown("---")


if page == "Overview":
    st.title("Fiber-Optic SPR Sensor: ML-Driven Design & Optimization")
    st.markdown("""


**Pipeline:**
1. A physics-informed simulator generates the FOSD dataset (wavelength,
   sensing length, analyte RI, Ag thickness -> Figure of Merit).
2. Four ML models (Random Forest, XGBoost, CatBoost, ANN) are trained and
   compared to predict FoM.
3. SHAP explains *why* the best model makes its predictions.
4. An inverse-design optimizer recommends the sensing length
   and Ag thickness that maximize FoM for a target analyte RI.
""")
    c1, c2, c3 = st.columns(3)
    c1.metric("Dataset rows", f"{len(df):,}")
    c2.metric("Best model", meta["best_model"])
    best_mae = metrics_df.sort_values("MAE").iloc[0]["MAE"]
    c3.metric("Best MAE (RIU⁻¹)", f"{best_mae:.3f}")

    st.subheader("Dataset preview")
    st.dataframe(df.sample(10, random_state=1), use_container_width=True)


# Page: Live FoM Predictor

elif page == "Live FoM Predictor":
    st.title("Live FoM Predictor")
   

    col1, col2 = st.columns([1, 1.3])
    with col1:
        thickness = st.slider("Ag thickness (nm)", float(AG_THICKNESS_RANGE_NM[0]),
                               float(AG_THICKNESS_RANGE_NM[1]), 42.0, 0.5)
        L = st.slider("Sensing length L (mm)", float(SENSING_LENGTH_RANGE_MM[0]),
                       float(SENSING_LENGTH_RANGE_MM[1]), 17.0, 0.5)
        ri = st.slider("Analyte refractive index", float(ANALYTE_RI_RANGE[0]),
                        float(ANALYTE_RI_RANGE[1]), 1.35, 0.001, format="%.3f")
        lam = resonance_wavelength(thickness, L, ri)
        fom = predict_fom(lam, L, ri, thickness)
        st.info(f"Implied resonance wavelength: **{lam:.1f} nm**")
        st.success(f"Predicted FoM: **{fom:.2f} RIU⁻¹**")

    with col2:
        # sweep RI at fixed L/thickness to show sensitivity curve
        ri_sweep = np.linspace(ANALYTE_RI_RANGE[0], ANALYTE_RI_RANGE[1], 60)
        wl_sweep = resonance_sweep(thickness, L, ri_sweep)
        foms = [predict_fom(wl, L, r, thickness) for wl, r in zip(wl_sweep, ri_sweep)]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(ri_sweep, foms, color="tab:blue")
        ax.axvline(ri, color="red", linestyle="--", label="current RI")
        ax.set_xlabel("Analyte RI")
        ax.set_ylabel("Predicted FoM (RIU⁻¹)")
        ax.set_title(f"FoM vs analyte RI (L={L} mm, t={thickness} nm)")
        ax.legend()
        st.pyplot(fig)


# Page: Model Comparison

elif page == "Model Comparison":
    st.title("Model Comparison")
    st.dataframe(metrics_df.sort_values("MAE").reset_index(drop=True), use_container_width=True)

    trend_path = os.path.join(BASE, "outputs", "trend_matching.png")
    if os.path.exists(trend_path):
        st.subheader("Actual vs Predicted FoM (trend matching)")
        st.image(trend_path, use_container_width=True)
    else:
        st.warning("Trend-matching plot not found. Run backend/train_models.py first.")


# Page: Explainable AI

elif page == "Explainable AI (SHAP)":
    st.title("Explainable AI - SHAP")
    st.markdown(f"Explaining the best model: **{meta['best_model']}**")

    summary_path = os.path.join(BASE, "outputs", "shap_summary.png")
    bar_path = os.path.join(BASE, "outputs", "shap_mean_importance.png")
    local_path = os.path.join(BASE, "outputs", "shap_local_waterfall.png")
    imp_csv = os.path.join(BASE, "outputs", "shap_feature_importance.csv")

    if os.path.exists(imp_csv):
        st.subheader("Global feature importance")
        st.dataframe(pd.read_csv(imp_csv), use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["Summary (beeswarm)", "Mean |SHAP| bar", "Local explanation (novelty)"])
    with tab1:
        if os.path.exists(summary_path):
            st.image(summary_path, use_container_width=True)
        else:
            st.warning("Run backend/explainability.py (requires `pip install shap`) to generate this plot.")
    with tab2:
        if os.path.exists(bar_path):
            st.image(bar_path, use_container_width=True)
        else:
            st.warning("Run backend/explainability.py to generate this plot.")
    with tab3:
        st.markdown("Per-prediction explanation - shows *why* one specific design got its FoM score "
                     "(the paper only reports global importance, not per-instance explanations).")
        if os.path.exists(local_path):
            st.image(local_path, use_container_width=True)
        else:
            st.warning("Run backend/explainability.py to generate this plot.")


# Page: Parameter Recommendation 

elif page == "Parameter Recommendation":
    st.title("Parameter Recommendation System ")
    
    target_ri = st.number_input("Target analyte refractive index", min_value=float(ANALYTE_RI_RANGE[0]),
                                 max_value=float(ANALYTE_RI_RANGE[1]), value=1.35, step=0.001, format="%.3f")

    if st.button("Recommend optimal design", type="primary"):
        with st.spinner("Optimizing..."):
            rec = recommend_parameters(target_ri)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ag thickness", f"{rec['recommended_ag_thickness_nm']} nm")
        c2.metric("Sensing length", f"{rec['recommended_sensing_length_mm']} mm")
        c3.metric("Resonance wavelength", f"{rec['recommended_wavelength_nm']} nm")
        c4.metric("Predicted FoM", f"{rec['predicted_fom_riu_inv']} RIU⁻¹")
        st.success("Recommendation generated using the trained ML model + differential evolution.")

    st.markdown("---")
    
    L_sweep = np.linspace(SENSING_LENGTH_RANGE_MM[0], SENSING_LENGTH_RANGE_MM[1], 40)
    fwhm_sweep = [fwhm_only(42.0, L, 1.335) for L in L_sweep]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(L_sweep, fwhm_sweep, color="tab:purple")
    ax.set_xlabel("Sensing length L (mm)")
    ax.set_ylabel("FWHM (nm)")
    ax.set_title("FWHM vs sensing length (Ag thickness = 42 nm, RI = 1.335)")
    st.pyplot(fig)
