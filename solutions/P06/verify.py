#!/usr/bin/env python3
"""P06 (WoW conjecture 129: std-dev of Laplacian eigenvalues <= Randic index).

V3 result verifier. No counterexample was found; the verified claim here is the
NEW exact-equality family discovered by the V3 run:

    G_t = K_t  UNION  (t-2) isolated vertices   (t >= 2, n = 2(t-1))
    ==>  std_dev(Laplacian spectrum of G_t) = R(G_t) = t/2   EXACTLY.

So conjecture 129 is *tight* on an infinite family (previously best known
near-misses, stars, have gap R^2 - dev^2 -> 2). This script verifies the claim
two independent ways:
  (1) numerically: build the Laplacian, eigensolve (numpy), population std-dev,
      compare to Randic index computed edge-by-edge;
  (2) exactly: dev^2 via the trace identity
        dev^2 = (sum d^2 + 2m)/n - (2m/n)^2   (rational arithmetic),
      and R = C(t,2)/(t-1) = t/2 exactly (all edge weights are 1/(t-1)).
Prints PASS iff every check succeeds. Dependencies: numpy only (stdlib otherwise).
"""
import sys
from fractions import Fraction

import numpy as np


def laplacian_eigen_dev2(t):
    n = 2 * (t - 1)
    A = np.zeros((n, n))
    A[:t, :t] = 1 - np.eye(t)
    L = np.diag(A.sum(1)) - A
    ev = np.linalg.eigvalsh(L)
    return float(np.mean((ev - ev.mean()) ** 2)), A


def randic(A):
    d = A.sum(1)
    n = len(d)
    tot = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            if A[i, j]:
                tot += 1.0 / np.sqrt(d[i] * d[j])
    return tot


def main():
    ok = True
    for t in list(range(2, 40)) + [100, 200]:
        n = 2 * (t - 1)
        if n < 1:
            continue
        # (1) numeric
        dev2_num, A = laplacian_eigen_dev2(t)
        R = randic(A)
        target = t / 2.0
        if abs(np.sqrt(dev2_num) - target) > 1e-8 or abs(R - target) > 1e-8:
            print(f"FAIL numeric t={t}: dev={np.sqrt(dev2_num)}, R={R}, target={target}")
            ok = False
        # (2) exact
        degs = [t - 1] * t + [0] * (t - 2)
        m2 = sum(degs)
        s2 = sum(d * d for d in degs)
        dev2_exact = Fraction(s2 + m2, n) - Fraction(m2 * m2, n * n)
        if dev2_exact != Fraction(t * t, 4):
            print(f"FAIL exact t={t}: dev^2={dev2_exact} != {Fraction(t*t,4)}")
            ok = False
        # R exact: t(t-1)/2 edges, each weight 1/(t-1) => R = t/2 (rational)
        R_exact = Fraction(t * (t - 1), 2) / (t - 1)
        if R_exact != Fraction(t, 2):
            print(f"FAIL exact R t={t}")
            ok = False
        # equality of the conjecture's two sides
        if dev2_exact != R_exact * R_exact:
            print(f"FAIL equality t={t}")
            ok = False
    if ok:
        print("PASS: dev(Laplacian) == Randic == t/2 exactly for K_t + (t-2)K_1, "
              "t in 2..39, 100, 200 (numeric eigensolve + exact rational arithmetic)")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
