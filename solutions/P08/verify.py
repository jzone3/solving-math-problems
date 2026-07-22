#!/usr/bin/env python3
"""Independent verifier for the proof of Graffiti conjectures 39/40 (see PROOF.md).

Claims checked, for every connected test graph G (distance matrix D, diameter d,
adjacency inertia n+/n-):

  [C1] Popoviciu step, EXACT rational arithmetic:  4 * Var(entries of D) <= d^2
       (i.e. dev(D) <= d/2).
  [C2] Interlacing step: n+ >= ceil(d/2) and n- >= ceil(d/2).
       Eigenvalues counted with a conservative tolerance (only ev > 1e-8 counts as
       positive, ev < -1e-8 as negative), which can only UNDER-count n+/n-, so a
       pass is safe.
  [C3] The conjectures themselves: dev(D) <= n+ and dev(D) <= n-  (dev computed as an
       exact rational squared value, compared to the integer counts of [C2]).

Test corpus:
  - ALL connected graphs on n <= 8 vertices (nauty 'geng'/'nauty-geng' if on PATH,
    else built-in exhaustive enumeration for n <= 7);
  - random connected graphs, various densities, n up to 120;
  - structured high-deviation families (paths, brooms, spiders, caterpillars,
    complete multipartite + pendant path) with n up to 1000.

Prints PASS iff every claim holds on every graph. Dependencies: numpy only.
"""
import itertools
import random
import shutil
import subprocess
import sys
from collections import deque
from fractions import Fraction

import numpy as np

TOL = 1e-8
checked = 0


def bfs_apsp(adj, n):
    D = [[-1] * n for _ in range(n)]
    for s in range(n):
        D[s][s] = 0
        q = deque([s])
        row = D[s]
        while q:
            u = q.popleft()
            for v in adj[u]:
                if row[v] < 0:
                    row[v] = row[u] + 1
                    q.append(v)
    return D


def check_graph(edges, n, name):
    global checked
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    D = bfs_apsp(adj, n)
    ent = [D[i][j] for i in range(n) for j in range(n)]
    if min(ent) < 0:
        return False  # not connected; caller should not pass these
    d = max(ent)

    # exact variance of the n^2 entries
    s1 = sum(ent)
    s2 = sum(e * e for e in ent)
    var4 = 4 * (Fraction(s2, n * n) - Fraction(s1, n * n) ** 2)  # 4*Var
    assert var4 <= d * d, ("C1 FAIL", name, float(var4), d)

    A = np.zeros((n, n))
    for u, v in edges:
        A[u, v] = A[v, u] = 1.0
    ev = np.linalg.eigvalsh(A)
    npos = int((ev > TOL).sum())
    nneg = int((ev < -TOL).sum())
    need = (d + 1) // 2  # ceil(d/2)
    assert npos >= need and nneg >= need or n == 1, ("C2 FAIL", name, npos, nneg, d)

    # conjectures: dev <= n+ and dev <= n-  <=>  4*Var <= (2*count)^2
    assert var4 <= (2 * npos) ** 2 or (n == 1), ("C3(39) FAIL", name, float(var4), npos)
    assert var4 <= (2 * nneg) ** 2 or (n == 1), ("C3(40) FAIL", name, float(var4), nneg)
    if n == 1:
        assert var4 == 0
    checked += 1
    return True


# ---------- exhaustive small graphs ----------

def g6_to_edges(line):
    b = [c - 63 for c in line.strip().encode()]
    n = b[0]
    bits = []
    for x in b[1:]:
        bits.extend((x >> (5 - i)) & 1 for i in range(6))
    edges, k = [], 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return edges, n


def exhaustive_geng(maxn):
    exe = shutil.which("geng") or shutil.which("nauty-geng")
    if not exe:
        return False
    for n in range(1, maxn + 1):
        out = subprocess.run([exe, "-c", "-q", str(n)], capture_output=True, text=True, check=True)
        cnt = 0
        for line in out.stdout.splitlines():
            if line:
                check_graph(*g6_to_edges(line), name="geng n=%d #%d" % (n, cnt))
                cnt += 1
        print("  exhaustive n=%d: %d connected graphs OK" % (n, cnt))
    return True


def exhaustive_builtin(maxn):
    for n in range(1, maxn + 1):
        pairs = list(itertools.combinations(range(n), 2))
        cnt = 0
        for mask in range(1 << len(pairs)):
            edges = [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]
            adj = [[] for _ in range(n)]
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
            seen = [False] * n
            q = deque([0])
            seen[0] = True
            m = 1
            while q:
                u = q.popleft()
                for v in adj[u]:
                    if not seen[v]:
                        seen[v] = True
                        m += 1
                        q.append(v)
            if m == n:
                check_graph(edges, n, "builtin n=%d mask=%d" % (n, mask))
                cnt += 1
        print("  exhaustive (builtin, w/ isomorphs) n=%d: %d connected graphs OK" % (n, cnt))


# ---------- random connected graphs ----------

def random_connected(n, extra_edges, rng):
    edges = set()
    order = list(range(n))
    rng.shuffle(order)
    for i in range(1, n):  # random tree
        j = rng.randrange(i)
        u, v = order[i], order[j]
        edges.add((min(u, v), max(u, v)))
    while len(edges) < min(n - 1 + extra_edges, n * (n - 1) // 2):
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return list(edges)


# ---------- structured families ----------

def path(n):
    return [(i, i + 1) for i in range(n - 1)], n


def broom(h, b):
    e = [(i, i + 1) for i in range(h - 1)] + [(h - 1, h + i) for i in range(b)]
    return e, h + b


def spider(k, L):
    e = []
    for leg in range(k):
        prev = 0
        for j in range(L):
            v = 1 + leg * L + j
            e.append((prev, v))
            prev = v
    return e, 1 + k * L


def caterpillar(s, l):
    e = [(i, i + 1) for i in range(s - 1)]
    n = s
    for i in range(s):
        for _ in range(l):
            e.append((i, n))
            n += 1
    return e, n


def multipartite_plus_path(k, m, L):
    n0 = k * m
    e = [(i, j) for i in range(n0) for j in range(i + 1, n0) if i // m != j // m]
    prev, n = 0, n0
    for _ in range(L):
        e.append((prev, n))
        prev, n = n, n + 1
    return e, n


def main():
    print("== exhaustive small graphs ==")
    if not exhaustive_geng(8):
        print("  (geng not found; using builtin enumeration up to n=7)")
        exhaustive_builtin(7)

    print("== random connected graphs ==")
    rng = random.Random(20260722)
    for n, extra, reps in ((15, 5, 400), (30, 10, 200), (60, 30, 100), (120, 60, 40), (120, 2000, 20)):
        for r in range(reps):
            check_graph(random_connected(n, extra, rng), n, "rand n=%d #%d" % (n, r))
        print("  n=%d extra=%d x%d OK" % (n, extra, reps))

    print("== structured families ==")
    fams = [("path", path(1000)), ("broom", broom(500, 500)), ("spider", spider(5, 199)),
            ("caterpillar", caterpillar(300, 2)), ("K3x30+P200", multipartite_plus_path(3, 30, 200)),
            ("K2x50+P300", multipartite_plus_path(2, 50, 300))]
    for name, (e, n) in fams:
        check_graph(e, n, name)
        print("  %s (n=%d) OK" % (name, n))

    print("\nAll claims C1 (exact), C2, C3 verified on %d connected graphs." % checked)
    print("PASS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("FAIL:", e.args)
        sys.exit(1)
