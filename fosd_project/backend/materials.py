
import numpy as np

#  PMMA core
_PMMA_A = 1.4780
_PMMA_B = 0.0044  # um^2


def n_core_pmma(lambda_nm):
    """Real refractive index of the PMMA fiber core (Cauchy dispersion)."""
    lam_um = np.asarray(lambda_nm, dtype=float) / 1000.0
    return _PMMA_A + _PMMA_B / lam_um ** 2

N_CLADDING = 1.41

CORE_DIAMETER_UM = 600.0

# Ag (silver)
_AG_OMEGA_P_EV = 9.01     # plasma energy, eV (Rakic et al. 1998)
_AG_GAMMA_EV = 0.048      # damping energy, eV (Rakic et al. 1998)
_HC_EV_NM = 1239.84193    # h*c in eV*nm


def eps_ag(lambda_nm):
    """Complex relative permittivity of silver (single-pole Drude model)."""
    lam_nm = np.asarray(lambda_nm, dtype=float)
    E = _HC_EV_NM / lam_nm  # photon energy, eV
    eps = 1.0 - (_AG_OMEGA_P_EV ** 2) / (E ** 2 + 1j * E * _AG_GAMMA_EV)
    return eps


def n_ag(lambda_nm):
    """Complex refractive index n + ik of silver."""
    eps = eps_ag(lambda_nm)
    return np.sqrt(eps)


if __name__ == "__main__":
    
    n = n_ag(632.8)
    print(f"Ag @632.8nm (this Drude model):  n={n.real:.3f}, k={n.imag:.3f}")
    print("Ag @632.8nm (Johnson & Christy):  n=0.14,  k=3.99  (reference)")
    print(f"PMMA core n @632.8nm: {n_core_pmma(632.8):.4f}  (lit. ~1.4895)")
