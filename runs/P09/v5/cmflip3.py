"""Round 11: exhaustive 3-edge-edit neighborhoods of every complete multipartite
graph and union of two complete multipartite graphs on n vertices.

Usage: python3 cmflip3.py <n> <shard> <nshards>
"""
import sys
import itertools
import numpy as np
from core import score
from cmflip import centers

def main(n, shard, nshards):
    pairs = list(itertools.combinations(range(n), 2))
    best = -1e18
    nc = nev = 0
    for ci, A in enumerate(centers(n)):
        if ci % nshards != shard:
            continue
        nc += 1
        for sel in itertools.combinations(range(len(pairs)), 3):
            for t in sel:
                i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
            s, w = score(A)
            nev += 1
            if s is not None:
                if s > 1e-9:
                    print(f"VIOLATION n={n} score={s} center={ci} sel={sel}", flush=True)
                if s > best:
                    best = s
            for t in sel:
                i, j = pairs[t]; A[i, j] = A[j, i] = 1 - A[i, j]
    print(f"CMFLIP3 SUMMARY n={n} shard={shard}/{nshards}: centers={nc} evals={nev} best={best:+.3e}", flush=True)

if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
