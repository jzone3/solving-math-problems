"""Sanity-check spectra.py closed forms against brute-force numpy eigensolves."""
import numpy as np
import networkx as nx
from fractions import Fraction
import sys
sys.path.insert(0, '.')
from spectra import (empty_graph, complete_graph, join, complement, kneser, johnson,
                     hamming, complete_multipartite, threshold_graph, brouwer_deficits)


def numeric_spec(G):
    L = nx.laplacian_matrix(G).toarray().astype(float)
    return sorted(np.linalg.eigvalsh(L), reverse=True)


def compare(spec, G, name):
    ex = []
    for v, mult in spec.eigs:
        ex += [float(v)] * mult
    num = numeric_spec(G)
    assert len(ex) == len(num), (name, len(ex), len(num))
    err = max(abs(a - b) for a, b in zip(ex, num))
    assert err < 1e-8, (name, err)
    assert spec.m == G.number_of_edges(), (name, spec.m, G.number_of_edges())
    spec.check_sum()
    print(f"OK {name}: n={spec.n} m={spec.m} maxerr={err:.1e}")


compare(complete_graph(7), nx.complete_graph(7), "K7")
compare(complete_multipartite([3, 4, 5]), nx.complete_multipartite_graph(3, 4, 5), "K345")
compare(kneser(5, 2), nx.petersen_graph(), "Kneser(5,2)=Petersen")
compare(kneser(7, 3), nx.kneser_graph(7, 3), "Kneser(7,3)")
from itertools import combinations
def johnson_graph(nn, k):
    G = nx.Graph()
    verts = list(combinations(range(nn), k))
    G.add_nodes_from(verts)
    for a, b in combinations(verts, 2):
        if len(set(a) & set(b)) == k - 1:
            G.add_edge(a, b)
    return G
compare(johnson(6, 3), johnson_graph(6, 3), "Johnson(6,3)")
compare(hamming(3, 2), nx.hypercube_graph(3), "Hamming(3,2)=Q3")

# join sanity: join(C-like) -- use complete_multipartite vs manual join
g1 = nx.complete_graph(4)
g2 = nx.empty_graph(3)
gj = nx.complete_multipartite_graph(1, 1, 1, 1, 3)  # K4 join empty(3)
compare(join(complete_graph(4), empty_graph(3)), gj, "K4 v E3")

# complement sanity
sp = complement(kneser(5, 2))
compare(sp, nx.complement(nx.petersen_graph()), "complement(Petersen)=J(5,2)")

# threshold graph equality check: deficits must be >=0 with equality at clique-related t
seq = [1, 0, 1, 1, 0, 1]
sp = threshold_graph(seq)
G = nx.empty_graph(1)
for b in seq:
    if b:
        Gn = nx.Graph(G)
        v = G.number_of_nodes()
        Gn.add_node(v)
        for u in list(G.nodes):
            Gn.add_edge(u, v)
        G = Gn
    else:
        G.add_node(G.number_of_nodes())
compare(sp, G, "threshold 101101")
ds = brouwer_deficits(sp)
assert all(d >= 0 for _, d in ds), ds
assert any(d == 0 for _, d in ds), ds
print("threshold deficits:", [(t, str(d)) for t, d in ds])
print("ALL SANITY PASS")
