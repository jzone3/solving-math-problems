#!/usr/bin/env python3
"""Find closest approaches to violation among connected graphs (geng -c),
excluding exact equality (score==0). Usage: near_miss_scan.py <n>"""
import sys, subprocess, numpy as np, heapq

n = int(sys.argv[1])
ZTOL = 1e-7
proc = subprocess.Popen(["nauty-geng", "-qc", str(n)], stdout=subprocess.PIPE, text=True)

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

top20, top21 = [], []
for line in proc.stdout:
    A = g6_to_adj(line)
    ev = np.linalg.eigvalsh(A)
    pos = ev[ev > ZTOL]; neg = ev[ev < -ZTOL]
    s = pos.sum()
    s20 = len(pos) - s; s21 = len(neg) - s
    if abs(s20) > 1e-9:
        heapq.heappush(top20, (s20, line.strip()))
        if len(top20) > 5: heapq.heappop(top20)
    if abs(s21) > 1e-9:
        heapq.heappush(top21, (s21, line.strip()))
        if len(top21) > 5: heapq.heappop(top21)
print(f"n={n} top connected non-equality score20:", sorted(top20, reverse=True))
print(f"n={n} top connected non-equality score21:", sorted(top21, reverse=True))
