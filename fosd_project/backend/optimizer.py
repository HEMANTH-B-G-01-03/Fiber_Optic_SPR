
import json
import numpy as np
import joblib
from scipy.optimize import differential_evolution
from tmm_simulator import resonance_wavelength

FEATURES = ["wavelength_nm", "sensing_length_mm", "analyte_ri", "ag_thickness_nm"]

with open("../models/best_model.json") as f:
    meta = json.load(f)
BEST_MODEL_NAME = meta["best_model"]
MODEL = joblib.load(f"../models/{BEST_MODEL_NAME}.joblib")

L_BOUNDS = (5.0, 29.0)
T_BOUNDS = (35.0, 50.0)


def _predict_fom(wavelength, L, ri, thickness):
    X = np.array([[wavelength, L, ri, thickness]])
    if BEST_MODEL_NAME == "ANN":
        scaler = joblib.load("../models/ann_scaler.joblib")
        X = scaler.transform(X)
    return float(MODEL.predict(X)[0])


def recommend_parameters(target_ri, n_iter=60, seed=42):
 
    def objective(x):
        L, thickness = x
        wavelength = resonance_wavelength(thickness, L, target_ri)
        fom = _predict_fom(wavelength, L, target_ri, thickness)
        return -fom  # maximize FoM -> minimize negative FoM

    bounds = [L_BOUNDS, T_BOUNDS]
    result = differential_evolution(objective, bounds, seed=seed, maxiter=n_iter,
                                     popsize=20, tol=1e-6, polish=True)

    L_opt, t_opt = result.x
    wl_opt = resonance_wavelength(t_opt, L_opt, target_ri)
    best_fom = -result.fun
    return {
        "target_ri": target_ri,
        "recommended_wavelength_nm": round(wl_opt, 2),
        "recommended_sensing_length_mm": round(float(L_opt), 2),
        "recommended_ag_thickness_nm": round(float(t_opt), 2),
        "predicted_fom_riu_inv": round(float(best_fom), 3),
        "model_used": BEST_MODEL_NAME,
    }


if __name__ == "__main__":
    for ri in [1.33, 1.35, 1.38, 1.40]:
        rec = recommend_parameters(ri)
        print(rec)
