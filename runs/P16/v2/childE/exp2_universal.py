"""Exp 2: per-exponent failure counts for ord2/ord4 certificates; is any single
universal a good? Also test y = 1 and y = d_i+d_j variants.
"""
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, max_arg44, line_graph_adj

AVALS = [i / 20 for i in range(21)]


def run(nmax):
    f2 = {a: 0 for a in AVALS}
    f4 = {a: 0 for a in AVALS}
    f2s = 0  # y_e = d_i + d_j
    f4s = 0
    tot = 0
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max_arg44(d, m, E)
            AL = line_graph_adj(E)
            tot += 1
            for a in AVALS:
                y = np.array([(d[i] * d[j]) ** a for i, j in E])
                z2 = AL @ (AL @ y)
                z4 = AL @ (AL @ z2)
                if (z2 / y).max() > R + 1e-9:
                    f2[a] += 1
                if (z4 / y).max() > R * R + 1e-9:
                    f4[a] += 1
            y = np.array([d[i] + d[j] for i, j in E])
            z2 = AL @ (AL @ y)
            z4 = AL @ (AL @ z2)
            if (z2 / y).max() > R + 1e-9:
                f2s += 1
            if (z4 / y).max() > R * R + 1e-9:
                f4s += 1
    print(f"n<={nmax}: graphs={tot}")
    print("a: ord2fail ord4fail")
    for a in AVALS:
        print(f"{a:4.2f}: {f2[a]:6d} {f4[a]:6d}")
    print(f"y=s_e=(d_i+d_j): ord2 {f2s}, ord4 {f4s}")


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
