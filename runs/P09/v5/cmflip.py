"""Round 9b: exhaustive 1- and 2-edge-edit neighborhoods of every complete
multipartite graph and every union of two complete multipartite graphs on n
vertices (the full BN equality superstructure), scored exactly.

Usage: python3 cmflip.py <n>
"""
import sys
import itertools
import numpy as np
from core import score

def partitions(n, minpart=1, maxparts=None):
    def gen(n, mx):
        if n == 0:
            yield []
            return
        for p in range(min(n, mx), minpart - 1, -1):
            for rest in gen(n - p, p):
                yield [p] + rest
    yield from gen(n, n)

def cm_adj(parts):
    n = sum(parts)
    A = np.ones((n, n)) - np.eye(n)
    s = 0
    for p in parts:
        A[s:s + p, s:s + p] = 0
        s += p
    return A

def centers(n):
    seen = set()
    for parts in partitions(n):
        if len(parts) < 2:
            continue
        key = ("cm", tuple(parts))
        if key not in seen:
            seen.add(key)
            yield cm_adj(parts)
    # unions of two complete multipartite graphs
    for n1 in range(2, n - 1):
        n2 = n - n1
        if n2 < 2 or n2 > n1:
            continue
        for p1 in partitions(n1):
            if len(p1) < 2:
                continue
            for p2 in partitions(n2):
                if len(p2) < 2:
                    continue
                key = ("u", tuple(p1), tuple(p2))
                if key in seen:
                    continue
                seen.add(key)
                A = np.zeros((n, n))
                A[:n1, :n1] = cm_adj(p1)
                A[n1:, n1:] = cm_adj(p2)
                yield A

def main(n):
    pairs = list(itertools.combinations(range(n), 2))
    best = -1e18
    ncenters = nev = 0
    for A in centers(n):
        ncenters += 1
        for k in (1, 2):
            for sel in itertools.combinations(range(len(pairs)), k):
                for t in sel:
                    i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
                s, w = score(A)
                nev += 1
                if s is not None and s > best:
                    best = s
                    if s > 1e-9:
                        print(f"VIOLATION n={n} score={s}", flush=True)
                for t in sel:
                    i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
    print(f"CMFLIP SUMMARY n={n}: centers={ncenters} evals={nev} best={best:+.6f}", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]))
