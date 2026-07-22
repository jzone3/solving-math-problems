#!/usr/bin/env python3
"""Independent adversarial verifier for the P08 claim:
   dev(D) <= diam/2 <= floor((diam+1)/2) <= min(n+, n-)  for all finite connected simple graphs.

Written from scratch: own graph6 parser, own BFS, exact rational variance,
exact integer inertia (Faddeev-LeVerrier char poly + Descartes' rule, valid since
adjacency matrices are real symmetric => all roots real).
Does NOT import networkx or reuse anything from solutions/P08/verify.py.
"""
import sys, random, itertools
from fractions import Fraction
import numpy as np

# ---------- graph6 ----------
def parse_g6(line):
    line = line.strip()
    data = [ord(c) - 63 for c in line]
    n = data[0]
    assert 0 <= n <= 62
    bits = []
    for d in data[1:]:
        for k in range(5, -1, -1):
            bits.append((d >> k) & 1)
    A = [[0]*n for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i][j] = A[j][i] = 1
            idx += 1
    return A

# ---------- BFS distance matrix ----------
def dist_matrix(A):
    n = len(A)
    nbrs = [[j for j in range(n) if A[i][j]] for i in range(n)]
    D = [[-1]*n for _ in range(n)]
    for s in range(n):
        D[s][s] = 0
        q = [s]
        while q:
            nq = []
            for u in q:
                for v in nbrs[u]:
                    if D[s][v] < 0:
                        D[s][v] = D[s][u] + 1
                        nq.append(v)
            q = nq
    return D  # -1 marks disconnected

# ---------- exact variance conventions ----------
def variances(D):
    n = len(D)
    flat = [D[i][j] for i in range(n) for j in range(n)]           # n^2, incl diagonal
    off  = [D[i][j] for i in range(n) for j in range(n) if i != j] # n(n-1)
    pairs = [D[i][j] for i in range(n) for j in range(i+1, n)]     # n(n-1)/2
    out = {}
    for name, xs in (('n2', flat), ('offdiag', off), ('pairs', pairs)):
        N = len(xs)
        if N == 0:
            out[name+'_pop'] = Fraction(0); out[name+'_samp'] = Fraction(0)
            out[name+'_mad'] = Fraction(0)
            continue
        s = sum(xs); ss = sum(x*x for x in xs)
        mu = Fraction(s, N)
        var_pop = Fraction(ss, N) - mu*mu
        out[name+'_pop'] = var_pop
        out[name+'_samp'] = var_pop * Fraction(N, N-1) if N > 1 else Fraction(0)
        out[name+'_mad'] = Fraction(sum(abs(Fraction(x) - mu) for x in xs), N)
    return out

# ---------- exact inertia ----------
def charpoly_int(A):
    """Faddeev-LeVerrier: integer coefficients of det(xI - A), leading first."""
    n = len(A)
    M = [[Fraction(0)]*n for _ in range(n)]
    c = [Fraction(1)] + [Fraction(0)]*n
    Af = [[Fraction(x) for x in row] for row in A]
    for k in range(1, n+1):
        # M = A*M + c[k-1]*I
        AM = [[sum(Af[i][l]*M[l][j] for l in range(n)) for j in range(n)] for i in range(n)]
        for i in range(n):
            AM[i][i] += c[k-1]
        M = AM
        tr = sum((sum(Af[i][l]*M[l][i] for l in range(n))) for i in range(n))
        c[k] = -tr / k
    coeffs = [int(x) for x in c]
    assert all(x == int(x) for x in c)
    return coeffs  # p(x) = sum coeffs[i] * x^(n-i)

def sign_variations(seq):
    v = 0; prev = 0
    for x in seq:
        if x == 0: continue
        s = 1 if x > 0 else -1
        if prev != 0 and s != prev: v += 1
        prev = s
    return v

def exact_inertia(A):
    """(n+, n0, n-) exactly, via Descartes (valid: all roots real)."""
    n = len(A)
    p = charpoly_int(A)
    # strip trailing zeros -> multiplicity of root 0
    t = 0
    while p[-1] == 0 and len(p) > 1:
        p = p[:-1]; t += 1
    npos = sign_variations(p)
    pneg = [c if (len(p)-1-i) % 2 == 0 else -c for i, c in enumerate(p)]
    nneg = sign_variations(pneg)
    assert npos + nneg + t == n
    return npos, t, nneg

def float_inertia(A, tol=1e-8):
    ev = np.linalg.eigvalsh(np.array(A, dtype=float))
    return int((ev > tol).sum()), int((np.abs(ev) <= tol).sum()), int((ev < -tol).sum())

# ---------- induced geodesic check ----------
def geodesic_induced_check(A, D):
    """Find a diametral shortest path, verify it is induced."""
    n = len(A)
    d = max(max(row) for row in D)
    # pick u,v with D[u][v]=d
    u = v = 0
    for i in range(n):
        for j in range(n):
            if D[i][j] == d: u, v = i, j
    # build one shortest path greedily
    path = [u]; cur = u
    while cur != v:
        for w in range(n):
            if A[cur][w] and D[w][v] == D[cur][v] - 1:
                path.append(w); cur = w; break
    assert len(path) == d + 1
    for a in range(len(path)):
        for b in range(a+2, len(path)):
            if A[path[a]][path[b]]:
                return False, d
    return True, d

# ---------- path inertia ----------
def path_adj(k):
    A = [[0]*k for _ in range(k)]
    for i in range(k-1):
        A[i][i+1] = A[i+1][i] = 1
    return A

def check_paths():
    # exact for k<=40, float for k up to 2000
    for k in range(1, 41):
        npos, nz, nneg = exact_inertia(path_adj(k))
        assert npos == nneg == k//2, (k, npos, nneg)
        assert nz == (1 if k % 2 == 1 else 0), (k, nz)
    for k in list(range(41, 200)) + [500, 1000, 1500, 2000]:
        ev = 2*np.cos(np.pi*np.arange(1, k+1)/(k+1))
        A = np.zeros((k, k)); idx = np.arange(k-1)
        A[idx, idx+1] = 1; A[idx+1, idx] = 1
        ev2 = np.linalg.eigvalsh(A)
        assert np.allclose(np.sort(ev), ev2, atol=1e-9)
        npos = int((ev2 > 1e-9).sum()); nneg = int((ev2 < -1e-9).sum())
        assert npos == nneg == k//2, (k, npos, nneg)
    print("Path inertia n+=n-=floor(k/2): PASS (exact k<=40, float k<=2000)")

# ---------- main sweeps ----------
def check_graph(A, exact=True):
    D = dist_matrix(A)
    if any(x < 0 for row in D for x in row):
        return None  # disconnected
    n = len(A)
    d = max(max(row) for row in D)
    ind_ok, _ = geodesic_induced_check(A, D)
    assert ind_ok, "geodesic not induced!"
    V = variances(D)
    if exact:
        npos, nz, nneg = exact_inertia(A)
        fi = float_inertia(A)
        assert (npos, nz, nneg) == fi, ("inertia mismatch", A, (npos, nz, nneg), fi)
    else:
        npos, nz, nneg = float_inertia(A)
    m = min(npos, nneg)
    # (a) Popoviciu: var <= d^2/4 for every convention (pop); sample too (track)
    assert V['n2_pop'] * 4 <= Fraction(d*d), ("popoviciu n2", A)
    assert V['offdiag_pop'] * 4 <= Fraction(d*d)
    assert V['pairs_pop'] * 4 <= Fraction(d*d)
    assert V['n2_mad'] * 2 <= Fraction(d)  # MAD <= std <= d/2
    # (b) integer chain
    assert 2*((d+1)//2) >= d
    assert m >= (d+1)//2 or n == 1, ("interlacing chain", A, m, d)
    # (c) end-to-end, every convention incl. SAMPLE std
    for key in ('n2_pop', 'offdiag_pop', 'pairs_pop', 'n2_samp', 'offdiag_samp',
                'pairs_samp'):
        assert V[key] <= Fraction(m*m) or (m == 0 and V[key] == 0), (key, A, V[key], m)
    for key in ('n2_mad', 'offdiag_mad', 'pairs_mad'):
        assert V[key] <= Fraction(m) or (m == 0 and V[key] == 0), (key, A)
    # margin (float) for tightness report, n2_pop convention
    import math
    return float(m - math.sqrt(V['n2_pop']))

def sweep_all_labeled(nmax=6):
    total = 0; worst = 1e9; worst_desc = None
    for n in range(1, nmax+1):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            A = [[0]*n for _ in range(n)]
            for b, (i, j) in enumerate(pairs):
                if mask >> b & 1:
                    A[i][j] = A[j][i] = 1
            r = check_graph(A, exact=(n <= 5))
            if r is not None:
                total += 1
                if r < worst: worst, worst_desc = r, (n, mask)
        print(f"  n={n} done, cumulative connected labeled graphs checked: {total}")
    print(f"Exhaustive labeled n<={nmax}: PASS, {total} graphs, "
          f"min margin min(n+,n-)-dev = {worst:.4f} at {worst_desc}")

def sweep_geng(n):
    import subprocess
    out = subprocess.run(["nauty-geng", "-c", str(n)], capture_output=True, text=True)
    worst = 1e9; cnt = 0
    for line in out.stdout.splitlines():
        A = parse_g6(line)
        r = check_graph(A, exact=True)
        assert r is not None
        cnt += 1
        worst = min(worst, r)
    print(f"geng -c {n}: PASS, {cnt} graphs (exact inertia), min margin = {worst:.4f}")

def random_graphs(trials=400, nmax=60):
    rng = random.Random(12345)
    worst = 1e9
    for t in range(trials):
        n = rng.randint(2, nmax)
        if t % 3 == 0:  # random tree via Prufer-like attachment
            A = [[0]*n for _ in range(n)]
            for v in range(1, n):
                u = rng.randrange(v)
                A[u][v] = A[v][u] = 1
        else:
            p = rng.uniform(0.05, 0.7)
            A = [[0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1, n):
                    if rng.random() < p:
                        A[i][j] = A[j][i] = 1
            D = dist_matrix(A)
            if any(x < 0 for row in D for x in row):
                continue
        r = check_graph(A, exact=(n <= 12))
        if r is None: continue
        worst = min(worst, r)
    print(f"Random graphs/trees ({trials} trials, n<= {nmax}): PASS, min margin = {worst:.4f}")

if __name__ == "__main__":
    check_paths()
    sweep_all_labeled(6)
    sweep_geng(7)
    random_graphs()
    print("ALL CHECKS PASS")
