#!/usr/bin/env python3
"""All connected 4-regular circulants C_n(a,b), 26<=n<=N: girth via BFS from 0 (VT), 3-col via SAT."""
import math, sys
from collections import deque
from pysat.solvers import Glucose4

def girth_vt(n, gens):
    steps = []
    for a in gens:
        steps += [a % n, -a % n]
    steps = list(set(steps))
    dist = {0: 0}
    par = {0: None}
    q = deque([0])
    best = None
    while q:
        v = q.popleft()
        if best is not None and dist[v] * 2 >= best:
            break
        for s in steps:
            u = (v + s) % n
            if u not in dist:
                dist[u] = dist[v] + 1
                par[u] = v
                q.append(u)
            elif par[v] != u and par[u] != v:
                c = dist[u] + dist[v] + 1
                if best is None or c < best:
                    best = c
    return best

def three_colorable(n, gens):
    s = Glucose4()
    v3 = lambda i, c: 3 * i + c + 1
    for i in range(n):
        s.add_clause([v3(i, 0), v3(i, 1), v3(i, 2)])
    for i in range(n):
        for a in gens:
            j = (i + a) % n
            for c in range(3):
                s.add_clause([-v3(i, c), -v3(j, c)])
    r = s.solve()
    s.delete()
    return r

if __name__ == "__main__":
    N = int(sys.argv[1])
    checked = g6 = non3 = 0
    for n in range(26, N + 1):
        for a in range(1, n // 2 + 1):
            for b in range(a + 1, n // 2 + 1):
                if math.gcd(math.gcd(a, b), n) != 1:
                    continue
                if 2 * a == n or 2 * b == n:
                    continue
                checked += 1
                if girth_vt(n, [a, b]) == 6:
                    g6 += 1
                    if not three_colorable(n, [a, b]):
                        non3 += 1
                        print(f"NON3COL C_{n}({a},{b})", flush=True)
        if n % 50 == 0:
            print(f"...n={n} checked={checked} girth6={g6}", flush=True)
    print(f"checked={checked} girth6={g6} non3col={non3}")
