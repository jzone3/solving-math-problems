"""Independent brute-force minimum cycle decomposition (for cross-checking
the SAT decider on small graphs). Exhaustive branch-and-bound: repeatedly take
the lowest-indexed remaining edge, enumerate all simple cycles through it in
the remaining graph, recurse."""

import sys
from functools import lru_cache


def cycles_through_edge(adj, edge_set, e0):
    """All simple cycles (as frozensets of edges) containing edge e0."""
    a, b = e0
    out = []

    def dfs(v, visited, path_edges):
        if v == b:
            out.append(frozenset(path_edges | {e0}))
            return
        for u in adj[v]:
            e = (min(u, v), max(u, v))
            if e == e0 or e not in edge_set or e in path_edges:
                continue
            if u in visited:
                continue
            visited.add(u)
            path_edges.add(e)
            dfs(u, visited, path_edges)
            path_edges.discard(e)
            visited.discard(u)

    dfs(a, {a, b} - {b} | {a}, set())
    return out


def min_decomp(n, edges):
    edges = [tuple(sorted(e)) for e in edges]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    best = [len(edges) // 3 + 1]

    def rec(remaining, used):
        if used >= best[0]:
            return
        if not remaining:
            best[0] = used
            return
        e0 = min(remaining)
        for cyc in cycles_through_edge(adj, remaining, e0):
            rec(remaining - cyc, used + 1)

    rec(frozenset(edges), 0)
    return best[0]


if __name__ == "__main__":
    import networkx as nx
    G = nx.complete_graph(5)
    print("K5 min decomp:", min_decomp(5, list(G.edges())))
