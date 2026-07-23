"""Debug the kappa=0.99 random failures: for each failing core, report
n, true rho(P), rho_bound(K=64), min eig of M (F2 check!), and whether ANY
alpha in a fine grid inside (0, 1/rho) satisfies R(alpha)."""
import numpy as np
import networkx as nx
from common import build

rng = np.random.default_rng(20260723)


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

for gi, g in enumerate(cases):
    g = core2(g)
    if g is None:
        continue
    A = nx.to_numpy_array(g)
    G = build(A)
    P = G["B"] / G["T"][:, None]
    d = G["d"]
    rho0 = np.inf
    v = d.copy(); scale = 0.0; k_ = 0
    for K in (1, 2, 4, 8, 16, 32, 64):
        while k_ < K:
            v = P @ v; s = v.max(); v /= s; scale += np.log(s); k_ += 1
        rho0 = min(rho0, np.exp((scale + np.log((v / d).max())) / K))
    I = np.eye(G["n"])
    a = 0.99 / max(rho0, 1.0)
    h = np.linalg.solve(I - a * P, d)
    if (d - (1 - a) * h).min() >= -1e-9:
        continue
    rho = max(abs(np.linalg.eigvals(P)))
    evmin = np.linalg.eigvalsh(G["M"])[0]
    anyok = None
    for aa in np.linspace(a, 0.999999 / max(rho, 1.0), 400):
        hh = np.linalg.solve(I - aa * P, d)
        if (d - (1 - aa) * hh).min() >= -1e-12 and (hh > 0).all():
            anyok = aa
            break
    print(f"case {gi}: n={G['n']} rho={rho:.10f} rho0_K64={rho0:.10f} "
          f"minEigM={evmin:.3e} kappa0.99 margin={(d-(1-a)*h).min():.3e} "
          f"first working alpha={anyok} (norm {None if anyok is None else anyok*rho:.8f})")
