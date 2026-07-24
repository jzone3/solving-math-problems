#!/usr/bin/env python3
"""Large-neighborhood search for a zero-mono-triangle coloring of E(G127).

Seed: best assignment found by walk.c (walk_best_<seed>.txt).
Loop: free the edges of a random sample of currently-mono triangles plus
random extra edges; solve the induced sub-MaxSAT exactly with RC2 (soft =
one unit-weight clause per affected triangle-side); accept if strictly
better. Restart neighborhood otherwise.

Usage: lns.py <seed_file> <out_prefix> [rng_seed]
"""
import random, sys, time

from pysat.formula import WCNF
from pysat.examples.rc2 import RC2

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)
edges_star = sorted((0, c) for c in C)
edges_rest = sorted((u, v) for u in range(1, p) for v in adj[u] if u < v)
edges = edges_star + edges_rest
NE = len(edges)
tris = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tris.append((u, v, w))
var = {e: i for i, e in enumerate(edges)}
tri_edges = []
for (u, v, w) in tris:
    tri_edges.append((var[(u, v)], var[(u, w)], var[(v, w)]))
etris = [[] for _ in range(NE)]
for t, (a, b, c) in enumerate(tri_edges):
    etris[a].append(t); etris[b].append(t); etris[c].append(t)

seed_file, out_prefix = sys.argv[1], sys.argv[2]
rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 42)

with open(seed_file) as f:
    lines = f.read().split()
bits = [ln for ln in lines if set(ln) <= {"0", "1"} and len(ln) == NE][0]
col = [int(b) for b in bits]


def mono_count(col):
    return sum(1 for (a, b, c) in tri_edges if col[a] == col[b] == col[c])


best = cur = mono_count(col)
print(f"seed cost {best}", flush=True)
t0 = time.time()
it = 0
stuck = 0
while True:
    it += 1
    viol = [t for t, (a, b, c) in enumerate(tri_edges)
            if col[a] == col[b] == col[c]]
    if not viol:
        break
    if stuck >= 800:
        for e in rng.sample(range(NE), 12):
            col[e] ^= 1
        cur = mono_count(col)
        stuck = 1
        print(f"it={it} kick -> cur {cur}", flush=True)
    boost = min(stuck // 400, 2)
    nv_pick = min(len(viol), rng.randint(20, 60 + 40 * boost))
    free = set()
    for t in rng.sample(viol, nv_pick):
        free.update(tri_edges[t])
    target = min(550 + 150 * boost, len(free) + 250 + 100 * boost)
    while len(free) < target:
        free.add(rng.randrange(NE))
    free = sorted(free)
    fidx = {e: i + 1 for i, e in enumerate(free)}  # RC2 vars 1..n
    wcnf = WCNF()
    base_cost = 0
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
    fixed_cost = 0
    for t, (a, b, c) in enumerate(tri_edges):
        if t not in seen and col[a] == col[b] == col[c]:
            fixed_cost += 1
    with RC2(wcnf) as rc2:
        model = rc2.compute()
        sub = rc2.cost
    total = fixed_cost + sub
    if total <= cur or (total == cur + 1 and rng.random() < 0.05):
        mset = {abs(l): l > 0 for l in model}
        for e in free:
            v = fidx[e]
            if v in mset:
                col[e] = 1 if mset[v] else 0
        cur = total
        if total < best:
            best = total
            stuck = 0
            print(f"it={it} t={time.time()-t0:.0f}s new best {best}", flush=True)
            with open(f"{out_prefix}_best.txt", "w") as f:
                f.write(f"c nmono {best}\n")
                f.write("".join(map(str, col)) + "\n")
            if best == 0:
                print("ZERO FOUND", flush=True)
                break
        else:
            stuck += 1
    else:
        stuck += 1
    if it % 500 == 0:
        print(f"it={it} t={time.time()-t0:.0f}s best {best} stuck={stuck}", flush=True)
