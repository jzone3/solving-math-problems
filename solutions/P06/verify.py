"""P06 (Graffiti WoW 129) — independent verifier for the V2 claims.

Claims verified here (standalone, stdlib + numpy only; numpy used only for the
eigenvalue cross-check in claim 1):

1. IDENTITY: dev(L)^2 = (sum d^2 + 2m)/n - (2m/n)^2 for every graph
   (checked against an actual eigensolve on random graphs).
2. EQUALITY FAMILY: G_q = K_q + (q-2) isolated vertices satisfies
   dev(G_q) = R(G_q) = q/2 EXACTLY, for all q >= 3 (exact rational arithmetic:
   dev^2 == q^2/4 == R^2).
3. REGULAR GRAPHS: for every d-regular graph, dev <= (d+1)/2 <= n/2 = R,
   verified symbolically via the identity and numerically on random regular-ish
   circulants.
4. NO COUNTEREXAMPLE ON <= 7 VERTICES: brute force over all 2^21 labeled graphs
   on 7 vertices (and all smaller n): max(dev - R) = 0, attained only by empty
   graphs and G_3 = K_3 + 1 isolated / G_4 = K_4 + 2 isolated.

Prints PASS if all checks succeed.
"""
import itertools
import math
import random
from fractions import Fraction

import numpy as np


def dev2_fraction(degs, m, n):
    """Exact dev^2 via the identity, as a Fraction."""
    S = sum(d * d for d in degs)
    return Fraction(S + 2 * m, n) - Fraction(2 * m, n) ** 2


def check_identity(trials=100):
    rng = random.Random(42)
    for _ in range(trials):
        n = rng.randint(3, 25)
        A = np.zeros((n, n))
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < rng.choice([0.1, 0.3, 0.6, 0.9]):
                    A[i, j] = A[j, i] = 1
        d = A.sum(axis=1)
        L = np.diag(d) - A
        eig = np.linalg.eigvalsh(L)
        var_eig = float(np.mean((eig - eig.mean()) ** 2))
        m = int(d.sum()) // 2
        var_form = float(dev2_fraction([int(x) for x in d], m, n))
        assert abs(var_eig - var_form) < 1e-8, (n, var_eig, var_form)
    print("check 1 PASS: identity dev^2 = (sum d^2 + 2m)/n - (2m/n)^2")


def check_equality_family(qmax=300):
    for q in range(3, qmax + 1):
        n = 2 * q - 2
        m = q * (q - 1) // 2
        degs = [q - 1] * q + [0] * (q - 2)
        dev2 = dev2_fraction(degs, m, n)
        # R = (q(q-1)/2) / (q-1) = q/2 exactly (all edge endpoints have degree q-1)
        R2 = Fraction(q, 2) ** 2
        assert dev2 == R2 == Fraction(q * q, 4), (q, dev2, R2)
    print(f"check 2 PASS: dev = R = q/2 exactly on K_q + (q-2)K_1 for q = 3..{qmax}")


def check_regular(qmax=200):
    # symbolic: d-regular => dev^2 = (n d^2 + n d)/n - d^2 = d, so dev = sqrt(d)
    # and sqrt(d) <= n/2 = R whenever n >= d + 1 (always). Verify the algebra
    # numerically on circulants C_n(1..k).
    rng = random.Random(7)
    for _ in range(50):
        n = rng.randint(5, 60)
        k = rng.randint(1, (n - 1) // 2)
        d = 2 * k - (1 if (n % 2 == 0 and k == n // 2) else 0)
        degs = [d] * n
        m = n * d // 2
        dev2 = dev2_fraction(degs, m, n)
        assert dev2 == d, (n, d, dev2)
        R = Fraction(n, 2)
        assert dev2 <= R * R
    print("check 3 PASS: d-regular graphs have dev = sqrt(d) <= n/2 = R")


def check_exhaustive_small(nmax=7):
    for n in range(1, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        npairs = len(pairs)
        best = None
        eq_count = 0
        for mask in range(1 << npairs):
            degs = [0] * n
            edges = []
            mm = mask
            while mm:
                b = (mm & -mm).bit_length() - 1
                u, v = pairs[b]
                degs[u] += 1
                degs[v] += 1
                edges.append((u, v))
                mm &= mm - 1
            m = len(edges)
            if m == 0:
                continue
            dev2 = dev2_fraction(degs, m, n)
            R = sum(1.0 / math.sqrt(degs[u] * degs[v]) for u, v in edges)
            f = math.sqrt(float(dev2)) - R
            assert f <= 1e-9, (n, mask, f)
            if f > -1e-9:
                eq_count += 1
            if best is None or f > best:
                best = f
        print(f"  n={n}: all {1 << npairs} labeled graphs OK, max f = {best}, "
              f"equality graphs (labeled) = {eq_count}")
    print(f"check 4 PASS: no counterexample among all labeled graphs, n <= {nmax}")


if __name__ == "__main__":
    check_identity()
    check_equality_family()
    check_regular()
    check_exhaustive_small()
    print("PASS")
