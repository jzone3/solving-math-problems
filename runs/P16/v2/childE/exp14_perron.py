"""Exp 14 (Route 2): test lam^2 <= S_{e*} <= max_e arg44 where e* is the Perron
edge of A(L(G)) (Lemma B4 gives the first ineq). Also test at the max-degree-sum
edge and weighted variants. Count failures of S_{e*} <= max arg44.
"""
import sys

import numpy as np

from common import graphs, g6_adj, graph_data, arg44, line_graph_adj


def run(nmax):
    tot = 0
    failP = []  # S at Perron edge > max arg44
    failDS = 0  # S at max-degree-sum edge > max arg44 (any max-ds edge all fail)
    for n in range(3, nmax + 1):
        for g6 in graphs(n):
            A = g6_adj(g6)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            AL = line_graph_adj(E)
            tot += 1
            w, V = np.linalg.eigh(AL)
            z = np.abs(V[:, -1])
            estar = int(np.argmax(z))

            def S(idx):
                i, j = E[idx]
                return ((d[i] - 1) * (d[i] - 2) + (d[j] - 1) * (d[j] - 2)
                        + d[i] * m[i] + d[j] * m[j] - d[i] - d[j])

            if S(estar) > R + 1e-9:
                failP.append(g6)
            smax = max(d[i] + d[j] for i, j in E)
            dsedges = [k for k, (i, j) in enumerate(E) if d[i] + d[j] == smax]
            if all(S(k) > R + 1e-9 for k in dsedges):
                failDS += 1
    print(f"n<={nmax}: graphs={tot}")
    print(f"S(Perron edge) > max arg44: {len(failP)} failures", failP[:20])
    print(f"S(all max-deg-sum edges) > max arg44: {failDS} failures")


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
