#!/usr/bin/env python3
"""Independent verifier for P08 (Graffiti conjectures 39 & 40).

Result being verified: for every connected graph G,
    dev(D) <= min(n+(G), n-(G)),
proved via the chain
    dev(D) <= diam/2   (Popoviciu, entries of D lie in [0, diam])
    diam/2 <= floor((diam+1)/2) = n+-(P_{diam+1}) <= n+-(G)   (Cauchy interlacing
              applied to the induced path formed by any diameter geodesic).

This script uses only numpy + stdlib. It machine-checks:
  1. Path inertia lemma: n+(P_k) = n-(P_k) = floor(k/2), numerically for k<=400.
  2. Interlacing inertia monotonicity on random graphs vs random induced subgraphs.
  3. Geodesic-is-induced-path on random graphs.
  4. The full inequality chain (and the conjectures themselves) on:
       - ALL labeled connected graphs with n <= 6 (exhaustive, 26704 graphs),
       - spectral-design families (complete multipartite cores + pendant tails,
         double brooms, spiders, paths) up to n = 1000,
       - random G(n,p) graphs and random trees up to n = 500.
Prints PASS iff every check succeeds.
"""
import itertools
import random
import sys
import numpy as np

TOL = 1e-8
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
        print("FAIL:", msg)


# ---------- graph utilities (self-contained) ----------

def bfs_dist(A):
    n = len(A)
    nbrs = [np.nonzero(A[i])[0] for i in range(n)]
    D = np.full((n, n), -1, dtype=int)
    for s in range(n):
        D[s, s] = 0
        q = [s]
        while q:
            nq = []
            for u in q:
                for v in nbrs[u]:
                    if D[s, v] < 0:
                        D[s, v] = D[s, u] + 1
                        nq.append(v)
            q = nq
    return D


def dev_pop(D):
    x = D.reshape(-1).astype(float)
    return float(np.sqrt(np.mean((x - x.mean()) ** 2)))


def inertia(A):
    ev = np.linalg.eigvalsh(A)
    return int(np.sum(ev > TOL)), int(np.sum(ev < -TOL))


def full_check(A, tag):
    """Check the conjectures and the proof chain on one connected graph."""
    D = bfs_dist(A)
    check(D.min() >= 0, f"{tag}: disconnected")
    d = int(D.max())
    dev = dev_pop(D)
    npos, nneg = inertia(A)
    check(dev <= npos + 1e-9, f"{tag}: conj39 violated dev={dev} n+={npos}")
    check(dev <= nneg + 1e-9, f"{tag}: conj40 violated dev={dev} n-={nneg}")
    check(dev <= d / 2 + 1e-9, f"{tag}: Popoviciu step dev={dev} d={d}")
    check(npos >= (d + 1) // 2, f"{tag}: interlacing step n+={npos} d={d}")
    check(nneg >= (d + 1) // 2, f"{tag}: interlacing step n-={nneg} d={d}")


# ---------- 1. path inertia lemma ----------
for k in list(range(1, 60)) + [101, 250, 400]:
    A = np.zeros((k, k))
    for i in range(k - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    npos, nneg = inertia(A)
    check(npos == k // 2 and nneg == k // 2,
          f"path lemma k={k}: n+={npos} n-={nneg} expected {k//2}")
print("1. path inertia lemma checked (k<=400)")

# ---------- 2. interlacing inertia monotonicity, random ----------
rng = random.Random(12345)
for trial in range(300):
    n = rng.randrange(4, 30)
    p = rng.uniform(0.1, 0.9)
    A = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                A[i, j] = A[j, i] = 1
    k = rng.randrange(2, n)
    S = rng.sample(range(n), k)
    B = A[np.ix_(S, S)]
    pa, na = inertia(A)
    pb, nb = inertia(B)
    check(pa >= pb and na >= nb,
          f"interlacing trial {trial}: ({pa},{na}) vs sub ({pb},{nb})")
print("2. interlacing inertia monotonicity checked (300 random trials)")

# ---------- 3. geodesic is induced path, random connected graphs ----------
def rand_connected(n, extra, rng):
    A = np.zeros((n, n))
    perm = list(range(n))
    rng.shuffle(perm)
    for i in range(1, n):  # random tree
        j = perm[rng.randrange(i)]
        A[perm[i], j] = A[j, perm[i]] = 1
    for _ in range(extra):
        i, j = rng.randrange(n), rng.randrange(n)
        if i != j:
            A[i, j] = A[j, i] = 1
    return A

for trial in range(200):
    n = rng.randrange(5, 60)
    A = rand_connected(n, rng.randrange(0, 2 * n), rng)
    D = bfs_dist(A)
    d = int(D.max())
    u, v = np.unravel_index(np.argmax(D), D.shape)
    # rebuild one geodesic via BFS parents
    path = [v]
    cur = v
    while cur != u:
        for w in np.nonzero(A[cur])[0]:
            if D[u, w] == D[u, cur] - 1:
                cur = w
                path.append(w)
                break
    check(len(path) == d + 1, f"geodesic length trial {trial}")
    for a in range(len(path)):
        for b in range(a + 2, len(path)):
            check(A[path[a], path[b]] == 0,
                  f"geodesic not induced, trial {trial}")
print("3. geodesic-induced-path checked (200 random trials)")

# ---------- 4a. exhaustive labeled connected graphs n <= 6 ----------
cnt = 0
for n in range(1, 7):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        A = np.zeros((n, n))
        mm = mask
        idx = 0
        while mm:
            if mm & 1:
                i, j = pairs[idx]
                A[i, j] = A[j, i] = 1
            mm >>= 1
            idx += 1
        D = bfs_dist(A)
        if D.min() < 0:
            continue  # not connected
        full_check(A, f"exh n={n} mask={mask}")
        cnt += 1
print(f"4a. exhaustive labeled connected graphs n<=6 checked ({cnt} graphs)")

# ---------- 4b. spectral-design families ----------
def add_tail(A, anchor, length):
    n = len(A)
    B = np.zeros((n + length, n + length))
    B[:n, :n] = A
    prev = anchor
    for t in range(length):
        B[prev, n + t] = B[n + t, prev] = 1
        prev = n + t
    return B

def complete_multipartite(parts):
    n = sum(parts)
    A = np.ones((n, n)) - np.eye(n)
    s = 0
    for p in parts:
        A[s:s + p, s:s + p] = 0
        s += p
    return A

fam = 0
for parts in [[1, 1], [2, 2], [3, 3, 3], [1, 1, 50], [5, 5, 5, 5], [10, 10],
              [1, 2, 3, 4, 5], [20, 20, 20]]:
    for tail in [0, 3, 10, 50, 200]:
        A = complete_multipartite(parts)
        A = add_tail(A, 0, tail)
        full_check(A, f"multipartite {parts} tail {tail}")
        fam += 1
# paths, spiders, double brooms
def path_graph(n):
    A = np.zeros((n, n))
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    return A

for n in [50, 200, 1000]:
    full_check(path_graph(n), f"path {n}")
    fam += 1
for legs, ll in [(3, 30), (10, 20), (50, 5)]:
    A = np.zeros((1, 1))
    for _ in range(legs):
        A = add_tail(A, 0, ll)
    full_check(A, f"spider {legs}x{ll}")
    fam += 1
for pl, a, b in [(40, 10, 10), (80, 30, 1), (20, 50, 50)]:
    A = path_graph(pl)
    for _ in range(a):
        A = add_tail(A, 0, 1)
    for _ in range(b):
        A = add_tail(A, pl - 1, 1)
    full_check(A, f"dbroom {pl},{a},{b}")
    fam += 1
print(f"4b. spectral-design families checked ({fam} graphs, n up to 1000)")

# ---------- 4c. random graphs / trees ----------
rc = 0
for trial in range(150):
    n = rng.randrange(5, 200)
    A = rand_connected(n, rng.randrange(0, 3 * n), rng)
    full_check(A, f"random {trial}")
    rc += 1
for n in [300, 500]:
    A = rand_connected(n, 0, rng)  # random tree
    full_check(A, f"rtree {n}")
    rc += 1
print(f"4c. random connected graphs/trees checked ({rc} graphs)")

if fails:
    print(f"\n{len(fails)} FAILURES")
    sys.exit(1)
print("\nPASS: dev(D) <= min(n+, n-) and every proof step verified on all "
      "tested graphs. Graffiti conjectures 39 and 40 hold on the entire "
      "test corpus, consistent with the proof in PROOF.md.")
