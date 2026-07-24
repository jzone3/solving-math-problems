#!/usr/bin/env python3
"""Path-relinking recombination: for pairs of basin-record colorings, free
exactly the edges where they disagree (plus a small random halo) and solve
that sub-MaxSAT exactly with RC2, keeping everything else fixed to the first
parent. Reports any coloring better than both parents.
Usage: recombine.py <out_prefix> <fileA> <fileB> [halo=150]
"""
import random, sys

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)
edges = sorted((0, c) for c in C) + sorted(
    (u, v) for u in range(1, p) for v in adj[u] if u < v)
NE = len(edges)
var = {e: i for i, e in enumerate(edges)}
tri_edges = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tri_edges.append((var[(u, v)], var[(u, w)], var[(v, w)]))
etris = [[] for _ in range(NE)]
for t, (a, b, c) in enumerate(tri_edges):
    etris[a].append(t); etris[b].append(t); etris[c].append(t)


def load(fn):
    toks = open(fn).read().split()
    bits = [t for t in toks if set(t) <= {"0", "1"} and len(t) == NE][0]
    return [int(b) for b in bits]


def mono_count(col):
    return sum(1 for (a, b, c) in tri_edges if col[a] == col[b] == col[c])


out_prefix, fa, fb = sys.argv[1], sys.argv[2], sys.argv[3]
halo = int(sys.argv[4]) if len(sys.argv) > 4 else 150
rng = random.Random(12345)

A, B = load(fa), load(fb)
ca, cb = mono_count(A), mono_count(B)
diff = [e for e in range(NE) if A[e] != B[e]]
print(f"parents {ca} {cb}; hamming {len(diff)}", flush=True)
free = set(diff)
while len(free) < len(diff) + halo:
    free.add(rng.randrange(NE))
free = sorted(free)
fidx = {e: i + 1 for i, e in enumerate(free)}
col = A[:]
wcnf = WCNF()
seen = set()
for e in free:
    for t in etris[e]:
        if t in seen:
            continue
        seen.add(t)
        lits_pos, lits_neg, sat_pos, sat_neg = [], [], False, False
        for x in tri_edges[t]:
            if x in fidx:
                lits_pos.append(fidx[x]); lits_neg.append(-fidx[x])
            else:
                if col[x] == 1: sat_pos = True
                else: sat_neg = True
        if not sat_pos:
            wcnf.append(lits_pos, weight=1)
        if not sat_neg:
            wcnf.append(lits_neg, weight=1)
fixed_cost = sum(1 for t, (a, b, c) in enumerate(tri_edges)
                 if t not in seen and col[a] == col[b] == col[c])
with RC2(wcnf) as rc2:
    model = rc2.compute()
    total = fixed_cost + rc2.cost
print(f"recombined cost {total}", flush=True)
if total < min(ca, cb):
    mset = {abs(l): l > 0 for l in model}
    for e in free:
        v = fidx[e]
        if v in mset:
            col[e] = 1 if mset[v] else 0
    with open(f"{out_prefix}_best.txt", "w") as f:
        f.write(f"c nmono {total}\n")
        f.write("".join(map(str, col)) + "\n")
    print(f"IMPROVED: {total} < min({ca},{cb}) -> {out_prefix}_best.txt", flush=True)
