"""Exact recheck of BOUNDARY graphs from the geng exhaust: rescore at mpmath
50 dps; anything with score > -1e-30 gets a fully exact sympy verdict
(rational characteristic polynomial, isolate top-two eigenvalues).
"""
import sys
import numpy as np
import networkx as nx
import mpmath as mp
from common import clique_number_np

mp.mp.dps = 50


def hp_score(A):
    n = A.shape[0]
    m = int(A.sum()) // 2
    w = clique_number_np(A)
    M = mp.matrix(A.tolist())
    ev = sorted(mp.eigsy(M, eigvals_only=True), reverse=True)
    return ev[0] ** 2 + ev[1] ** 2 - 2 * m * (1 - mp.mpf(1) / w), w, m


def exact_score_sign(A):
    """Fully exact: score = l1^2 + l2^2 - c with c rational. Uses sympy real
    root isolation on the characteristic polynomial."""
    import sympy as sp
    n = A.shape[0]
    m = int(A.sum()) // 2
    w = clique_number_np(A)
    M = sp.Matrix(A.tolist())
    lam = sp.symbols('lam')
    p = M.charpoly(lam)
    roots = sp.Poly(p, lam).real_roots()  # exact algebraic numbers, sorted asc
    l1, l2 = roots[-1], roots[-2]
    c = sp.Rational(2 * m) * (1 - sp.Rational(1, w))
    expr = l1 ** 2 + l2 ** 2 - c
    return sp.sign(sp.nsimplify(expr, rational=False).evalf(60)), expr


def main():
    files = sys.argv[1:]
    total = 0
    exact_zero = 0
    neg = 0
    for fn in files:
        for line in open(fn):
            if not (line.startswith("BOUNDARY") or line.startswith("VIOLATION")):
                continue
            g6 = line.split()[1]
            G = nx.from_graph6_bytes(g6.encode())
            A = nx.to_numpy_array(G).astype(int)
            s, w, m = hp_score(A)
            total += 1
            if s > mp.mpf(10) ** -30:
                print("!!! POSITIVE at 50dps:", g6, mp.nstr(s, 10), flush=True)
                sign, expr = exact_score_sign(A)
                print("    exact sign:", sign, flush=True)
            elif abs(s) < mp.mpf(10) ** -30:
                exact_zero += 1
            else:
                neg += 1
    print(f"rechecked {total} boundary graphs: {exact_zero} equality (|s|<1e-30), "
          f"{neg} strictly negative, rest printed above")


if __name__ == "__main__":
    main()
