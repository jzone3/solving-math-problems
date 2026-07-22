"""Independent cross-check of the conj-143 witnesses, written differently from
solutions/P07/verify.py:
  - exact integer characteristic polynomial via Faddeev-LeVerrier (Fractions),
  - all roots at 50-digit precision with mpmath.polyroots,
  - variance of positive roots vs exact m/mu.
"""
from fractions import Fraction
from collections import deque
import mpmath as mp

mp.mp.dps = 50

WITNESSES = [(7, 12, 20), (25, 18, 17), (36, 28, 36)]


def dumbbell_adj(a, ell, b):
    n = a + ell + b
    A = [[0] * n for _ in range(n)]
    for i in range(a):
        for j in range(a):
            if i != j:
                A[i][j] = 1
    for i in range(a + ell, n):
        for j in range(a + ell, n):
            if i != j:
                A[i][j] = 1
    chain = [0] + list(range(a, a + ell)) + [a + ell]
    for u, v in zip(chain, chain[1:]):
        A[u][v] = A[v][u] = 1
    return n, A


def charpoly(A):
    """Faddeev-LeVerrier: coefficients of det(xI - A), exact Fractions."""
    n = len(A)
    M = [[Fraction(0)] * n for _ in range(n)]
    c = [Fraction(1)]
    for k in range(1, n + 1):
        # M = A*M + c[-1]*I
        AM = [[sum(Fraction(A[i][t]) * M[t][j] for t in range(n)) for j in range(n)]
              for i in range(n)]
        for i in range(n):
            AM[i][i] += c[-1]
        M = AM
        tr = sum(Fraction(A[i][t]) * M[t][i] for i in range(n) for t in range(n))
        c.append(-tr / k)
    return c  # c[0]=1 ... c[n], poly = sum c[k] x^{n-k}


for a, ell, b in WITNESSES:
    n, A = dumbbell_adj(a, ell, b)
    m = sum(sum(r) for r in A) // 2
    # BFS distance sum
    adj = [[j for j in range(n) if A[i][j]] for i in range(n)]
    dsum = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    q.append(v)
        assert all(d >= 0 for d in dist)
        dsum += sum(dist)
    mu_rc = Fraction(dsum, n * n)
    mu_pair = Fraction(dsum, n * (n - 1))

    c = charpoly(A)
    assert all(x.denominator == 1 for x in c)

    # exact deflation of repeated roots at -1 (cliques) and 0, keeps polyroots stable
    def divide_out(coeffs, root):
        # synthetic division by (x - root); returns (quotient, remainder)
        out = [coeffs[0]]
        for k in coeffs[1:]:
            out.append(k + root * out[-1])
        return out[:-1], out[-1]

    n_minus1 = 0
    n_zero = 0
    while True:
        q, r = divide_out(c, Fraction(-1))
        if r != 0:
            break
        c = q
        n_minus1 += 1
    while c[-1] == 0:
        c = c[:-1]
        n_zero += 1
    croots = mp.polyroots([mp.mpf(int(x)) for x in c], maxsteps=5000, extraprec=1000)
    assert all(abs(mp.im(r)) < mp.mpf('1e-30') for r in croots)
    roots = [mp.re(r) for r in croots]
    pos = [r for r in roots if r > mp.mpf('1e-20')]
    zero = [r for r in roots if abs(r) <= mp.mpf('1e-20')] + [mp.mpf(0)] * n_zero
    p = len(pos)
    mean = sum(pos) / p
    var = sum((x - mean) ** 2 for x in pos) / p
    r_rc = var * mp.mpf(mu_rc.numerator) / mu_rc.denominator / m
    r_pair = var * mp.mpf(mu_pair.numerator) / mu_pair.denominator / m
    print(f"D({a},{ell},{b}): n={n} m={m} p={p} zeros={len(zero)} var={mp.nstr(var, 20)}")
    print(f"  Var*mu_rc/m   = {mp.nstr(r_rc, 20)}  {'VIOLATED' if r_rc > 1 else 'no'}")
    print(f"  Var*mu_pair/m = {mp.nstr(r_pair, 20)}  {'VIOLATED' if r_pair > 1 else 'no'}")
