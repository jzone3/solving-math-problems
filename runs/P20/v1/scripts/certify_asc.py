#!/usr/bin/env python3
"""certify_asc.py n input.asc output.jsonl — like certify.py but reads a plain asc file."""
import json, re, sys
from pysat.solvers import Glucose4

def three_color(adj, n):
    s = Glucose4()
    v = lambda i, c: 3 * i + c + 1
    for i in range(n):
        s.add_clause([v(i, 0), v(i, 1), v(i, 2)])
    for a in range(n):
        for b in adj[a]:
            if b - 1 > a:
                for c in range(3):
                    s.add_clause([-v(a, c), -v(b - 1, c)])
    if not s.solve():
        s.delete()
        return None
    m = s.get_model()
    s.delete()
    return [next(c for c in range(3) if m[3 * i + c] > 0) for i in range(n)]

n = int(sys.argv[1])
out = open(sys.argv[3], "w")
total = bad = 0
adj = None
got = 0
for line in open(sys.argv[2]):
    if line.startswith("Graph"):
        adj = [[] for _ in range(n)]
        got = 0
        continue
    if adj is None or got >= n:
        continue
    m = re.match(r"\s*(\d+)\s*:\s*([\d ]+)", line)
    if not m:
        continue
    adj[int(m.group(1)) - 1] = [int(x) for x in m.group(2).split()]
    got += 1
    if got == n:
        total += 1
        col = three_color(adj, n)
        if col is None:
            bad += 1
            print(f"NON3COL graph #{total}", flush=True)
        out.write(json.dumps({"n": n, "adj": adj, "coloring": col}) + "\n")
        adj = None
out.close()
print(f"n={n} graphs={total} non3col={bad}")
