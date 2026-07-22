"""V3 spectral-design sweep (the assigned attack): cores with forced small
inertia (complete multipartite, joins) stretched by pendant paths; plus
control families (paths, brooms, double brooms, spiders, random trees,
random graphs). Records best (largest) margin39/margin40 seen, and checks
the proof-chain (dev <= diam/2 <= n+, n-) on every instance.
"""
import random
import numpy as np
import networkx as nx
from core import scores
from explore import npos_path

best = {"m39": (-1e9, None), "m40": (-1e9, None)}
viol = []
count = 0


def note(G, tag):
    global count
    count += 1
    s = scores(G)
    d = s["diam"]
    npp, npm = npos_path(d + 1)
    ok = (s["dev"] <= d / 2 + 1e-9 and s["npos"] >= npp and s["nneg"] >= npm)
    if not ok:
        viol.append((tag, s))
    if s["margin39"] > best["m39"][0]:
        best["m39"] = (s["margin39"], (tag, s))
    if s["margin40"] > best["m40"][0]:
        best["m40"] = (s["margin40"], (tag, s))
    if s["margin39"] > 0 or s["margin40"] > 0:
        print("!!! COUNTEREXAMPLE", tag, s)
    return s


def multipartite_with_tail(parts, tail_len, n_tails=1):
    """complete multipartite core + pendant path(s) attached to one vertex."""
    G = nx.complete_multipartite_graph(*parts)
    G = nx.convert_node_labels_to_integers(G)
    n0 = G.number_of_nodes()
    nid = n0
    anchors = list(range(min(n_tails, n0)))
    for a in anchors:
        prev = a
        for _ in range(tail_len):
            G.add_edge(prev, nid)
            prev = nid
            nid += 1
    return G


def double_broom(path_len, a, b):
    G = nx.path_graph(path_len)
    nid = path_len
    for _ in range(a):
        G.add_edge(0, nid); nid += 1
    for _ in range(b):
        G.add_edge(path_len - 1, nid); nid += 1
    return G


def spider(legs, leg_len):
    G = nx.Graph(); G.add_node(0)
    nid = 1
    for _ in range(legs):
        prev = 0
        for _ in range(leg_len):
            G.add_edge(prev, nid); prev = nid; nid += 1
    return G


def main():
    random.seed(8)
    # 1. complete multipartite cores (n+ small core) + tails
    for k in [2, 3, 4, 6]:
        for psize in [1, 2, 3, 5, 10, 20]:
            for tail in [0, 2, 5, 10, 20, 40, 80]:
                for ntails in [1, 2]:
                    parts = [psize] * k
                    G = multipartite_with_tail(parts, tail, ntails)
                    if G.number_of_nodes() > 400:
                        continue
                    note(G, f"K_{parts}+{ntails}x tail{tail}")
    # unbalanced multipartite
    for parts in [[1, 1, 50], [1, 5, 25], [2, 2, 100], [1, 1, 1, 80], [30, 30], [1, 99]]:
        for tail in [0, 5, 15, 40]:
            note(multipartite_with_tail(parts, tail), f"K_{parts}+tail{tail}")
    # 2. joins of graphs with pendant paths: K_m join empty, stretched
    # 3. brooms / double brooms (near-path, spectrally degenerate ends)
    for pl in [5, 10, 20, 40, 80]:
        for a in [0, 3, 10, 30]:
            for b in [0, 3, 10, 30]:
                if a == b == 0:
                    continue
                note(double_broom(pl, a, b), f"dbroom({pl},{a},{b})")
    # 4. spiders
    for legs in [3, 5, 10, 30]:
        for ll in [2, 5, 15, 40]:
            note(spider(legs, ll), f"spider({legs},{ll})")
    # 5. paths & random trees to n=1000
    for n in [100, 300, 600, 1000]:
        note(nx.path_graph(n), f"P_{n}")
        for _ in range(3):
            note(nx.random_labeled_tree(n), f"rtree{n}")
    # 6. random connected graphs
    for n in [20, 50, 100]:
        for p in [0.05, 0.1, 0.3]:
            for _ in range(5):
                G = nx.gnp_random_graph(n, p, seed=random.randrange(10**9))
                if nx.is_connected(G):
                    note(G, f"gnp({n},{p})")

    print(f"\nchecked {count} graphs; proof-chain violations: {len(viol)}")
    for v in viol[:5]:
        print("VIOL", v)
    for key in ["m39", "m40"]:
        m, info = best[key]
        print(f"best {key}: {m:.4f}  <- {info[0]}  {info[1]}")


if __name__ == "__main__":
    main()
