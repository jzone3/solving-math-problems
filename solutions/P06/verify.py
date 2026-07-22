#!/usr/bin/env python3
"""P06 (Graffiti 129) V4 verifier — standalone, stdlib only.

No counterexample is claimed (negative result). This script independently
verifies the two structural claims made in runs/P06/v4/NOTES.md:

1. Degree-only identity: the population standard deviation of the Laplacian
   eigenvalues satisfies dev^2 = (sum d^2 + 2m)/n - (2m/n)^2.
   Verified here WITHOUT external libs by a Jacobi eigensolver on a suite of
   graphs (paths, stars, complete, complete bipartite, random).

2. Exact equality family: G_k = K_k U (k-2)K_1 (n = 2k-2 vertices) has
   dev(G_k) = R(G_k) = k/2 EXACTLY, where R = sum_{uv in E} 1/sqrt(d_u d_v).
   Verified in exact integer arithmetic (Fraction): dev^2 = k^2/4 and, since
   all edges of K_k join degree-(k-1) vertices, R = C(k,2)/(k-1) = k/2.

Prints PASS iff all checks succeed.
"""
import random
from fractions import Fraction


def jacobi_eigenvalues(A, sweeps=100, tol=1e-12):
    n = len(A)
    a = [row[:] for row in A]
    for _ in range(sweeps):
        off = max((abs(a[i][j]), i, j)
                  for i in range(n) for j in range(n) if i != j)
        if off[0] < tol:
            break
        _, p, q = off
        if a[p][p] == a[q][q]:
            import math
            theta = math.pi / 4
        else:
            import math
            theta = 0.5 * math.atan2(2 * a[p][q], a[q][q] - a[p][p])
        import math
        c, s = math.cos(theta), math.sin(theta)
        for k in range(n):
            akp, akq = a[k][p], a[k][q]
            a[k][p] = c * akp - s * akq
            a[k][q] = s * akp + c * akq
        for k in range(n):
            apk, aqk = a[p][k], a[q][k]
            a[p][k] = c * apk - s * aqk
            a[q][k] = s * apk + c * aqk
    return [a[i][i] for i in range(n)]


def laplacian(n, edges):
    L = [[0.0] * n for _ in range(n)]
    for u, v in edges:
        L[u][u] += 1; L[v][v] += 1
        L[u][v] -= 1; L[v][u] -= 1
    return L


def dev_eig(n, edges):
    w = jacobi_eigenvalues(laplacian(n, edges))
    mean = sum(w) / n
    return (sum((x - mean) ** 2 for x in w) / n) ** 0.5


def dev_formula(n, edges):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    m = len(edges)
    var = (sum(d * d for d in deg) + 2 * m) / n - (2 * m / n) ** 2
    return max(var, 0.0) ** 0.5


def check1():
    suite = []
    for n in range(2, 9):
        suite.append((n, [(i, i + 1) for i in range(n - 1)]))          # path
        suite.append((n, [(0, i) for i in range(1, n)]))               # star
        suite.append((n, [(i, j) for i in range(n) for j in range(i + 1, n)]))  # K_n
    suite.append((7, [(i, j) for i in range(3) for j in range(3, 7)]))  # K_{3,4}
    rng = random.Random(7)
    for _ in range(30):
        n = rng.randint(4, 9)
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if rng.random() < 0.5]
        suite.append((n, edges))
    for n, edges in suite:
        d1, d2 = dev_eig(n, edges), dev_formula(n, edges)
        assert abs(d1 - d2) < 1e-8, (n, edges, d1, d2)
    print(f"check1: degree-only identity == Jacobi eigensolve on "
          f"{len(suite)} graphs OK")


def check2():
    for k in range(3, 200):
        n = 2 * k - 2
        m = k * (k - 1) // 2
        S = k * (k - 1) ** 2                       # sum of squared degrees
        var = Fraction(S + 2 * m, n) - Fraction(2 * m, n) ** 2
        assert var == Fraction(k * k, 4), (k, var)  # dev = k/2 exactly
        # R: every edge joins two degree-(k-1) vertices -> R = m/(k-1) = k/2
        assert Fraction(m, k - 1) == Fraction(k, 2)
    print("check2: equality family K_k U (k-2)K_1 has dev = R = k/2 "
          "exactly for k = 3..199 OK")


if __name__ == "__main__":
    check1()
    check2()
    print("PASS")
