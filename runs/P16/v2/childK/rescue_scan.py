"""(a) wheels & complete split graphs; (b) route-3 rescue: does ANY sigma
(diagonal D >= 0) give M(D) = 2D + 4I - Q - D H D >= 0 on windmill F_k?

By vertex-transitivity of the outer vertices and convexity of the feasible
D-set, WLOG D = diag(s0, s1, s1, ..., s1): 2-parameter grid + refine.
"""
import numpy as np
from common import build
from family_scan import hub_plus_cliques


def wheel(n):
    A = np.zeros((n, n))
    for i in range(1, n):
        A[0, i] = A[i, 0] = 1
        j = i % (n - 1) + 1
        A[i, j] = A[j, i] = 1
    return A


def complete_split(a, k):
    """K_a joined to k independent vertices."""
    n = a + k
    A = np.ones((n, n)) - np.eye(n)
    A[a:, a:] = 0
    return A


print("wheels W_n:")
for n in [10, 20, 30, 40, 60, 100]:
    e = np.linalg.eigvalsh(build(wheel(n))["M"])[0]
    print(f"  n={n} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")

print("complete split K_a + kK1:")
for a in [2, 3, 4]:
    for k in [10, 40, 160]:
        e = np.linalg.eigvalsh(build(complete_split(a, k))["M"])[0]
        print(f"  a={a} k={k} n={a+k} mineig={e:.6f} {'FAIL' if e < -1e-9 else ''}")


def M_of_s(bd, s):
    D = np.diag(s)
    return 2 * D + 4 * np.eye(bd["n"]) - bd["Q"] - D @ bd["H"] @ D


def rescue_windmill(k):
    bd = build(hub_plus_cliques(k, 2))
    n = bd["n"]
    best = -1e18
    barg = None
    for s0 in np.linspace(0, 3 * (2 * k - 2), 120):
        for s1 in np.linspace(0, 12, 120):
            s = np.full(n, s1)
            s[0] = s0
            e = np.linalg.eigvalsh(M_of_s(bd, s))[0]
            if e > best:
                best, barg = e, (s0, s1)
    # refine
    for _ in range(3):
        s0c, s1c = barg
        for s0 in np.linspace(max(0, s0c - 2), s0c + 2, 60):
            for s1 in np.linspace(max(0, s1c - 1), s1c + 1, 60):
                s = np.full(n, s1)
                s[0] = s0
                e = np.linalg.eigvalsh(M_of_s(bd, s))[0]
                if e > best:
                    best, barg = e, (s0, s1)
    return best, barg


for k in [8, 14, 17, 25, 40]:
    best, barg = rescue_windmill(k)
    print(f"F_{k}: best achievable mineig over D = {best:.6f} at (s0,s1)={barg}"
          f" -> {'RESCUABLE' if best > -1e-9 else 'NO D WORKS'}", flush=True)
