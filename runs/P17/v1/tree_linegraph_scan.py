#!/usr/bin/env python3
"""score21(L(T)) = sum_{mu in Lap(T), 0<mu<2}(mu-1). Exhaustive over trees
(nauty-gentreeg) for given n; prints max and argmax."""
import sys, subprocess, numpy as np

n = int(sys.argv[1])
proc = subprocess.Popen("nauty-gentreeg -q %d | nauty-copyg -gq" % n, shell=True, stdout=subprocess.PIPE, text=True)

def g6_to_adj(s):
    data = [ord(c) - 63 for c in s.strip()]
    nn = data[0]; bits = []
    for d in data[1:]:
        bits.extend((d >> k) & 1 for k in range(5, -1, -1))
    A = np.zeros((nn, nn)); idx = 0
    for j in range(1, nn):
        for i in range(j):
            A[i, j] = A[j, i] = bits[idx]; idx += 1
    return A

best = -1e18; barg = None; cnt = 0
for line in proc.stdout:
    A = g6_to_adj(line)
    L = np.diag(A.sum(1)) - A
    mu = np.linalg.eigvalsh(L)
    m = mu[(mu > 1e-9) & (mu < 2 - 1e-12)]
    s = (m - 1).sum()
    cnt += 1
    if s > best: best, barg = s, line.strip()
print(f"trees n={n}: {cnt} trees, max score21(L(T))={best:.8f} at {barg}")
