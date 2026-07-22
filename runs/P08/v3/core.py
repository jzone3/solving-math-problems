"""Core harness for P08 (Graffiti 39/40).

Definitions (matched to reference impl RoucairolMilo/refutationGBR,
src/models/conjectures/GenerateGraph.rs + invariants.rs):

  D        = distance matrix of connected G (d(i,i)=0), n x n.
  dev(D)   = POPULATION standard deviation of all n^2 entries of D
             (mean over n^2 entries, variance dividing by n^2, then sqrt).
             This includes the n diagonal zeros.
  n+(G)    = number of adjacency eigenvalues > +tol.
  n-(G)    = number of adjacency eigenvalues < -tol.

Conjecture 39:  dev(D) <= n+(G).   Refuted if dev(D) > n+(G).
Conjecture 40:  dev(D) <= n-(G).   Refuted if dev(D) > n-(G).

Both open (Roucairol-Cazenave ECAI 2025 Table 1, rows 39O/40O; searched
size 50, any & tree). Original source Favaron-Maheo-Sacle, Discrete Math.
111 (1993) 197-220 (Graffiti II).
"""
import numpy as np
import networkx as nx


def dist_matrix(G):
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    idx = {u: i for i, u in enumerate(nodes)}
    D = np.zeros((n, n), dtype=float)
    lengths = dict(nx.all_pairs_shortest_path_length(G))
    for u, dd in lengths.items():
        for v, d in dd.items():
            D[idx[u], idx[v]] = d
    return D


def dev_of_D(D):
    x = D.reshape(-1)
    m = x.mean()
    var = np.mean((x - m) ** 2)
    return float(np.sqrt(var))


def dev_from_graph(G):
    return dev_of_D(dist_matrix(G))


def inertia(G, tol=1e-6):
    A = nx.to_numpy_array(G, dtype=float)
    ev = np.linalg.eigvalsh(A)
    npos = int(np.sum(ev > tol))
    nneg = int(np.sum(ev < -tol))
    nzero = len(ev) - npos - nneg
    return npos, nneg, nzero, ev


def scores(G, tol=1e-6):
    """Return dict with dev, n+, n-, and margins for conj 39 and 40.
    margin39 = dev - n+  (>0 refutes 39); margin40 = dev - n- (>0 refutes 40)."""
    if not nx.is_connected(G):
        raise ValueError("graph not connected")
    D = dist_matrix(G)
    dev = dev_of_D(D)
    npos, nneg, nzero, ev = inertia(G, tol)
    return {
        "n": G.number_of_nodes(),
        "m": G.number_of_edges(),
        "dev": dev,
        "npos": npos,
        "nneg": nneg,
        "nzero": nzero,
        "diam": int(D.max()),
        "margin39": dev - npos,
        "margin40": dev - nneg,
    }


if __name__ == "__main__":
    # sanity: paths, cycles, complete multipartite
    for n in [3, 5, 8, 13, 21, 34, 50, 100]:
        s = scores(nx.path_graph(n))
        print(f"P_{n}: dev={s['dev']:.4f} n+={s['npos']} n-={s['nneg']} "
              f"m39={s['margin39']:.4f} m40={s['margin40']:.4f} diam={s['diam']}")
    print("---")
    for n in [4, 5, 8, 12, 17, 21, 25]:
        s = scores(nx.cycle_graph(n))
        print(f"C_{n}: dev={s['dev']:.4f} n+={s['npos']} n-={s['nneg']} "
              f"m39={s['margin39']:.4f} m40={s['margin40']:.4f}")
