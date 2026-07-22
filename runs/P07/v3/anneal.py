"""V3 annealed search for Graffiti-154 counterexamples over general connected graphs.

Score(G) = 8 m W^2 / n^7  (float during search; exact integer check on candidates).
Violation of conj. 154 (source-code mu2 definition) iff score > 1.

Moves: toggle a random non-tree edge / add random edge / remove random edge while
keeping the graph connected. All-pairs BFS via scipy.sparse.csgraph (C speed).

Usage: python3 anneal.py <n> <seconds> [seed_type]
  seed_type: 'dumbbell' (best dumbbell for that n), 'path', 'random'
Prints best score found, and if score>1 writes witness to viol_n<N>_<score>.txt
after an exact-integer re-check.
"""
import random
import sys
import time

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, connected_components


def score_exact(n, m, W):
    return 8 * m * W * W, n ** 7


def evaluate(n, edges_set):
    m = len(edges_set)
    rows, cols = [], []
    for (u, v) in edges_set:
        rows += [u, v]
        cols += [v, u]
    A = csr_matrix((np.ones(2 * m, dtype=np.int8), (rows, cols)), shape=(n, n))
    ncomp, _ = connected_components(A, directed=False)
    if ncomp != 1:
        return None, None
    D = shortest_path(A, method="D", unweighted=True, directed=False)
    W = int(D.sum()) // 2
    return 8 * m * W * W / n ** 7, W


def best_dumbbell(n):
    best = None
    for a in range(2, n - 2):
        for ell in range(0, n - a - 1):
            b = n - a - ell
            if b < 1:
                continue
            m = a * (a - 1) // 2 + b * (b - 1) // 2 + ell + 1 if b >= 2 else a * (a - 1) // 2 + ell
            # build W by formula is messy for b=1; just construct edges and BFS later.
            # here we only pick (a,ell,b) by coarse continuum estimate; skip formula
            pass
    return None


def make_dumbbell_edges(a, ell, b):
    edges = set()
    n = a + ell + b
    for i in range(a):
        for j in range(i + 1, a):
            edges.add((i, j))
    P = list(range(a, a + ell))
    for i in range(len(P) - 1):
        edges.add((P[i], P[i + 1]))
    for i in range(a + ell, n):
        for j in range(i + 1, n):
            edges.add((i, j))
    if ell:
        edges.add((0, P[0]))
        if b:
            edges.add((P[-1], a + ell))
    elif b:
        edges.add((0, a + ell))
    return edges


def seed(n, kind, rng):
    if kind == "path":
        return set((i, i + 1) for i in range(n - 1))
    if kind == "dumbbell":
        best = (None, -1.0)
        for a in range(2, n - 1):
            for b in (1, 2, 3):
                ell = n - a - b
                if ell < 1:
                    continue
                e = make_dumbbell_edges(a, ell, b)
                s, _ = evaluate(n, e)
                if s is not None and s > best[1]:
                    best = (e, s)
        return best[0]
    # random tree
    edges = set()
    for v in range(1, n):
        u = rng.randrange(v)
        edges.add((u, v))
    return edges


def main():
    n = int(sys.argv[1])
    budget = float(sys.argv[2])
    kind = sys.argv[3] if len(sys.argv) > 3 else "dumbbell"
    rng = random.Random(12345 + n)
    edges = seed(n, kind, rng)
    cur, W = evaluate(n, edges)
    best, best_edges = cur, set(edges)
    t0 = time.time()
    T0, T1 = 3e-3, 1e-5
    it = 0
    while time.time() - t0 < budget:
        it += 1
        frac = (time.time() - t0) / budget
        T = T0 * (T1 / T0) ** frac
        u = rng.randrange(n)
        v = rng.randrange(n)
        if u == v:
            continue
        e = (min(u, v), max(u, v))
        new_edges = set(edges)
        if e in new_edges:
            new_edges.remove(e)
        else:
            new_edges.add(e)
        s, w = evaluate(n, new_edges)
        if s is None:
            continue
        if s >= cur or rng.random() < pow(2.718281828, (s - cur) / T):
            edges, cur = new_edges, s
            if cur > best:
                best, best_edges = cur, set(edges)
    m = len(best_edges)
    _, Wb = evaluate(n, best_edges)
    lhs, rhs = score_exact(n, m, Wb)
    print(f"n={n} iters={it} best_score={best:.6f} m={m} W={Wb} exact_violation={lhs > rhs}")
    if lhs > rhs:
        fn = f"viol_n{n}.txt"
        with open(fn, "w") as f:
            f.write(f"# annealed violation n={n} m={m} W={Wb} score={best:.6f}\n")
            for u, v in sorted(best_edges):
                f.write(f"{u} {v}\n")
        print("WROTE", fn)


if __name__ == "__main__":
    main()
