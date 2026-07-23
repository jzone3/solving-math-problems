"""Randomized + annealed search over GRAPHICAL degree sequences with the
capacity-constrained transportation LP lower bound on Randic (see seq_lp.py).

score(d, n) = dev(d, n) - LP_minRandic(d): conjecture 129 fails only if some
graph beats its sequence's LP bound... (converse: score > 0 does NOT give a
counterexample, but flags candidate sequences for realization search;
score <= 0 everywhere would prove the conjecture).

Anneal over sequences at fixed n with moves +-1 on random entries (Erdos-Gallai
maintained), seeded from clique+iso / star / random graphical sequences.
"""
import math
import random
import sys
from collections import Counter

import numpy as np
from scipy.optimize import linprog


def erdos_gallai(degs_sorted_desc):
    d = degs_sorted_desc
    n = len(d)
    if sum(d) % 2:
        return False
    pref = 0
    for k in range(1, n + 1):
        pref += d[k - 1]
        tail = sum(min(x, k) for x in d[k:])
        if pref > k * (k - 1) + tail:
            return False
    return True


def lp_min_randic(degs):
    cnt = Counter(d for d in degs if d > 0)
    vals = sorted(cnt)
    iv = {a: i for i, a in enumerate(vals)}
    pairs = [(a, b) for i, a in enumerate(vals) for b in vals[i:]]
    c = np.array([1.0 / math.sqrt(a * b) for a, b in pairs])
    A_eq = np.zeros((len(vals), len(pairs)))
    b_eq = np.array([a * cnt[a] for a in vals], dtype=float)
    for j, (a, b) in enumerate(pairs):
        A_eq[iv[a], j] += 1
        A_eq[iv[b], j] += 1
    ub = [cnt[a] * cnt[b] if a != b else cnt[a] * (cnt[a] - 1) / 2 for a, b in pairs]
    res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=[(0, u) for u in ub], method="highs")
    return res.fun if res.status == 0 else None


def dev_of(degs, n):
    m = sum(degs) // 2
    S = sum(d * d for d in degs)
    var = (S + 2 * m) / n - (2 * m / n) ** 2
    return math.sqrt(max(var, 0.0))


def score(degs, n):
    lp = lp_min_randic(degs)
    if lp is None:
        return None
    return dev_of(degs, n) - lp


def anneal(n, iters, seed, start):
    rng = random.Random(seed)
    degs = sorted(start, reverse=True)
    cur = score(degs, n)
    best, barg = cur, list(degs)
    for it in range(iters):
        T = 0.02 * (1e-5 / 0.02) ** (it / iters)
        nd = list(degs)
        for _ in range(rng.choice([1, 1, 1, 2])):
            i = rng.randrange(len(nd))
            nd[i] += rng.choice([-1, 1])
        if any(x < 0 or x > n - 1 for x in nd):
            continue
        nd = sorted(nd, reverse=True)
        if sum(nd) % 2 or not erdos_gallai([x for x in nd if x > 0]):
            continue
        val = score([x for x in nd if x > 0], n)
        if val is None:
            continue
        dlt = val - cur
        if dlt >= 0 or rng.random() < math.exp(dlt / T):
            degs, cur = nd, val
            if cur > best:
                best, barg = cur, list(nd)
    return best, barg


if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [14, 18, 26, 38, 50, 74, 98]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    for n in ns:
        q = (n + 2) // 2
        seeds = [
            [q - 1] * q + [0] * (n - q),                # equality family
            [n - 1] + [1] * (n - 1),                    # star
            [2 * ((n - 1) // 3)] * n if ([2 * ((n - 1) // 3)] * n and sum([2 * ((n - 1) // 3)] * n) % 2 == 0) else [2] * n,  # regular-ish
        ]
        overall, oa = -1e18, None
        for r, s in enumerate(seeds):
            b, arg = anneal(n, iters, 31 * n + r, s)
            if b > overall:
                overall, oa = b, arg
        print(f"n={n:4d} best dev-LP = {overall:+.9f} at degs={dict(Counter(oa))}",
              flush=True)
        if overall > 1e-7:
            print("CANDIDATE SEQUENCE (needs realization search)", flush=True)
