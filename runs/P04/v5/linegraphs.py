"""Probe 3e: line graphs of 4-regular (and (2,4)-even) graphs.

Rationale (V5): L(G) of a 4-regular G is 6-regular Eulerian, triangle-dense,
with cycle structure tightly constrained by G — exactly the profile the
literature does NOT cover (delta=6, non-planar in general, K6-minors present).
n_L = |E(G)| = 2|V(G)|: take |V(G)| = 7..10 for n_L = 14..20.
Also connected even graphs with degrees in {2,4} and 13..16 edges.
"""
import subprocess
import sys
import networkx as nx
from hajos import hajos_ok, is_eulerian, rlc_decompose

def check(name, H):
    H = nx.convert_node_labels_to_integers(H)
    n = H.number_of_nodes()
    edges = tuple(sorted((min(u, v), max(u, v)) for u, v in H.edges()))
    if not is_eulerian(n, edges):
        return False
    bound = (n - 1) // 2
    h = rlc_decompose(n, edges, tries=400)
    if h is not None and len(h) <= bound:
        return False
    ok, _ = hajos_ok(n, edges, time_limit=1200)
    print(f"HARD {name}: n={n} m={len(edges)} cpSAT={ok}", flush=True)
    if ok is False:
        print(f"*** COUNTEREXAMPLE {name} n={n} edges={edges}", flush=True)
        with open(f"counterexample_{name}.txt", "w") as f:
            f.write(repr((n, edges)))
        return True
    return False

def main():
    total = 0
    for nv in range(7, 11):
        out = subprocess.run(["nauty-geng", "-c", "-d4", "-D4", str(nv)],
                             capture_output=True, text=True)
        graphs = [g for g in out.stdout.split() if g]
        for i, g6 in enumerate(graphs):
            G = nx.from_graph6_bytes(g6.encode())
            check(f"L(4reg_{nv}v_{i})", nx.line_graph(G))
            total += 1
        print(f"4-regular on {nv} vertices: {len(graphs)} line graphs checked", flush=True)
    # even graphs with degrees in {2,4}, 13..16 edges (line graph Eulerian iff G even)
    for nv in range(7, 12):
        out = subprocess.run(["nauty-geng", "-c", "-d2", "-D4", str(nv)],
                             capture_output=True, text=True)
        cnt = 0
        for i, g6 in enumerate(out.stdout.split()):
            G = nx.from_graph6_bytes(g6.encode())
            if any(d % 2 for _, d in G.degree()):
                continue
            m = G.number_of_edges()
            if not 13 <= m <= 20:
                continue
            check(f"L(even24_{nv}v_{i})", nx.line_graph(G))
            cnt += 1
        print(f"even (2,4)-graphs on {nv} vertices: {cnt} line graphs checked", flush=True)
    print("linegraphs done", flush=True)

if __name__ == "__main__":
    main()
