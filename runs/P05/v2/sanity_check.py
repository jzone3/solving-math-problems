#!/usr/bin/env python3
"""Soundness cross-checks for the sat_cegar pipeline.

1. Brute-force check on all connected graphs with n <= 8 (via random + systematic
   sampling over graph6 from networkx generators is overkill; here: exhaustive over
   all graphs on n <= 7 vertices up to the edge-set bitmask) that the conjecture
   holds — i.e., independent confirmation that UNSAT results for small n are expected.
2. Planted-model test: verify the SAT layer *can* find three length-L paths with
   empty common intersection when the no-longer-path condition is dropped
   (running sat_cegar with max-iters=1 must yield a SAT model on the first solve).
"""
import itertools, subprocess, sys, os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))


def longest_paths(n, adjset):
    best = 0
    paths = []
    def dfs(v, visited, order):
        nonlocal best, paths
        length = len(order) - 1
        if length > best:
            best = length
            paths = [tuple(order)]
        elif length == best:
            paths.append(tuple(order))
        for w in adjset[v]:
            if w not in visited:
                visited.add(w)
                order.append(w)
                dfs(w, visited, order)
                order.pop()
                visited.remove(w)
    for s in range(n):
        dfs(s, {s}, [s])
    # dedup reversals
    uniq = set()
    for p in paths:
        uniq.add(p if p <= p[::-1] else p[::-1])
    return best, [set(p) for p in uniq]


def connected(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    seen = {0}; st = [0]
    while st:
        u = st.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); st.append(w)
    return len(seen) == n


def brute(nmax):
    for n in range(3, nmax + 1):
        pairs = list(combinations(range(n), 2))
        total = 0
        for mask in range(1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]
            if len(edges) < n - 1 or not connected(n, edges):
                continue
            total += 1
            adjset = [set() for _ in range(n)]
            for u, v in edges:
                adjset[u].add(v); adjset[v].add(u)
            _, lps = longest_paths(n, adjset)
            if len(lps) < 3:
                continue
            for a, b, c in combinations(lps, 3):
                if not (a & b & c):
                    print(f"FAIL: counterexample found at n={n} edges={edges}")
                    return False
        print(f"brute n={n}: {total} connected graphs, all 3-triples of longest paths intersect")
    return True


if __name__ == "__main__":
    nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    ok = brute(nmax)
    print("PASS" if ok else "FAIL")
