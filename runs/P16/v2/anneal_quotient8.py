"""Simulated annealing over equitable-partition quotient matrices, minimizing
gap = RHS(bound) - lam_max(L_B).  gap < 0 (beyond float noise) => counterexample
candidate (goes to exact verifier).  Starts include perturbed regular-bipartite
quotients (the equality manifold of both bounds).

Usage: python3 anneal_quotient.py <44|46> <seconds> [maxentry]
"""
import math
import random
import sys
import time

import numpy as np

from search_common import quotient_data, quotient_ok, quotient_rhs, rhs44_edge, rhs46_edge


def gap(B, edge_fn):
    if (B.sum(axis=1) == 0).any():
        return math.inf
    if quotient_ok(B) is None:
        return math.inf
    lam, s, m = quotient_data(B, None)
    r = quotient_rhs(B, s, m, edge_fn)
    return r - lam


def bipartite_start(k, maxe):
    """Random near-regular-bipartite quotient on k cells: split cells into two
    sides, only cross edges, row sums ~ d."""
    while True:
        sides = [random.randint(0, 1) for _ in range(k)]
        if 0 < sum(sides) < k:
            break
    d = random.randint(3, maxe)
    B = np.zeros((k, k), dtype=int)
    for i in range(k):
        others = [j for j in range(k) if sides[j] != sides[i]]
        rem = d
        for idx, j in enumerate(others):
            if idx == len(others) - 1:
                B[i, j] = rem
            else:
                B[i, j] = random.randint(0, rem)
                rem -= B[i, j]
    # fix support symmetry
    for i in range(k):
        for j in range(k):
            if B[i, j] > 0 and B[j, i] == 0:
                B[j, i] = 1
    return B


def mutate(B, maxe):
    B = B.copy()
    k = B.shape[0]
    i, j = random.randrange(k), random.randrange(k)
    step = random.choice([1, 1, 1, 2, 3, 5, 10])
    B[i, j] = min(maxe, max(0, B[i, j] + random.choice([-1, 1]) * step))
    if i != j:
        if B[i, j] > 0 and B[j, i] == 0:
            B[j, i] = 1
        if B[i, j] == 0:
            B[j, i] = 0
    return B


def main():
    bound = int(sys.argv[1])
    seconds = float(sys.argv[2])
    maxe = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    edge_fn = rhs44_edge if bound == 44 else rhs46_edge
    t0 = time.time()
    best = (math.inf, None)
    restarts = 0
    while time.time() - t0 < seconds:
        k = random.choice([3, 4, 5, 5, 6, 6, 7, 8])
        B = bipartite_start(k, min(60, maxe)) if random.random() < 0.6 else \
            np.random.randint(0, 20, size=(k, k))
        g = gap(B, edge_fn)
        T = 1.0
        for it in range(3000):
            if time.time() - t0 > seconds:
                break
            T = max(0.001, 1.0 * (1 - it / 3000))
            C = mutate(B, maxe)
            g2 = gap(C, edge_fn)
            if g2 <= g or (g2 < math.inf and random.random() < math.exp(-(g2 - g) / T)):
                B, g = C, g2
            if g < best[0]:
                best = (g, B.copy())
            if g < -1e-7:
                print(f"VIOLATION CANDIDATE bound {bound} gap={g}\n{B}", flush=True)
                np.save(f"anneal_violation_{bound}.npy", B)
                return
        restarts += 1
    print(f"bound {bound}: min gap found = {best[0]:.6g} after {restarts} restarts")
    print(best[1])


if __name__ == "__main__":
    main()
