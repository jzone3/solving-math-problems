"""Numeric checks for the two-case proof program of WoW 129:
  Case 1 (dense, 8m^2 >= A n): claim 4mR >= A  (sharp at cliques).
  Case 2 (sparse, 8m^2 <= A n): claim R^2 >= A/n - 4m^2/n^2 (= dev^2).
Also tests the GM refinement of Case 1:
  4m^2 * exp(-(1/2m) sum_v d_v ln d_v) >= A ?
Scans all graphs from geng (stdin) and reports minima of the slack in each case.
"""
import sys, math

def parse_g6(line):
    data = [c - 63 for c in line.encode()]
    n = data[0]
    bits = []
    for b in data[1:]:
        for i in range(5, -1, -1):
            bits.append((b >> i) & 1)
    edges = []
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                edges.append((i, j))
            k += 1
    return n, edges

min1 = min2 = ming = (1e18, None)
cnt1 = cnt2 = 0
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    n, edges = parse_g6(line)
    if not edges: continue
    d = [0]*n
    for u,v in edges: d[u]+=1; d[v]+=1
    m = len(edges); m2 = 2*m
    S = sum(x*x for x in d); A = S + m2
    R = sum(1.0/math.sqrt(d[u]*d[v]) for u,v in edges)
    if 8*m*m >= A*n:
        cnt1 += 1
        s = 4*m*R - A
        if s < min1[0]: min1 = (s, line)
        gm = 4*m*m*math.exp(-sum(x*math.log(x) for x in d if x)/m2) - A
        if gm < ming[0]: ming = (gm, line)
    else:
        cnt2 += 1
        s = R*R - (A/n - 4*m*m/(n*n))
        if s < min2[0]: min2 = (s, line)
print(f"case1 graphs {cnt1}: min slack 4mR-A = {min1[0]:.9f} at {min1[1]}")
print(f"  GM refinement min slack = {ming[0]:.9f} at {ming[1]}")
print(f"case2 graphs {cnt2}: min slack R^2-dev^2 = {min2[0]:.9f} at {min2[1]}")
