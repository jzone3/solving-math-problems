"""Probe the equality family K_m + k isolated vertices and perturbations."""
import itertools
import math

import numpy as np


def dev_R(A):
    n = A.shape[0]
    d = A.sum(axis=1)
    m = d.sum() / 2
    var = (np.sum(d ** 2) + 2 * m) / n - (2 * m / n) ** 2
    iu, ju = np.nonzero(np.triu(A, 1))
    R = np.sum(1.0 / np.sqrt(d[iu] * d[ju]))
    return math.sqrt(max(var, 0.0)), R


def clique_plus_iso(mq, k):
    n = mq + k
    A = np.zeros((n, n))
    A[:mq, :mq] = 1
    np.fill_diagonal(A, 0)
    return A


print("K_m + k isolated: (m,k), dev-R  [predicted equality at k=m-2]")
for mq in [4, 5, 8, 12, 20, 50, 100]:
    for k in [mq - 3, mq - 2, mq - 1]:
        dev, R = dev_R(clique_plus_iso(mq, k))
        print(f"  m={mq:3d} k={k:3d} dev={dev:.6f} R={R:.6f} f={dev-R:+.9f}")

print("\nperturbations of K_m + (m-2) isolated:")
for mq in [8, 12, 20, 50]:
    k = mq - 2
    base = clique_plus_iso(mq, k)
    variants = {}
    # remove one clique edge
    A = base.copy(); A[0, 1] = A[1, 0] = 0; variants["minus clique edge"] = A
    # add edge between two isolated
    A = base.copy(); A[mq, mq + 1] = A[mq + 1, mq] = 1; variants["iso-iso edge"] = A
    # add pendant from clique to isolated
    A = base.copy(); A[0, mq] = A[mq, 0] = 1; variants["clique-iso pendant"] = A
    # one fewer / one more isolated with an extra structure: K_m + K_2 + (m-4) iso
    for name, A in variants.items():
        dev, R = dev_R(A)
        print(f"  m={mq:3d} {name:20s} f={dev-R:+.9f}")
