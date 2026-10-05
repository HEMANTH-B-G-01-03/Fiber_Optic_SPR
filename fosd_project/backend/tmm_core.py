"""
Multilayer Transfer-Matrix-Method (TMM) reflectance for p-polarized
(TM) light incident from a fiber core, through a thin Ag film, into a
semi-infinite analyte/sensing medium 

    q_j   = sqrt(n_j^2 - n0^2 sin^2(theta0)) / n_j^2      (p-polarization)
    beta  = (2*pi/lambda) * t_film * sqrt(n_film^2 - n0^2 sin^2(theta0))
    r01   = (q0 - q1) / (q0 + q1)
    r12   = (q1 - q2) / (q1 + q2)
    r     = (r01 + r12*exp(2i*beta)) / (1 + r01*r12*exp(2i*beta))
    R     = |r|^2

"""
import numpy as np


def _q(n_complex, n0, sin_theta0_sq):
    """p-polarization optical admittance for a layer of index n_complex."""
    n2 = n_complex ** 2
    return np.sqrt(n2 - (n0 ** 2) * sin_theta0_sq) / n2


def reflectance_p(theta0_rad, lambda_nm, n0, n_film, t_film_nm, n_sub):
    
    sin2 = np.sin(theta0_rad) ** 2
    q0 = _q(np.asarray(n0, dtype=complex), n0, sin2)
    q1 = _q(n_film, n0, sin2)
    q2 = _q(np.asarray(n_sub, dtype=complex), n0, sin2)

    beta = (2.0 * np.pi / lambda_nm) * t_film_nm * np.sqrt(
        n_film ** 2 - (n0 ** 2) * sin2
    )

    r01 = (q0 - q1) / (q0 + q1)
    r12 = (q1 - q2) / (q1 + q2)
    phase = np.exp(2j * beta)
    r = (r01 + r12 * phase) / (1.0 + r01 * r12 * phase)
    return np.abs(r) ** 2


if __name__ == "__main__":
    import materials

    # Quick sanity check: a single (theta, lambda) reflectance value should
    # be a real number in [0, 1].
    n0 = materials.n_core_pmma(700.0)
    n_ag = materials.n_ag(700.0)
    R = reflectance_p(np.radians(85.0), 700.0, n0, n_ag, 40.0, 1.335)
    print(f"R(theta=85deg, lambda=700nm, t=40nm, RI=1.335) = {float(R):.4f}")
    assert 0.0 <= float(R) <= 1.0 + 1e-9
    print("OK: reflectance is physically bounded in [0,1].")
