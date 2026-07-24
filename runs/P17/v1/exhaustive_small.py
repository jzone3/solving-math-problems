#!/usr/bin/env python3
"""Exhaustive float scan of all graphs on n vertices (geng) for WoW 20/21.
Near misses (score > -1e-6, excluding exact-equality graphs) are printed
for exact re-checking with verify_exact.py.
Usage: python3 exhaustive_small.py <n>
"""
import sys, subprocess, numpy as np

n = int(sys.argv[1])
ZTOL = 1e-7
proc = subprocess.Popen(["nauty-geng", "-q", str(n)], stdout=subprocess.PIPE, text=True)

def g6_to_adj(s):
    data = [ord(c) - 63 for c in s.strip()]
    nn = data[0]
    bits = []
    for d in data[1:]:
        bits.extend((d >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((nn, nn))
    idx = 0
    for j in range(1, nn):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]; idx += 1
    return A

best20 = best21 = -1e18
b20g = b21g = None
count = 0
for line in proc.stdout:
    A = g6_to_adj(line)
    ev = np.linalg.eigvalsh(A)
    pos = ev[ev > ZTOL]; neg = ev[ev < -ZTOL]
    s = pos.sum()
    s20 = len(pos) - s; s21 = len(neg) - s
    count += 1
    if s20 > best20: best20, b20g = s20, line.strip()
    if s21 > best21: best21, b21g = s21, line.strip()
    if max(s20, s21) > 1e-6:
        print("VIOLATION CANDIDATE:", line.strip(), s20, s21, flush=True)
print(f"n={n}: {count} graphs; best20={best20:.8f} ({b20g}) best21={best21:.8f} ({b21g})")
