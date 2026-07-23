#!/usr/bin/env python3
"""Parse Potocnik Census4val-640.mgm (magma), keep girth-6 graphs, test 3-colorability."""
import re, sys
import networkx as nx
from pysat.solvers import Glucose4

def three_colorable(G):
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    s = Glucose4()
    def var(i, c): return 3 * i + c + 1
    for i in range(len(nodes)):
        s.add_clause([var(i, 0), var(i, 1), var(i, 2)])
    for u, v in G.edges():
        for c in range(3):
            s.add_clause([-var(idx[u], c), -var(idx[v], c)])
    r = s.solve()
    s.delete()
    return r

text = open(sys.argv[1]).read()
pat = re.compile(r"AT4val\[(\d+),(\d+)\]\s*:=\s*Graph<\s*(\d+)\s*\|\s*\{(.*?)\}>\s*;", re.S)
count = 0
girth6 = 0
non3 = 0
for m in pat.finditer(text):
    n, k, nn, body = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4)
    edges = re.findall(r"\{(\d+),(\d+)\}", body)
    G = nx.Graph()
    G.add_nodes_from(range(1, nn + 1))
    G.add_edges_from((int(a), int(b)) for a, b in edges)
    count += 1
    assert all(d == 4 for _, d in G.degree()), (n, k)
    g = nx.girth(G)
    if g == 6:
        girth6 += 1
        if not three_colorable(G):
            non3 += 1
            print(f"NON3COL AT4val[{n},{k}]")
print(f"total={count} girth6={girth6} non3col={non3}")
