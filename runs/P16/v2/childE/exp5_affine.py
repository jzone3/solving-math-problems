"""Exp 5: affine family phi(x) = x + b, b >= 0. For each graph find whether some b
works: max_e [d_i(m_i+b)/(d_j+b) + d_j(m_j+b)/(d_i+b)] <= 2 + sqrt(max arg44).
Record failures and the working-b intervals (coarse grid + refinement).
"""
import math
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44

BGRID = [0, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.6, 2.0, 2.5, 3.0, 4.0,
         5.0, 7.0, 10.0, 15.0, 25.0, 50.0, 100.0, 1e4]


def cw_affine(d, m, E, b):
    return max(d[i] * (m[i] + b) / (d[j] + b) + d[j] * (m[j] + b) / (d[i] + b)
               for i, j in E)


def run(nmax):
    tot = 0
    fails = []
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            target = 2 + math.sqrt(max(R, 0))
            tot += 1
            if not any(cw_affine(d, m, E, b) <= target + 1e-9 for b in BGRID):
                # fine scan before declaring failure
                bs = np.concatenate([np.linspace(0, 5, 501),
                                     np.linspace(5, 200, 391)])
                v = min(cw_affine(d, m, E, b) for b in bs)
                if v > target + 1e-9:
                    fails.append((g6, v - target))
    print(f"n<={nmax}: graphs={tot}, affine-family failures: {len(fails)}")
    for g, dv in sorted(fails, key=lambda x: -x[1])[:20]:
        print("  ", g, f"deficit {dv:.4g}")


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
