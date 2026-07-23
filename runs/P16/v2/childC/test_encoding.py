"""Sanity checks for the childC CP-SAT encoding algebra.

1. The cleared-denominator violation inequalities used in cpsat_quotient.py are
   equivalent to  t > rhs_edge  (search_common float formulas) on random data.
2. Collatz-Wielandt on Q_B = diag(s)+B (bipartite tree support) lower-bounds
   lam_max(L_B).
"""
import math
import random
import sys

import numpy as np

sys.path.insert(0, "..")
import search_common  # noqa: E402


def check_edge_algebra(trials=20000):
    rng = random.Random(1)
    bad = 0
    for _ in range(trials):
        sa, sb = rng.randint(1, 50), rng.randint(1, 50)
        Pa = rng.randint(sa, 50 * sa)   # P_i = s_i * m_i, m_i in [1, 50]
        Pb = rng.randint(sb, 50 * sb)
        t = rng.uniform(2.01, 120.0)
        ma, mb = Pa / sa, Pb / sb
        # bound 44
        ref = t > search_common.rhs44_edge(sa, sb, ma, mb)
        lhs = (t - 2) ** 2 * sa * sb
        rhs = 2 * (((sa - 1) ** 2 + (sb - 1) ** 2 - sa * sb) * sa * sb + Pa * Pb)
        enc = lhs > rhs
        if enc != ref:
            # tolerate float ties only
            if abs(lhs - rhs) > 1e-6 * max(1, abs(rhs)):
                bad += 1
                print("44 mismatch", sa, sb, Pa, Pb, t)
        # bound 46
        ref = t > search_common.rhs46_edge(sa, sb, ma, mb)
        D = Pa * sb + Pb * sa
        lhs = (t - 2) ** 2 * D
        rhs = (2 * (sa ** 2 + sb ** 2) + 4) * D - 16 * (sa * sb) ** 2
        enc = lhs > rhs
        if enc != ref:
            if abs(lhs - rhs) > 1e-6 * max(1, abs(rhs)):
                bad += 1
                print("46 mismatch", sa, sb, Pa, Pb, t)
    assert bad == 0, bad
    print(f"edge algebra OK ({trials} trials)")


def check_cw(trials=2000):
    rng = np.random.default_rng(2)
    for _ in range(trials):
        k = rng.integers(3, 8)
        # random tree support
        import networkx as nx
        T = nx.random_labeled_tree(int(k), seed=int(rng.integers(10 ** 9)))
        B = np.zeros((k, k), dtype=int)
        for (a, b) in T.edges():
            B[a, b] = rng.integers(1, 40)
            B[b, a] = rng.integers(1, 40)
        s = B.sum(axis=1)
        Q = np.diag(s) + B
        lamL = float(np.max(np.linalg.eigvals(np.diag(s) - B).real))
        lamQ = float(np.max(np.linalg.eigvals(Q).real))
        assert abs(lamL - lamQ) < 1e-8 * max(1, lamQ), (lamL, lamQ)
        x = rng.integers(1, 100, size=k).astype(float)
        cw = np.min((Q @ x) / x)
        assert cw <= lamQ + 1e-9
    print(f"Collatz-Wielandt / bipartite similarity OK ({trials} trials)")


if __name__ == "__main__":
    check_edge_algebra()
    check_cw()
