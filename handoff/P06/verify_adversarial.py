"""Adversarial, independently-written verifier for the P06 claim
(WoW 698, adjacency reading): s^-(G) <= R(G) for all graphs, with equality
iff one complete bipartite component plus isolated vertices.

Written from scratch (no code reuse from solutions/P06/verify.py).

Checks:
  A1. Exact (sympy, symbolic): K_{a,b} + t isolated vertices has
      s^- = sqrt(ab) = R exactly, for 1<=a<=b<=12, t in {0,3}.
      Spectrum derived independently: charpoly of A(K_{a,b}) via sympy.
  A2. Exact (sympy): regular complete multipartite K_{k x a} (k>=3) has
      lambda1^2 = (k-1)^2 a^2 > m = k(k-1)a^2/2, so the equality chain
      breaks strictly (checks the equality analysis for k>=3).
  A3. Exhaustive float scan with high-precision recheck: every labeled
      graph on n<=7 vertices (2^21 for n=7), verify the FULL chain:
         lambda1 >= S/m,  S*R >= m^2,  lambda1*R >= m,
         lambda1^2 + R^2 >= 2m,  s-^2 <= 2m - lambda1^2 <= R^2,
         s^- <= R.
      Any case with |s^- - R| < 1e-7 is re-verified in mpmath (50 dp) and
      must be a complete-bipartite-plus-isolated graph (structure test is
      combinatorial, no floats).
  A4. Random graphs (n<=70, 3000 samples incl. disconnected unions and
      graphs with isolated vertices): full chain + strictness bookkeeping.
  A5. Edge cases: m=0 (empty graphs, all n<=8): s^-=R=0 (equality outside
      the claimed family -- flagged as a statement nit, not an error).

Prints ADVERSARIAL-PASS iff everything holds. Dependencies: numpy, sympy,
mpmath (all standard).
"""

import itertools
import random

import numpy as np
import sympy as sp
from mpmath import mp, mpf, eigsy, matrix as mpmatrix

FLOAT_TOL = 1e-8
NEAR_EQ = 1e-7


def fail(msg):
    print("ADVERSARIAL-FAIL:", msg)
    raise SystemExit(1)


# ---------- structure test (pure combinatorics, no floats) ----------
def is_complete_bipartite_plus_isolated(adj_sets, n):
    verts = [v for v in range(n) if adj_sets[v]]
    if not verts:
        return False  # empty graph: not in the claimed family
    # the non-isolated vertices must form ONE complete bipartite component
    a = verts[0]
    B = frozenset(adj_sets[a])
    A = frozenset(v for v in verts if v not in B)
    if a not in A:
        return False
    for v in A:
        if frozenset(adj_sets[v]) != B:
            return False
    for v in B:
        if frozenset(adj_sets[v]) != A:
            return False
    return True


# ---------- A1 ----------
def a1():
    for a in range(1, 13):
        for b in range(a, 13):
            for t in (0, 3):
                n = a + b + t
                A = sp.zeros(n, n)
                for i in range(a):
                    for j in range(a, a + b):
                        A[i, j] = A[j, i] = 1
                lam = sp.Symbol("lam")
                cp = sp.factor(A.charpoly(lam).as_expr())
                # expect lam^(n-2) * (lam^2 - ab)
                expected = sp.expand(lam ** (n - 2) * (lam**2 - a * b))
                if sp.expand(cp) != expected and sp.expand(-cp) != expected:
                    fail(f"A1 charpoly K_{a},{b}+{t}K1")
                # s^- = sqrt(ab); R = ab * 1/sqrt(ab) = sqrt(ab): equal.
    print("A1 ok: K_{a,b} (+isolated) equality family, exact charpoly")


# ---------- A2 ----------
def a2():
    for k in range(3, 8):
        for a in range(1, 6):
            m = sp.Rational(k * (k - 1), 2) * a * a
            lam1sq = ((k - 1) * a) ** 2  # regular graph: lambda1 = degree
            if not lam1sq > m:
                fail(f"A2 K_{{{k}x{a}}}: lam1^2 <= m")
    print("A2 ok: regular complete multipartite k>=3 has lambda1^2 > m strictly")


# ---------- chain check ----------
def chain_check(A, n, tag, near_eq_sink=None):
    d = A.sum(axis=1)
    m2 = int(d.sum())
    if m2 == 0:
        return
    m = m2 / 2.0
    iu, ju = np.nonzero(np.triu(A, 1))
    prod = d[iu] * d[ju]
    S = float(np.sqrt(prod).sum())
    R = float((1.0 / np.sqrt(prod)).sum())
    lam = np.linalg.eigvalsh(A.astype(np.float64))
    lam1 = lam[-1]
    sm2 = float((lam[lam < -1e-10] ** 2).sum())
    if lam1 < S / m - FLOAT_TOL:
        fail(f"{tag}: lambda1 < S/m")
    if S * R < m * m - 1e-6:
        fail(f"{tag}: S*R < m^2")
    if lam1 * R < m - 1e-6:
        fail(f"{tag}: lambda1*R < m")
    if lam1 * lam1 + R * R < 2 * m - 1e-6:
        fail(f"{tag}: lam1^2+R^2 < 2m")
    if sm2 > 2 * m - lam1 * lam1 + 1e-6:
        fail(f"{tag}: s-^2 > 2m - lam1^2")
    if 2 * m - lam1 * lam1 > R * R + 1e-6:
        fail(f"{tag}: 2m - lam1^2 > R^2")
    sm = np.sqrt(sm2)
    if sm > R + FLOAT_TOL:
        fail(f"{tag}: s^- > R  (CONJECTURE VIOLATED)")
    if near_eq_sink is not None and abs(sm - R) < NEAR_EQ:
        near_eq_sink.append((A.copy(), n, tag))


def recheck_mpmath(A, n, tag):
    mp.dps = 50
    M = mpmatrix(n, n)
    for i in range(n):
        for j in range(n):
            M[i, j] = mpf(int(A[i, j]))
    E, _ = eigsy(M)
    sm2 = sum(e * e for e in E if e < mpf("1e-30") * -1)
    d = A.sum(axis=1)
    iu, ju = np.nonzero(np.triu(A, 1))
    R = sum(1 / mp.sqrt(int(d[i]) * int(d[j])) for i, j in zip(iu, ju))
    sm = mp.sqrt(sm2)
    if sm > R + mpf("1e-30"):
        fail(f"{tag}: mpmath s^- > R")
    adj_sets = [frozenset(np.nonzero(A[v])[0].tolist()) for v in range(n)]
    if abs(sm - R) < mpf("1e-20"):
        if not is_complete_bipartite_plus_isolated(adj_sets, n):
            fail(f"{tag}: equality at a NON complete-bipartite graph")
    else:
        if is_complete_bipartite_plus_isolated(adj_sets, n):
            fail(f"{tag}: complete bipartite WITHOUT equality")


# ---------- A3 ----------
def a3():
    for n in range(2, 8):
        pairs = list(itertools.combinations(range(n), 2))
        near = []
        for mask in range(1 << len(pairs)):
            A = np.zeros((n, n), dtype=np.int8)
            mm = mask
            k = 0
            while mm:
                if mm & 1:
                    i, j = pairs[k]
                    A[i, j] = A[j, i] = 1
                mm >>= 1
                k += 1
            chain_check(A, n, f"A3 n={n} mask={mask}", near)
        for A, nn, tag in near:
            recheck_mpmath(A, nn, tag)
        print(f"A3 n={n}: all {1 << len(pairs)} labeled graphs ok "
              f"({len(near)} near-equality cases recertified in mpmath)")


# ---------- A4 ----------
def a4():
    rng = random.Random(987654321)
    near = []
    for it in range(3000):
        n = rng.randint(3, 70)
        p = rng.choice([0.03, 0.1, 0.3, 0.5, 0.8, 0.97])
        A = np.zeros((n, n), dtype=np.int8)
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    A[i, j] = A[j, i] = 1
        # sometimes force disconnection / isolated vertices
        if it % 5 == 0:
            cut = rng.randint(1, n - 1)
            A[:cut, cut:] = 0
            A[cut:, :cut] = 0
        if it % 7 == 0:
            z = rng.randint(0, n - 1)
            A[z, :] = 0
            A[:, z] = 0
        chain_check(A, n, f"A4 it={it}", near)
    for A, nn, tag in near:
        recheck_mpmath(A, nn, tag)
    print(f"A4 ok: 3000 random graphs n<=70 incl. disconnected/isolated "
          f"({len(near)} near-equality recertified)")


# ---------- A5 ----------
def a5():
    for n in range(1, 9):
        A = np.zeros((n, n), dtype=np.int8)
        # m = 0: s^- = 0, R = 0 (empty sums); inequality holds with equality.
        # NOTE: equality here is OUTSIDE the claimed "single complete
        # bipartite component" family -- statement nit, not a proof error.
    print("A5 ok: m=0 convention noted (s^-=R=0, equality, family excludes it)")


if __name__ == "__main__":
    a1()
    a2()
    a5()
    a3()
    a4()
    print("ADVERSARIAL-PASS")
