"""P16 v2 — realization search: random simple graphs with near-(bipartite-)regular
degree sequences.  Rationale: all prior quotient searches lower-bound mu(G) by
lam_max(L_B); for a fixed equitable structure the ACTUAL mu of a realization can be
strictly larger while the RHS (a function of (d_i, m_i) only) is unchanged or barely
changed.  Floats for screening only; any hit goes to verify_p16.py.

Usage: python3 realization_search.py <44|46> <seconds> [seed]
"""
import sys
import time
import random
import numpy as np
import networkx as nx
from search_common import mu, rhs_graph, rhs44_edge, rhs46_edge


def near_regular_bipartite(nl, nr, d, flips, rng):
    """d-regular-ish bipartite graph on nl+nr vertices, then `flips` random edge
    swaps/removals/additions to perturb degrees by +-1."""
    if nl * d % 1:
        return None
    try:
        G = nx.bipartite.configuration_model(
            [d] * nl, [d * nl // nr] * nr, seed=rng.randrange(1 << 30))
    except Exception:
        return None
    G = nx.Graph(G)
    G.remove_edges_from(nx.selfloop_edges(G))
    nodes = list(G.nodes())
    for _ in range(flips):
        op = rng.random()
        u, v = rng.sample(nodes, 2)
        if op < 0.5:
            if G.has_edge(u, v):
                G.remove_edge(u, v)
            else:
                G.add_edge(u, v)
        else:
            edges = list(G.edges())
            if edges:
                a, b = rng.choice(edges)
                G.remove_edge(a, b)
    G.remove_nodes_from([n for n in G.nodes() if G.degree(n) == 0])
    if G.number_of_nodes() < 2 or not nx.is_connected(G):
        comps = sorted(nx.connected_components(G), key=len)
        if not comps:
            return None
        G = G.subgraph(comps[-1]).copy()
    if G.number_of_nodes() < 2:
        return None
    return nx.to_numpy_array(G).astype(np.int8)


def main():
    bound = int(sys.argv[1])
    seconds = float(sys.argv[2])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    fn = rhs44_edge if bound == 44 else rhs46_edge
    rng = random.Random(seed)
    t0 = time.time()
    best = 1e18
    trials = 0
    while time.time() - t0 < seconds:
        trials += 1
        d = rng.choice([3, 4, 5, 6, 8, 10, 12, 16, 20, 30])
        nl = rng.choice([d, d + 1, d + 2, 2 * d, 3 * d])
        nr = nl
        flips = rng.choice([0, 1, 2, 3, 5, 8])
        A = near_regular_bipartite(nl, nr, d, flips, rng)
        if A is None:
            continue
        gap = rhs_graph(A, fn) - mu(A)
        if gap < best:
            best = gap
            if gap < -1e-7:
                np.save(f"realization_violation_{bound}.npy", A)
                print("VIOLATION", bound, gap, A.shape, flush=True)
        if trials % 2000 == 0:
            print(f"t={time.time()-t0:.0f}s trials={trials} best_gap={best:.3e}",
                  flush=True)
    print(f"DONE bound={bound} trials={trials} best_gap={best:.6e}")


if __name__ == "__main__":
    main()
