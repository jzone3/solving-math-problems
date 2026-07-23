"""Test whether max edge term of bound 44/46 dominates various KNOWN-VALID
upper bounds V(G) (so that 44/46 would follow). Also sanity-check each V >= mu."""
import numpy as np, math, sys
from harness import graphs, g6_adj, term44, term46

def run(nmax):
    names = ["AM maxdeg-sum", "Merris", "GuoDas edge quad", "LiZhang",
             "sqrt(2d(d+m))", "Das (d+m+d+m)/2", "bound42"]
    worst44 = [(1e9, None)] * len(names)
    worst46 = [(1e9, None)] * len(names)
    worstV = [(1e9, None)] * len(names)  # V - mu sanity
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            L = np.diag(d) - A
            mu = np.linalg.eigvalsh(L)[-1]
            E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
            r44 = max(term44(d[i], d[j], m[i], m[j]) for i, j in E)
            r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in E)
            Vs = [
                max(d[i] + d[j] for i, j in E),
                (d + m).max(),
                max((d[i] + d[j] + math.sqrt((d[i] - d[j]) ** 2 + 4 * m[i] * m[j])) / 2 for i, j in E),
                max((d[i] * (d[i] + m[i]) + d[j] * (d[j] + m[j])) / (d[i] + d[j]) for i, j in E),
                math.sqrt((2 * d * (d + m)).max()),
                max((d[i] + m[i] + d[j] + m[j]) / 2 for i, j in E),
                max(math.sqrt(d[i] ** 2 + d[j] ** 2 + 2 * m[i] * m[j]) for i, j in E),
            ]
            for k, V in enumerate(Vs):
                if V - mu < worstV[k][0]: worstV[k] = (V - mu, g6)
                if r44 - V < worst44[k][0]: worst44[k] = (r44 - V, g6)
                if r46 - V < worst46[k][0]: worst46[k] = (r46 - V, g6)
    for k, nm in enumerate(names):
        print(f"{nm:22s} validity min(V-mu)={worstV[k][0]:+.4g} @{worstV[k][1]}   "
              f"min(r44-V)={worst44[k][0]:+.4g} @{worst44[k][1]}   "
              f"min(r46-V)={worst46[k][0]:+.4g} @{worst46[k][1]}")

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
