"""V4 asymptotic-family study for Graffiti 39/40.

For candidate families, compute dev(D) (std of all n^2 entries of the distance
matrix), n+ / n- (positive / negative adjacency eigenvalues), diameter, and the
"score" dev - min(n+, n-).  The proof (see PROOF.md) says dev <= diam/2 <=
ceil(diam/2) <= min(n+, n-), so every score must be <= 0; this script shows the
gap actually diverges to -infinity on all natural high-deviation families.
"""
import numpy as np
from collections import deque

TOL = 1e-8


def apsp(adj, n):
    D = np.full((n, n), -1, dtype=np.int64)
    for s in range(n):
        D[s, s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if D[s, v] < 0:
                    D[s, v] = D[s, u] + 1
                    q.append(v)
    assert (D >= 0).all(), "graph not connected"
    return D


def stats(edges, n):
    adj = [[] for _ in range(n)]
    A = np.zeros((n, n))
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
        A[u, v] = A[v, u] = 1.0
    D = apsp(adj, n)
    flat = D.astype(float).ravel()
    dev = flat.std()
    ev = np.linalg.eigvalsh(A)
    np_, nm = int((ev > TOL).sum()), int((ev < -TOL).sum())
    d = int(D.max())
    return dev, np_, nm, d


def path(n):
    return [(i, i + 1) for i in range(n - 1)], n


def broom(handle, bristles):
    """path of `handle` vertices with `bristles` pendant leaves on one end"""
    e = [(i, i + 1) for i in range(handle - 1)]
    n = handle + bristles
    e += [(handle - 1, handle + i) for i in range(bristles)]
    return e, n


def spider(k, L):
    """k legs of length L from a center (subdivided star)"""
    e = []
    n = 1 + k * L
    for leg in range(k):
        prev = 0
        for j in range(L):
            v = 1 + leg * L + j
            e.append((prev, v))
            prev = v
    return e, n


def caterpillar(spine, legs_per):
    e = [(i, i + 1) for i in range(spine - 1)]
    n = spine
    for i in range(spine):
        for _ in range(legs_per):
            e.append((i, n))
            n += 1
    return e, n


def multipartite_plus_path(k, m, L):
    """complete k-partite K_{m,...,m} (n+ = k-1) with a pendant path of L vertices"""
    n0 = k * m
    e = []
    for i in range(n0):
        for j in range(i + 1, n0):
            if i // m != j // m:
                e.append((i, j))
    prev = 0
    n = n0
    for _ in range(L):
        e.append((prev, n))
        prev = n
        n += 1
    return e, n


def main():
    rows = []
    for n in (10, 50, 200, 1000):
        rows.append(("path n=%d" % n,) + stats(*path(n)))
    for h, b in ((50, 50), (200, 200), (500, 500)):
        rows.append(("broom h=%d b=%d" % (h, b),) + stats(*broom(h, b)))
    for k, L in ((3, 100), (5, 100), (10, 50), (3, 300)):
        rows.append(("spider k=%d L=%d" % (k, L),) + stats(*spider(k, L)))
    for s, l in ((100, 1), (100, 3), (300, 1)):
        rows.append(("caterpillar s=%d l=%d" % (s, l),) + stats(*caterpillar(s, l)))
    for k, m, L in ((3, 5, 100), (3, 30, 200), (2, 50, 300)):
        rows.append(("K_%dx%d + P_%d" % (k, m, L),) + stats(*multipartite_plus_path(k, m, L)))

    print("%-22s %10s %6s %6s %5s %10s %12s" % ("family", "dev(D)", "n+", "n-", "diam", "diam/2", "dev-min(n+,n-)"))
    worst = -1e18
    for name, dev, np_, nm, d in rows:
        score = dev - min(np_, nm)
        worst = max(worst, score)
        print("%-22s %10.4f %6d %6d %5d %10.1f %12.4f" % (name, dev, np_, nm, d, d / 2, score))
        assert dev <= d / 2 + 1e-9, (name, dev, d)
        assert np_ >= (d + 1) // 2 and nm >= (d + 1) // 2, (name, np_, nm, d)
    print("\nmax score over families: %.4f (conjecture violated iff > 0)" % worst)


if __name__ == "__main__":
    main()
