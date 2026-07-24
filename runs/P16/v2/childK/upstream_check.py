"""Check that upstream D1 (K >= 0) and Bound 46 SURVIVE on all families where
F2 fails: windmills F_k, wheels W_n, hub+kC_c, hub+kK_q, incl. large sizes."""
import numpy as np
import numpy.linalg as la
from graphs import hub_plus_cliques, hub_plus_cycles, wheel


def check(A, name):
    n = A.shape[0]
    d = A.sum(1)
    m = (A @ d) / d
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j]]
    E = len(edges)
    AL = np.zeros((E, E))
    for x in range(E):
        for y in range(x + 1, E):
            if len(set(edges[x]) & set(edges[y])) == 1:
                AL[x, y] = AL[y, x] = 1
    arg = np.array([2 * (d[i] ** 2 + d[j] ** 2) - 16 * d[i] * d[j] / (m[i] + m[j]) + 4
                    for (i, j) in edges])
    evK = la.eigvalsh(np.diag(arg) - AL @ AL)[0]
    rhoQ = max(la.eigvalsh(np.diag(d) + A))
    from common import build
    evM = la.eigvalsh(build(A)["M"])[0]
    print(f"{name:22s} n={n:4d} minK={evK:12.6f} {'D1ok ' if evK > -1e-8 else 'D1FAIL'}"
          f" b46 {'ok' if rhoQ**2 <= arg.max() + 1e-8 else 'FAIL'}"
          f" minM={evM:10.4f} {'F2ok' if evM > -1e-8 else 'F2FAIL'}", flush=True)


for k in [14, 20, 40, 80, 150]:
    check(hub_plus_cliques(k, 2), f"windmill F_{k}")
for n in [30, 40, 60, 100, 150]:
    check(wheel(n), f"wheel W_{n}")
for k in [10, 15, 25, 40]:
    check(hub_plus_cycles(k, 4), f"hub+{k}C4")
for k in [15, 25, 40]:
    check(hub_plus_cliques(k, 3), f"hub+{k}K3")
