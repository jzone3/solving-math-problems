"""n=9 verification: (1) strengthened bounds rho(Q) <= RHS44/RHS46;
(2) power-family coverage of bound 46 for delta>=2 graphs."""
import numpy as np, math, sys
from harness import graphs, g6_adj, term44, term46

mode = sys.argv[1]
res = int(sys.argv[2]); mod = int(sys.argv[3])

if mode == "rho":
    worst44 = (1e9, None); worst46 = (1e9, None); cnt = 0
    for g6 in graphs(9, "", f"{res}/{mod}"):
        A = g6_adj(g6); nn = A.shape[0]
        d = A.sum(1); m = A @ d / d
        rho = np.linalg.eigvalsh(np.diag(d) + A)[-1]
        E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
        r44 = max(term44(d[i], d[j], m[i], m[j]) for i, j in E)
        r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in E)
        if r44 - rho < worst44[0]: worst44 = (r44 - rho, g6)
        if r46 - rho < worst46[0]: worst46 = (r46 - rho, g6)
        cnt += 1
    print(f"part {res}/{mod}: n={cnt} min(r44-rho)={worst44[0]:.3g}@{worst44[1]} "
          f"min(r46-rho)={worst46[0]:.3g}@{worst46[1]}")
elif mode == "pow46":
    avals = [i / 20 for i in range(21)]
    fails = []; cnt = 0
    for g6 in graphs(9, "-d2", f"{res}/{mod}"):
        A = g6_adj(g6); nn = A.shape[0]
        d = A.sum(1); m = A @ d / d
        E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
        r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in E)
        ok = False
        for a in avals:
            if 2 + max(d[i]*m[i]**a/d[j]**a + d[j]*m[j]**a/d[i]**a - 2
                       for i, j in E) <= r46 + 1e-9:
                ok = True; break
        if not ok: fails.append(g6)
        cnt += 1
    print(f"part {res}/{mod}: n={cnt} pow46 fails={len(fails)} {fails[:20]}")
