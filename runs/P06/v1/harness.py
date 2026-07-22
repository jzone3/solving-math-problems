"""
P06 / V1 harness: Graffiti WoW conjecture 129
    dev(Laplacian eigenvalues of G)  <=  Randic index R(G)

Definitions confirmed against reference invariant code
(github.com/RoucairolMilo/refutationGBR, src/models/conjectures/{GenerateGraph,invariants}.rs):
  - dev = POPULATION standard deviation (divide by n) of the eigenvalues of L = D - A.
  - R(G) = sum over edges uv of 1/sqrt(d(u) d(v)).

KEY IDENTITY (machine-checked in selftest below):
  sum(lambda_i) = 2m,  sum(lambda_i^2) = trace(L^2) = sum_i d_i^2 + 2m
  => dev^2 = (sum d_i^2 + 2m)/n - (2m/n)^2  = Var(d) + dbar
  i.e. the LHS depends ONLY on the degree sequence.

score(G) = dev(G) - R(G); conjecture 129 refuted iff score > 0 (strictly).
"""
import math
import numpy as np


def degrees(adj):
    return [len(nb) for nb in adj]


def edges(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]


def randic(adj):
    d = degrees(adj)
    return sum(1.0 / math.sqrt(d[u] * d[v]) for u, v in edges(adj))


def dev_from_degseq(d):
    n = len(d)
    m2 = sum(d)                      # 2m
    s2 = sum(x * x for x in d)
    var = (s2 + m2) / n - (m2 / n) ** 2
    return math.sqrt(max(var, 0.0))


def dev_eig(adj):
    n = len(adj)
    L = np.zeros((n, n))
    for u, nbs in enumerate(adj):
        L[u, u] = len(nbs)
        for v in nbs:
            L[u, v] = -1.0
    ev = np.linalg.eigvalsh(L)
    return float(np.sqrt(np.mean((ev - ev.mean()) ** 2)))


def score(adj):
    return dev_from_degseq(degrees(adj)) - randic(adj)


# ---------- graph builders (adjacency lists) ----------

def from_edges(n, es):
    adj = [set() for _ in range(n)]
    for u, v in es:
        adj[u].add(v)
        adj[v].add(u)
    return [sorted(s) for s in adj]


def star(n):
    return from_edges(n, [(0, i) for i in range(1, n)])


def double_star(a, b):
    # centers 0,1 adjacent; 0 has a leaves, 1 has b leaves
    n = a + b + 2
    es = [(0, 1)] + [(0, 2 + i) for i in range(a)] + [(1, 2 + a + i) for i in range(b)]
    return from_edges(n, es)


def spider(k, ell):
    # k legs of length ell from a center
    n = 1 + k * ell
    es = []
    idx = 1
    for _ in range(k):
        prev = 0
        for _ in range(ell):
            es.append((prev, idx))
            prev = idx
            idx += 1
    return from_edges(n, es)


def star_pendant_paths(k_leaves, k_paths, ell):
    # star center with k_leaves pendant leaves + k_paths paths of length ell
    n = 1 + k_leaves + k_paths * ell
    es = [(0, 1 + i) for i in range(k_leaves)]
    idx = 1 + k_leaves
    for _ in range(k_paths):
        prev = 0
        for _ in range(ell):
            es.append((prev, idx))
            prev = idx
            idx += 1
    return from_edges(n, es)


def complete_split(n, k):
    # k dominating vertices (clique) + independent set of n-k
    es = [(i, j) for i in range(k) for j in range(i + 1, n)]
    return from_edges(n, es)


def pineapple(q, p):
    # clique K_q, p extra pendant vertices attached to vertex 0
    n = q + p
    es = [(i, j) for i in range(q) for j in range(i + 1, q)]
    es += [(0, q + i) for i in range(p)]
    return from_edges(n, es)


def kite(q, ell):
    # clique K_q with a path of length ell attached to vertex 0
    n = q + ell
    es = [(i, j) for i in range(q) for j in range(i + 1, q)]
    prev = 0
    for i in range(ell):
        es.append((prev, q + i))
        prev = q + i
    return from_edges(n, es)


def double_broom(ell, a, b):
    # path with ell internal vertices, a leaves on one end, b on the other
    n = ell + a + b
    es = [(i, i + 1) for i in range(ell - 1)]
    es += [(0, ell + i) for i in range(a)]
    es += [(ell - 1, ell + a + i) for i in range(b)]
    return from_edges(n, es)


def threshold_graph(bits):
    # creation sequence: bits[i]=1 -> dominating vertex, 0 -> isolated; first vertex implicit
    n = len(bits) + 1
    es = []
    for i, b in enumerate(bits):
        v = i + 1
        if b:
            es += [(u, v) for u in range(v)]
    return from_edges(n, es)


def selftest():
    import random
    rng = random.Random(0)
    for _ in range(200):
        n = rng.randint(2, 12)
        es = [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < 0.4]
        adj = from_edges(n, es)
        d1 = dev_from_degseq(degrees(adj))
        d2 = dev_eig(adj)
        assert abs(d1 - d2) < 1e-9, (n, es, d1, d2)
    print("selftest PASS: dev(L) == sqrt(Var(deg)+avgdeg) on 200 random graphs")


if __name__ == "__main__":
    selftest()
