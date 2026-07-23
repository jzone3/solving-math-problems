#!/usr/bin/env python3
"""Independent re-verification of the key CW(120,49) computation.

Different implementation choices from verify_no_cw120_49.py:
- norm-feasible assignments counted TWO ways: generating function (poly mult)
  vs direct DFS enumeration;
- flatness tested via numpy FFT power spectrum (must equal 49 at every bin)
  instead of integer autocorrelation.
"""
import numpy as np
from itertools import product

m, d, k, t = 40, 3, 49, 7

# <7>-orbits of Z_40
seen, orbs = set(), []
for x in range(m):
    if x in seen:
        continue
    o, y = [], x
    while y not in o:
        o.append(y)
        y = (y * t) % m
    orbs.append(o)
    seen.update(o)
sizes = [len(o) for o in orbs]
print("orbits:", sorted(sizes))
assert sum(sizes) == m

# generating function: number of (c_1..c_no) with sum c_i^2 * s_i = 49
poly = np.zeros(k + 1, dtype=object)
poly[0] = 1
for s in sizes:
    nxt = np.zeros(k + 1, dtype=object)
    for c in range(-d, d + 1):
        w = c * c * s
        if w > k:
            continue
        for old in range(k + 1 - w):
            if poly[old]:
                nxt[old + w] += poly[old]
    poly = nxt
gf_count = poly[k]
print("norm-feasible assignments (generating function):", gf_count)

# direct enumeration with numpy-FFT flat test
count = 0
flat_hits = 0
no = len(orbs)
suffix = [0] * (no + 1)
for i in range(no - 1, -1, -1):
    suffix[i] = suffix[i + 1] + d * d * sizes[i]
cs = [0] * no


def dfs(pos, norm):
    global count, flat_hits
    if norm > k or norm + suffix[pos] < k:
        return
    if pos == no:
        if norm != k:
            return
        count += 1
        w = np.zeros(m)
        for c, o in zip(cs, orbs):
            for x in o:
                w[x] = c
        ps = np.abs(np.fft.fft(w)) ** 2
        if np.allclose(ps, k, atol=1e-6):
            flat_hits += 1
            print("FLAT SOLUTION:", cs)
        return
    for c in range(-d, d + 1):
        cs[pos] = c
        dfs(pos + 1, norm + c * c * sizes[pos])
    cs[pos] = 0


dfs(0, 0)
print("norm-feasible assignments (DFS):", count)
assert count == gf_count, "count mismatch!"
print("flat-spectrum solutions:", flat_hits)
assert flat_hits == 0
print("PASS: independent check confirms no <7>-fixed ICW_3(40,49)")
