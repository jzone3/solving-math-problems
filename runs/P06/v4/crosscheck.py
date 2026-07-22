#!/usr/bin/env python3
"""Cross-validation of the C checker pipeline for P06 V4 (Graffiti 129).

The exhaustive C checker (check.c) uses the degree-only identity
    dev(L)^2 = (sum d_i^2 + 2m)/n - (2m/n)^2
(from trace(L) = 2m, trace(L^2) = sum d_i^2 + 2m).

This script independently validates, WITHOUT that identity, by direct
Laplacian eigendecomposition (numpy.linalg.eigvalsh):
  1. every graph on n <= 7 vertices (geng), comparing gap = dev - R
     computed both ways (agreement < 1e-9);
  2. 2000 random G(n,p) graphs, n in [8,30];
  3. the equality family K_k U (k-2)K_1 (dev = R = k/2) in exact
     arithmetic via sympy, k = 3..40.
Prints PASS if all checks succeed.
"""
import subprocess, sys, random, math
import numpy as np

def randic(deg, edges):
    return sum(1.0/math.sqrt(deg[u]*deg[v]) for u, v in edges)

def dev_eig(n, edges):
    L = np.zeros((n, n))
    for u, v in edges:
        L[u, u] += 1; L[v, v] += 1
        L[u, v] -= 1; L[v, u] -= 1
    w = np.linalg.eigvalsh(L)
    return float(np.sqrt(np.mean((w - w.mean())**2)))

def dev_formula(n, deg, m):
    s2 = sum(d*d for d in deg)
    var = (s2 + 2*m)/n - (2*m/n)**2
    return math.sqrt(max(var, 0.0))

def parse_g6(line):
    b = line.strip()
    n = ord(b[0]) - 63
    bits = []
    for ch in b[1:]:
        c = ord(ch) - 63
        bits.extend(((c >> k) & 1) for k in range(5, -1, -1))
    edges, bi = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[bi]: edges.append((i, j))
            bi += 1
    return n, edges

def check_graph(n, edges):
    deg = [0]*n
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    m = len(edges)
    d1 = dev_eig(n, edges)
    d2 = dev_formula(n, deg, m)
    assert abs(d1 - d2) < 1e-9, (n, edges, d1, d2)
    R = randic(deg, edges)
    assert d1 <= R + 1e-9, ("CONJECTURE 129 VIOLATION?", n, edges, d1, R)

def main():
    total = 0
    for n in range(2, 8):
        out = subprocess.run(["nauty-geng", "-q", str(n)],
                             capture_output=True, text=True).stdout
        for line in out.splitlines():
            check_graph(*parse_g6(line)); total += 1
    print(f"exhaustive n<=7: {total} graphs OK (formula==eigensolve, 129 holds)")

    rng = random.Random(12345)
    for _ in range(2000):
        n = rng.randint(8, 30); p = rng.random()
        edges = [(i, j) for i in range(n) for j in range(i+1, n)
                 if rng.random() < p]
        check_graph(n, edges)
    print("2000 random graphs n in [8,30] OK")

    import sympy as sp
    for k in range(3, 41):
        n = 2*k - 2                       # K_k plus (k-2) isolated vertices
        m = k*(k-1)//2
        S = k*(k-1)**2
        var = sp.Rational(S + 2*m, n) - sp.Rational(2*m, n)**2
        dev = sp.sqrt(var)
        R = sp.Rational(m, 1)/sp.sqrt(sp.Integer((k-1)*(k-1)))
        assert sp.simplify(dev - sp.Rational(k, 2)) == 0
        assert sp.simplify(R - sp.Rational(k, 2)) == 0
    print("equality family K_k U (k-2)K_1: dev = R = k/2 exactly, k=3..40")
    print("PASS")

if __name__ == "__main__":
    main()
