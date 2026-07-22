#!/usr/bin/env python3
"""Independent verifier for counterexamples to Graffiti conjectures 143 AND 154 (WoW list):

    "143. variance of positive eigenvalues < size / average distance."
    "154. deviation of eigenvalues < n / average distance."
    (size = number of edges m; average distance = mean of inter-vertex distances)

Since the adjacency eigenvalues have mean 0 and sum of squares 2m, the deviation of
the eigenvalues is exactly sqrt(2m/n), so conjecture 154 is equivalent to
    2 * m * mu(D)^2 <= n^3,
which this script checks in EXACT integer arithmetic (no eigensolve at all).

For conjecture 143, a witness graph refutes the conjecture if
    Var(positive adjacency eigenvalues) * mu(D) > m
under BOTH conventions for the average distance mu(D):
  - 'pair': mean over the n(n-1) ordered pairs of distinct vertices (classical),
  - 'rc'  : mean over all n^2 entries of the distance matrix including the diagonal
            (the convention in Roucairol-Cazenave's refutationGBR search code).
Since mu_pair > mu_rc, violating the 'rc' form is the stronger statement; this
script requires violation of both.

Witnesses are dumbbells D(a, ell, b): a clique K_a and a clique K_b joined by a
path with ell internal vertices (attached to one vertex of each clique).

Rigor notes:
  * m, the distance matrix (BFS), mu (Fraction), and the nullity of A (exact
    Gaussian elimination over Q) are computed exactly in integer/rational arithmetic.
  * Eigenvalues come from numpy's symmetric eigensolver (LAPACK), which is
    backward stable: computed eigenvalues are the exact eigenvalues of A+E with
    ||E||_2 <= c*eps*||A||_2. We use the very generous certified perturbation
    bound EPS_EIG = 1e-11 * n * max|lambda|, cross-check the spectrum against the
    exact traces of A^k (k=1..4, integer arithmetic), match the count of (near-)zero
    eigenvalues against the exact nullity, and require every nonzero eigenvalue to
    be at least 1e-4 in absolute value (>> EPS_EIG), so the count p of positive
    eigenvalues is certified. The variance is then lower-bounded by adversarially
    perturbing every positive eigenvalue by EPS_EIG.
  * The final comparison uses the certified lower bound on Var against the exact
    rational m/mu, and demands a strict violation.

Dependencies: python3 + numpy only.
"""
import sys
from collections import deque
from fractions import Fraction

import numpy as np

# (a, ell, b): dumbbell witnesses. First is the smallest found violating both
# conventions (n=39); the rest have larger margins.
WITNESSES_143 = [
    (7, 12, 20),    # n = 39, margin ~0.2% (rc), ~2.9% (pair)
    (25, 18, 17),   # n = 60, margin ~23%
    (36, 28, 36),   # n = 100, margin ~47%
]

WITNESSES_154 = [
    (2, 68, 50),    # n = 120: minimal found violating both conventions
    (2, 114, 84),   # n = 200: margin ~60%
]


def dumbbell_edges(a, ell, b):
    n = a + ell + b
    edges = []
    for i in range(a):
        for j in range(i + 1, a):
            edges.append((i, j))
    for i in range(a + ell, n):
        for j in range(i + 1, n):
            edges.append((i, j))
    chain = [0] + list(range(a, a + ell)) + [a + ell]
    for u, v in zip(chain, chain[1:]):
        edges.append((u, v))
    return n, edges


def bfs_distance_sum(n, adj):
    total = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        seen = 1
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    seen += 1
                    q.append(v)
        assert seen == n, "graph is not connected"
        total += sum(dist)
    return total


def exact_nullity(A_int):
    """Rank-nullity of the integer matrix over Q by exact Gaussian elimination."""
    n = len(A_int)
    M = [[Fraction(x) for x in row] for row in A_int]
    rank = 0
    row = 0
    for col in range(n):
        piv = next((r for r in range(row, n) if M[r][col] != 0), None)
        if piv is None:
            continue
        M[row], M[piv] = M[piv], M[row]
        inv = 1 / M[row][col]
        M[row] = [x * inv for x in M[row]]
        for r in range(n):
            if r != row and M[r][col] != 0:
                f = M[r][col]
                M[r] = [x - f * y for x, y in zip(M[r], M[row])]
        rank += 1
        row += 1
    return n - rank


def check_witness(a, ell, b):
    n, edges = dumbbell_edges(a, ell, b)
    m = len(edges)
    adj = [[] for _ in range(n)]
    A_int = [[0] * n for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
        A_int[u][v] = A_int[v][u] = 1
    assert 2 * m == sum(sum(r) for r in A_int)

    dsum = bfs_distance_sum(n, adj)  # exact integer
    mu_pair = Fraction(dsum, n * (n - 1))
    mu_rc = Fraction(dsum, n * n)

    A = np.array(A_int, dtype=float)
    w = np.linalg.eigvalsh(A)

    # certified perturbation bound: LAPACK dsyevd is backward stable with
    # |w_i - lambda_i| <= c*eps_machine*n*||A||_2, eps_machine ~ 2.2e-16;
    # 1e-11 leaves a safety factor of several thousand over realistic c.
    eps_eig = 1e-11 * n * float(np.max(np.abs(w)))

    # cross-check spectrum against exact integer traces of A^k, k=1..4
    Ak = np.eye(n, dtype=object)
    A_obj = np.array(A_int, dtype=object)
    for k in range(1, 5):
        Ak = Ak @ A_obj
        tr_exact = int(np.trace(Ak))
        tr_num = float(np.sum(w ** k))
        assert abs(tr_num - tr_exact) <= 1e-6 * max(1.0, abs(tr_exact)), (
            f"trace check failed k={k}: {tr_num} vs {tr_exact}")

    # certify the positive-eigenvalue count using the exact nullity
    z = exact_nullity(A_int)
    aw = np.sort(np.abs(w))
    assert (aw[:z] < 1e-6).all(), "numerical zeros do not match exact nullity"
    assert (aw[z:] > 1e-4).all(), "nonzero eigenvalue too close to 0 to classify"
    assert 1e-4 > 100 * eps_eig, "perturbation bound too large for classification"
    pos = w[w > 1e-4]
    p = len(pos)

    mean = float(np.mean(pos))
    var = float(np.mean((pos - mean) ** 2))
    # adversarial lower bound on the variance under +-eps_eig perturbation
    maxdev = float(np.max(np.abs(pos - mean)))
    var_lo = var - (2 * eps_eig * maxdev + eps_eig ** 2)

    ok = True
    print(f"D({a},{ell},{b}): n={n} m={m} p={p} var>={var_lo:.6f}")
    for name, mu in [("rc  (n^2 mean)", mu_rc), ("pair (n(n-1) mean)", mu_pair)]:
        rhs = Fraction(m) / mu
        violated = var_lo > float(rhs) + 1e-12
        ratio = var_lo / float(rhs)
        print(f"  mu_{name} = {float(mu):.6f}  m/mu = {float(rhs):.6f}  "
              f"Var/(m/mu) = {ratio:.6f}  -> {'VIOLATED' if violated else 'not violated'}")
        ok = ok and violated
    return ok


def check_witness_154(a, ell, b):
    """Exact integer check of 2*m*dsum^2 > n^3 * D^2 for D = n^2 and n(n-1)."""
    n, edges = dumbbell_edges(a, ell, b)
    m = len(edges)
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    dsum = bfs_distance_sum(n, adj)
    # sanity: deviation of eigenvalues really is sqrt(2m/n)
    A = np.zeros((n, n))
    for u, v in edges:
        A[u, v] = A[v, u] = 1
    w = np.linalg.eigvalsh(A)
    assert abs(float(np.std(w)) - (2 * m / n) ** 0.5) < 1e-9
    ok = True
    print(f"D({a},{ell},{b}): n={n} m={m} sum_dist={dsum}")
    for name, D in [("rc  (n^2 mean)", n * n), ("pair (n(n-1) mean)", n * (n - 1))]:
        lhs = 2 * m * dsum * dsum          # exact int
        rhs = n ** 3 * D * D               # exact int
        violated = lhs > rhs
        print(f"  mu_{name}: 2*m*mu^2 / n^3 = {lhs / rhs:.6f}  "
              f"-> {'VIOLATED' if violated else 'not violated'}")
        ok = ok and violated
    return ok


def main():
    all_ok = True
    print("=== Conjecture 143: Var(positive eigenvalues) < m / mu(D) ===")
    for a, ell, b in WITNESSES_143:
        all_ok = check_witness(a, ell, b) and all_ok
        print()
    print("=== Conjecture 154: dev(eigenvalues) < n / mu(D), i.e. 2*m*mu^2 <= n^3 ===")
    for a, ell, b in WITNESSES_154:
        all_ok = check_witness_154(a, ell, b) and all_ok
        print()
    if all_ok:
        print("PASS: all witnesses strictly violate Graffiti conjectures 143 and 154 "
              "under both average-distance conventions.")
    else:
        print("FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
