#!/usr/bin/env python3
"""Check exported Cayley graphs (cayley_graphs.txt): keep girth>=6, test 3-colorability."""
import sys
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
    r = s.solve()
    s.delete()
    return r

total = g6 = non3 = 0
G = None
hdr = None
for line in open(sys.argv[1]):
    line = line.strip()
    if line.startswith("G "):
        hdr = line
        G = nx.Graph()
        continue
    if line == "END":
        total += 1
        if nx.girth(G) >= 6:
            g6 += 1
            if not three_colorable(G):
                non3 += 1
                print(f"NON3COL {hdr}", flush=True)
        G = None
        continue
    if G is not None:
        a, b = map(int, line.split())
        G.add_edge(a, b)
print(f"total={total} girth>=6={g6} non3col={non3}")
