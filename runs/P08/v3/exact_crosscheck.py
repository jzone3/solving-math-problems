"""Exact-arithmetic crosscheck (no floating point in the final comparison).

For a sample of graphs: compute the adjacency characteristic polynomial over
the integers (sympy), count positive/negative roots exactly (sympy real root
isolation; adjacency matrices are symmetric so all roots are real), and
compare dev(D)^2 (an exact rational) against (n+)^2 and (n-)^2 exactly:
    dev^2 <= (n+)^2  <=>  dev <= n+   (both sides nonnegative).
Confirms the float-based checks are not tolerance artifacts.
"""
from fractions import Fraction
import numpy as np
import networkx as nx
import sympy as sp
from core import dist_matrix


def exact_inertia(G):
    A = sp.Matrix(nx.to_numpy_array(G, dtype=int).tolist())
    lam = sp.symbols("lam")
    p = A.charpoly(lam)
    roots = sp.Poly(p, lam).real_roots()  # exact isolated algebraic numbers
    npos = sum(1 for r in roots if r.is_positive)
    nneg = sum(1 for r in roots if r.is_negative)
    return npos, nneg


def exact_dev_sq(G):
    D = dist_matrix(G).astype(int)
    n2 = D.size
    s = int(D.sum())
    s2 = int((D.astype(object) ** 2).sum())
    # population variance = E[x^2] - E[x]^2, exact rational
    return Fraction(s2, n2) - Fraction(s, n2) ** 2


def check(G, tag):
    npos, nneg = exact_inertia(G)
    v = exact_dev_sq(G)
    ok39 = v <= Fraction(npos) ** 2
    ok40 = v <= Fraction(nneg) ** 2
    print(f"{tag}: dev^2={float(v):.4f} n+={npos} n-={nneg} "
          f"conj39 {'OK' if ok39 else 'VIOLATED'} conj40 {'OK' if ok40 else 'VIOLATED'}")
    assert ok39 and ok40, tag
    return npos, nneg


if __name__ == "__main__":
    # worst-margin graphs from exhaustive sweeps + representative designs
    check(nx.star_graph(3), "K_{1,3} (worst margin n=4)")
    check(nx.cycle_graph(4), "C_4")
    check(nx.complete_multipartite_graph(1, 1, 10), "K_{1,1,10}")
    G = nx.complete_multipartite_graph(2, 2, 2)
    G = nx.convert_node_labels_to_integers(G)
    nid = G.number_of_nodes()
    prev = 0
    for _ in range(12):
        G.add_edge(prev, nid); prev = nid; nid += 1
    check(G, "K_{2,2,2}+tail12")
    check(nx.path_graph(15), "P_15")
    check(nx.path_graph(24), "P_24")
    rng = np.random.default_rng(7)
    for t in range(5):
        while True:
            H = nx.gnp_random_graph(12, 0.25, seed=int(rng.integers(1 << 30)))
            if nx.is_connected(H):
                break
        check(H, f"gnp12 #{t}")
    print("PASS: exact-arithmetic crosscheck agrees; conjectures hold exactly "
          "on all sampled graphs.")
