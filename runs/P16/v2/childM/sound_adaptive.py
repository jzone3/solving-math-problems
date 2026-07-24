"""Sound ADAPTIVE resolvent certificate for sigma-hat: try a geometric grid of
alpha climbing toward min(1, 1/rho_K) (rho_K = order-K CW bound >= rho, so
alpha*rho < 1 is guaranteed); accept first alpha with R(alpha).
Sound by childI Lemma I4 (any diagonal). By Lemma I6 the certificate set is a
terminal interval, so climbing from above-threshold alphas is the right scan.

Usage: python3 sound_adaptive.py <n> [res mod]  |  python3 sound_adaptive.py fam
"""
import sys
import numpy as np
from common import (build_base, with_diag, sigma_cap, geng, g6_to_adj,
                    windmill, hub_gadgets, gadget_cycle, gadget_clique,
                    gadget_path)


def cert(b, s, K=24, jmax=44):
    bd = with_diag(b, s)
    B, T, d, n = bd["B"], bd["T"], b["d"], b["n"]
    P = B / T[:, None]
    x = d.copy()
    for _ in range(K):
        x = P @ x
        x /= x.max()
    rhoK = np.max((P @ x) / x)
    top = min(1.0, 1.0 / rhoK)
    I = np.eye(n)
    for j in range(1, jmax + 1):
        alpha = top * (1 - 0.5 ** j)
        h = np.linalg.solve(I - alpha * P, d)
        if np.max((1 - alpha) * h - d) <= 1e-11:
            return j, rhoK
    return None, rhoK


if sys.argv[1] == "fam":
    G = {"K3": (2, [(0, 1)]), "C4": gadget_cycle(4), "C5": gadget_cycle(5),
         "P4": gadget_path(4), "K4": gadget_clique(4)}
    ok = True
    for c in (2.0, 4.0):
        for k in (5, 14, 40, 150, 300, 600):
            b = build_base(windmill(k))
            j, r = cert(b, sigma_cap(b["d"], b["m"], c))
            ok = ok and j is not None
            print(f"F_{k} c={c}: certified at j={j} (alpha step), rhoK={r:.4f}")
        for name, g in G.items():
            for k in (10, 25, 60, 150):
                b = build_base(hub_gadgets([g] * k))
                j, r = cert(b, sigma_cap(b["d"], b["m"], c))
                ok = ok and j is not None
                print(f"hub+{name}x{k} c={c}: j={j} rhoK={r:.4f}")
    print("FAMILIES:", "ALL CERTIFIED" if ok else "FAILURES PRESENT")
    sys.exit(0 if ok else 1)

n = int(sys.argv[1])
res, mod = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
st = {c: [0, 0, 0] for c in (2.0, 4.0)}   # tot, fail, max_j
for g6 in geng(n, res=res, mod=mod):
    b = build_base(g6_to_adj(g6))
    for c in st:
        j, r = cert(b, sigma_cap(b["d"], b["m"], c))
        st[c][0] += 1
        if j is None:
            st[c][1] += 1
            print("UNCERTIFIED:", g6, c)
        else:
            st[c][2] = max(st[c][2], j)
for c, (tot, bad, mj) in st.items():
    print(f"adaptive n={n} res={res}/{mod} cap={c}: tot={tot} fail={bad} max_j={mj}")
