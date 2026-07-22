#!/usr/bin/env python3
"""Non-coprime subgroup-product search.

For a target cell (n, k) and factorization k = k1*k2, take every DB witness F0
of a CW(m1, k1) with m1 | n and every DB witness G0 of a CW(m2, k2) with m2 | n,
embed each into Z[x]/(x^n - 1) via every injective map x -> x^{(n/mi) * v}
(gcd(v, mi) = 1), and test h = F * G. Group-ring identity: h h* = k1 k2 always;
h is a CW(n, k) iff its coefficients are ternary (and then weight k follows).
We machine-verify PACF anyway and check properness.

Global multiplier equivalence h(x^w), gcd(w, n) = 1, lets us fix F's embedding
exponent only when the normalizing w exists mod n; to stay safe we brute force
all (u, v) pairs — the space is tiny.
"""
import sys
from math import gcd
from itertools import product
sys.path.insert(0, "../../../solutions/P11")
from verify import check, is_proper
from extract_table import load, table

D = table(load())


def db_sets(m, k):
    v = D.get((m, k))
    return v["sets"] if v else []


def embed(n, m, P, N, e):
    """coeff vector of f(x^e) in Z_n, f supported on Z_m, e = (n/m)*v."""
    a = [0] * n
    for x in P:
        a[(x * e) % n] += 1
    for x in N:
        a[(x * e) % n] -= 1
    return a


def polymul(n, a, b):
    h = [0] * n
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    h[(i + j) % n] += ai * bj
    return h


def search(n, k, k1, k2, verbose=True):
    found = []
    tried = 0
    fs = [(m, s) for m in range(1, n + 1) if n % m == 0 for s in db_sets(m, k1)]
    gs = [(m, s) for m in range(1, n + 1) if n % m == 0 for s in db_sets(m, k2)]
    for (m1, (P1, N1)), (m2, (P2, N2)) in product(fs, gs):
        for u in range(1, m1):
            if gcd(u, m1) != 1:
                continue
            F = embed(n, m1, P1, N1, (n // m1) * u)
            for v in range(1, m2):
                if gcd(v, m2) != 1:
                    continue
                G = embed(n, m2, P2, N2, (n // m2) * v)
                h = polymul(n, F, G)
                tried += 1
                if all(abs(c) <= 1 for c in h):
                    P = [i for i, c in enumerate(h) if c == 1]
                    N = [i for i, c in enumerate(h) if c == -1]
                    if len(P) + len(N) == k:
                        check(n, k, P, N, proper=False)
                        pr = is_proper(n, P, N)
                        found.append((m1, u, m2, v, P, N, pr))
                        if verbose:
                            print(f"  HIT n={n} k={k} from ({m1},{k1})x({m2},{k2}) "
                                  f"u={u} v={v} proper={pr}")
    print(f"target ({n},{k}) via {k1}*{k2}: factors {len(fs)}x{len(gs)}, "
          f"{tried} products tried, {len(found)} ternary hits, "
          f"{sum(1 for f in found if f[6])} proper")
    return found


if __name__ == "__main__":
    # 36 = 4*9 and 9*4 (order matters only for bookkeeping; product commutes)
    search(96, 36, 4, 9)
    search(96, 36, 9, 4)
    search(105, 36, 4, 9)
    search(112, 36, 4, 9)
    search(117, 36, 4, 9)
    search(120, 49, 49, 1)
    search(132, 81, 9, 9)
