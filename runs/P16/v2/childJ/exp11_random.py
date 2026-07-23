"""childJ exp11: pooled envelope over random larger graphs (n up to 80):
Erdos-Renyi (various p), Barabasi-Albert, random trees, graphs with planted
dense core + pendant paths (the hard-instance shape). Saves env npz.
Usage: exp11_random.py seed count out.npz
"""
import sys

import numpy as np

from exp10_bigpool import process, RHO


def rand_graph(rng):
    kind = rng.integers(0, 4)
    n = int(rng.integers(8, 60))
    A = np.zeros((n, n))
    if kind == 0:  # ER
        p = rng.uniform(0.05, 0.7)
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < p:
                    A[i, j] = A[j, i] = 1
    elif kind == 1:  # BA-ish preferential attachment
        mdeg = int(rng.integers(1, 5))
        deg = np.zeros(n)
        for v in range(1, n):
            k = min(v, mdeg)
            w = deg[:v] + 1
            tg = rng.choice(v, size=k, replace=False, p=w / w.sum())
            for u in tg:
                A[v, u] = A[u, v] = 1
                deg[u] += 1
                deg[v] += 1
    elif kind == 2:  # random tree (Prufer-ish random attachment)
        for v in range(1, n):
            u = int(rng.integers(0, v))
            A[v, u] = A[u, v] = 1
    else:  # clique core + pendant paths/leaves
        k = int(rng.integers(3, 10))
        n = k + int(rng.integers(3, 30))
        A = np.zeros((n, n))
        for i in range(k):
            for j in range(i + 1, k):
                A[i, j] = A[j, i] = 1
        for v in range(k, n):
            u = int(rng.integers(0, v)) if rng.random() < .5 else int(rng.integers(0, k))
            A[v, u] = A[u, v] = 1
    # ensure connected: attach isolated/components crudely
    d = A.sum(1)
    for v in np.where(d == 0)[0]:
        A[v, 0] = A[0, v] = 1
    # connectivity check via BFS; if disconnected, link components
    n = A.shape[0]
    seen = np.zeros(n, bool)
    stack = [0]
    seen[0] = True
    while stack:
        v = stack.pop()
        for u in np.nonzero(A[v])[0]:
            if not seen[u]:
                seen[u] = True
                stack.append(u)
    while not seen.all():
        v = int(np.where(~seen)[0][0])
        A[v, 0] = A[0, v] = 1
        stack = [v]
        seen[v] = True
        while stack:
            w = stack.pop()
            for u in np.nonzero(A[w])[0]:
                if not seen[u]:
                    seen[u] = True
                    stack.append(u)
    return A


def g6ify(A):
    return A  # process() takes g6; provide wrapper below instead


def main():
    seed, count, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(seed)
    Lsup = np.full(len(RHO), -np.inf)
    Uinf = np.full(len(RHO), np.inf)
    import exp10_bigpool as bp
    # monkey-wrap: reuse the per-graph body with adjacency directly
    from common import graph_data, arg44, line_graph_adj
    TOL = 1e-9
    for t in range(count):
        A = rand_graph(rng)
        d, m, E = graph_data(A)
        ne = len(E)
        a44 = np.array([arg44(d[i], d[j], m[i], m[j]) for i, j in E])
        AL = line_graph_adj(E)
        s = np.array([d[i] + d[j] for i, j in E])
        z1 = AL @ (AL @ np.ones(ne))
        zs = AL @ (AL @ s)
        N1 = AL + np.eye(ne)
        N2 = N1 @ N1
        for a in range(ne):
            rho0 = a44[N2[a] > 0].max()
            mask = RHO >= rho0 - TOL
            up = mask & (z1[a] > RHO + 1e-6)
            dn = mask & (z1[a] < RHO - 1e-6)
            if up.any():
                Uv = (RHO[up] * s[a] - zs[a]) / (z1[a] - RHO[up])
                Uinf[up] = np.minimum(Uinf[up], Uv)
            if dn.any():
                Lv = (RHO[dn] * s[a] - zs[a]) / (z1[a] - RHO[dn])
                Lsup[dn] = np.maximum(Lsup[dn], Lv)
    np.savez(out, L=Lsup, U=Uinf, rho=RHO)
    print(f"{out}: {count} random graphs done")


if __name__ == "__main__":
    main()
