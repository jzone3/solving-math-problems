"""V3 exploration: test the interlacing + Popoviciu bound hypothesis.

Hypothesis (proof candidate for BOTH conjectures):
  Let G be connected, diameter d. A shortest u-v path (d=dist(u,v)) is an
  INDUCED path P_{d+1} (non-consecutive vertices non-adjacent, else shortcut).
  Its adjacency matrix is a principal submatrix of A(G), so by Cauchy
  interlacing  n+(G) >= n+(P_{d+1})  and  n-(G) >= n-(P_{d+1}).
  For P_{d+1}:  n+ = n- = floor((d+1)/2) >= d/2  (bipartite, symmetric spectrum).
  Meanwhile Popoviciu's inequality on variance: entries of D lie in [0,d], so
  dev(D) <= (d-0)/2 = d/2.
  Hence  dev(D) <= d/2 <= n+(G)  and  <= n-(G).   => both conjectures hold.

This script empirically checks:
  (A) margin39<0 and margin40<0 across exhaustive small graphs + random large,
  (B) the chain dev <= d/2 and n+ >= n+(geodesic) >= d/2 holds every time,
  (C) reports the largest observed margins (closest near-misses).
"""
import itertools
import numpy as np
import networkx as nx
from core import scores, dist_matrix, inertia, dev_of_D


def npos_path(k):
    """n+ of path on k vertices via closed form; also n-."""
    ev = np.array([2 * np.cos(j * np.pi / (k + 1)) for j in range(1, k + 1)])
    return int(np.sum(ev > 1e-9)), int(np.sum(ev < -1e-9))


def geodesic_len(G):
    """diameter d."""
    return nx.diameter(G)


def check_graph(G, tol=1e-6):
    s = scores(G, tol)
    d = s["diam"]
    # proof ingredients
    dev = s["dev"]
    npp, npm = npos_path(d + 1)
    ing = {
        "dev_le_d2": dev <= d / 2 + 1e-9,
        "npos_ge_pathpos": s["npos"] >= npp,
        "nneg_ge_pathneg": s["nneg"] >= npm,
        "pathpos_ge_d2": npp >= d / 2 - 1e-9,
        "pathneg_ge_d2": npm >= d / 2 - 1e-9,
    }
    return s, ing


def run_atlas(max_n=7):
    """All connected graphs up to max_n vertices via graph atlas."""
    from networkx.generators.atlas import graph_atlas_g
    worst39 = worst40 = -1e9
    w39g = w40g = None
    fails = []
    cnt = 0
    for G in graph_atlas_g():
        if G.number_of_nodes() < 2 or G.number_of_nodes() > max_n:
            continue
        if not nx.is_connected(G):
            continue
        cnt += 1
        s, ing = check_graph(G)
        if not all(ing.values()):
            fails.append((G.number_of_nodes(), dict(G.edges()), ing))
        if s["margin39"] > worst39:
            worst39, w39g = s["margin39"], (s, list(G.edges()))
        if s["margin40"] > worst40:
            worst40, w40g = s["margin40"], (s, list(G.edges()))
    print(f"atlas n<= {max_n}: {cnt} connected graphs")
    print(f"  worst (max) margin39 = {worst39:.4f}  {w39g[0]}")
    print(f"  worst (max) margin40 = {worst40:.4f}  {w40g[0]}")
    print(f"  proof-ingredient failures: {len(fails)}")
    return fails


if __name__ == "__main__":
    fails = run_atlas(7)
    for f in fails[:5]:
        print("FAIL", f)
