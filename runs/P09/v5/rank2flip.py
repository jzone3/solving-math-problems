"""Round 9c: the omega=2 equality plateau is much larger than unions of
complete bipartite graphs: any bipartite graph whose biadjacency matrix has
rank 2 with two equal-mass singular pairs... in fact every "double complete
bipartite" graph B(a1,a2;b1,b2) (left type-1 vertices joined to all of B,
left type-2 vertices joined only to the first b1 right vertices) satisfies
lambda1^2 + lambda2^2 = m exactly (rank-2 biadjacency => only two nonzero
singular values => sum of squares of ALL eigenvalues 2m is split equally
between {l1,l2} and {-l1,-l2}).

This script exhaustively applies all 1- and 2-edge edits to every such graph
on n vertices (all a1,a2,b1,b2 >= 1 compositions) and scores exactly.

Usage: python3 rank2flip.py <n>
"""
import sys
import itertools
import numpy as np
from core import score

def centers(n):
    seen = set()
    for a in range(2, n - 1):
        b = n - a
        for a1 in range(1, a + 1):
            a2 = a - a1
            for b1 in range(1, b + 1):
                b2 = b - b1
                if a2 == 0 and b2 > 0:
                    continue  # plain K_{a,b} with isolated? no: a2=0 -> K_{a,b} full
                key = (a1, a2, b1, b2)
                if key in seen:
                    continue
                seen.add(key)
                A = np.zeros((n, n))
                # right vertices: first b1 "core", then b2 "outer"
                A[:a1, a:] = 1                    # type-1 left: all of B
                A[a1:a, a:a + b1] = 1             # type-2 left: core only
                A += A.T
                yield A

def main(n):
    pairs = list(itertools.combinations(range(n), 2))
    best = -1e18
    nc = nev = 0
    for A in centers(n):
        nc += 1
        for k in (1, 2):
            for sel in itertools.combinations(range(len(pairs)), k):
                for t in sel:
                    i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
                s, w = score(A)
                nev += 1
                if s is not None:
                    if s > 1e-9:
                        print(f"VIOLATION n={n} score={s}", flush=True)
                    if s > best:
                        best = s
                for t in sel:
                    i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
    print(f"RANK2FLIP SUMMARY n={n}: centers={nc} evals={nev} best={best:+.3e}", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]))
