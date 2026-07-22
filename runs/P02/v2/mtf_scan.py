#!/usr/bin/env python3
"""P02 V2 scanner: read graph6 on stdin (triangle-free, mindeg >= k from geng),
filter maximal triangle-free (MTF) with delta(G) >= n/3, LP-check the vertex
multiplication system  A x = d*1, x >= 1  (rational feasibility <=> integer).

Usage: nauty-geng -t -d{k} -q {n} | python3 mtf_scan.py {n} [--boundary-only]
Prints counters and any LP-infeasible instance (graph6) to stdout.
"""
import sys
import numpy as np
from scipy.optimize import linprog


def g6_to_adj(line):
    data = [c - 63 for c in line.encode('ascii')]
    n = data[0]
    assert n < 63
    bits = []
    for b in data[1:]:
        bits.extend((b >> i) & 1 for i in range(5, -1, -1))
    A = np.zeros((n, n), dtype=np.int8)
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                A[i, j] = A[j, i] = 1
            idx += 1
    return n, A


def is_maximal_tf(n, A):
    # every non-adjacent pair (incl. i==j? no, i<j) must have a common neighbor
    A2 = (A.astype(np.int32) @ A.astype(np.int32))
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j] == 0 and A2[i, j] == 0:
                return False
    return True


def lp_feasible(n, A):
    # vars: x_0..x_{n-1}, d ; A x - d*1 = 0, x >= 1, d >= 1
    Aeq = np.hstack([A.astype(float), -np.ones((n, 1))])
    beq = np.zeros(n)
    c = np.zeros(n + 1)
    bounds = [(1, None)] * n + [(1, None)]
    res = linprog(c, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    return res.status == 0


def main():
    n_target = int(sys.argv[1])
    boundary_only = '--boundary-only' in sys.argv
    k = (n_target + 2) // 3  # ceil(n/3)
    total = mtf = tested = infeas = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        total += 1
        n, A = g6_to_adj(line)
        deg = A.sum(axis=1)
        dmin = deg.min()
        if 3 * dmin < n:
            continue
        if boundary_only and 3 * dmin != n:
            continue
        if not is_maximal_tf(n, A):
            continue
        mtf += 1
        tested += 1
        if not lp_feasible(n, A):
            infeas += 1
            print(f'INFEASIBLE-CANDIDATE {line}', flush=True)
    print(f'n={n_target} total_read={total} mtf_delta_ok={mtf} tested={tested} '
          f'infeasible={infeas}', flush=True)


if __name__ == '__main__':
    main()
