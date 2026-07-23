"""childD: random large-graph stress test of Conjecture D1 (K PSD, delta>=2).
Models: G(n,p) conditioned delta>=2 & connected; random regular +/- edges;
near-bipartite-regular (equality manifold perturbations); power-law-ish.
Usage: rand_psd.py SECONDS
"""
import numpy as np, sys, time, math
import networkx as nx

def K_mineig(G):
    A = nx.to_numpy_array(G)
    n = A.shape[0]
    d = A.sum(1); m = A @ d / d
    edges = [(i, j) for i in range(n) for j in range(i+1, n) if A[i, j]]
    E = len(edges)
    arg = np.array([2*(d[i]**2+d[j]**2) - 16*d[i]*d[j]/(m[i]+m[j]) + 4 for i, j in edges])
    R = np.zeros((n, E))
    for e, (i, j) in enumerate(edges):
        R[i, e] = R[j, e] = 1
    M = R.T @ (np.diag(d) + A - 4*np.eye(n)) @ R
    return np.linalg.eigvalsh(np.diag(arg - 4) - M)[0]

def gen(rng):
    t = rng.integers(0, 4)
    if t == 0:
        n = int(rng.integers(10, 40)); p = rng.uniform(0.1, 0.7)
        G = nx.gnp_random_graph(n, p, seed=int(rng.integers(1e9)))
    elif t == 1:
        n = int(rng.integers(10, 40)); d = int(rng.integers(3, min(8, n-1)))
        if (n*d) % 2: n += 1
        G = nx.random_regular_graph(d, n, seed=int(rng.integers(1e9)))
        for _ in range(int(rng.integers(0, 5))):
            u, v = rng.integers(0, n, 2)
            if u != v: G.add_edge(int(u), int(v))
    elif t == 2:
        d = int(rng.integers(3, 12))
        G = nx.complete_bipartite_graph(d, d)
        es = list(G.edges())
        for k in rng.choice(len(es), size=int(rng.integers(1, 3)), replace=False):
            G.remove_edge(*es[int(k)])
    else:
        n = int(rng.integers(10, 30))
        G = nx.barabasi_albert_graph(n, 2, seed=int(rng.integers(1e9)))
    return G

if __name__ == "__main__":
    secs = float(sys.argv[1])
    rng = np.random.default_rng(1)
    t0 = time.time(); cnt = 0; worst = (1e18, None)
    while time.time() - t0 < secs:
        G = gen(rng)
        if not nx.is_connected(G): continue
        if min(d for _, d in G.degree()) < 2: continue
        lam = K_mineig(G); cnt += 1
        if lam < worst[0]: worst = (lam, (G.number_of_nodes(), G.number_of_edges()))
        if lam < -1e-7:
            print("VIOLATION?", lam, nx.to_graph6_bytes(G))
    print(f"random graphs tested: {cnt}, min eig {worst[0]:.3e} at (n,m)={worst[1]}")
