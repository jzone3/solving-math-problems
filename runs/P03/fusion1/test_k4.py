"""Validate the k=4 SAT partition checker against brute-force coloring."""

import random
from itertools import product

from harness import has_k_disjoint_dijoins, tau


def brute_pack(n, arcs, k=4):
    for coloring in product(range(k), repeat=len(arcs)):
        classes = [set() for _ in range(k)]
        for i, color in enumerate(coloring):
            classes[color].add(i)
        good = True
        for cls in classes:
            # Schrijver's criterion: J is a dijoin iff adding its reverse
            # arcs makes the digraph strongly connected.
            adj = [[] for _ in range(n)]
            rev = [[] for _ in range(n)]
            for i, (u, v) in enumerate(arcs):
                adj[u].append(v)
                if i in cls:
                    rev[v].append(u)
            seen = {0}
            stack = [0]
            while stack:
                u = stack.pop()
                for v in adj[u] + rev[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            if len(seen) != n:
                good = False
                break
            radj = [[] for _ in range(n)]
            for u in range(n):
                for v in adj[u] + rev[u]:
                    radj[v].append(u)
            seen = {0}
            stack = [0]
            while stack:
                u = stack.pop()
                for v in radj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            if len(seen) != n:
                good = False
                break
        if good:
            return True
    return False


rng = random.Random(4004)
tested = 0
while tested < 300:
    n = rng.randrange(4, 7)
    order = list(range(n))
    possible = [(u, v) for u in order for v in order if u < v]
    rng.shuffle(possible)
    arcs = possible[:rng.randrange(4, min(9, len(possible) + 1))]
    if len(arcs) > 8 or tau(n, arcs) != 4:
        continue
    a = has_k_disjoint_dijoins(n, arcs, 4)
    b = brute_pack(n, arcs)
    assert a == b, (n, arcs, a, b)
    tested += 1
print(f"PASS k=4 SAT vs brute force: {tested}/{tested} agree")
