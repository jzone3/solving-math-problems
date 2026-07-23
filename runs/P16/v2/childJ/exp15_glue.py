"""childJ exp15: try to REFUTE Conjecture H by gluing the two rho=14 extremal
configurations into one tree, connected by a long path.

T1 = HkE?K?@ (n=9): contains pendant edge with L(14) = -2.1
T2 = Li_GS?@?S??@?A (n=13): contains core edge with U(14) = -2.2
Join: path of length k between a chosen vertex of T1 and one of T2.
Keep R = 14: verify max arg44 stays 14 and the two critical edges' 2-ball
data survives. Then run exact ord2-sum interval feasibility.
"""
import itertools

import numpy as np

from common import g6_adj, graph_data, arg44, line_graph_adj
from exp1_structure import feasible, describe


def join(A1, A2, v1, v2, k):
    """connect v1 in A1 to v2 in A2 by a path with k internal vertices."""
    n1, n2 = A1.shape[0], A2.shape[0]
    n = n1 + n2 + k
    A = np.zeros((n, n))
    A[:n1, :n1] = A1
    A[n1:n1 + n2, n1:n1 + n2] = A2
    chain = [v1] + [n1 + n2 + t for t in range(k)] + [n1 + v2]
    for a, b in zip(chain, chain[1:]):
        A[a, b] = A[b, a] = 1
    return A


def g6_of(A):
    n = A.shape[0]
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(int(A[i, j]))
    while len(bits) % 6:
        bits.append(0)
    chars = [chr(63 + n)]
    for t in range(0, len(bits), 6):
        v = 0
        for b in bits[t:t + 6]:
            v = v * 2 + b
        chars.append(chr(63 + v))
    return "".join(chars)


A1 = g6_adj("HkE?K?@")
A2 = g6_adj("Li_GS?@?S??@?A")
d1 = A1.sum(1)
d2 = A2.sum(1)
print("T1 degrees:", d1.astype(int), "T2 degrees:", d2.astype(int))

best = None
for v1 in range(A1.shape[0]):
    for v2 in range(A2.shape[0]):
        for k in (4, 6):
            A = join(A1, A2, v1, v2, k)
            d, m, E = graph_data(A)
            R = max(arg44(d[i], d[j], m[i], m[j]) for i, j in E)
            ok, r = feasible(A)
            if not ok:
                g6 = g6_of(A)
                print(f"*** INFEASIBLE: v1={v1} v2={v2} k={k} R={R:.4f} "
                      f"n={A.shape[0]} g6={g6}")
                print("   ", describe(g6))
                best = (v1, v2, k, g6)
if best is None:
    print("no infeasible gluing found (v1 x v2 x k grid)")
