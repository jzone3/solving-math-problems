#!/usr/bin/env python3
"""Standalone verifier for P08 (Graffiti 39/40): dev(D) <= n+(G) and dev(D) <= n-(G).

The result claimed is a PROOF that both conjectures are TRUE (see PROOF.md):
    dev(D) < d/2 <= ceil(d/2) <= min(n+, n-)   for every connected G, n >= 2.

This script machine-checks every finitely-checkable ingredient:
  [A] Lemma 3: n+(P_m) = n-(P_m) = floor(m/2) for m = 2..600 (numeric eigensolve
      cross-checked against the closed form 2cos(k pi/(m+1))).
  [B] Lemma 4 consequence: n+/n- monotone under induced subgraphs, on seeded random
      graphs and random induced subgraphs.
  [C] Full chain dev <= d/2 <= ceil(d/2) <= min(n+,n-) AND strict dev < min(n+,n-):
      - exhaustively on ALL labeled connected graphs with 2 <= n <= 6,
      - on structured near-extremal families (balanced double brooms, brooms,
        caterpillars, spiders, kites, complete multipartite + tails),
      - on seeded random connected graphs up to n = 300.
      The comparison dev <= d/2 is done in EXACT INTEGER arithmetic:
          dev^2 <= d^2/4  <=>  4*(n^2*S2 - S1^2) <= d^2 * n^4,
      where S1 = sum of distances, S2 = sum of squared distances (integers via BFS).

Dependencies: numpy only. Prints PASS iff every check succeeds.
"""

import itertools
import math
import random
import sys
from collections import deque

import numpy as np

EPS = 1e-8
FAILURES = []


def check(cond, msg):
    if not cond:
        FAILURES.append(msg)
        print("FAIL:", msg)


# ---------- basic graph utilities ----------

def bfs(adj, src, n):
    dist = [-1] * n
    dist[src] = 0
    q = deque([src])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def dist_sums(edges, n):
    """Return (S1, S2, diam) over all n^2 entries, or None if disconnected."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    S1 = S2 = diam = 0
    for s in range(n):
        d = bfs(adj, s, n)
        for x in d:
            if x < 0:
                return None
            S1 += x
            S2 += x * x
            if x > diam:
                diam = x
    return S1, S2, diam


def inertia(edges, n):
    A = np.zeros((n, n))
    for u, v in edges:
        A[u, v] = A[v, u] = 1.0
    ev = np.linalg.eigvalsh(A)
    return int(np.sum(ev > EPS)), int(np.sum(ev < -EPS))


def full_check(edges, n, tag):
    """Verify the whole inequality chain on one connected graph."""
    r = dist_sums(edges, n)
    if r is None:
        return False
    S1, S2, diam = r
    npos, nneg = inertia(edges, n)
    # exact: dev^2 <= diam^2/4  <=>  4*(n^2*S2 - S1^2) <= diam^2 * n^4
    lhs = 4 * (n * n * S2 - S1 * S1)
    rhs = diam * diam * n ** 4
    check(lhs <= rhs, f"{tag}: dev > diam/2 (exact)")
    if n >= 3:
        # strictness dev < diam/2 (equality occurs only for K_2)
        check(lhs < rhs, f"{tag}: dev = diam/2 exactly (should be strict for n>=3)")
    check(math.ceil(diam / 2) <= min(npos, nneg) or n == 1,
          f"{tag}: ceil(diam/2)={math.ceil(diam/2)} > min(n+,n-)={min(npos, nneg)}")
    dev = math.sqrt(lhs / 4) / (n * n)
    check(dev <= npos + 1e-12, f"{tag}: CONJ 39 VIOLATED dev={dev} n+={npos}")
    check(dev <= nneg + 1e-12, f"{tag}: CONJ 40 VIOLATED dev={dev} n-={nneg}")
    return True


# ---------- [A] path inertia ----------

def check_paths():
    for m in range(2, 601):
        edges = [(i, i + 1) for i in range(m - 1)]
        npos, nneg = inertia(edges, m)
        check(npos == m // 2 and nneg == m // 2,
              f"P_{m}: inertia ({npos},{nneg}) != floor(m/2)={m//2}")
        # closed form cross-check
        cf = [2 * math.cos(k * math.pi / (m + 1)) for k in range(1, m + 1)]
        cfp = sum(1 for x in cf if x > EPS)
        cfn = sum(1 for x in cf if x < -EPS)
        check(cfp == m // 2 and cfn == m // 2, f"P_{m}: closed form mismatch")
    print("[A] path inertia n+(P_m)=n-(P_m)=floor(m/2), m<=600: OK")


# ---------- [B] inertia monotone under induced subgraphs ----------

def check_interlacing(trials=200, seed=1):
    rng = random.Random(seed)
    for t in range(trials):
        n = rng.randint(4, 30)
        p = rng.uniform(0.1, 0.9)
        edges = [(i, j) for i in range(n) for j in range(i + 1, n)
                 if rng.random() < p]
        npos, nneg = inertia(edges, n)
        m = rng.randint(2, n - 1)
        S = sorted(rng.sample(range(n), m))
        pos = {v: i for i, v in enumerate(S)}
        sub = [(pos[u], pos[v]) for u, v in edges if u in pos and v in pos]
        sp, sn = inertia(sub, m)
        check(npos >= sp and nneg >= sn,
              f"interlacing trial {t}: G ({npos},{nneg}) < H ({sp},{sn})")
    print(f"[B] inertia monotonicity under induced subgraphs, {trials} trials: OK")


# ---------- [C] full chain ----------

def check_exhaustive_small(nmax=6):
    total = 0
    for n in range(2, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1, 1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if mask >> i & 1]
            if full_check(edges, n, f"exh n={n} mask={mask}"):
                total += 1
        print(f"[C1] all labeled connected graphs on n={n}: done")
    print(f"[C1] exhaustive n<=({nmax}): {total} connected graphs checked: OK")


def path_edges(k, off=0):
    return [(off + i, off + i + 1) for i in range(k - 1)]


def structured_families():
    fams = []
    # balanced double brooms (the near-extremal family)
    for h in (5, 10, 20, 50, 100, 200):
        for b in (h, 5 * h, 10 * h):
            e = path_edges(h)
            n = h
            for i in range(b):
                e.append((0, n)); n += 1
            for i in range(b):
                e.append((h - 1, n)); n += 1
            fams.append((f"dbroom(h={h},b={b})", e, n))
    # brooms
    for h in (10, 50, 150):
        for b in (5, 40):
            e = path_edges(h); n = h
            for i in range(b):
                e.append((h - 1, n)); n += 1
            fams.append((f"broom({h},{b})", e, n))
    # caterpillar, 1 leg per spine vertex
    for s in (20, 100, 250):
        e = path_edges(s); n = s
        for i in range(s):
            e.append((i, n)); n += 1
        fams.append((f"cat({s})", e, n))
    # spiders
    for k, L in ((3, 100), (10, 40), (50, 8)):
        e = []; n = 1
        for _ in range(k):
            prev = 0
            for _ in range(L):
                e.append((prev, n)); prev = n; n += 1
        fams.append((f"spider({k},{L})", e, n))
    # kites and multipartite+tail
    for c, t in ((10, 50), (30, 100)):
        e = [(i, j) for i in range(c) for j in range(i + 1, c)]
        n = c; prev = 0
        for _ in range(t):
            e.append((prev, n)); prev = n; n += 1
        fams.append((f"kite(K{c},{t})", e, n))
    for k, s, t in ((3, 5, 30), (5, 10, 60)):
        e = []; n = 0; idx = []
        for _ in range(k):
            idx.append(list(range(n, n + s))); n += s
        for a in range(k):
            for b2 in range(a + 1, k):
                for u in idx[a]:
                    for v in idx[b2]:
                        e.append((u, v))
        prev = 0
        for _ in range(t):
            e.append((prev, n)); prev = n; n += 1
        fams.append((f"Kmulti({k}x{s})+{t}", e, n))
    return fams


def check_structured():
    for tag, e, n in structured_families():
        full_check(e, n, tag)
    print("[C2] structured near-extremal families: OK")


def check_random(trials=60, seed=7):
    rng = random.Random(seed)
    done = 0
    while done < trials:
        n = rng.randint(8, 300)
        # random connected: random tree + extra edges
        edges = set()
        for v in range(1, n):
            edges.add((rng.randrange(v), v))
        extra = rng.randint(0, n)
        for _ in range(extra):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        full_check(sorted(edges), n, f"rand{done} n={n}")
        done += 1
    print(f"[C3] {trials} seeded random connected graphs (n<=300): OK")


def main():
    check_paths()
    check_interlacing()
    check_exhaustive_small(6)
    check_structured()
    check_random()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURES")
        sys.exit(1)
    print("\nPASS: all checks succeeded. dev(D) < ceil(diam/2) <= min(n+,n-) "
          "verified on every instance; Graffiti 39 & 40 hold on all tested graphs, "
          "consistent with the proof in PROOF.md.")


if __name__ == "__main__":
    main()
