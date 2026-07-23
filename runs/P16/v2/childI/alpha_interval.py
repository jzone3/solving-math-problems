"""Structure of {alpha in (0,1/rho): R(alpha) holds},
R(alpha): (1-alpha)(I-alpha P)^{-1} d <= d.

Empirics on all n<=8 graphs: is the set an interval [alpha*(G), 1/rho)?
Report max over graphs of alpha* (relative to 1/rho0), and check
monotonicity violations on a fine grid.
"""
import sys
import numpy as np
from common import g6_to_adj, build, geng

nmax = int(sys.argv[1]) if len(sys.argv) > 1 else 8
grid = np.linspace(0.01, 0.999, 200)
worst_astar = -1.0
worst_g = None
nonmono = 0
for n in range(3, nmax + 1):
    for g6 in geng(n):
        G = build(g6_to_adj(g6))
        P = G["B"] / G["T"][:, None]
        d = G["d"]
        rho = max(abs(np.linalg.eigvals(P)))
        I = np.eye(G["n"])
        ok = []
        for a in grid:
            if a * rho >= 0.9999:
                break
            h = np.linalg.solve(I - a * P, d)
            ok.append(((1 - a) * h <= d + 1e-9).all())
        ok = np.array(ok)
        if not ok.any():
            print("NEVER OK", g6)
            continue
        first = np.argmax(ok)
        if not ok[first:].all():
            nonmono += 1
        astar = grid[first] * rho  # normalized position in (0,1)
        if astar > worst_astar:
            worst_astar, worst_g = astar, g6
print(f"n<={nmax}: worst normalized alpha* = {worst_astar:.4f} at {worst_g}, "
      f"non-monotone (holes) graphs: {nonmono}")
