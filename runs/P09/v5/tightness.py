"""Tightness of known extremal / near-extremal families for BN.

Prints score = lam1^2+lam2^2 - 2m(1-1/omega) (must be <=0 if conjecture holds).
"""
import numpy as np
from core import *

def report(name, A, omega=None):
    s, w = score(A, omega)
    m = int(A.sum() // 2)
    n = A.shape[0]
    print(f"{name:45s} n={n:3d} m={m:5d} w={w} score={s:+.6f}")
    return s

if __name__ == "__main__":
    print("== Turan graphs (equality expected) ==")
    for r in [2, 3, 4, 5]:
        for n in [r * 3, r * 5, r * 5 + 1]:
            report(f"T({n},{r})", turan_graph(n, r))
    print("== union of two equal Turan graphs (equality per Zhang) ==")
    for r in [3, 4]:
        for n in [r * 3, r * 5]:
            A = turan_graph(n, r)
            report(f"T({n},{r}) + T({n},{r})", union(A, A))
    print("== union of two unequal Turan graphs ==")
    for r in [3, 4]:
        A, B = turan_graph(3 * r, r), turan_graph(5 * r, r)
        report(f"T({3*r},{r}) + T({5*r},{r})", union(A, B))
    print("== two Turan graphs + single cross edge (perturbation) ==")
    for r in [3, 4, 5]:
        for k in [3, 5]:
            n = k * r
            A = union(turan_graph(n, r), turan_graph(n, r))
            A[0, n] = A[n, 0] = 1.0
            report(f"2xT({n},{r}) + edge", A)
    print("== two cliques K_w sharing structure: kite/book style ==")
    for w in [3, 4, 5, 6]:
        # two disjoint K_w plus a path of cross edges
        Kw = np.ones((w, w)) - np.eye(w)
        A = union(Kw, Kw)
        report(f"2K{w} disjoint", A)
        B = A.copy(); B[0, w] = B[w, 0] = 1
        report(f"2K{w} + bridge", B)
    print("== K_w joined with independent set / sparse ==")
    for w in [3, 4, 5]:
        Kw = np.ones((w, w)) - np.eye(w)
        for t in [5, 10, 20]:
            I = np.zeros((t, t))
            report(f"K{w-1} join I_{t}", join(np.ones((w-1,w-1))-np.eye(w-1), I))
    print("== books B(w,t): K_w sharing an edge base? complete split etc ==")
    for w in [4, 5]:
        for t in [3, 8, 15]:
            # t cliques K_w sharing a common K_{w-2}
            base = w - 2
            n = base + 2 * t
            edges = [(i, j) for i in range(base) for j in range(i + 1, base)]
            for c in range(t):
                a, b = base + 2 * c, base + 2 * c + 1
                edges.append((a, b))
                for i in range(base):
                    edges += [(i, a), (i, b)]
            report(f"book base K{base}, {t} pages K{w}", adj_from_edges(n, edges))
