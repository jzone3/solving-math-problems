"""Windmill/friendship F_k stress: is 1^T M d >= 0 actually universal?
Also track d^T M d, min eig M, rho(P), max Pd/d, and alpha-window."""
import numpy as np
from common import build, resolvent_check


def windmill(k):
    n = 2 * k + 1
    A = np.zeros((n, n))
    for t in range(k):
        u, v = 1 + 2 * t, 2 + 2 * t
        A[0, u] = A[u, 0] = 1
        A[0, v] = A[v, 0] = 1
        A[u, v] = A[v, u] = 1
    return A


for k in [2, 3, 5, 8, 12, 17, 25, 40, 60, 100, 200]:
    bd = build(windmill(k))
    M, d, T, B = bd["M"], bd["d"], bd["T"], bd["B"]
    n = bd["n"]
    oneMd = np.ones(n) @ M @ d
    dMd = d @ M @ d
    ev = np.linalg.eigvalsh(M)
    P = B / T[:, None]
    rho = max(np.linalg.eigvals(P).real)
    rho0 = np.max((B @ d) / (T * d))
    # find smallest alpha on a grid where R(alpha) holds
    astar = None
    for a in np.linspace(0.001, 0.999, 999):
        if a * rho < 1 and resolvent_check(bd, a) <= 1e-11:
            astar = a
            break
    print(f"k={k:4d} n={n:4d} 1Md={oneMd:12.4f} dMd={dMd:12.4f} "
          f"mineig={ev[0]:.3e} rho={rho:.6f} rho0={rho0:.6f} astar~{astar}",
          flush=True)
