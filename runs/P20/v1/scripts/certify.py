#!/usr/bin/env python3
"""Read gzipped GENREG -a stdout streams for one n, produce a certificate file.

Certificate: one JSON object per line: {"n":..., "adj":[[...],...], "coloring":[...]}
adj is 1-based adjacency lists; coloring is list of colors 0/1/2 per vertex (1-based order).
If a graph is NOT 3-colorable it is recorded with "coloring": null (a P20 witness candidate!).
"""
import gzip, json, re, sys, glob
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
    col = [None] * n
    for i in range(n):
        for c in range(3):
            if m[3 * i + c] > 0:
                col[i] = c
    return col

def parse_stream(fh, n):
    adj = None
    got = 0
    for raw in fh:
        line = raw.decode() if isinstance(raw, bytes) else raw
        if line.startswith("Graph"):
            adj = [[] for _ in range(n)]
            got = 0
            continue
        if adj is None or got >= n:
            continue
        m = re.match(r"\s*(\d+)\s*:\s*([\d ]+)", line)
        if not m:
            continue
        v = int(m.group(1))
        adj[v - 1] = [int(x) for x in m.group(2).split()]
        got += 1
        if got == n:
            yield adj
            adj = None

n = int(sys.argv[1])
outf = open(sys.argv[2], "w")
total = bad = 0
for f in sorted(glob.glob(f"/home/ubuntu/p20/gen/n{n}/asc.*.gz")):
    with gzip.open(f, "rt") as fh:
        for adj in parse_stream(fh, n):
            total += 1
            col = three_color(adj, n)
            if col is None:
                bad += 1
                print(f"NON3COL found! graph #{total} in {f}", flush=True)
            outf.write(json.dumps({"n": n, "adj": adj, "coloring": col}) + "\n")
outf.close()
print(f"n={n} graphs={total} non3col={bad}")
