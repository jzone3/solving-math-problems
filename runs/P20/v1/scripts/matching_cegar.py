#!/usr/bin/env python3
"""CEGAR: find perfect matching M of a 5-regular 4-chromatic girth-6 graph G
such that G-M is non-3-colorable (=> 4-regular girth>=6 4-chromatic witness)."""
import sys, networkx as nx
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

G = nx.read_adjlist(sys.argv[1] if len(sys.argv)>1 else "eg66.adjlist", nodetype=int)
n = G.number_of_nodes()
edges = sorted(tuple(sorted(e)) for e in G.edges())
pool = IDPool()
mv = {e: pool.id(('m', e)) for e in edges}

match_solver = Glucose4()
for v in G.nodes():
    inc = [mv[tuple(sorted((v, u)))] for u in G.neighbors(v)]
    cnf = CardEnc.equals(lits=inc, bound=1, vpool=pool, encoding=EncType.seqcounter)
    for cl in cnf.clauses:
        match_solver.add_clause(cl)

def three_color(removed):
    s = Glucose4()
    var = lambda v, c: 3*v + c + 1
    for v in range(n):
        s.add_clause([var(v,0), var(v,1), var(v,2)])
        s.add_clause([-var(v,0), -var(v,1)]); s.add_clause([-var(v,0), -var(v,2)]); s.add_clause([-var(v,1), -var(v,2)])
    for e in edges:
        if e in removed: continue
        u, v = e
        for c in range(3):
            s.add_clause([-var(u,c), -var(v,c)])
    res = s.solve()
    col = None
    if res:
        m = s.get_model()
        col = {}
        for v in range(n):
            for c in range(3):
                if m[3*v+c] > 0: col[v] = c; break
    s.delete()
    return res, col

it = 0
while match_solver.solve():
    it += 1
    model = set(l for l in match_solver.get_model() if l > 0)
    M = set(e for e in edges if mv[e] in model)
    sat, col = three_color(M)
    if not sat:
        print("WITNESS! matching:", sorted(M), flush=True)
        H = G.copy(); H.remove_edges_from(M)
        nx.write_adjlist(H, "witness66.adjlist")
        print("degrees:", set(dict(H.degree()).values()), "girth:", nx.girth(H))
        sys.exit(0)
    mono = [e for e in edges if col[e[0]] == col[e[1]]]
    assert all(e in M for e in mono)
    match_solver.add_clause([-mv[e] for e in mono])
    if it % 200 == 0:
        print(f"iter={it} |mono|={len(mono)}", flush=True)
print(f"UNSAT after {it} iterations: no perfect matching works", flush=True)
