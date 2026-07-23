#!/usr/bin/env python3
"""Random cyclic lifts of known 4-regular 4-chromatic graphs (Chvatal, Brinkmann,
Gruenbaum25). A Z_k lift of a 4-regular graph is 4-regular; girth can increase.
Search voltages making girth>=6, then SAT-check 3-colorability."""
import random, sys, networkx as nx
from pysat.solvers import Glucose4

def gruenbaum25():
    # MathWorld Gruenbaum graph 25 vertices: build via LCF? use networkx? not available.
    # Skip if unavailable.
    return None

BASES = {}
BASES['chvatal'] = nx.chvatal_graph()
# Brinkmann graph via its known adjacency (from Wikipedia LCF-like construction):
BASES['brinkmann'] = nx.Graph([(0,2),(0,5),(0,7),(0,13),(1,3),(1,6),(1,7),(1,8),(2,4),(2,8),(2,9),
 (3,5),(3,9),(3,10),(4,6),(4,10),(4,11),(5,11),(5,12),(6,12),(6,13),(7,15),(7,20),(8,16),(8,14),
 (9,17),(9,15),(10,18),(10,16),(11,19),(11,17),(12,20),(12,18),(13,14),(13,19),(14,17),(14,18),
 (15,18),(15,19),(16,19),(16,20),(17,20)])

def lift(G, volt, k):
    H = nx.Graph()
    n = G.number_of_nodes()
    for (u, v), t in volt.items():
        for j in range(k):
            H.add_edge(u + n*j, v + n*((j + t) % k))
    return H

def girth_ge(H, g):
    try:
        return nx.girth(H) >= g
    except Exception:
        return True

def three_colorable(H):
    s = Glucose4()
    idx = {v: i for i, v in enumerate(H.nodes())}
    var = lambda v, c: 3*idx[v] + c + 1
    for v in H:
        s.add_clause([var(v,0), var(v,1), var(v,2)])
    for u, v in H.edges():
        for c in range(3):
            s.add_clause([-var(u,c), -var(v,c)])
    res = s.solve(); s.delete(); return res

def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    rng = random.Random(seed)
    tried = g6 = 0
    names = list(BASES)
    while True:
        name = rng.choice(names)
        G = BASES[name]
        k = rng.choice([3,4,5,6,7,8,9,10,11,12,13])
        edges = list(G.edges())
        volt = {e: rng.randrange(k) for e in edges}
        H = lift(G, volt, k)
        if not nx.is_connected(H): continue
        tried += 1
        if not girth_ge(H, 6): continue
        g6 += 1
        if not three_colorable(H):
            print(f"WITNESS base={name} k={k} volt={volt}", flush=True)
            nx.write_adjlist(H, f"/home/ubuntu/p20/sms/WITNESS_lift_{seed}_{name}_{k}.adjlist")
        if g6 % 1000 == 0:
            print(f"seed={seed} tried={tried} g6={g6}", flush=True)

if __name__ == "__main__":
    main()
