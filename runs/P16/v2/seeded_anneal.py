"""Low-temperature annealing seeded at the tightest known configurations:
DHS Table-3 counterexample quotients (for other bounds) and K_{d,d}-minus-
biregular quotients. Minimizes gap = RHS - lam_max(L_B) for Bound 44 or 46.

Usage: python3 seeded_anneal.py <44|46> <seconds>
"""
import math
import random
import sys
import time

import numpy as np

from anneal_quotient import gap, mutate
from search_common import rhs44_edge, rhs46_edge

SEEDS = [
    [[0, 0, 76], [0, 0, 8], [69, 2, 0]],
    [[0, 0, 0, 88], [0, 0, 22, 0], [0, 19, 0, 6], [83, 0, 3, 0]],
    [[0, 1, 0, 42], [4, 0, 14, 0], [0, 4, 0, 4], [36, 0, 3, 0]],
    [[0, 5, 0, 0], [1, 0, 3, 0], [0, 1, 0, 1], [0, 0, 1, 0]],
]


def kdd_minus_e(d):
    # K_{d,d} minus one edge: cells A0(d-1,deg d), A1(1,deg d-1), B0(d-1,deg d), B1(1,deg d-1)
    return [[0, 0, d - 1, 1], [0, 0, d - 1, 0], [d - 1, 1, 0, 0], [d - 1, 0, 0, 0]]


def main():
    bound = int(sys.argv[1])
    seconds = float(sys.argv[2])
    edge_fn = rhs44_edge if bound == 44 else rhs46_edge
    seeds = [np.array(S) for S in SEEDS] + [np.array(kdd_minus_e(d)) for d in (5, 20, 80, 200)]
    t0 = time.time()
    best = (math.inf, None)
    chain = 0
    while time.time() - t0 < seconds:
        B = random.choice(seeds).copy()
        g = gap(B, edge_fn)
        T0 = random.choice([0.02, 0.1, 0.5])
        for it in range(5000):
            if time.time() - t0 > seconds:
                break
            T = max(1e-4, T0 * (1 - it / 5000))
            C = mutate(B, 500)
            g2 = gap(C, edge_fn)
            if g2 <= g or (g2 < math.inf and random.random() < math.exp(-(g2 - g) / T)):
                B, g = C, g2
            if g < best[0]:
                best = (g, B.copy())
            if g < -1e-7:
                print(f"VIOLATION CANDIDATE bound {bound} gap={g}\n{B}", flush=True)
                np.save(f"seeded_violation_{bound}.npy", B)
                return
        chain += 1
    print(f"bound {bound}: min gap = {best[0]:.6g} over {chain} chains")
    print(best[1])


if __name__ == "__main__":
    main()
