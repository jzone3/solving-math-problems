"""exp9: (B)/(W=) verification on random graphs up to n = 60 (exact)."""
import random
import numpy as np
from common import edge_env


def rand_connected(n, rng):
    kind = rng.randrange(4)
    A = np.zeros((n, n), dtype=np.int64)
    # random spanning tree
    perm = list(range(n)); rng.shuffle(perm)
    for t in range(1, n):
        u = perm[t]; v = perm[rng.randrange(t)]
        A[u, v] = A[v, u] = 1
    if kind == 0:      # tree only
        pass
    elif kind == 1:    # ER extra edges
        p = rng.uniform(0.02, 0.3)
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    A[i, j] = A[j, i] = 1
    elif kind == 2:    # dense core + pendants
        c = rng.randrange(4, min(10, n))
        for i in range(c):
            for j in range(i + 1, c):
                if rng.random() < 0.8:
                    A[i, j] = A[j, i] = 1
    else:              # BA-ish
        for j in range(1, n):
            deg = A.sum(1)[:j] + 1
            for _ in range(min(j, 3)):
                i = rng.choices(range(j), weights=deg.tolist())[0]
                A[i, j] = A[j, i] = 1
    return A


def main():
    rng = random.Random(20260723)
    minB = None
    for trial in range(400):
        n = rng.randrange(10, 61)
        A = rand_connected(n, rng)
        d, m, E, s, z1, zs, a44, rho0, rho1, AL = edge_env(A)
        for a in range(len(E)):
            if z1[a] > rho0[a]:
                val = rho0[a] * (s[a] - 3) + 3 * z1[a] - zs[a]
                if minB is None or val < minB:
                    minB = val
                if val <= 0:
                    print("VIOLATION B", trial, n, a, val, flush=True)
            elif z1[a] == rho0[a] and zs[a] > s[a] * z1[a]:
                print("VIOLATION W=", trial, n, a, flush=True)
        if trial % 50 == 0:
            print("...", trial, "minB", minB, flush=True)
    print("DONE 400 random graphs; min B-margin =", minB)


if __name__ == "__main__":
    main()
