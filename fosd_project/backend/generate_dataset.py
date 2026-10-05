
import time
import numpy as np
import pandas as pd
from tmm_simulator import (
    compute_fom, AG_THICKNESS_RANGE_NM, SENSING_LENGTH_RANGE_MM, ANALYTE_RI_RANGE
)

RNG = np.random.default_rng(42)

thickness_values = np.arange(AG_THICKNESS_RANGE_NM[0], AG_THICKNESS_RANGE_NM[1] + 1, 1)    
sensing_length_values = np.linspace(SENSING_LENGTH_RANGE_MM[0], SENSING_LENGTH_RANGE_MM[1], 25) 
ri_values = np.linspace(ANALYTE_RI_RANGE[0], ANALYTE_RI_RANGE[1], 88)  

print(f"thickness values: {len(thickness_values)}, L values: {len(sensing_length_values)}, RI values: {len(ri_values)}")
print(f"total rows: {len(thickness_values)*len(sensing_length_values)*len(ri_values)}")

rows = []
t0 = time.time()
total = len(thickness_values) * len(sensing_length_values) * len(ri_values)
n_done = 0
for t in thickness_values:
    for L in sensing_length_values:
        for ri in ri_values:
            rec = compute_fom(float(t), float(L), float(ri), noise_std=0.02, rng=RNG)
            rows.append(rec)
            n_done += 1
    elapsed = time.time() - t0
    print(f"  thickness={t}nm done ({n_done}/{total} rows, {elapsed:.1f}s elapsed)")

df = pd.DataFrame(rows)
# wavelength(res), L, RI, thickness -> FoM
df = df[["wavelength_nm", "sensing_length_mm", "analyte_ri", "ag_thickness_nm",
         "fwhm_nm", "sensitivity_nm_per_riu", "fom_riu_inv"]]

out_path = "../data/fosd_dataset.csv"
df.to_csv(out_path, index=False)
print(f"Saved {len(df)} rows to {out_path}")
print(df.describe())
