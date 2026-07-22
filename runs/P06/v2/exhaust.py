"""Exhaustive scan of all graphs of order n (via nauty-geng) for f = dev - R > 0.

Uses the degree-sequence identity dev^2 = (sum d^2 + 2m)/n - (2m/n)^2.
Reads graph6 on stdin. Prints max f and any positives / near-misses.
"""
import math
import sys


def parse_g6(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]
    bits = []
    for x in data[1:]:
        for k in range(5, -1, -1):
            bits.append((x >> k) & 1)
    adj = [[] for _ in range(n)]
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i].append(j)
                adj[j].append(i)
            idx += 1
    return n, adj


def f_value(n, adj):
    d = [len(a) for a in adj]
    m = sum(d) / 2
    if m == 0:
        return 0.0
    var = (sum(x * x for x in d) + 2 * m) / n - (2 * m / n) ** 2
    R = 0.0
    for u in range(n):
        du = d[u]
        for v in adj[u]:
            if v > u:
                R += 1.0 / math.sqrt(du * d[v])
    return math.sqrt(max(var, 0.0)) - R


best = -1e9
best_line = None
count = 0
near = []
for line in sys.stdin:
    n, adj = parse_g6(line)
    f = f_value(n, adj)
    count += 1
    if f > best:
        best, best_line = f, line.strip()
    if f > -1e-9:
        near.append((f, line.strip()))

print(f"scanned {count} graphs; max f = {best:.9f} at {best_line}")
for f, g in sorted(near, reverse=True)[:20]:
    print(f"  f={f:+.9f}  {g}")
