"""Scan parameterized families near the equality manifold K_m + (m-2)K_1.

f(G) = sqrt((sum d^2 + 2m)/n - (2m/n)^2) - sum_{uv in E} 1/sqrt(d_u d_v)
Conjecture 129 says f <= 0. Report the max over each family.
"""
import math
from itertools import product


def f_from_graph(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    m = len(edges)
    if m == 0:
        return 0.0
    var = (sum(x * x for x in d) + 2 * m) / n - (2 * m / n) ** 2
    R = sum(1.0 / math.sqrt(d[u] * d[v]) for u, v in edges)
    return math.sqrt(max(var, 0.0)) - R


def clique_edges(mq, off=0):
    return [(off + i, off + j) for i in range(mq) for j in range(i + 1, mq)]


def best(name, gen):
    b, arg = -1e9, None
    for params, n, edges in gen:
        f = f_from_graph(n, edges)
        if f > b:
            b, arg = f, params
    print(f"{name:45s} max f = {b:+.9f} at {arg}")
    return b, arg


# 1. clique + extra vertex adjacent to j clique vertices + k isolated
def gen_clique_plus_apex():
    for mq in range(3, 60):
        for j in range(1, mq + 1):
            for k in range(0, 2 * mq):
                edges = clique_edges(mq) + [(i, mq) for i in range(j)]
                yield (mq, j, k), mq + 1 + k, edges


# 2. clique minus a matching of size t + k isolated
def gen_clique_minus_matching():
    for mq in range(4, 80):
        for t in range(0, mq // 2 + 1):
            removed = {(2 * i, 2 * i + 1) for i in range(t)}
            edges = [e for e in clique_edges(mq) if e not in removed]
            for k in range(max(0, mq - 5), mq + 5):
                yield (mq, t, k), mq + k, edges


# 3. complete split graph: clique q joined to s independent + k isolated
def gen_complete_split():
    for q in range(2, 40):
        for s in range(1, 40):
            edges = clique_edges(q) + [(i, q + j) for i in range(q) for j in range(s)]
            for k in range(0, 3 * (q + s)):
                yield (q, s, k), q + s + k, edges


# 4. two disjoint cliques a,b + k isolated (proved <=0; sanity)
def gen_two_cliques():
    for a in range(2, 40):
        for b in range(2, a + 1):
            edges = clique_edges(a) + clique_edges(b, off=a)
            for k in range(0, 2 * (a + b)):
                yield (a, b, k), a + b + k, edges


# 5. clique + pendant path of length p attached + k isolated
def gen_kite():
    for mq in range(3, 50):
        for p in range(1, 6):
            edges = clique_edges(mq) + [(mq - 1 if i == 0 else mq + i - 1, mq + i) for i in range(p)]
            for k in range(max(0, mq - 6), mq + 6):
                yield (mq, p, k), mq + p + k, edges


# 6. clique with one vertex of the clique also joined to extra leaves
def gen_clique_leaves():
    for mq in range(3, 50):
        for l in range(1, 10):
            edges = clique_edges(mq) + [(0, mq + i) for i in range(l)]
            for k in range(max(0, mq - 6), mq + 6):
                yield (mq, l, k), mq + l + k, edges


# 7. clique + double edge subdivision? instead: clique with one edge subdivided + k iso
def gen_clique_subdiv():
    for mq in range(4, 60):
        base = [e for e in clique_edges(mq) if e != (0, 1)]
        edges = base + [(0, mq), (1, mq)]
        for k in range(max(0, mq - 6), mq + 8):
            yield (mq, k), mq + 1 + k, edges


if __name__ == "__main__":
    best("clique + apex(j) + k iso", gen_clique_plus_apex())
    best("clique - matching(t) + k iso", gen_clique_minus_matching())
    best("complete split K_q v sK_1 + k iso", gen_complete_split())
    best("two cliques + k iso", gen_two_cliques())
    best("kite (clique + path p) + k iso", gen_kite())
    best("clique + l leaves on one vtx + k iso", gen_clique_leaves())
    best("clique w/ subdivided edge + k iso", gen_clique_subdiv())
