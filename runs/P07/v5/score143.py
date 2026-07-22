"""Scorer for Graffiti conjecture 143: Var(positive adjacency eigenvalues) <= m / mu(D).

Two definitions of average distance mu:
  - 'rc'  : Roucairol-Cazenave encoding, mean over all n^2 ordered entries incl. diagonal.
  - 'pair': mean over the n(n-1) ordered pairs of distinct vertices (classical average distance).
A violation is Var * mu > m. Larger mu => easier; mu_pair > mu_rc, so violating the
'rc' form implies violating the 'pair' form as well.
"""
import numpy as np
from collections import deque


def bfs_all_dist_sum(adj_list, n):
    """Returns (sum of distances over ordered pairs, connected: bool)."""
    total = 0
    for s in range(n):
        dist = [-1] * n
        dist[s] = 0
        q = deque([s])
        seen = 1
        while q:
            u = q.popleft()
            for v in adj_list[u]:
                if dist[v] < 0:
                    dist[v] = dist[u] + 1
                    seen += 1
                    q.append(v)
        if seen != n:
            return 0, False
        total += sum(dist)
    return total, True


def stats143(A, eig_tol=1e-7):
    """A: numpy 0/1 symmetric adjacency. Returns dict with var, m, mu_rc, mu_pair, ratios."""
    n = A.shape[0]
    adj_list = [np.nonzero(A[i])[0].tolist() for i in range(n)]
    m = int(A.sum()) // 2
    dsum, conn = bfs_all_dist_sum(adj_list, n)
    if not conn:
        return None
    mu_rc = dsum / (n * n)
    mu_pair = dsum / (n * (n - 1))
    ev = np.linalg.eigvalsh(A)
    pos = ev[ev > eig_tol]
    p = len(pos)
    var = float(np.mean((pos - pos.mean()) ** 2)) if p > 0 else 0.0
    return dict(n=n, m=m, p=p, var=var, mu_rc=mu_rc, mu_pair=mu_pair,
                ratio_rc=var * mu_rc / m, ratio_pair=var * mu_pair / m)


def lollipop(a, ell):
    """Clique K_a with a path of ell extra vertices attached to one clique vertex."""
    n = a + ell
    A = np.zeros((n, n))
    A[:a, :a] = 1
    np.fill_diagonal(A, 0)
    prev = 0
    for i in range(a, n):
        A[prev, i] = A[i, prev] = 1
        prev = i
    return A


def dumbbell(a, ell, b):
    """K_a -- path of ell internal vertices -- K_b."""
    n = a + ell + b
    A = np.zeros((n, n))
    A[:a, :a] = 1
    A[a + ell:, a + ell:] = 1
    np.fill_diagonal(A, 0)
    chain = [0] + list(range(a, a + ell)) + [a + ell]
    for u, v in zip(chain, chain[1:]):
        A[u, v] = A[v, u] = 1
    return A


if __name__ == "__main__":
    best = None
    for n in [30, 50, 75, 100, 150, 200, 300, 400, 600, 800]:
        loc = None
        for a in range(3, n - 2):
            s = stats143(lollipop(a, n - a))
            if loc is None or s["ratio_rc"] > loc[0]:
                loc = (s["ratio_rc"], a, s)
        print(f"n={n}: best a={loc[1]} ratio_rc={loc[0]:.4f} ratio_pair={loc[2]['ratio_pair']:.4f} "
              f"var={loc[2]['var']:.2f} m={loc[2]['m']} mu_rc={loc[2]['mu_rc']:.3f} p={loc[2]['p']}")
