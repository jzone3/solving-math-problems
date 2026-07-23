"""Exhaustive check of Bounds 44/46 on all connected graphs with n <= N via nauty-geng.
Float screening; margin tracking. Usage: python3 exhaustive_small.py N"""
import subprocess
import sys

import numpy as np

from search_common import mu, rhs_graph, rhs44_edge, rhs46_edge


def g6_to_adj(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        bits.extend((x >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((n, n), dtype=np.int8)
    t = 0
    for j in range(1, n):
        for i in range(j):
            A[i, j] = A[j, i] = bits[t]
            t += 1
    return A


def main():
    N = int(sys.argv[1])
    worst = {44: (1e9, None), 46: (1e9, None)}
    count = 0
    for n in range(2, N + 1):
        p = subprocess.Popen(["nauty-geng", "-c", "-q", str(n)], stdout=subprocess.PIPE, text=True)
        for line in p.stdout:
            A = g6_to_adj(line.strip())
            lam = mu(A)
            for b, fn in ((44, rhs44_edge), (46, rhs46_edge)):
                r = rhs_graph(A, fn)
                gap = r - lam  # negative => violation
                if gap < worst[b][0]:
                    worst[b] = (gap, (n, line.strip()))
                if gap < -1e-9:
                    print(f"VIOLATION bound {b}: n={n} g6={line.strip()} mu={lam} rhs={r}")
            count += 1
        p.wait()
        print(f"n={n} done, cumulative graphs={count}, worst gaps: 44={worst[44]}, 46={worst[46]}", flush=True)


if __name__ == "__main__":
    main()
