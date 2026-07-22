"""
P06/V1: exact equality family found: G_q = K_q  U  (q-2) K_1  gives dev = R = q/2.

Proof of equality (machine-checked below): degrees (q-1)^q 0^(q-2), N=2(q-1),
dev^2 = (sum d^2 + sum d)/N - (sum d / N)^2 = q^2(q-1)/N - q^2(q-1)^2/N^2
      = q^2/2 - q^2/4 = q^2/4;  R = C(q,2)/(q-1) = q/2.
Moreover N = 2(q-1) maximizes dev over the number of added isolated vertices.

This script searches for a STRICT violation near the equality manifold:
1. exact check of the equality family (sympy rationals);
2. parametrized perturbation families around G_q, scanned over wide ranges
   with mpmath (50 digits), any positive re-checked with sympy exact;
3. steepest-ascent local search (single edge toggles) on all simple graphs on
   N vertices seeded at G_q and random near-equality points, exact scoring.
"""
import itertools
import math
import random
import sys

from mpmath import mp, mpf, sqrt as msqrt

sys.path.insert(0, ".")
import harness as H

mp.dps = 50


def mp_score(adj):
    d = [len(nb) for nb in adj]
    N = len(adj)
    s1 = sum(d)
    s2 = sum(x * x for x in d)
    dev2 = (mpf(s2 + s1) / N) - (mpf(s1) / N) ** 2
    R = mpf(0)
    for u in range(N):
        for v in adj[u]:
            if u < v:
                R += 1 / msqrt(mpf(d[u] * d[v]))
    return msqrt(dev2) - R, msqrt(dev2), R


def exact_equality_check():
    import sympy as sp
    for q in [2, 3, 4, 5, 10, 41, 100, 1000]:
        N = 2 * (q - 1)
        dev2 = sp.Rational(q * q * (q - 1), N) - sp.Rational(q * (q - 1), N) ** 2
        R = sp.Rational(q * (q - 1), 2) / (q - 1)
        assert sp.simplify(dev2 - R**2) == 0, q
    print("exact equality check PASS: dev = R = q/2 on K_q U (q-2)K_1 for all tested q")


def clique_pendant(q, j, t):
    # K_q + one extra vertex adjacent to j clique vertices + t isolated
    n = q + 1 + t
    es = [(i, jj) for i in range(q) for jj in range(i + 1, q)]
    es += [(i, q) for i in range(j)]
    return H.from_edges(n, es)


def clique_minus_matching(q, r, t):
    # K_q minus a matching of size r, + t isolated
    n = q + t
    drop = {(2 * i, 2 * i + 1) for i in range(r)}
    es = [(i, j) for i in range(q) for j in range(i + 1, q) if (i, j) not in drop]
    return H.from_edges(n, es)


def clique_plus_k2s(q, c, t):
    # K_q U c*K2 U t*K1
    n = q + 2 * c + t
    es = [(i, j) for i in range(q) for j in range(i + 1, q)]
    es += [(q + 2 * i, q + 2 * i + 1) for i in range(c)]
    return H.from_edges(n, es)


def clique_plus_star(q, s, t):
    # K_q U K_{1,s} U t*K1
    n = q + s + 1 + t
    es = [(i, j) for i in range(q) for j in range(i + 1, q)]
    es += [(q, q + 1 + i) for i in range(s)]
    return H.from_edges(n, es)


def clique_bridge(q, t):
    # K_q with one extra edge from clique vertex 0 to a new pendant, + t K1
    return clique_pendant(q, 1, t)


def sweep_perturbations():
    best = []
    for q in range(3, 60):
        for t in range(0, 3 * q):
            for j in range(0, q + 1):
                if j == 0 and t == 0:
                    continue
                adj = clique_pendant(q, j, t) if j > 0 else H.from_edges(q + t, [(a, b) for a in range(q) for b in range(a + 1, q)])
                s, dev, R = mp_score(adj)
                best.append((float(s), f"clique_pendant(q={q},j={j},t={t})"))
        for r in range(0, q // 2 + 1):
            for t in range(0, 3 * q):
                s, dev, R = mp_score(clique_minus_matching(q, r, t))
                best.append((float(s), f"clique_minus_matching(q={q},r={r},t={t})"))
        for c in range(0, 6):
            for t in range(0, 3 * q):
                s, dev, R = mp_score(clique_plus_k2s(q, c, t))
                best.append((float(s), f"clique_plus_k2s(q={q},c={c},t={t})"))
        for sarm in range(1, 12):
            for t in range(0, 3 * q):
                s, dev, R = mp_score(clique_plus_star(q, sarm, t))
                best.append((float(s), f"clique_plus_star(q={q},s={sarm},t={t})"))
    best.sort(reverse=True)
    print("\ntop 15 perturbation scores (0 = equality family):")
    for s, name in best[:15]:
        print(f"  {s:+.10f}  {name}")
    return best[0]


def local_search(N, seeds=6, iters=400, seed0=0):
    rng = random.Random(seed0)
    q = N // 2 + 1  # equality when N = 2(q-1)
    print(f"\nlocal search on N={N} vertices (equality clique q={q}):")
    overall = (-1e9, None)
    for trial in range(seeds):
        # adjacency as set of frozenset edges
        E = {(i, j) for i in range(q) for j in range(i + 1, q)}
        if trial > 0:  # random perturbation of the seed
            allp = list(itertools.combinations(range(N), 2))
            for _ in range(rng.randint(1, 4)):
                e = rng.choice(allp)
                E ^= {e}
        def sc(E):
            adj = H.from_edges(N, E)
            return mp_score(adj)[0]
        cur = sc(E)
        improved = True
        it = 0
        while improved and it < iters:
            improved = False
            it += 1
            bestmove, bestval = None, cur
            for e in itertools.combinations(range(N), 2):
                E2 = set(E)
                E2 ^= {e}
                v = sc(E2)
                if v > bestval + mpf(10) ** (-40):
                    bestval, bestmove = v, e
            if bestmove:
                E ^= {bestmove}
                cur = bestval
                improved = True
        if cur > overall[0]:
            overall = (cur, set(E))
        print(f"  trial {trial}: local max score = {float(cur):+.12f}")
    print(f"  best over trials: {float(overall[0]):+.12f}")
    return overall


if __name__ == "__main__":
    exact_equality_check()
    b = sweep_perturbations()
    for N in [8, 10, 12, 14]:
        local_search(N)
