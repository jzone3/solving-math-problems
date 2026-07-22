#!/usr/bin/env python3
"""Exact check: can graph G (graph6 on stdin) be decomposed into <= K
edge-disjoint cycles? K = floor((n-1)/2).

ILP (CBC via pulp): x[e,i] = edge e in cycle slot i, y[v,i] = v on cycle i.
Degree-2 constraints per slot; each slot's chosen edges must form a single
cycle -- enforced lazily: solve, inspect slots, if a slot decomposes into >=2
vertex-disjoint circuits add a connectivity cut, resolve.

Prints for each input graph: g6 SAT/UNSAT [decomposition].
Exit code 1 if any UNSAT (potential counterexample!).
"""
import sys
import networkx as nx
import pulp


def components_of_slot(edges):
    g = nx.Graph()
    g.add_edges_from(edges)
    return [c for c in nx.connected_components(g)]


def check(g6):
    G = nx.from_graph6_bytes(g6.encode())
    n = G.number_of_nodes()
    K = (n - 1) // 2
    E = list(G.edges())
    prob = pulp.LpProblem("hajos", pulp.LpMinimize)
    x = {(e, i): pulp.LpVariable(f"x_{e}_{i}", cat="Binary")
         for e in E for i in range(K)}
    y = {(v, i): pulp.LpVariable(f"y_{v}_{i}", cat="Binary")
         for v in G.nodes for i in range(K)}
    for e in E:
        prob += pulp.lpSum(x[e, i] for i in range(K)) == 1
    for v in G.nodes:
        for i in range(K):
            prob += pulp.lpSum(x[e, i] for e in E if v in e) == 2 * y[v, i]
    prob += 0
    while True:
        status = prob.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[status] != "Optimal":
            return None
        slots = []
        cuts_added = False
        for i in range(K):
            edges = [e for e in E if x[e, i].value() > 0.5]
            slots.append(edges)
            if not edges:
                continue
            comps = components_of_slot(edges)
            if len(comps) > 1:
                # cut: for each extra component S, if all its vertices are used
                # in slot i then some edge leaving S must be in slot i
                for S in comps:
                    boundary = [e for e in E
                                if (e[0] in S) != (e[1] in S)]
                    inside = [v for v in S]
                    prob += (pulp.lpSum(x[e, i] for e in boundary)
                             >= pulp.lpSum(y[v, i] for v in inside)
                             - len(inside) + 1)
                cuts_added = True
        if not cuts_added:
            return slots


def main():
    bad = 0
    for line in sys.stdin:
        g6 = line.strip()
        if not g6:
            continue
        res = check(g6)
        if res is None:
            print(g6, "UNSAT  *** potential counterexample ***")
            bad += 1
        else:
            print(g6, "SAT", [sorted(s) for s in res if s])
        sys.stdout.flush()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
