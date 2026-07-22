#!/usr/bin/env python3
"""P08 V5 unified harness for Graffiti 39/40.

Computes, for a connected graph:
  dev_full  : population std over all n^2 entries of the distance matrix
              (the Roucairol-Cazenave 2025 encoding of "deviation")
  dev_off   : population std over the n(n-1) off-diagonal entries
  dev_pairs : population std over the n(n-1)/2 unordered pairs (== dev_off)
  n_pos / n_neg : adjacency inertia (counts with 1e-4 threshold, as in RC code)
  diam      : diameter

Score for conjecture 39: dev - n_pos; for 40: dev - n_neg.
Unified V5 score: dev - min(n_pos, n_neg)  (>0 would refute at least one).

Also checks the PROOF chain discovered in this run:
   dev_full <= diam/2  (Popoviciu, entries in [0, diam])
   min(n_pos, n_neg) >= floor((diam+1)/2)  (interlacing with induced geodesic P_{diam+1})
so dev - min(n_pos,n_neg) <= diam/2 - floor((diam+1)/2) <= 0.
"""
import sys
import numpy as np
import networkx as nx

EPS = 1e-4  # eigenvalue sign threshold, same as Roucairol-Cazenave


def invariants(G):
    n = G.number_of_nodes()
    D = np.zeros((n, n))
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    for v, dd in nx.all_pairs_shortest_path_length(G):
        for u, d in dd.items():
            D[idx[v], idx[u]] = d
    diam = int(D.max())
    full = D.ravel()
    off = D[~np.eye(n, dtype=bool)]
    dev_full = float(full.std())
    dev_off = float(off.std())
    A = nx.to_numpy_array(G, nodelist=nodes)
    ev = np.linalg.eigvalsh(A)
    n_pos = int((ev > EPS).sum())
    n_neg = int((ev < -EPS).sum())
    return dev_full, dev_off, n_pos, n_neg, diam


def check(G, where=""):
    """Returns unified score; asserts proof chain."""
    dev_full, dev_off, n_pos, n_neg, diam = invariants(G)
    n = G.number_of_nodes()
    score = max(dev_full, dev_off) - min(n_pos, n_neg)
    # proof chain checks
    assert dev_full <= diam / 2 + 1e-9, (where, "Popoviciu(full) fails", dev_full, diam)
    assert dev_off <= diam / 2 + 1e-9, (where, "Popoviciu(off) fails", dev_off, diam)
    if n >= 2:
        assert min(n_pos, n_neg) >= (diam + 1) // 2, (
            where, "interlacing lower bound fails", n_pos, n_neg, diam)
    return score


def main():
    rng = np.random.default_rng(8)
    worst = -1e9
    worst_desc = None
    tested = 0

    def note(G, desc):
        nonlocal worst, worst_desc, tested
        s = check(G, desc)
        tested += 1
        if s > worst:
            worst, worst_desc = s, desc
            print(f"new max score {s:.4f}  {desc}", flush=True)
        if s > 1e-6:
            print("REFUTATION CANDIDATE:", desc)
            print(nx.to_numpy_array(G).astype(int))
            sys.exit(123)

    # adversarial closed families
    for n in list(range(2, 200)) + [300, 500, 1000, 2000]:
        note(nx.path_graph(n), f"path n={n}")
    for n in range(3, 120):
        note(nx.cycle_graph(n), f"cycle n={n}")
    for n in range(2, 80):
        note(nx.complete_graph(n), f"K{n}")
    # brooms: path of length L with b pendant leaves at one end
    for L in range(3, 150, 7):
        for b in (2, 5, 10, 30):
            G = nx.path_graph(L)
            for i in range(b):
                G.add_edge(0, L + i)
            note(G, f"broom L={L} b={b}")
    # complete multipartite (small n_pos) with pendant path (stretch diameter)
    for parts in [(3, 3, 3), (5, 5), (10, 10), (4, 4, 4, 4), (20, 20)]:
        for tail in (0, 5, 20, 60):
            G = nx.complete_multipartite_graph(*parts)
            m = G.number_of_nodes()
            last = 0
            for i in range(tail):
                G.add_edge(last, m + i)
                last = m + i
            note(G, f"multipartite {parts} tail={tail}")
    # spiders / subdivided stars
    for legs in (3, 5, 10):
        for leglen in (5, 20, 60):
            G = nx.Graph()
            c = 0
            nid = 1
            for _ in range(legs):
                prev = c
                for _ in range(leglen):
                    G.add_edge(prev, nid)
                    prev = nid
                    nid += 1
            note(G, f"spider legs={legs} len={leglen}")
    # random trees, escalating n
    for n in (20, 50, 100, 200, 400, 800):
        for _ in range(60):
            G = nx.random_labeled_tree(n, seed=int(rng.integers(1 << 31)))
            note(G, f"random tree n={n}")
    # random caterpillars with periodic legs
    for spine in (30, 100, 300):
        for period in (1, 2, 3):
            G = nx.path_graph(spine)
            nid = spine
            for i in range(0, spine, period):
                G.add_edge(i, nid)
                nid += 1
            note(G, f"caterpillar spine={spine} period={period}")
    # random sparse connected non-trees
    for n in (20, 50, 100, 200):
        for extra in (1, 3, 10):
            for _ in range(30):
                G = nx.random_labeled_tree(n, seed=int(rng.integers(1 << 31)))
                cnt = 0
                while cnt < extra:
                    u, v = rng.integers(0, n, 2)
                    if u != v and not G.has_edge(u, v):
                        G.add_edge(int(u), int(v))
                        cnt += 1
                note(G, f"tree+{extra} edges n={n}")
    # random G(n,p) connected
    for n in (15, 30, 60, 120):
        for p in (0.05, 0.1, 0.3, 0.7):
            for _ in range(20):
                G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 31)))
                if nx.is_connected(G):
                    note(G, f"gnp n={n} p={p}")

    print(f"\ntested {tested} graphs; max unified score = {worst:.6f}  ({worst_desc})")
    print("NO REFUTATION (consistent with proof)")


if __name__ == "__main__":
    main()
