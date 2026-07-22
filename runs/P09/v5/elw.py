"""Attack the Elphick-Linz-Wocjan generalization (arXiv:2101.05229, Conj. 2):
sum of squares of the min(omega, n+) largest (positive) eigenvalues <= 2m(1-1/omega).
Refuting it (without refuting BN) is still a publishable near-miss.

Score = sum_{i<=omega, lam_i>0} lam_i^2 - 2m(1-1/omega).

Usage: python3 elw.py families | anneal <n> <restarts> <steps> <seed>
"""
import sys, json
import numpy as np
from core import turan_graph, union, join, max_clique

def elw_score(A, w=None):
    n = A.shape[0]
    if w is None:
        w = max_clique(A)
    if w >= n:
        return None, w
    lam = np.linalg.eigvalsh(A)[::-1]
    s = sum(l * l for l in lam[:w] if l > 0)
    return s - 2 * (A.sum() / 2) * (1 - 1 / w), w

def families():
    best = (-1e9, None)
    def rep(name, A):
        nonlocal best
        s, w = elw_score(A)
        if s is not None and s > best[0]:
            best = (s, name)
        if s is not None and s > -0.05:
            print(f"near-tight {name} elw={s:+.6f} w={w}")
    for r in [3, 4, 5]:
        for a in [1, 2, 3]:
            for b in [1, 2, 3]:
                rep(f"T({a*r},{r})uT({b*r},{r})", union(turan_graph(a * r, r), turan_graph(b * r, r)))
    # unions of MANY balanced Turan graphs: omega components each tight
    for r in [3, 4, 5]:
        for cnt in [3, 4, 5]:
            A = turan_graph(2 * r, r)
            for _ in range(cnt - 1):
                A = union(A, turan_graph(2 * r, r))
            rep(f"{cnt}x T({2*r},{r})", A)
    for w in [4, 5, 6]:
        K = np.ones((w, w)) - np.eye(w)
        A = K.copy()
        for cnt in [2, 3, 4, 5, 6]:
            A = union(A, K)
            rep(f"{cnt}x K{w}", A)
    print("ELW families best:", best)

def anneal(n, restarts, steps, seed):
    rng = np.random.default_rng(seed)
    gb = -1e9
    for r in range(restarts):
        # seed: union of several cliques (tight for ELW when count <= omega)
        w = int(rng.integers(3, 7))
        K = np.ones((w, w)) - np.eye(w)
        A = K.copy()
        while A.shape[0] + w <= n:
            A = union(A, K)
        pad = n - A.shape[0]
        B = np.zeros((n, n)); B[:A.shape[0], :A.shape[0]] = A; A = B
        s, _ = elw_score(A); s = s if s is not None else -1e9
        best, bestA = s, A.copy()
        T0, T1 = 0.8, 0.005
        for t in range(steps):
            T = T0 * (T1 / T0) ** (t / steps)
            i, j = rng.integers(0, n, 2)
            if i == j: continue
            A[i, j] = A[j, i] = 1 - A[i, j]
            s2, _ = elw_score(A)
            if s2 is None: s2 = -1e9
            if s2 >= s or rng.random() < np.exp((s2 - s) / T):
                s = s2
                if s > best: best, bestA = s, A.copy()
            else:
                A[i, j] = A[j, i] = 1 - A[i, j]
        flag = " ***POSITIVE***" if best > 1e-9 else ""
        print(f"ELW n={n} restart={r} best={best:+.6f}{flag}", flush=True)
        if best > 1e-9:
            edges = [(int(i), int(j)) for i in range(n) for j in range(i + 1, n) if bestA[i, j]]
            json.dump({"n": n, "edges": edges, "elw_score": best}, open(f"elw_witness_n{n}_{seed}.json", "w"))
        gb = max(gb, best)
    print(f"ELW GLOBAL BEST n={n}: {gb:+.6f}")

if __name__ == "__main__":
    if sys.argv[1] == "families":
        families()
    else:
        anneal(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
