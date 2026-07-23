#!/usr/bin/env python3
"""CEGAR v2: perfect matching M with G-M non-3-colorable.
Incremental coloring solver with per-edge relax vars + greedy mono minimization."""
import sys, random, networkx as nx
from pysat.solvers import Glucose4
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

path = sys.argv[1]
G = nx.read_adjlist(path, nodetype=int)
n = G.number_of_nodes()
edges = sorted(tuple(sorted(e)) for e in G.edges())
eidx = {e: i for i, e in enumerate(edges)}
pool = IDPool(start_from=1)
mv = {e: pool.id(('m', e)) for e in edges}

mode = sys.argv[2] if len(sys.argv) > 2 else "pm"
match_solver = Glucose4()
for v in G.nodes():
    inc = [mv[tuple(sorted((v, u)))] for u in G.neighbors(v)]
    if mode == "pm":
        for cl in CardEnc.equals(lits=inc, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses:
            match_solver.add_clause(cl)
    else:  # edge cover: every vertex loses >=1 incident edge (Delta<=4 after removal)
        match_solver.add_clause(inc)

# coloring solver: color vars x_{v,c}, relax vars r_e
cp = IDPool(start_from=1)
xv = lambda v, c: cp.id(('x', v, c))
rv = {e: cp.id(('r', e)) for e in edges}
cs = Glucose4()
for v in range(n):
    cs.add_clause([xv(v,0), xv(v,1), xv(v,2)])
for e in edges:
    u, w = e
    for c in range(3):
        cs.add_clause([-xv(u,c), -xv(w,c), rv[e]])

adj = {v: set(G.neighbors(v)) for v in G.nodes()}

def minimize(col, M):
    """Greedy recoloring to shrink mono-edge set (keep mono subset of anything)."""
    changed = True
    while changed:
        changed = False
        for v in range(n):
            cur = col[v]
            base = sum(1 for u in adj[v] if col[u] == cur)
            for c in range(3):
                if c == cur: continue
                cost = sum(1 for u in adj[v] if col[u] == c)
                if cost < base:
                    col[v] = c; base = cost; changed = True
    return [e for e in edges if col[e[0]] == col[e[1]]]

it = 0
while match_solver.solve():
    it += 1
    model = match_solver.get_model()
    pos = set(l for l in model if l > 0)
    M = set(e for e in edges if mv[e] in pos)
    assum = [-rv[e] for e in edges if e not in M]
    if not cs.solve(assumptions=assum):
        print("WITNESS! matching:", sorted(M), flush=True)
        H = G.copy(); H.remove_edges_from(M)
        out = path.replace(".adjlist", "") + f".WITNESS_{mode}.adjlist"
        nx.write_adjlist(H, out)
        print("degrees:", set(dict(H.degree()).values()), "girth:", nx.girth(H), "->", out, flush=True)
        sys.exit(0)
    m = cs.get_model()
    mset = set(l for l in m if l > 0)
    col = {}
    for v in range(n):
        for c in range(3):
            if xv(v,c) in mset: col[v] = c; break
    mono = minimize(col, M)
    match_solver.add_clause([-mv[e] for e in mono])
    if it % 500 == 0:
        print(f"iter={it} |mono|={len(mono)}", flush=True)
print(f"UNSAT after {it} iterations: no perfect matching of {path} works", flush=True)
