"""Scan all graphs of order n (geng) for:
  (a) direct violation:  dev(G) - R(G) > 0
  (b) padded violation:  A/(4m) - R(H) > 0  (H + isolated-vertex padding)
Fast float pass; prints top-k scores. Reads graph6 on stdin.
"""
import sys, math, heapq

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

def main():
    topd, topp = [], []
    cnt = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        n, edges = parse_g6(line)
        if not edges:
            continue
        cnt += 1
        d = [0]*n
        for u, v in edges:
            d[u] += 1; d[v] += 1
        m2 = sum(d); m = m2 // 2
        S = sum(x*x for x in d)
        R = sum(1.0/math.sqrt(d[u]*d[v]) for u, v in edges)
        dev = math.sqrt((S + m2)/n - (m2/n)**2)
        A = S + m2
        sd = dev - R
        sp = A/(4*m) - R
        heapq.heappush(topd, (sd, line))
        heapq.heappush(topp, (sp, line))
        if len(topd) > 15: heapq.heappop(topd)
        if len(topp) > 15: heapq.heappop(topp)
    print(f"graphs scanned: {cnt}")
    print("top direct dev-R:")
    for s, g in sorted(topd, reverse=True):
        print(f"  {s:+.10f}  {g}")
    print("top padded A/(4m)-R:")
    for s, g in sorted(topp, reverse=True):
        print(f"  {s:+.10f}  {g}")

main()
