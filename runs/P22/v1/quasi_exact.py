"""Exact decision of quasi-Folkman existence on n vertices (n<=9) using the
complete low-popcount mono-mask enumeration from enum_mono.c.

A triple system T (no 4-set with all 4 faces) is quasi-Folkman iff it hits the
mono-set of EVERY coloring. Constraints from masks with popcount <= thresh are
necessary; a SAT model is then checked exactly against ALL colorings by a
single kissat call (UNSAT of the coloring instance = T quasi-Folkman). CEGAR:
a colorable model's coloring adds its (full) mono-mask as a new clause.
UNSAT of the synthesis => NO quasi-Folkman system on n vertices (constraints
are a subset of the necessary ones).

Usage: python3 quasi_exact.py n maskfile
"""
import sys, json, time, random
from itertools import combinations
from pysat.solvers import Cadical153
from arrow import solve as kissat_solve

n = int(sys.argv[1])
maskfile = sys.argv[2]
VERTS = list(range(n))
EDGES = list(combinations(VERTS, 2))
E_IDX = {e: i for i, e in enumerate(EDGES)}
TRIPLES = list(combinations(VERTS, 3))
tri_edges = {t: [(t[0], t[1]), (t[0], t[2]), (t[1], t[2])] for t in TRIPLES}
NT = len(TRIPLES)

rng = random.Random(7)
PERMS = [tuple(range(n))] + [tuple(rng.sample(VERTS, n)) for _ in range(299)]

solver = Cadical153()
for q in combinations(VERTS, 4):
    solver.add_clause([-(TRIPLES.index(f) + 1) for f in combinations(q, 3)])

t0 = time.time()
nmask = 0
with open(maskfile) as f:
    for line in f:
        h, l = line.strip().split(":"); m = (int(h, 16) << 64) | int(l, 16)
        solver.add_clause([i + 1 for i in range(NT) if (m >> i) & 1])
        nmask += 1
print(f"[{time.time()-t0:.0f}s] loaded {nmask} mask clauses", flush=True)

def check(T):
    clauses = []
    for t in T:
        evs = [E_IDX[e] + 1 for e in tri_edges[t]]
        clauses.append(evs)
        clauses.append([-v for v in evs])
    status, model, _ = kissat_solve(len(EDGES), clauses)
    if status == "UNSAT":
        return None
    color = [1 if (i + 1) in model else 0 for i in range(len(EDGES))]
    for t in T:
        c = [color[E_IDX[e]] for e in tri_edges[t]]
        assert not (c[0] == c[1] == c[2])
    return color

it = 0
while True:
    it += 1
    if not solver.solve():
        print(f"[{time.time()-t0:.0f}s] n={n}: SYNTHESIS UNSAT after {it-1} CEGAR iters "
              f"=> NO quasi-Folkman system exists on {n} vertices.")
        break
    model = set(l for l in solver.get_model() if l > 0)
    T = [TRIPLES[i] for i in range(NT) if (i + 1) in model]
    color = check(T)
    if color is None:
        print(f"[{time.time()-t0:.0f}s] n={n}: EXISTS — |T|={len(T)}, verified.")
        json.dump({"n": n, "T": T}, open(f"out/quasi_exact_n{n}.json", "w"))
        break
    mono_t = [t for t in TRIPLES
              if len({color[E_IDX[e]] for e in tri_edges[t]}) == 1]
    T_ID = {t: i + 1 for i, t in enumerate(TRIPLES)}
    seen = set()
    for p in PERMS:
        img = frozenset(tuple(sorted((p[a], p[b], p[c]))) for (a, b, c) in mono_t)
        if img not in seen:
            seen.add(img)
            solver.add_clause([T_ID[t] for t in img])
    if it % 100 == 0:
        print(f"[{time.time()-t0:.0f}s] iter {it}: |T|={len(T)} colorable", flush=True)
