"""Deterministic 1- and 2-edge-move neighborhood scan of score-1 optima
harvested from anneal_hits.log. If any neighbor has score 0 we have a witness.

Usage: pypy3 refine.py <depth(1|2)> [start_idx end_idx]
"""
import ast
import re
import sys
import time
from itertools import combinations

from lp_core import analyze, edges_to_adj, is_connected


def load_seeds(path="anneal_hits.log"):
    seeds = []
    seen = set()
    for line in open(path):
        m = re.search(r"best=1 n=(\d+) L=\S+ edges=(\[.*\])", line)
        if m:
            n = int(m.group(1))
            edges = tuple(sorted(tuple(sorted(e)) for e in ast.literal_eval(m.group(2))))
            if (n, edges) not in seen:
                seen.add((n, edges))
                seeds.append((n, list(edges)))
    return seeds


def score(n, edges):
    adj = edges_to_adj(n, edges)
    if not is_connected(n, adj):
        return 999, None
    try:
        res = analyze(n, adj, cap=1500)
    except RecursionError:
        return 999, None
    return res["score"], res


def moves(n, edges):
    eset = set(edges)
    non = [tuple(sorted((u, v))) for u, v in combinations(range(n), 2)
           if tuple(sorted((u, v))) not in eset]
    for e in edges:                       # remove
        yield [x for x in edges if x != e]
    for e in non:                         # add
        yield edges + [e]
    for e in edges:                       # swap
        base = [x for x in edges if x != e]
        for f in non:
            yield base + [f]


def main():
    depth = int(sys.argv[1])
    seeds = load_seeds()
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else len(seeds)
    print("seeds:", len(seeds), "range", lo, hi); sys.stdout.flush()
    t0 = time.time()
    best = 99
    for si, (n, edges) in enumerate(seeds[lo:hi]):
        frontier = [edges]
        for d in range(depth):
            nxt = []
            for cur in frontier:
                for cand in moves(n, cur):
                    sc, res = score(n, cand)
                    if sc < best:
                        best = sc
                        print("seed %d depth %d score %d" % (si + lo, d + 1, sc))
                        sys.stdout.flush()
                    if sc == 0:
                        with open("WITNESS_refine.txt", "w") as f:
                            f.write("n=%d edges=%s witness=%s\n" % (n, cand, res["witness"]))
                        print("WITNESS FOUND"); return
                    if d + 1 < depth and sc <= 1:
                        nxt.append(cand)
            frontier = nxt[:200]
        print("seed %d/%d done best=%d elapsed=%.0fs" % (si + lo, hi, best, time.time() - t0))
        sys.stdout.flush()
    print("DONE best=%d" % best)


if __name__ == "__main__":
    main()
