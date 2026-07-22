"""
Cross-validate harness.has_k_disjoint_dijoins against an independent,
differently-written brute-force checker on random small tau=3 instances.

Brute force: try all 3^m colorings (m <= 12); a coloring is valid iff every
color class is a dijoin, checked *without* the minimal-dicut machinery:
class J is a dijoin iff contracting J leaves the digraph strongly connected,
tested via reachability in (V, A union J^-1) [Schrijver's characterization:
J is a dijoin iff (V, A u J^{-1}) is strongly connected].
"""

import random
from itertools import product

import networkx as nx

from harness import tau, has_k_disjoint_dijoins
from search import random_shape_dag

K = 3


def is_dijoin_bruteforce(n, arcs, J):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i, (u, v) in enumerate(arcs):
        G.add_edge(u, v)
        if i in J:
            G.add_edge(v, u)
    return nx.is_strongly_connected(G)


def packs_bruteforce(n, arcs):
    m = len(arcs)
    for coloring in product(range(K), repeat=m):
        classes = [set(), set(), set()]
        for i, c in enumerate(coloring):
            classes[c].add(i)
        if all(is_dijoin_bruteforce(n, arcs, cl) for cl in classes):
            return True
    return False


if __name__ == "__main__":
    rng = random.Random(99)
    agree = 0
    tested = 0
    while tested < 40:
        g = random_shape_dag(rng.choice([1, 2]), rng.choice([1, 2]),
                             rng.choice([2, 4]), rng)
        if g is None:
            continue
        n, arcs = g
        if len(arcs) > 12:
            continue
        if tau(n, arcs) != K:
            continue
        a = has_k_disjoint_dijoins(n, arcs, K)
        b = packs_bruteforce(n, arcs)
        assert a == b, f"MISMATCH on {arcs}: sat={a} brute={b}"
        tested += 1
        agree += 1
    print(f"PASS crosscheck: {agree}/{tested} agree")
