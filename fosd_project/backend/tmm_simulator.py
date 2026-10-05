
import numpy as np
import materials
from tmm_core import reflectance_p

AG_THICKNESS_RANGE_NM = (35, 50)
SENSING_LENGTH_RANGE_MM = (5, 29)
ANALYTE_RI_RANGE = (1.330, 1.418)
LAMBDA_SCAN_RANGE_NM = (400.0, 2400.0)  # search window for the resonance dip

N_ANGLES = 40
N_LAMBDA = 260

_theta_c_cache = None


def _theta_c():
    
    global _theta_c_cache
    if _theta_c_cache is None:
        n_core_mid = materials.n_core_pmma(800.0)
        _theta_c_cache = np.arcsin(materials.N_CLADDING / n_core_mid)
    return _theta_c_cache


def _angle_grid():
    tc = _theta_c()
    return np.linspace(tc + 1e-4, np.pi / 2 - 1e-3, N_ANGLES)


def transmitted_spectrum(ag_thickness_nm, sensing_length_mm, analyte_ri,
                          lambda_grid_nm=None):
    """Returns (lambda_grid_nm, P) - the normalized transmitted power
    spectrum for a given sensor design."""
    if lambda_grid_nm is None:
        lambda_grid_nm = np.linspace(*LAMBDA_SCAN_RANGE_NM, N_LAMBDA)

    theta = _angle_grid()                       # (N_ANGLES,)
    lam = lambda_grid_nm                         # (N_LAMBDA,)

    n_core = materials.n_core_pmma(lam)          # (N_LAMBDA,)
    n_ag = materials.n_ag(lam)                   # (N_LAMBDA,)

    TH, LAM = np.meshgrid(theta, lam, indexing="ij")   # (N_ANGLES, N_LAMBDA)
    N_CORE = np.broadcast_to(n_core, LAM.shape)
    N_AG = np.broadcast_to(n_ag, LAM.shape)

    R = reflectance_p(TH, LAM, N_CORE, N_AG, ag_thickness_nm, analyte_ri)

    D_um = materials.CORE_DIAMETER_UM
    L_um = sensing_length_mm * 1000.0
    n_reflections = L_um / (D_um * np.tan(theta))          # (N_ANGLES,)
    n_reflections = n_reflections[:, None]                 # broadcast over lambda

    weight = (np.sin(theta) * np.cos(theta))[:, None]       # (N_ANGLES,1)

    with np.errstate(over="ignore"):
        R_pow_N = R ** n_reflections

    P = np.sum(R_pow_N * weight, axis=0) / np.sum(weight)
    return lam, P


def _dip_index(lam, P, ref_lambda=None, window_nm=150.0):
    
    if ref_lambda is not None:
        mask = np.abs(lam - ref_lambda) <= window_nm
        if np.any(mask):
            sub_idx = np.where(mask)[0]
            return int(sub_idx[np.argmin(P[sub_idx])])
    return int(np.argmin(P))


def _fwhm_from_dip(lam, P, ref_lambda=None):
    """Half-max FWHM of the (continuity-tracked) transmission dip via linear interpolation."""
    idx_min = _dip_index(lam, P, ref_lambda)
    p_min = P[idx_min]
    p_base = np.max(P)  # off-resonance transmittance as the local baseline
    half = (p_base + p_min) / 2.0

    # walk left from the minimum to the half-depth crossing
    i = idx_min
    while i > 0 and P[i] < half:
        i -= 1
    if i == idx_min:
        lam_left = lam[idx_min]
    else:
        lam_left = np.interp(half, [P[i], P[i + 1]], [lam[i], lam[i + 1]])

    # walk right
    j = idx_min
    while j < len(P) - 1 and P[j] < half:
        j += 1
    if j == idx_min:
        lam_right = lam[idx_min]
    else:
        lam_right = np.interp(half, [P[j - 1], P[j]], [lam[j - 1], lam[j]])

    return float(lam_right - lam_left), float(lam[idx_min])


def fwhm_only(ag_thickness_nm, sensing_length_mm, analyte_ri):
    """Convenience wrapper: just the FWHM (nm) of the resonance dip for a
    given design, used by the Streamlit app's FWHM-vs-sensing-length plot."""
    lam, P = transmitted_spectrum(ag_thickness_nm, sensing_length_mm, analyte_ri)
    fwhm, _ = _fwhm_from_dip(lam, P)
    return fwhm


def resonance_wavelength(ag_thickness_nm, sensing_length_mm, analyte_ri, ref_lambda=None):
   
    lam, P = transmitted_spectrum(ag_thickness_nm, sensing_length_mm, analyte_ri)
    return float(lam[_dip_index(lam, P, ref_lambda)])


def resonance_sweep(ag_thickness_nm, sensing_length_mm, ri_array):
    
    ri_array = np.asarray(ri_array, dtype=float)
    out = np.empty_like(ri_array)
    ref = None
    for i, ri in enumerate(ri_array):
        out[i] = resonance_wavelength(ag_thickness_nm, sensing_length_mm, ri, ref_lambda=ref)
        ref = out[i]
    return out


def compute_fom(ag_thickness_nm, sensing_length_mm, analyte_ri, delta_ri=0.005,
                 noise_std=0.0, rng=None):
    lam, P = transmitted_spectrum(ag_thickness_nm, sensing_length_mm, analyte_ri)
    fwhm, lambda_res = _fwhm_from_dip(lam, P)

    lam2, P2 = transmitted_spectrum(ag_thickness_nm, sensing_length_mm,
                                     analyte_ri + delta_ri)
    _, lambda_res2 = _fwhm_from_dip(lam2, P2, ref_lambda=lambda_res)
    sensitivity = abs(lambda_res2 - lambda_res) / delta_ri

    fom = sensitivity / fwhm if fwhm > 0 else 0.0

    if noise_std > 0:
        rng = rng or np.random.default_rng()
        fom = max(fom * (1.0 + rng.normal(0, noise_std)), 0.01)

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
    import time

    print(f"theta_c = {np.degrees(_theta_c()):.2f} deg")

    t0 = time.time()
    r = compute_fom(40, 15, 1.335)
    print(f"single compute_fom: {time.time()-t0:.3f}s ->", r)

    print("\nRed-shift check (RI increasing, t=40nm, L=15mm):")
    for ri in [1.33, 1.35, 1.37, 1.40]:
        rr = compute_fom(40, 15, ri)
        print(f"  RI={ri:.3f}  lambda_res={rr['wavelength_nm']:.1f}nm  "
              f"FWHM={rr['fwhm_nm']:.1f}nm  FoM={rr['fom_riu_inv']:.2f}")

    print("\nFWHM broadening check (RI=1.335, L=15mm):")
    for t in [35, 40, 45, 50]:
        rr = compute_fom(t, 15, 1.335)
        print(f"  t={t}nm  lambda_res={rr['wavelength_nm']:.1f}nm  "
              f"FWHM={rr['fwhm_nm']:.1f}nm  FoM={rr['fom_riu_inv']:.2f}")

    print("\nOptimal sensing-length check (RI=1.335, t=40nm):")
    for L in [5, 10, 15, 20, 25, 29]:
        rr = compute_fom(40, L, 1.335)
        print(f"  L={L}mm  FWHM={rr['fwhm_nm']:.2f}nm  FoM={rr['fom_riu_inv']:.2f}")
