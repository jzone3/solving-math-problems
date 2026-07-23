"""Frank-Wolfe / ILP duality attack (new method, round 6).

Iterate: given current graph A with top-2 eigenpairs (l1,x), (l2,y), the exact
first-order expansion of F(A) = l1^2 + l2^2 - 2m(1-1/w) w.r.t. edge variables is
  dF/dA_ij = 4*l1*x_i*x_j + 4*l2*y_i*y_j - 2(1-1/w)   (for i<j, A symmetric).
Solve an ILP: choose the ENTIRE edge set maximizing sum of these weights subject
to K_{w+1}-freeness enforced by lazy clique cuts; recompute eigenpairs; repeat.
This makes global jumps that flip-based annealing cannot.

Usage: python3 fw_ilp.py <n> <omega> <iters> <seed>
"""
import sys
import numpy as np
from mip import Model, xsum, BINARY, maximize, OptimizationStatus
from core import turan_graph, union, max_clique, top2

def find_cliques_of_size(A, k):
    """Return up to 200 (k)-cliques (as tuples) in A."""
    n = A.shape[0]
    out = []
    adj = [set(np.nonzero(A[i])[0].tolist()) for i in range(n)]
    def extend(clq, cand):
        if len(out) >= 200:
            return
        if len(clq) == k:
            out.append(tuple(clq)); return
        for v in list(cand):
            if v > clq[-1]:
                extend(clq + [v], cand & adj[v])
    for v in range(n):
        extend([v], adj[v])
    return out

def ilp_step(n, W, forbidden_cliques, time_limit=60):
    m = Model()
    m.verbose = 0
    e = {}
    for i in range(n):
        for j in range(i + 1, n):
            e[i, j] = m.add_var(var_type=BINARY)
    m.objective = maximize(xsum(W[i, j] * e[i, j] for (i, j) in e))
    for clq in forbidden_cliques:
        m += xsum(e[min(a, b), max(a, b)] for ai, a in enumerate(clq)
                  for b in clq[ai + 1:]) <= len(clq) * (len(clq) - 1) // 2 - 1
    m.max_seconds = time_limit
    st = m.optimize()
    A = np.zeros((n, n))
    for (i, j), v in e.items():
        if v.x is not None and v.x > 0.5:
            A[i, j] = A[j, i] = 1
    return A, st

def run(n, w, iters, seed):
    rng = np.random.default_rng(seed)
    coef = 2 * (1 - 1 / w)
    # init: connected roughened Turan union
    k = max(1, n // (2 * w))
    A = union(turan_graph(k * w, w), turan_graph(k * w, w))
    s0 = A.shape[0]
    B = np.zeros((n, n)); B[:s0, :s0] = A; A = B
    for _ in range(n // 3):
        i, j = rng.integers(0, n, 2)
        if i != j: A[i, j] = A[j, i] = 1
    cuts = []
    best = -1e9
    for it in range(iters):
        # ensure K_{w+1}-free by adding cuts + resolving inside the loop
        l1, l2 = top2(A)
        lam, V = np.linalg.eigh(A)
        x, y = V[:, -1], V[:, -2]
        Wt = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                Wt[i, j] = 4 * l1 * x[i] * x[j] + 4 * max(l2, 0) * y[i] * y[j] - coef
        # inner loop: solve ILP, add violated clique cuts until K_{w+1}-free
        for inner in range(30):
            A2, st = ilp_step(n, Wt, cuts)
            viol = find_cliques_of_size(A2, w + 1)
            if not viol:
                break
            cuts.extend(viol)
        A = A2
        om = max_clique(A)
        l1n, l2n = top2(A)
        mten = A.sum() / 2
        if om >= n or om != w:
            score = l1n**2 + l2n**2 - 2 * mten * (1 - 1 / om) if om < n else -1e9
        else:
            score = l1n**2 + l2n**2 - coef * mten
        best = max(best, score)
        print(f"n={n} w={w} it={it} m={int(mten)} omega={om} score={score:+.6f} cuts={len(cuts)}"
              + (" ***POSITIVE***" if score > 1e-9 else ""), flush=True)
        if score > 1e-9:
            edges = [(int(i), int(j)) for i in range(n) for j in range(i+1, n) if A[i, j]]
            import json; json.dump({"n": n, "edges": edges, "score": score},
                                   open(f"fw_witness_n{n}_w{w}_{seed}.json", "w"))
            break
        # random restart of eigen-direction: perturb A slightly to escape cycles
        if it % 5 == 4:
            for _ in range(3):
                i, j = rng.integers(0, n, 2)
                if i != j: A[i, j] = A[j, i] = 1 - A[i, j]
    print(f"FW BEST n={n} w={w}: {best:+.6f}")

if __name__ == "__main__":
    run(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
