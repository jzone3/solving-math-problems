#!/usr/bin/env python3
"""P16: refine the continuous relaxation on promising k=3/k=4 supports,
parametrizing b_ij >= 1 (i<j) and n_i >= 1 directly (b_ji derived).
Goal: find feasible-scale positive-margin regions to guide integer search."""
import itertools
import math
import sys

import numpy as np
from scipy.optimize import minimize


def make_eval(which, k, offsup, loopsup):
    def margin(x):
        n = 1 + np.exp(x[:k])
        b = {}
        t = k
        for (i, j) in offsup:
            b[(i, j)] = 1 + np.exp(x[t]); t += 1
        loops = {}
        for i in loopsup:
            loops[i] = 1 + np.exp(x[t]); t += 1
        B = np.zeros((k, k))
        pen = 0.0
        for (i, j) in offsup:
            B[i, j] = b[(i, j)]
            B[j, i] = n[i] * b[(i, j)] / n[j]
            pen += max(0.0, 1.0 - B[j, i]) ** 2
            pen += max(0.0, B[i, j] - n[j]) ** 2 + max(0.0, B[j, i] - n[i]) ** 2
        for i in loopsup:
            B[i, i] = loops[i]
            pen += max(0.0, B[i, i] - (n[i] - 1)) ** 2
        d = B.sum(axis=1)
        if d.min() <= 1e-12:
            return -1e6
        m = (B @ d) / d
        M = np.diag(d) - np.diag(np.sqrt(n)) @ B @ np.diag(1 / np.sqrt(n))
        M = (M + M.T) / 2
        if not np.all(np.isfinite(M)):
            return -1e6
        try:
            mu = np.max(np.linalg.eigvalsh(M))
        except np.linalg.LinAlgError:
            return -1e6
        rhs = -np.inf
        for (i, j) in list(offsup) + [(i, i) for i in loopsup]:
            di, dj, mi, mj = d[i], d[j], m[i], m[j]
            if which == 44:
                inner = 2 * ((di - 1) ** 2 + (dj - 1) ** 2 + mi * mj - di * dj)
            else:
                inner = 2 * (di ** 2 + dj ** 2) - 16 * di * dj / (mi + mj) + 4
            if inner < 0:
                return -1e6
            rhs = max(rhs, 2 + math.sqrt(inner))
        return mu - rhs - 1000.0 * pen

    return margin


def run(which):
    rng = np.random.default_rng(1)
    cases = []
    # k=3 all connected supports with any loops
    for offs in [[(0, 1), (0, 2)], [(0, 1), (0, 2), (1, 2)]]:
        for loops in itertools.chain.from_iterable(itertools.combinations(range(3), s) for s in range(4)):
            cases.append((3, offs, list(loops)))
    # k=4 selected supports (bipartite-ish + pendant gadgets)
    for offs in [[(0, 1), (0, 2), (1, 2), (2, 3)],
                 [(0, 1), (0, 2), (1, 3), (2, 3)],
                 [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)],
                 [(0, 1), (1, 2), (2, 3)],
                 [(0, 1), (0, 2), (0, 3)]]:
        for loops in itertools.chain.from_iterable(itertools.combinations(range(4), s) for s in range(3)):
            cases.append((4, offs, list(loops)))
    best = (-1e18, None)
    for (k, offs, loops) in cases:
        f = make_eval(which, k, offs, loops)
        for r in range(12):
            x0 = rng.uniform(-2, 5, k + len(offs) + len(loops))
            res = minimize(lambda x: -f(x), x0, method="Nelder-Mead",
                           options={"maxiter": 8000, "xatol": 1e-12, "fatol": 1e-14})
            v = -res.fun
            if v > best[0]:
                best = (v, (k, offs, loops, res.x))
            if v > 1e-5:
                k_, x = k, res.x
                n = 1 + np.exp(x[:k])
                print(f"[{which}] POSITIVE {v:.8f} k={k} offs={offs} loops={loops} n={n} x={np.exp(x[k:])+1}", flush=True)
    v, info = best
    print(f"[{which}] REFINE OVERALL best {v:.10f}")
    if info:
        k, offs, loops, x = info
        print(f"  k={k} offs={offs} loops={loops} n={1+np.exp(x[:k])} b/loops={1+np.exp(x[k:])}")


if __name__ == "__main__":
    run(int(sys.argv[1]))
