"""Recheck the NEGATIVE points reported by continuous_quotient.py with 60-digit
mpmath arithmetic (the reported gaps are exact binary fractions at entry scales
e^20..e^33 ~ 1e9..1e14, the signature of float64 cancellation noise)."""
import math
import re
import sys

import mpmath as mp
import numpy as np

sys.path.insert(0, "..")

mp.mp.dps = 60


def gap_mp(k, edges, theta, bound):
    n = [mp.e ** t for t in theta[:k]]
    S = mp.zeros(k, k)
    for t, (a, b) in enumerate(edges):
        S[a, b] = S[b, a] = mp.e ** theta[k + t]
    B = mp.zeros(k, k)
    for i in range(k):
        for j in range(k):
            B[i, j] = S[i, j] / n[i]
    s = [sum(B[i, j] for j in range(k)) for i in range(k)]
    m = [sum(B[i, j] * s[j] for j in range(k)) / s[i] for i in range(k)]
    LB = mp.zeros(k, k)
    for i in range(k):
        for j in range(k):
            LB[i, j] = (s[i] if i == j else 0) - B[i, j]
    ev = mp.eig(LB, left=False, right=False)
    lam = max(e.real for e in ev)
    rhs = mp.mpf('-inf')
    for (a, b) in edges:
        if bound == 44:
            arg = 2 * ((s[a] - 1) ** 2 + (s[b] - 1) ** 2 + m[a] * m[b] - s[a] * s[b])
        else:
            arg = 2 * (s[a] ** 2 + s[b] ** 2) - 16 * s[a] * s[b] / (m[a] + m[b]) + 4
        if arg >= 0:
            rhs = max(rhs, 2 + mp.sqrt(arg))
    return rhs - lam, lam


CASES = []
pat = re.compile(r"NEGATIVE k=(\d+) bound=(\d+) edges=(\[\[.*?\]\]) gap=(\S+) theta=(\[.*\])")
for fn in ("cont44.log", "cont46.log"):
    for line in open(fn):
        mo = pat.search(line)
        if mo:
            CASES.append((int(mo.group(1)), int(mo.group(2)),
                          eval(mo.group(3)), float(mo.group(4)), eval(mo.group(5))))

for (k, bound, edges, g0, theta) in CASES:
    g, lam = gap_mp(k, edges, theta, bound)
    verdict = "GENUINE NEGATIVE!!" if g < 0 else "noise (nonneg at high precision)"
    print(f"k={k} bound={bound} float_gap={g0:.3g} lam~{mp.nstr(lam,5)} "
          f"mp_gap={mp.nstr(g, 8)} -> {verdict}", flush=True)
