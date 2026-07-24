#!/usr/bin/env python3
"""Numerical sanity checks of Kumar-Pragada arXiv:2607.19817 (22 Jul 2026),
which proves Fajtlowicz's conjecture E(G) >= 2(n - alpha(G)) and thereby
resolves WoW 20 & 21 (E >= 2 max{n+, n-} via the Cvetkovic inertia bound).

Checks on random graphs:
  (1) Lemma 2.2 (neighbourhood deletion): n*E(G) >= 4m + sum_v E(G - N[v])
  (2) Theorem 1.2: E(G) >= 2(n - alpha(G))
  (3) Corollary: E(G) >= 2*max(n+, n-)  [= WoW 20 & 21]
"""
import numpy as np
import networkx as nx

rng = np.random.default_rng(42)
ZTOL = 1e-8

def energy(A):
    return np.abs(np.linalg.eigvalsh(A)).sum() if len(A) else 0.0

fails = 0
for t in range(400):
    n = int(rng.integers(2, 16))
    p = rng.uniform(0.1, 0.9)
    G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1 << 30)))
    A = nx.to_numpy_array(G)
    E = energy(A)
    m = G.number_of_edges()
    # (1) Lemma 2.2
    tot = 0.0
    for v in G.nodes():
        keep = [u for u in G.nodes() if u != v and not G.has_edge(u, v)]
        tot += energy(nx.to_numpy_array(G.subgraph(keep)))
    if n * E < 4 * m + tot - 1e-7:
        print("LEMMA 2.2 FAIL", t); fails += 1
    # (2) Theorem 1.2
    alpha = len(nx.max_weight_clique(nx.complement(G), weight=None)[0])
    if E < 2 * (n - alpha) - 1e-7:
        print("THM 1.2 FAIL", t); fails += 1
    # (3) corollary = WoW 20 & 21
    ev = np.linalg.eigvalsh(A)
    npos = (ev > ZTOL).sum(); nneg = (ev < -ZTOL).sum()
    if E < 2 * max(npos, nneg) - 1e-7:
        print("COROLLARY FAIL", t); fails += 1
print("checks done; failures:", fails)
