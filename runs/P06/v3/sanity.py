import numpy as np, networkx as nx, random, sys
sys.path.insert(0, '.')
from lib_p06 import dev2_exact, randic_mp, degrees_from_edges

# 1) trace-identity dev^2 vs eigensolve dev^2 on random graphs
for trial in range(200):
    n = random.randint(2, 15)
    p = random.random()
    G = nx.gnp_random_graph(n, p, seed=trial)
    L = nx.laplacian_matrix(G).todense().astype(float)
    ev = np.linalg.eigvalsh(L)
    dev2_eig = float(np.mean((ev - ev.mean()) ** 2))
    d2 = dev2_exact(n, [d for _, d in G.degree()])
    assert abs(dev2_eig - float(d2)) < 1e-9, (n, dev2_eig, float(d2))
print("identity check PASS (200 random graphs)")

# 2) K_t + (t-2) isolated vertices: dev == R == t/2 exactly
from fractions import Fraction
for t in range(3, 60):
    n = 2 * (t - 1)
    degs = [t - 1] * t + [0] * (t - 2)
    d2 = dev2_exact(n, degs)
    assert d2 == Fraction(t * t, 4), (t, d2)
    # R of K_t = C(t,2)/(t-1) = t/2 exactly
print("equality family K_t + (t-2)K_1: dev = R = t/2 exact PASS")
