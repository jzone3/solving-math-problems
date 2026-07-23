#!/usr/bin/env python3
"""Exhaustively check all connected 4-regular circulants C_n(a,b) for girth 6 and 3-colorability."""
import math, sys
import networkx as nx
from pysat.solvers import Glucose4

def three_colorable(G):
    idx = {v: i for i, v in enumerate(G.nodes())}
    s = Glucose4()
    v3 = lambda i, c: 3 * i + c + 1
    for i in range(len(idx)):
        s.add_clause([v3(i, 0), v3(i, 1), v3(i, 2)])
    for u, v in G.edges():
        for c in range(3):
            s.add_clause([-v3(idx[u], c), -v3(idx[v], c)])
    r = s.solve(); s.delete(); return r

N = int(sys.argv[1])
checked = g6 = non3 = 0
for n in range(26, N + 1):
    for a in range(1, n // 2 + 1):
        for b in range(a + 1, n // 2 + 1):
            if math.gcd(math.gcd(a, b), n) != 1:
                continue
            # degrees: a,b generate; degree 4 requires a != n/2 and b != n/2 (else deg 3)
            if 2 * a == n or 2 * b == n:
                continue
            G = nx.circulant_graph(n, [a, b])
            if not all(d == 4 for _, d in G.degree()):
                continue
            checked += 1
            if nx.girth(G) == 6:
                g6 += 1
                if not three_colorable(G):
                    non3 += 1
                    print(f"NON3COL circulant C_{n}({a},{b})", flush=True)
print(f"checked={checked} girth6={g6} non3col={non3}")
