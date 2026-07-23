"""Phase-3 maximality CEGAR for Problem 5.1, upgraded:
- full PGammaU(3,3) (order 12096) available; new counterexamples blocked over a
  random sample of ORBIT_SAMPLE group elements; resumed pool blocked over the
  192-element monomial subgroup (memory economy).
- partial lex symmetry breaking on the candidate: s <=_lex g(s) for LEX_BREAK
  random group elements (sound: solution orbits are closed under Aut(H_3),
  maximality and K4-freeness are invariant).
- multiple workers share out/cegar_max_cex.txt (append; atomic-ish 1KB lines).
Usage: python3 cegar_max2.py <seed> [orbit_sample] [lex_break]
"""
import random, sys, time, json, os
from itertools import combinations
from pysat.solvers import Cadical153
from pysat.formula import IDPool
from h3 import adj, edges as h3_edges
from arrow import cnf_for_arrowing, solve as kissat_solve, verify_coloring, has_k4
from aut import generate_group
from aut_full import full_group

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 1
ORBIT_SAMPLE = int(sys.argv[2]) if len(sys.argv) > 2 else 256
LEX_BREAK = int(sys.argv[3]) if len(sys.argv) > 3 else 48

N = 63
ADJ = [set(j for j in range(N) if adj[i][j]) for i in range(N)]
EDGES = sorted((min(i, j), max(i, j)) for i, j in h3_edges)

TRIS = []
for i in range(N):
    for j in sorted(x for x in ADJ[i] if x > i):
        for k in sorted(x for x in ADJ[i] & ADJ[j] if x > j):
            TRIS.append((i, j, k))
K4S = []
for i in range(N):
    ni = sorted(x for x in ADJ[i] if x > i)
    for a, j in enumerate(ni):
        common = [x for x in ni[a+1:] if x in ADJ[j]]
        for b, k in enumerate(common):
            for l in common[b+1:]:
                if l in ADJ[k]:
                    K4S.append((i, j, k, l))

pool = IDPool()
S = {e: pool.id(("s", e)) for e in EDGES}
T = {t: pool.id(("t", t)) for t in TRIS}
solver = Cadical153()
tri_edges = {t: [(t[0], t[1]), (t[0], t[2]), (t[1], t[2])] for t in TRIS}

for Q in K4S:
    solver.add_clause([-S[e] for e in combinations(Q, 2)])
for t in TRIS:
    evs = [S[e] for e in tri_edges[t]]
    tv = T[t]
    for ev in evs:
        solver.add_clause([-tv, ev])
    solver.add_clause([tv] + [-ev for ev in evs])

# maximality
k4s_of_edge = {e: [] for e in EDGES}
for Q in K4S:
    for e in combinations(Q, 2):
        k4s_of_edge[e].append(Q)
for e in EDGES:
    ors = []
    for Q in k4s_of_edge[e]:
        y = pool.id(("y", Q, e))
        others = [S[f] for f in combinations(Q, 2) if f != e]
        for ov in others:
            solver.add_clause([-y, ov])
        solver.add_clause([y] + [-ov for ov in others])
        ors.append(y)
    solver.add_clause([S[e]] + ors)
solver.add_clause([T[t] for t in TRIS])

rng = random.Random(SEED)
GROUP192 = generate_group()
GROUPFULL = full_group()
print(f"worker seed={SEED}: groups {len(GROUP192)}/{len(GROUPFULL)}", flush=True)

def edge_perm(g):
    m = {}
    for (a, b) in EDGES:
        x, y = g[a], g[b]
        m[(a, b)] = (min(x, y), max(x, y))
    return m

# partial lex symmetry breaking: s <=_lex s o g  (lex-leader, full equivalence chain)
for gi, g in enumerate(rng.sample(GROUPFULL, LEX_BREAK)):
    ep = edge_perm(g)
    moved = [e for e in EDGES if ep[e] != e]
    if not moved:
        continue
    prev = None  # None means "equal so far" is vacuously true
    for e in moved:
        a, b = S[e], S[ep[e]]
        if prev is None:
            solver.add_clause([-a, b])                      # a <= b
        else:
            solver.add_clause([-prev, -a, b])               # eq -> (a <= b)
        nxt = pool.id(("lex", SEED, gi, e))
        if prev is None:
            # nxt <-> (a == b)
            solver.add_clause([-nxt, -a, b])
            solver.add_clause([-nxt, a, -b])
            solver.add_clause([nxt, -a, -b])
            solver.add_clause([nxt, a, b])
        else:
            # nxt <-> prev & (a == b)
            solver.add_clause([-nxt, prev])
            solver.add_clause([-nxt, -a, b])
            solver.add_clause([-nxt, a, -b])
            solver.add_clause([nxt, -prev, -a, -b])
            solver.add_clause([nxt, -prev, a, b])
        prev = nxt

TRI_IDX = {t: n for n, t in enumerate(TRIS)}
def tri_perm(g):
    return [TRI_IDX[tuple(sorted((g[a], g[b], g[c])))] for (a, b, c) in TRIS]

PERMS192 = [tri_perm(g) for g in GROUP192]

def mono_idx(color):
    out = []
    for n, t in enumerate(TRIS):
        c = [color[e] for e in tri_edges[t]]
        if c[0] == c[1] == c[2]:
            out.append(n)
    return out

def block(mono, tps):
    seen = set()
    for tp in tps:
        img = frozenset(tp[m] for m in mono)
        if img not in seen:
            seen.add(img)
            solver.add_clause([T[TRIS[m]] for m in img])

CEX = "out/cegar_max_cex.txt"
nload = 0
if os.path.exists(CEX):
    with open(CEX) as f:
        for line in f:
            bits = line.strip()
            if len(bits) == len(EDGES):
                color = {e: int(bits[k]) for k, e in enumerate(EDGES)}
                block(mono_idx(color),
                      [PERMS192[0]] + rng.sample(PERMS192, 24))
                nload += 1
print(f"worker {SEED}: resumed {nload} cex", flush=True)
for _ in range(1000):
    block(mono_idx({e: rng.getrandbits(1) for e in EDGES}), [list(range(len(TRIS)))])
cex_out = open(CEX, "a")

t0 = time.time()
it = 0
seen_bits = 0
while True:
    it += 1
    if not solver.solve():
        print(f"[{time.time()-t0:.0f}s] worker {SEED}: SYNTHESIS UNSAT (within lex-broken "
              f"space) after {it-1} iters — with sound symmetry breaking this proves "
              f"Problem 5.1 is NO.", flush=True)
        break
    model = set(l for l in solver.get_model() if l > 0)
    kept = [e for e in EDGES if S[e] in model]
    adjset = [set() for _ in range(N)]
    for a, b in kept:
        adjset[a].add(b); adjset[b].add(a)
    assert has_k4(N, adjset) is None
    tris = [t for t in TRIS if all(b in adjset[a] for a, b in tri_edges[t])]
    var, clauses = cnf_for_arrowing(kept, tris)
    status, cmodel, _ = kissat_solve(len(var), clauses)
    if status == "UNSAT":
        print(f"!!! worker {SEED} iter {it}: FOLKMAN FOUND: {len(kept)} edges", flush=True)
        json.dump({"edges": kept}, open(f"out/FOLKMAN_w{SEED}.json", "w"))
        break
    assert verify_coloring(kept, tris, var, cmodel) is None
    color = {e: (1 if var[e] in cmodel else 0) if e in var else rng.getrandbits(1)
             for e in EDGES}
    tps = [tri_perm(g) for g in rng.sample(GROUPFULL, ORBIT_SAMPLE)]
    block(mono_idx(color), tps)
    cex_out.write("".join(str(color[e]) for e in EDGES) + "\n")
    cex_out.flush()
    if it % 10 == 0:
        print(f"[{time.time()-t0:.0f}s] w{SEED} iter {it}: {len(kept)} edges, "
              f"{len(tris)} tris — colorable", flush=True)
