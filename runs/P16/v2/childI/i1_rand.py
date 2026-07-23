"""Random large-graph stress test of Conjecture I1 (sound resolvent
certificate), f2_rand-style: G(n,p), random regular +/- edges, K_{a,b} minus
edges, BA; prune to delta>=2 core.  kappa = 0.9, 0.99.
"""
import numpy as np
import networkx as nx
from common import build

rng = np.random.default_rng(20260723)
KAPPAS = [0.9, 0.99]
fails = {k: 0 for k in KAPPAS}
tot = 0
worst = {k: np.inf for k in KAPPAS}

def core2(g):
    g = nx.k_core(g, 2)
    if g.number_of_nodes() < 4 or not nx.is_connected(g):
        return None
    return g

cases = []
for rep in range(1000):
    n = rng.integers(12, 120)
    p = rng.uniform(0.03, 0.5)
    cases.append(nx.gnp_random_graph(int(n), float(p), seed=int(rng.integers(1 << 30))))
for rep in range(600):
    n = int(rng.integers(10, 100))
    r = int(rng.integers(3, min(9, n - 1)))
    if (n * r) % 2:
        n += 1
    g = nx.random_regular_graph(r, n, seed=int(rng.integers(1 << 30)))
    for _ in range(int(rng.integers(0, 6))):
        u, v = list(g.edges())[int(rng.integers(g.number_of_edges()))]
        g.remove_edge(u, v)
    cases.append(g)
for rep in range(300):
    a, b = int(rng.integers(3, 30)), int(rng.integers(3, 30))
    g = nx.complete_bipartite_graph(a, b)
    for _ in range(int(rng.integers(0, a * b // 3))):
        es = list(g.edges())
        g.remove_edge(*es[int(rng.integers(len(es)))])
    cases.append(g)
for rep in range(300):
    n = int(rng.integers(15, 120))
    m = int(rng.integers(2, 6))
    cases.append(nx.barabasi_albert_graph(n, m, seed=int(rng.integers(1 << 30))))

for g in cases:
    g = core2(g)
    if g is None:
        continue
    tot += 1
    A = nx.to_numpy_array(g)
    G = build(A)
    P = G["B"] / G["T"][:, None]
    d = G["d"]
    # sound upper bound: rho(P) <= min_K (max_i (P^K d)_i/d_i)^{1/K}
    rho0 = np.inf
    v = d.copy()
    scale = 0.0  # log of accumulated normalization
    k_ = 0
    for K in (1, 2, 4, 8, 16, 32, 64):
        while k_ < K:
            v = P @ v
            s = v.max()
            v /= s
            scale += np.log(s)
            k_ += 1
        logratio = (scale + np.log((v / d).max())) / K
        rho0 = min(rho0, np.exp(logratio))
    I = np.eye(G["n"])
    for k in KAPPAS:
        a = k / max(rho0, 1.0)
        h = np.linalg.solve(I - a * P, d)
        margin = (d - (1 - a) * h).min()
        worst[k] = min(worst[k], margin)
        if margin < -1e-9:
            fails[k] += 1
print(f"random stress: {tot} delta>=2 cores, "
      + ", ".join(f"kappa={k}: fails {fails[k]} worst {worst[k]:.3e}" for k in KAPPAS))
