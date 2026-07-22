#!/usr/bin/env python3
"""Independent verifier for the P10/V4 structured-family results (stdlib only).

No counterexample to Brouwer's conjecture was found; the V4 run's positive claims are:
  (1) closed-form Laplacian spectra used in the scans are correct, and
  (2) the Brouwer deficit  min_t [m + t(t+1)/2 - S_t]  is >= 0 on sampled members of
      every scanned family, including the two families proved symbolically:
        F1: K_a v (b*K_c)    F3: K_a v (K_b u E_c)   (all parameters).

This script rebuilds actual graphs (adjacency lists), computes eigenvalue multiplicities
EXACTLY by Fraction Gaussian-elimination nullity of (L - lam*I)^  -- no numpy, no sympy --
verifies each claimed closed-form spectrum, then checks all Brouwer partial-sum
inequalities exactly. Prints PASS iff everything checks out.
"""
from fractions import Fraction
from itertools import combinations
import random

random.seed(12)


def nullity(M):
    """Exact nullity of a square Fraction matrix via Gaussian elimination."""
    M = [row[:] for row in M]
    n = len(M)
    rank = 0
    col = 0
    for col in range(n):
        piv = None
        for r in range(rank, n):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        pv = M[rank][col]
        M[rank] = [x / pv for x in M[rank]]
        for r in range(n):
            if r != rank and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[rank])]
        rank += 1
    return n - rank


def laplacian(n, edges):
    L = [[Fraction(0)] * n for _ in range(n)]
    for u, v in edges:
        L[u][u] += 1
        L[v][v] += 1
        L[u][v] -= 1
        L[v][u] -= 1
    return L


def check_spectrum(n, edges, spec):
    """spec: list of (eigenvalue, multiplicity), values Fraction/int. Verify exactly."""
    assert sum(m for _, m in spec) == n, "multiplicities must sum to n"
    L = laplacian(n, edges)
    for lam, mult in spec:
        M = [[L[i][j] - (lam if i == j else 0) for j in range(n)] for i in range(n)]
        assert nullity(M) == mult, f"eigenvalue {lam}: expected mult {mult}"


def brouwer_ok(n, edges, spec):
    m = len(edges)
    eigs = []
    for v, mult in sorted(spec, key=lambda x: -Fraction(x[0])):
        eigs += [Fraction(v)] * mult
    S = Fraction(0)
    for t, v in enumerate(eigs, 1):
        S += v
        assert m + Fraction(t * (t + 1), 2) - S >= 0, \
            f"BROUWER VIOLATION t={t} deficit={m + Fraction(t*(t+1),2) - S}"


def join_edges(n1, e1, n2, e2):
    """Join: e2's vertices shifted by n1; all cross edges."""
    e = list(e1) + [(u + n1, v + n1) for u, v in e2] + \
        [(i, j + n1) for i in range(n1) for j in range(n2)]
    return n1 + n2, e


def clique_edges(k, off=0):
    return [(i + off, j + off) for i, j in combinations(range(k), 2)]


checked = 0

# --- F1: K_a v (b*K_c) ---
for _ in range(12):
    a, b, c = random.randint(1, 5), random.randint(1, 4), random.randint(2, 5)
    e2 = []
    for i in range(b):
        e2 += clique_edges(c, i * c)
    n, e = join_edges(a, clique_edges(a), b * c, e2)
    spec = [(a + b * c, a), (a + c, b * (c - 1)), (a, b - 1), (0, 1)]
    spec = [(v, m) for v, m in spec if m > 0]
    # merge duplicates
    d = {}
    for v, m in spec:
        d[v] = d.get(v, 0) + m
    check_spectrum(n, e, list(d.items()))
    brouwer_ok(n, e, list(d.items()))
    checked += 1

# --- F3: K_a v (K_b u E_c) ---
for _ in range(12):
    a, b, c = random.randint(1, 5), random.randint(2, 6), random.randint(1, 5)
    n, e = join_edges(a, clique_edges(a), b + c, clique_edges(b))
    spec = {}
    for v, m in [(a + b + c, a), (a + b, b - 1), (a, c), (0, 1)]:
        if m > 0:
            spec[v] = spec.get(v, 0) + m
    check_spectrum(n, e, list(spec.items()))
    brouwer_ok(n, e, list(spec.items()))
    checked += 1

# --- Kneser K(nn,k) small samples ---
from math import comb
for nn, k in [(5, 2), (6, 2), (7, 2), (7, 3), (8, 3)]:
    verts = list(combinations(range(nn), k))
    idx = {v: i for i, v in enumerate(verts)}
    e = [(idx[x], idx[y]) for x, y in combinations(verts, 2) if not set(x) & set(y)]
    spec = {}
    for i in range(k + 1):
        lam = comb(nn - k, k) - (-1) ** i * comb(nn - k - i, k - i)
        mult = comb(nn, i) - (comb(nn, i - 1) if i else 0)
        spec[lam] = spec.get(lam, 0) + mult
    check_spectrum(len(verts), e, list(spec.items()))
    brouwer_ok(len(verts), e, list(spec.items()))
    checked += 1

# --- complete multipartite samples ---
for _ in range(8):
    parts = [random.randint(1, 5) for _ in range(random.randint(2, 5))]
    n = sum(parts)
    off = [sum(parts[:i]) for i in range(len(parts))]
    e = []
    for i, j in combinations(range(len(parts)), 2):
        for u in range(parts[i]):
            for v in range(parts[j]):
                e.append((off[i] + u, off[j] + v))
    spec = {Fraction(n): len(parts) - 1, Fraction(0): 1}
    for p in parts:
        if p > 1:
            v = Fraction(n - p)
            spec[v] = spec.get(v, 0) + (p - 1)
    check_spectrum(n, e, list(spec.items()))
    brouwer_ok(n, e, list(spec.items()))
    checked += 1

print(f"checked {checked} instances: closed-form spectra exact-verified, "
      f"all Brouwer partial sums satisfied.")
print("PASS")
