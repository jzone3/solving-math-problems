"""P06 V2 second encoding: optimize over DEGREE SEQUENCES with a rigorous
Randic lower bound (transportation relaxation).

For any graph G with degree sequence d: R(G) = sum_e 1/sqrt(d_u d_v). Viewing
each edge as pairing two "stubs" (degree slots), the edge-type histogram x_ab
is a feasible point of the transportation polytope {x >= 0, sum_b x_ab-stubs =
a*n_a}. The cost c_ab = 1/sqrt(ab) = f(a)f(b) with f decreasing satisfies the
anti-Monge condition, so the transportation minimum is the ANTI-MONOTONE stub
matching: sort the 2m stubs by degree and pair i-th smallest with i-th largest.
Hence for every graph G:

    R(G) >= R_LP(d) := sum_{i=1..m} 1/sqrt(s_i * s_{2m+1-i}),   s = sorted stubs.

Since dev(G) also depends only on d, the inequality dev(d) <= R_LP(d) over all
degree sequences (no graphicality needed!) would PROVE conjecture 129.
This script searches for sequences violating dev <= R_LP (or near-misses).

Search: simulated annealing over (n, multiset of degrees), moves: +-1 a random
degree (0 allowed), add/remove a degree-0 vertex, duplicate/remove a vertex.
"""
import math
import random
import sys


def dev_and_rlp(degs, n):
    """degs: list of positive degrees (len <= n); n: total vertices."""
    m2 = sum(degs)
    if m2 == 0 or m2 % 2 == 1:
        return None
    m = m2 // 2
    S = sum(d * d for d in degs)
    var = (S + 2 * m) / n - (2 * m / n) ** 2
    dev = math.sqrt(max(var, 0.0))
    stubs = []
    for d in degs:
        stubs.extend([d] * d)
    stubs.sort()
    rlp = 0.0
    for i in range(m):
        rlp += 1.0 / math.sqrt(stubs[i] * stubs[m2 - 1 - i])
    return dev - rlp


def anneal(n0, iters, seed):
    rng = random.Random(seed)
    # start at equality family shape: q = (n0+2)//2 vertices of degree q-1
    q = (n0 + 2) // 2
    degs = [q - 1] * q
    n = n0
    cur = dev_and_rlp(degs, n)
    best, bestarg = cur, (list(degs), n)
    for it in range(iters):
        T = 0.02 * (1e-6 / 0.02) ** (it / iters)
        nd, nn = list(degs), n
        mv = rng.random()
        if mv < 0.4 and nd:
            i = rng.randrange(len(nd))
            nd[i] += rng.choice([-1, 1])
            if nd[i] <= 0:
                nd.pop(i)
            elif nd[i] > nn - 1:
                continue
        elif mv < 0.6:
            nn += rng.choice([-1, 1])
            if nn < max(2, len(nd)):
                continue
        elif mv < 0.8 and nd:
            nd.append(nd[rng.randrange(len(nd))])  # duplicate a degree
            nn += 1
        elif nd:
            nd.pop(rng.randrange(len(nd)))
        else:
            continue
        if len(nd) > nn or any(d > nn - 1 for d in nd):
            continue
        val = dev_and_rlp(nd, nn)
        if val is None:
            continue
        dlt = val - cur
        if dlt >= 0 or rng.random() < math.exp(dlt / T):
            degs, n, cur = nd, nn, val
            if cur > best:
                best, bestarg = cur, (sorted(degs), n)
    return best, bestarg


if __name__ == "__main__":
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 400000
    for n0 in [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [10, 20, 40, 80, 160, 320]:
        overall, oa = -1e9, None
        for r in range(4):
            b, arg = anneal(n0, iters, seed=77 * n0 + r)
            if b > overall:
                overall, oa = b, arg
        from collections import Counter
        print(f"n0={n0:4d} best dev-R_LP = {overall:+.9f} at n={oa[1]} "
              f"degs={dict(Counter(oa[0]))}", flush=True)
        if overall > 1e-9:
            print("RELAXATION VIOLATION (candidate degree sequence)", flush=True)
