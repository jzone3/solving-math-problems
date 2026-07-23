"""childJ: combine all env_*.npz pooled envelopes; report pointwise
separation Lsup(rho) <= Uinf(rho) and the tightest gaps."""
import glob

import numpy as np

L = None
for f in sorted(glob.glob("env_*.npz")):
    z = np.load(f)
    if L is None:
        rho, L, U = z["rho"], z["L"], z["U"]
    else:
        L = np.maximum(L, z["L"])
        U = np.minimum(U, z["U"])
    print(f"loaded {f}")
gap = U - L
bad = gap < -1e-7
print(f"gridpoints={len(rho)}, conflicts={bad.sum()}")
order = np.argsort(gap)
print("tightest 15 gridpoints:")
for k in order[:15]:
    print(f"  rho={rho[k]:8.2f} Lsup={L[k]:9.4f} Uinf={U[k]:9.4f} gap={gap[k]:8.4f}")
