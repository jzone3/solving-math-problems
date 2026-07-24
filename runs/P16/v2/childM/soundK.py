"""Sound resolvent certificate with order-K Collatz-Wielandt bound, for
sigma-hat (c = 2, 4).

rho_K := max_i (P^{K+1} d)_i / (P^K d)_i  >= rho(P)  (P^K d > 0), sound.
alpha := kappa / max(rho_K, 1); certificate R(alpha): (1-alpha)h_alpha <= d.
By childI Lemma I4 (valid for ANY diagonal), R(alpha) & alpha*rho<1 => M PSD.

Usage: python3 soundK.py <n> [K kappa res mod]   (exhaustive geng)
       python3 soundK.py fam                     (hub families incl. windmills)
"""
import sys
import numpy as np
from common import (build_base, with_diag, sigma_cap, geng, g6_to_adj,
                    windmill, hub_gadgets, gadget_cycle, gadget_clique,
                    gadget_path)


def cert(b, s, K=16, kappa=0.99):
    bd = with_diag(b, s)
    B, T, d, n = bd["B"], bd["T"], b["d"], b["n"]
    P = B / T[:, None]
    x = d.copy()
    for _ in range(K):
        x = P @ x
    y = P @ x
    rhoK = np.max(y / x)
    alpha = kappa / max(rhoK, 1.0)
    h = np.linalg.solve(np.eye(n) - alpha * P, d)
    return np.max((1 - alpha) * h - d), rhoK


if sys.argv[1] == "fam":
    G = {"K3": (2, [(0, 1)]), "C4": gadget_cycle(4), "C5": gadget_cycle(5),
         "P4": gadget_path(4), "K4": gadget_clique(4)}
    worst = -1e18
    for c in (2.0, 4.0):
        for k in (5, 10, 14, 20, 40, 80, 150, 300):
            b = build_base(windmill(k))
            v, r = cert(b, sigma_cap(b["d"], b["m"], c))
            worst = max(worst, v)
            print(f"F_{k} c={c}: viol={v:.3e} rhoK={r:.4f}")
        for name, g in G.items():
            for k in (10, 25, 60):
                b = build_base(hub_gadgets([g] * k))
                v, r = cert(b, sigma_cap(b["d"], b["m"], c))
                worst = max(worst, v)
                print(f"hub+{name}x{k} c={c}: viol={v:.3e} rhoK={r:.4f}")
    print("FAMILIES worst violation:", worst, "OK" if worst < 1e-9 else "FAIL")
    sys.exit(0)

n = int(sys.argv[1])
K = int(sys.argv[2]) if len(sys.argv) > 2 else 16
kappa = float(sys.argv[3]) if len(sys.argv) > 3 else 0.99
res, mod = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1)

st = {c: [0, 0, -1e18] for c in (2.0, 4.0)}
for g6 in geng(n, res=res, mod=mod):
    b = build_base(g6_to_adj(g6))
    for c in st:
        v, r = cert(b, sigma_cap(b["d"], b["m"], c), K, kappa)
        st[c][0] += 1
        st[c][2] = max(st[c][2], v)
        if v > 1e-9:
            st[c][1] += 1
for c, (tot, bad, w) in st.items():
    print(f"soundK n={n} K={K} kappa={kappa} res={res}/{mod} cap={c}: "
          f"tot={tot} fail={bad} worst={w:.3e}")
