#!/usr/bin/env python3
"""P09 round 10b: closed-form check of Kneser / Johnson / Hamming families.

Exact integer arithmetic throughout (gap reported as a float of an exact
Fraction).  Clique numbers are the known exact values:
  Kneser K(n,k):  omega = floor(n/k)                       (n >= 2k+1)
  Johnson J(n,k): omega = max(n-k+1, k+1)                  (cliques are stars
                  through a (k-1)-set or subsets of a (k+1)-set)
  Hamming H(d,q): omega = q                                (d >= 2, q >= 2;
                  a maximum clique is a line varying one coordinate)
Eigenvalues (integers):
  Kneser:  (-1)^i * C(n-k-i, k-i), i = 0..k
  Johnson: (k-j)(n-k-j) - j,       j = 0..k
  Hamming: d(q-1) - q*i,           i = 0..d
"""
from math import comb
from fractions import Fraction

worst = []

def check(name, v, lam_list, omega):
    lam_sorted = sorted(lam_list, reverse=True)
    l1, l2 = lam_sorted[0], lam_sorted[1]
    two_m = v * l1  # regular of degree l1
    gap = Fraction(l1 * l1 + l2 * l2) - Fraction(two_m) * (1 - Fraction(1, omega))
    worst.append((float(gap), name))
    return gap

cnt = 0
# Kneser
for n in range(5, 81):
    for k in range(2, (n - 1) // 2 + 1):
        v = comb(n, k)
        eig = [(-1) ** i * comb(n - k - i, k - i) for i in range(k + 1)]
        g = check(f"Kneser({n},{k})", v, eig, n // k)
        cnt += 1
        assert g <= 0, (n, k, g)
# Johnson
for n in range(4, 81):
    for k in range(2, n // 2 + 1):
        v = comb(n, k)
        eig = [(k - j) * (n - k - j) - j for j in range(k + 1)]
        g = check(f"Johnson({n},{k})", v, eig, max(n - k + 1, k + 1))
        cnt += 1
        assert g <= 0, (n, k, g)
# Hamming
for q in range(2, 41):
    for d in range(2, 21):
        v = q ** d
        eig = [d * (q - 1) - q * i for i in range(d + 1)]
        g = check(f"Hamming({d},{q})", v, eig, q)
        cnt += 1
        assert g <= 0, (d, q, g)

worst.sort(key=lambda t: -t[0])
print(f"family members checked: {cnt}; violations: 0 (all asserts passed)")
print("closest to the bound:")
for g, name in worst[:12]:
    print(f"  gap={g:+.4f}  {name}")
