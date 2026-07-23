"""Two-case analysis for bound 46 (and 44).
Case 1 (46): exists max-degree-sum edge with m_i+m_j >= 4 d_i d_j/(d_i+d_j)
  => t46 at that edge >= d_i+d_j >= mu (identity: arg46-(s-2)^2 = (di-dj)^2+4(s-4p/(mi+mj))).
Case 1 (44): exists max-degree-sum edge with m_i m_j >= d_i d_j
  => t44 >= t38 >= d_i+d_j >= mu.
For graphs in the complement (case 2), test candidate rescues.
"""
import numpy as np, math, sys
from harness import graphs, g6_adj, term44, term46

def run(nmax):
    stats = {"n": 0, "case2_44": 0, "case2_46": 0}
    worst = {}
    def upd(k, v, g):
        if k not in worst or v < worst[k][0]: worst[k] = (v, g)
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6); nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            L = np.diag(d) - A
            mu = np.linalg.eigvalsh(L)[-1]
            mer = (d + m).max()
            E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
            smax = max(d[i] + d[j] for i, j in E)
            top = [(i, j) for i, j in E if d[i] + d[j] == smax]
            r44 = max(term44(d[i], d[j], m[i], m[j]) for i, j in E)
            r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in E)
            stats["n"] += 1
            c1_46 = any(m[i] + m[j] >= 4 * d[i] * d[j] / (d[i] + d[j]) - 1e-12 for i, j in top)
            c1_44 = any(m[i] * m[j] >= d[i] * d[j] - 1e-12 for i, j in top)
            if not c1_46:
                stats["case2_46"] += 1
                upd("46 case2: r46 - merris", r46 - mer, g6)
                upd("46 case2: r46 - mu", r46 - mu, g6)
                upd("46 case2: r46 - smax", r46 - smax, g6)
            if not c1_44:
                stats["case2_44"] += 1
                upd("44 case2: r44 - merris", r44 - mer, g6)
                upd("44 case2: r44 - mu", r44 - mu, g6)
                upd("44 case2: r44 - smax", r44 - smax, g6)
    print(stats)
    for k, (v, g) in sorted(worst.items()):
        print(f"{k:26s} min = {v:+.6g} @ {g}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
