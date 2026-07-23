"""Test max term44/46 >= min over a SET of valid bounds (case-analysis proof shape)."""
import numpy as np, math, sys
from harness import graphs, g6_adj, term44, term46

def run(nmax):
    worst44 = (1e9, None); worst46 = (1e9, None)
    for n in range(2, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            nn = A.shape[0]
            d = A.sum(1); m = A @ d / d
            E = [(i, j) for i in range(nn) for j in range(i + 1, nn) if A[i, j]]
            r44 = max(term44(d[i], d[j], m[i], m[j]) for i, j in E)
            r46 = max(term46(d[i], d[j], m[i], m[j]) for i, j in E)
            Vmin = min(
                (d + m).max(),
                max((d[i] + d[j] + math.sqrt((d[i] - d[j]) ** 2 + 4 * m[i] * m[j])) / 2 for i, j in E),
                max((d[i] * (d[i] + m[i]) + d[j] * (d[j] + m[j])) / (d[i] + d[j]) for i, j in E),
                max(math.sqrt(d[i] ** 2 + d[j] ** 2 + 2 * m[i] * m[j]) for i, j in E),
                max(d[i] + d[j] for i, j in E),
                math.sqrt((2 * d * (d + m)).max()),
            )
            if r44 - Vmin < worst44[0]: worst44 = (r44 - Vmin, g6)
            if r46 - Vmin < worst46[0]: worst46 = (r46 - Vmin, g6)
    print("min( r44 - min_k V_k ):", worst44)
    print("min( r46 - min_k V_k ):", worst46)

if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
