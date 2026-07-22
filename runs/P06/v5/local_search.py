"""Hill-climbing / annealed edge-flip search maximizing violation scores.

129:  score = sqrt(Var(deg)+mean(deg)) - R   (degree-based identity, O(n^2)/eval)
698A: score = ||negative adjacency eigenvalues||_2 - R

Seeds: equality families (K_k u (k-2)K_1 for 129; K_{a,b} for 698A), stars,
random graphs. Simulated annealing on single edge flips.

Usage: python3 local_search.py <conj:129|698> <n> <restarts> <iters> [seed]
"""

import sys
import numpy as np

rng = np.random.default_rng(12345 if len(sys.argv) < 6 else int(sys.argv[5]))


def randic(A):
    d = A.sum(axis=1).astype(float)
    i, j = np.nonzero(np.triu(A, 1))
    return float(np.sum(1.0 / np.sqrt(d[i] * d[j])))


def score129(A):
    n = len(A)
    d = A.sum(axis=1).astype(float)
    if d.sum() == 0:
        return -1e9
    dev2 = np.sum(d * (d + 1)) / n - (d.sum() / n) ** 2
    return float(np.sqrt(dev2)) - randic(A)


def score698(A):
    d = A.sum(axis=1)
    if d.sum() == 0:
        return -1e9
    lam = np.linalg.eigvalsh(A.astype(float))
    sm = float(np.sqrt(np.sum(lam[lam < 0] ** 2)))
    return sm - randic(A)


def seed_graph(n, kind):
    A = np.zeros((n, n), dtype=np.int8)
    if kind == 0:  # K_k u (k-2)K_1 with k = n//2+1
        k = n // 2 + 1
        A[:k, :k] = 1
        np.fill_diagonal(A, 0)
    elif kind == 1:  # star
        A[0, 1:] = A[1:, 0] = 1
    elif kind == 2:  # complete bipartite balanced
        a = n // 2
        A[:a, a:] = 1
        A[a:, :a] = 1
    elif kind == 3:  # random G(n, p)
        p = rng.uniform(0.05, 0.6)
        U = rng.random((n, n)) < p
        A = np.triu(U, 1).astype(np.int8)
        A = A + A.T
    elif kind == 4:  # complete bipartite skewed
        a = max(1, n // 5)
        A[:a, a:] = 1
        A[a:, :a] = 1
    return A


def anneal(score, n, iters, kind):
    A = seed_graph(n, kind)
    s = score(A)
    best, bestA = s, A.copy()
    T0, T1 = 0.05, 1e-4
    for t in range(iters):
        T = T0 * (T1 / T0) ** (t / iters)
        i, j = rng.integers(0, n, 2)
        if i == j:
            continue
        A[i, j] ^= 1
        A[j, i] ^= 1
        s2 = score(A)
        if s2 >= s or rng.random() < np.exp((s2 - s) / T):
            s = s2
            if s > best:
                best, bestA = s, A.copy()
        else:
            A[i, j] ^= 1
            A[j, i] ^= 1
    return best, bestA


def adj_to_g6(A):
    n = len(A)
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(int(A[i, j]))
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return "".join(out)


def main():
    conj, n, restarts, iters = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    score = score129 if conj == "129" else score698
    gbest, gbestA = -1e9, None
    for r in range(restarts):
        kind = r % 5
        b, A = anneal(score, n, iters, kind)
        if b > gbest:
            gbest, gbestA = b, A
    print(f"conj={conj} n={n} best={gbest:+.8f} g6={adj_to_g6(gbestA)}")
    if gbest > 1e-9:
        print("VIOLATION-CANDIDATE")
        np.save(f"candidate_{conj}_{n}.npy", gbestA)


if __name__ == "__main__":
    main()
