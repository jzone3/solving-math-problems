"""Cross-check SAT decider against brute force on small Eulerian graphs."""
import random
import networkx as nx
from sat_decider import min_cycles_sat, decompose_le_k
from brute_min_decomp import min_decomp


def random_eulerian(n, p, rng):
    while True:
        G = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10**9))
        # make all degrees even: pair up odd-degree vertices, toggle path edges
        odd = [v for v in G.nodes if G.degree(v) % 2 == 1]
        rng.shuffle(odd)
        for i in range(0, len(odd), 2):
            u, v = odd[i], odd[i + 1]
            if G.has_edge(u, v):
                G.remove_edge(u, v)
            else:
                G.add_edge(u, v)
        G.remove_nodes_from([v for v in list(G.nodes) if G.degree(v) == 0])
        if G.number_of_nodes() >= 3 and nx.is_connected(G) and \
           all(G.degree(v) % 2 == 0 for v in G.nodes):
            G = nx.convert_node_labels_to_integers(G)
            return G


def verify_coloring(n, edges, coloring, k):
    """Independent check that a SAT-returned coloring is a valid <=k cycle decomp."""
    classes = {}
    for e, c in coloring.items():
        classes.setdefault(c, []).append(e)
    assert len(classes) <= k
    assert sum(len(v) for v in classes.values()) == len(edges)
    for c, es in classes.items():
        H = nx.Graph(es)
        assert all(d == 2 for _, d in H.degree()), f"class {c} not 2-regular"
        assert nx.is_connected(H), f"class {c} not connected"
    return True


if __name__ == "__main__":
    rng = random.Random(42)
    # known cases
    for nk in (5, 7, 9):
        G = nx.complete_graph(nk)
        e = list(G.edges())
        b = min_decomp(nk, e) if nk <= 7 else None
        s = min_cycles_sat(nk, e, nk)
        bound = (nk - 1) // 2
        print(f"K{nk}: brute={b} sat={s} bound={bound}", flush=True)
        assert s == bound and (b is None or b == s)
    # random Eulerian graphs
    for trial in range(30):
        n0 = rng.choice([6, 7, 8, 9])
        G = random_eulerian(n0, 0.5, rng)
        n, e = G.number_of_nodes(), list(G.edges())
        if len(e) > 22:
            continue
        b = min_decomp(n, e)
        s = min_cycles_sat(n, e, len(e) // 3 + 1)
        ok, col = decompose_le_k(n, e, s, return_model=True)
        assert ok and verify_coloring(n, e, col, s)
        status = "OK" if b == s else "MISMATCH"
        print(f"trial {trial}: n={n} m={len(e)} brute={b} sat={s} {status}", flush=True)
        assert b == s
    print("ALL CROSSCHECKS PASS")
