"""Random + annealed search over equitable-partition quotient matrices (DHS Sec. 4
family — where all 12 DHS counterexamples were found) for violations of Bounds 44/46.

Search space: k x k nonnegative integer matrices B with symmetrizable support,
k in {2,3,4,5}, entries up to MAXE.  Score = lam_max(L_B) - RHS(bound) (want > 0).
Floats only; any hit goes to the exact verifier.

Usage: python3 quotient_search.py <bound: 44|46> <seconds>
"""
import math
import random
import sys
import time

import numpy as np

from search_common import (quotient_data, quotient_ok, quotient_rhs,
                           rhs44_edge, rhs46_edge)

MAXE = 120


def score(B, edge_fn):
    if quotient_ok(B) is None:
        return -math.inf, None
    s = B.sum(axis=1).astype(float)
    if (s == 0).any():
        return -math.inf, None
    lam, s, m = quotient_data(B, None)
    r = quotient_rhs(B, s, m, edge_fn)
    if r == -math.inf:
        # every edge term undefined cannot happen for a graph with an edge? It can:
        # convention makes the bound vacuous-false ONLY if some edge exists; DHS treat
        # max over well-defined terms; if none well-defined, bound is violated by any mu>0.
        return math.inf, (lam, r)
    return lam - r, (lam, r)


def random_B(k):
    B = np.zeros((k, k), dtype=int)
    for i in range(k):
        for j in range(i, k):
            if random.random() < 0.7:
                v = random.randint(0, MAXE)
                if i == j:
                    B[i, i] = v
                else:
                    B[i, j] = v
                    B[j, i] = random.randint(1, MAXE) if v > 0 else 0
    return B


def mutate(B):
    B = B.copy()
    k = B.shape[0]
    i, j = random.randrange(k), random.randrange(k)
    delta = random.choice([-3, -2, -1, 1, 2, 3])
    B[i, j] = max(0, B[i, j] + delta)
    if i != j and B[i, j] > 0 and B[j, i] == 0:
        B[j, i] = 1
    if i != j and B[i, j] == 0:
        B[j, i] = 0
    return B


def main():
    bound = int(sys.argv[1])
    seconds = float(sys.argv[2])
    edge_fn = rhs44_edge if bound == 44 else rhs46_edge
    t0 = time.time()
    best_overall = -math.inf
    best_B = None
    trials = 0
    while time.time() - t0 < seconds:
        k = random.choice([2, 3, 3, 4, 4, 5])
        B = random_B(k)
        sc, _ = score(B, edge_fn)
        # hill climb with restarts
        for _ in range(400):
            if time.time() - t0 > seconds:
                break
            C = mutate(B)
            sc2, info2 = score(C, edge_fn)
            if sc2 >= sc:
                B, sc = C, sc2
            if sc > 1e-9 and sc != math.inf:
                print(f"VIOLATION bound {bound}: B=\n{B}\nscore={sc}")
                np.save(f"violation_{bound}.npy", B)
                return
        trials += 1
        if sc > best_overall and sc != math.inf:
            best_overall = sc
            best_B = B.copy()
    print(f"bound {bound}: no violation. restarts={trials}, best gap={best_overall}")
    print(f"best B=\n{best_B}")


if __name__ == "__main__":
    main()
