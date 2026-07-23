"""Round 7b: quantify the blowup gap for genuinely non-Turan directions.

For every connected pattern H, |H| <= 7, omega >= 3, maximize f_H(x) subject to the
support of x inducing a NON-complete-multipartite subgraph (enforced by post-hoc
classification: maximize freely, then if the support-induced subgraph is complete
multipartite, penalize those supports by restarting from interior points and keeping
the best x whose support is non-CM). Reports the largest such f (the 'non-Turan gap'):
how close any non-Turan blowup direction gets to equality.
"""
import subprocess
import numpy as np
from blowup import g6_to_adj, f_and_grad
from hybrid import is_complete_multipartite, opt_x
from core import max_clique

def support_class(A, x, tol=1e-3):
    idx = np.nonzero(x > tol)[0]
    if len(idx) < 2:
        return True
    return is_complete_multipartite(A[np.ix_(idx, idx)])

def constrained_max(A, coef, rng, restarts=40, iters=1200):
    n = A.shape[0]
    best = -1e9
    for r in range(restarts):
        x = rng.dirichlet(np.ones(n) * rng.uniform(0.5, 5))
        lr = 0.04
        floor = 10 ** rng.uniform(-3.5, -1.3)  # keep x interior: enforce x_i >= floor
        for t in range(iters):
            f, g = f_and_grad(A, x, coef)
            g = g - g.mean()
            x = np.maximum(x + lr * g, floor)
            x /= x.sum()
        f, _ = f_and_grad(A, x, coef)
        if not support_class(A, x) and f > best:
            best = f
    return best

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    results = []
    for n in [5, 6, 7]:
        out = subprocess.run(["nauty-geng", "-cq", str(n)], capture_output=True).stdout.splitlines()
        for ln in out:
            A = g6_to_adj(ln.strip(), n)
            w = max_clique(A)
            if w < 3 or w >= n or is_complete_multipartite(A):
                continue
            f = constrained_max(A, 1 - 1 / w, rng, restarts=12, iters=600)
            results.append((f, ln.strip().decode(), n, w))
        results.sort(key=lambda t: -t[0])
        print(f"after n={n}: top non-Turan-direction gaps:", flush=True)
        for f, g6, nn, w in results[:8]:
            print(f"  {g6} (n={nn}, w={w}): max interior/non-CM f = {f:+.6f}")
    print("NONTURAN GAP SUMMARY: largest =", results[0][0])
