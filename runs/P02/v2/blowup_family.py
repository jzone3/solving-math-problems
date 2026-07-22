#!/usr/bin/env python3
"""Verify the infinite counterexample family: W with vertices 1, 2, 8 multiplied
by k gives an MTF graph of order n = 6+3k with delta = n/3 whose vertex-
multiplication system A x = d*1, x >= 1 is exactly infeasible. Checks k = 1..K.
"""
import sys
from exact_check import g6_to_adj, nullspace, lp_feasible_exact

K = int(sys.argv[1]) if len(sys.argv) > 1 else 7


def blowup(A, w):
    idx = []
    for v in range(len(A)):
        idx += [v] * w[v]
    N = len(idx)
    return [[1 if A[idx[i]][idx[j]] else 0 for j in range(N)] for i in range(N)]


def main():
    _, A = g6_to_adj('H?q`qjo')
    ok = True
    for k in range(1, K + 1):
        B = blowup(A, [1, k, k, 1, 1, 1, 1, 1, k])
        N = len(B)
        deg = [sum(r) for r in B]
        tf = all(not (B[i][j] and B[j][t] and B[i][t]) for i in range(N)
                 for j in range(i + 1, N) for t in range(j + 1, N))
        mx = all(B[i][j] or any(B[i][t] and B[j][t] for t in range(N))
                 for i in range(N) for j in range(i + 1, N))
        feas = lp_feasible_exact(nullspace(B, N), N)
        good = tf and mx and 3 * min(deg) == N and not feas
        print(f'k={k} n={N} delta={min(deg)} MTF={tf and mx} feasible={feas}')
        ok &= good
    print('PASS' if ok else 'FAIL')


if __name__ == '__main__':
    main()
