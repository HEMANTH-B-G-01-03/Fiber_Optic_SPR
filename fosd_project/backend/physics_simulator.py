
import numpy as np

AG_THICKNESS_RANGE_NM = (35, 50)
SENSING_LENGTH_RANGE_MM = (5, 29)
ANALYTE_RI_RANGE = (1.330, 1.418)
LAMBDA_RANGE_NM = (559, 1127)

_T_MID = np.mean(AG_THICKNESS_RANGE_NM)
_L_MID = np.mean(SENSING_LENGTH_RANGE_MM)
_RI_REF = 1.33


def _lambda_res(thickness_nm, sensing_length_mm, analyte_ri):
    lam = (700.0
           + 3500.0 * (analyte_ri - _RI_REF)
           + 4.0 * (thickness_nm - _T_MID)
           + 0.8 * (sensing_length_mm - _L_MID)
           - 600.0 * (analyte_ri - _RI_REF) ** 2)
    return np.clip(lam, LAMBDA_RANGE_NM[0], LAMBDA_RANGE_NM[1])


def _fwhm(thickness_nm, sensing_length_mm):
    base = 70.0 + 2.6 * (thickness_nm - AG_THICKNESS_RANGE_NM[0])
    l_term = -1.1 * (sensing_length_mm - _L_MID) + 0.11 * (sensing_length_mm - _L_MID) ** 2
    return np.clip(base + l_term, 12.0, 400.0)


def _sensitivity(thickness_nm, sensing_length_mm, analyte_ri, delta_ri=0.05):
    lam1 = _lambda_res(thickness_nm, sensing_length_mm, analyte_ri)
    lam2 = _lambda_res(thickness_nm, sensing_length_mm, analyte_ri + delta_ri)
    return abs(lam2 - lam1) / delta_ri


def compute_fom(ag_thickness_nm, sensing_length_mm, analyte_ri, delta_ri=0.05,
                 noise_std=0.0, rng=None):
    lambda_res = _lambda_res(ag_thickness_nm, sensing_length_mm, analyte_ri)
    fwhm = _fwhm(ag_thickness_nm, sensing_length_mm)
    sensitivity = _sensitivity(ag_thickness_nm, sensing_length_mm, analyte_ri, delta_ri)
    fom = sensitivity / fwhm

    if noise_std > 0:
        rng = rng or np.random.default_rng()
        fom *= (1.0 + rng.normal(0, noise_std))
        fom = max(fom, 0.01)

    return {
        "wavelength_nm": float(lambda_res),
        "sensing_length_mm": float(sensing_length_mm),
        "analyte_ri": float(analyte_ri),
        "ag_thickness_nm": float(ag_thickness_nm),
        "fwhm_nm": float(fwhm),
        "sensitivity_nm_per_riu": float(sensitivity),
        "fom_riu_inv": float(fom),
    }


if __name__ == "__main__":
    r = compute_fom(ag_thickness_nm=40, sensing_length_mm=15, analyte_ri=1.335)
    print(r)
    for L in [5, 10, 15, 17.5, 20, 25, 29]:
        rr = compute_fom(40, L, 1.335)
        print(L, round(rr["fwhm_nm"], 2), round(rr["fom_riu_inv"], 3))
