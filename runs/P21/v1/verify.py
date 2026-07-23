#!/usr/bin/env python3
"""
Exact independent verifier for P21 witnesses (no floats anywhere).

Input: text file, lines "c u v" = edge {u,v} of K50 assigned to copy c.
Checks, using only integer arithmetic and set operations:
  1. 0 <= u < v <= 49, colors form 0..k-1, no edge appears twice (across all colors).
  2. Each color class has 175 edges, every vertex has degree exactly 7,
     contains no triangle and no 4-cycle (girth >= 5; C(50,2)-regularity makes
     girth exactly 5).
     A 7-regular graph with girth >= 5 has >= 1+7+7*6 = 50 vertices per connected
     component, so on 50 vertices it is connected, and it is the unique
     (7,5)-Moore graph: the Hoffman-Singleton graph.  No isomorphism test needed.
  3. If k == 7: the union is all 1225 edges of K50 (a decomposition).

Prints PASS/FAIL and a summary.
"""
import sys
from itertools import combinations

def main(path):
    edges_by_color = {}
    all_edges = set()
    with open(path) as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            c, u, v = map(int, line.split())
            assert 0 <= u < v <= 49, f"line {ln}: bad edge {u},{v}"
            e = (u, v)
            assert e not in all_edges, f"line {ln}: duplicate edge {e}"
            all_edges.add(e)
            edges_by_color.setdefault(c, set()).add(e)
    colors = sorted(edges_by_color)
    k = len(colors)
    assert colors == list(range(k)), f"colors not 0..{k-1}: {colors}"
    for c in colors:
        E = edges_by_color[c]
        assert len(E) == 175, f"color {c}: {len(E)} edges != 175"
        adj = {v: set() for v in range(50)}
        for (u, v) in E:
            adj[u].add(v); adj[v].add(u)
        for v in range(50):
            assert len(adj[v]) == 7, f"color {c}: deg({v}) = {len(adj[v])} != 7"
        # no triangle and no 4-cycle: any two distinct vertices have
        # at most one common neighbour, and adjacent ones have none.
        for u, v in combinations(range(50), 2):
            common = len(adj[u] & adj[v])
            if v in adj[u]:
                assert common == 0, f"color {c}: triangle at {u},{v}"
            else:
                assert common <= 1, f"color {c}: 4-cycle at {u},{v}"
        print(f"color {c}: 175 edges, 7-regular, girth>=5 => Hoffman-Singleton  OK")
    print(f"{k} pairwise edge-disjoint Hoffman-Singleton copies in K50: OK")
    if k == 7:
        assert len(all_edges) == 1225, "union is not all of E(K50)"
        print("union = E(K50): full decomposition  OK")
    print("PASS")

if __name__ == '__main__':
    main(sys.argv[1])
