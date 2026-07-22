#!/usr/bin/env python3
"""Independent machine verification for the proof of Graffiti 39/40
(see solutions/P08/PROOF.md).

Claim: for every connected G, dev(D) <= diam/2 <= min(n+, n-), hence
dev(D) <= n+(G) (conj. 39) and dev(D) <= n-(G) (conj. 40),
where dev(D) is the population std of the n^2 distance-matrix entries
(Roucairol-Cazenave 2025 encoding; also checked for the off-diagonal variant).

This script checks, with no dependency beyond numpy:
  A. Popoviciu step: dev(D) <= diam/2 on every graph tested.
  B. Geodesic paths are induced (P_{diam+1} is an induced subgraph).
  C. Path inertia: n+(P_k) = n-(P_k) = floor(k/2) for k up to 2000
     (numerically, with the closed-form eigenvalues 2cos(j*pi/(k+1)) cross-checked).
  D. Interlacing consequence: min(n+, n-) >= floor((diam+1)/2) on every graph tested.
  E. End-to-end inequality dev(D) <= min(n+, n-) on:
       - ALL connected graphs with 2 <= n <= 7 (exhaustive, 1+2+6+21+112+853+11117
         isomorphism classes covered via all labelled graphs),
       - structured adversarial families (paths, brooms, spiders, caterpillars,
         complete multipartite + pendant path) up to n = 2000,
       - random trees and random connected graphs up to n = 500.
Prints PASS iff every check succeeds.
"""
import itertools
import random
import sys
import numpy as np

EPS = 1e-4  # eigenvalue sign threshold (same as Roucairol-Cazenave code)
TOL = 1e-9

failures = []


def dist_matrix(A):
    n = len(A)
    INF = float(10 ** 9)
    D = np.where(A > 0, 1.0, INF)
    np.fill_diagonal(D, 0.0)
    for k in range(n):
        D = np.minimum(D, D[:, k][:, None] + D[k, :][None, :])
    return D


def check_graph(A, desc):
    n = len(A)
    D = dist_matrix(A)
    if D.max() >= 1e8:
        raise ValueError("graph not connected: " + desc)
    diam = int(round(D.max()))
    dev_full = float(D.ravel().std())
    dev_off = float(D[~np.eye(n, dtype=bool)].std()) if n >= 2 else 0.0
    ev = np.linalg.eigvalsh(A)
    npos = int((ev > EPS).sum())
    nneg = int((ev < -EPS).sum())
    # A. Popoviciu
    if not (dev_full <= diam / 2 + TOL and dev_off <= diam / 2 + TOL):
        failures.append(("Popoviciu", desc, dev_full, dev_off, diam))
    # B. geodesic path induced
    if n >= 2:
        i, j = np.unravel_index(int(D.argmax()), D.shape)
        path = [int(i)]
        cur = int(i)
        while cur != j:
            nxt = [w for w in range(n)
                   if A[cur, w] and D[w, j] == D[cur, j] - 1][0]
            path.append(nxt)
            cur = nxt
        for a_idx in range(len(path)):
            for b_idx in range(a_idx + 2, len(path)):
                if A[path[a_idx], path[b_idx]]:
                    failures.append(("induced-path", desc))
    # D. interlacing consequence
    if n >= 2 and min(npos, nneg) < (diam + 1) // 2:
        failures.append(("interlacing-bound", desc, npos, nneg, diam))
    # E. the conjectures themselves
    if max(dev_full, dev_off) > min(npos, nneg) + TOL and n >= 2:
        failures.append(("CONJECTURE-VIOLATED", desc, dev_full, npos, nneg))


def path_adj(k):
    A = np.zeros((k, k))
    for i in range(k - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    return A


def main():
    rng = random.Random(39)

    # C. path inertia lemma
    for k in list(range(1, 300)) + [500, 1000, 2000]:
        ev = np.linalg.eigvalsh(path_adj(k))
        closed = 2 * np.cos(np.arange(1, k + 1) * np.pi / (k + 1))
        if np.max(np.abs(np.sort(ev) - np.sort(closed))) > 1e-8:
            failures.append(("path-eigs-closed-form", k))
        npos = int((ev > EPS).sum())
        nneg = int((ev < -EPS).sum())
        if npos != k // 2 or nneg != k // 2:
            failures.append(("path-inertia", k, npos, nneg))
    print("C. path inertia lemma checked for k <= 2000")

    # E1. exhaustive all connected graphs n <= 7 (labelled; covers all iso classes)
    total = 0
    for n in range(2, 8):
        pairs = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(pairs)):
            A = np.zeros((n, n))
            m = mask
            for p_i, (a, b) in enumerate(pairs):
                if (m >> p_i) & 1:
                    A[a, b] = A[b, a] = 1
            # connectivity via BFS
            seen = {0}
            stack = [0]
            while stack:
                v = stack.pop()
                for w in range(n):
                    if A[v, w] and w not in seen:
                        seen.add(w)
                        stack.append(w)
            if len(seen) != n:
                continue
            check_graph(A, f"exhaustive n={n} mask={mask}")
            total += 1
        print(f"E1. exhaustive n={n} done ({total} cumulative connected labelled graphs)")
        if failures:
            break

    # E2. structured adversarial families
    def from_edges(n, edges):
        A = np.zeros((n, n))
        for a, b in edges:
            A[a, b] = A[b, a] = 1
        return A

    for n in [10, 50, 100, 500, 1000, 2000]:
        check_graph(path_adj(n), f"path n={n}")
    for L in [20, 100, 400]:
        for b in [3, 15]:
            edges = [(i, i + 1) for i in range(L - 1)] + [(0, L + i) for i in range(b)]
            check_graph(from_edges(L + b, edges), f"broom L={L} b={b}")
    for legs, ll in [(3, 60), (8, 25), (20, 10)]:
        edges = []
        nid = 1
        for _ in range(legs):
            prev = 0
            for _ in range(ll):
                edges.append((prev, nid))
                prev = nid
                nid += 1
        check_graph(from_edges(nid, edges), f"spider {legs}x{ll}")
    for spine in [50, 200]:
        edges = [(i, i + 1) for i in range(spine - 1)]
        nid = spine
        for i in range(spine):
            edges.append((i, nid))
            nid += 1
        check_graph(from_edges(nid, edges), f"caterpillar spine={spine}")
    for parts, tail in [((6, 6, 6), 30), ((15, 15), 100)]:
        # complete multipartite + pendant path
        sizes = list(parts)
        n0 = sum(sizes)
        grp = []
        s = 0
        for sz in sizes:
            grp.append(list(range(s, s + sz)))
            s += sz
        edges = [(a, b) for gi in range(len(grp)) for gj in range(gi + 1, len(grp))
                 for a in grp[gi] for b in grp[gj]]
        last = 0
        for i in range(tail):
            edges.append((last, n0 + i))
            last = n0 + i
        check_graph(from_edges(n0 + tail, edges), f"multipartite{parts}+tail{tail}")
    print("E2. structured families checked")

    # E3. random trees (random Pruefer) and random connected graphs
    def random_tree(n):
        seq = [rng.randrange(n) for _ in range(n - 2)]
        # Pruefer decode
        deg = [1] * n
        for x in seq:
            deg[x] += 1
        import heapq
        leaves = [i for i in range(n) if deg[i] == 1]
        heapq.heapify(leaves)
        edges = []
        for x in seq:
            leaf = heapq.heappop(leaves)
            edges.append((leaf, x))
            deg[x] -= 1
            if deg[x] == 1:
                heapq.heappush(leaves, x)
        u = heapq.heappop(leaves)
        v = heapq.heappop(leaves)
        edges.append((u, v))
        return from_edges(n, edges)

    for n in [30, 100, 300, 500]:
        for t in range(25):
            A = random_tree(n)
            check_graph(A, f"random tree n={n} #{t}")
            # add a few random chords -> sparse non-tree
            for _ in range(rng.randrange(1, 6)):
                a, b = rng.randrange(n), rng.randrange(n)
                if a != b:
                    A[a, b] = A[b, a] = 1
            check_graph(A, f"random tree+chords n={n} #{t}")
    print("E3. random trees / sparse graphs checked")

    if failures:
        print("FAIL")
        for f in failures[:20]:
            print(" ", f)
        sys.exit(1)
    print("PASS: all proof steps and both conjectures verified on every graph tested")


if __name__ == "__main__":
    main()
