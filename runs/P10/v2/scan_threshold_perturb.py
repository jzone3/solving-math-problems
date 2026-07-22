#!/usr/bin/env python3
"""P10 V2: equality-perturbation scan around threshold/split graphs.

Brouwer's conjecture: for every graph G (n vertices, m edges), for all 1<=t<=n,
    S_t(G) := sum of t largest Laplacian eigenvalues <= m + t(t+1)/2.

V2 strategy: threshold graphs achieve equality (for t = clique number - 1).
We (1) exhaustively enumerate all threshold graphs up to N_MAX via 0/1 creation
sequences, confirm equality/no-violation using the EXACT integer spectrum
(Laplacian spectrum of a threshold graph = conjugate of its degree sequence,
Merris), and (2) apply all single-edge perturbations (add/remove/swap one edge)
to each threshold graph, computing the deficit
    d(G) = max_t ( S_t - m - t(t+1)/2 )
numerically, hunting for sign flips (d > 0). Near-misses (d > -0.5) are logged.

Context: the conjecture was proved by Kothari & Tudose (arXiv:2606.12197, June
2026), so no violation exists; this scan is independent numerical corroboration
of the equality structure and its rigidity under perturbation.
"""
import itertools, sys
import numpy as np

N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 16
PERT_MAX = int(sys.argv[2]) if len(sys.argv) > 2 else 12
NEAR = -0.5

def threshold_adj(seq):
    """seq of 0/1 (first vertex implicit isolated). 1 = dominating vertex."""
    n = len(seq) + 1
    A = np.zeros((n, n), dtype=np.int64)
    for i, b in enumerate(seq, start=1):
        if b:
            A[i, :i] = 1
            A[:i, i] = 1
    return A

def exact_threshold_check(A):
    """Exact integer check via Merris: Laplacian spectrum = conjugate degrees."""
    deg = A.sum(axis=1)
    n = len(deg)
    m = int(deg.sum()) // 2
    # conjugate of degree sequence: c_k = #{i : deg_i >= k}, k=1..n
    spec = sorted((int((deg >= k).sum()) for k in range(1, n + 1)), reverse=True)
    worst = None
    s = 0
    for t in range(1, n + 1):
        s += spec[t - 1]
        d = s - m - t * (t + 1) // 2
        if worst is None or d > worst[0]:
            worst = (d, t)
        if d > 0:
            return ('VIOLATION', d, t)
    return ('ok',) + worst

def deficit(A):
    deg = A.sum(axis=1)
    L = np.diag(deg).astype(float) - A
    ev = np.linalg.eigvalsh(L)[::-1]
    m = int(deg.sum()) // 2
    cs = np.cumsum(ev)
    t = np.arange(1, len(ev) + 1)
    d = cs - m - t * (t + 1) / 2
    i = int(np.argmax(d))
    return d[i], i + 1

def perturbations(A):
    n = len(A)
    pairs = list(itertools.combinations(range(n), 2))
    edges = [(i, j) for i, j in pairs if A[i, j]]
    nons = [(i, j) for i, j in pairs if not A[i, j]]
    for i, j in edges:                      # remove one edge
        B = A.copy(); B[i, j] = B[j, i] = 0; yield B
    for i, j in nons:                       # add one edge
        B = A.copy(); B[i, j] = B[j, i] = 1; yield B
    for (i, j) in edges:                    # move one edge
        for (k, l) in nons:
            B = A.copy(); B[i, j] = B[j, i] = 0; B[k, l] = B[l, k] = 1; yield B

def main():
    total_thr = total_pert = near = zero = 0
    best = (-1e9, None, None)
    for n in range(2, N_MAX + 1):
        cnt = 0
        for seq in itertools.product((0, 1), repeat=n - 1):
            A = threshold_adj(seq)
            r = exact_threshold_check(A)
            if r[0] == 'VIOLATION':
                print('EXACT VIOLATION (threshold!)', n, seq, r); return
            cnt += 1
            if n <= PERT_MAX:  # full perturbation scan only up to PERT_MAX (cost)
                for B in perturbations(A):
                    d, t = deficit(B)
                    total_pert += 1
                    if d > best[0]:
                        best = (d, n, t)
                    if d > 1e-7:
                        print('NUMERIC VIOLATION', n, seq, d, t)
                        np.save('violation_adj.npy', B); return
                    if d > -1e-7:
                        zero += 1  # perturbed graph is itself an equality (threshold) graph
                    elif d > NEAR:
                        near += 1
                        if near <= 20:
                            print(f'near-miss n={n} t={t} deficit={d:.6f}')
        total_thr += cnt
        print(f'n={n}: {cnt} threshold seqs OK (exact); cumulative perturbs={total_pert}', flush=True)
    print(f'DONE. threshold graphs checked exactly: {total_thr}; perturbed graphs: {total_pert}')
    print(f'perturbed graphs at exact equality (still threshold): {zero}; strict near-misses in ({NEAR},0): {near}')
    print(f'max perturbed deficit = {best[0]:.6f} at n={best[1]}, t={best[2]} (violation would need > 0)')

if __name__ == '__main__':
    main()
