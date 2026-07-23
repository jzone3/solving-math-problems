"""Structured 2-level (exists-forall) search for Problem 5.1 of arXiv:2506.14942:
does H_3 have a K4-free subgraph H with H -> (3,3)^e ?

This is a Sigma_2 question. We solve it CEGAR-style over the FULL space of
spanning subgraphs of H_3 (edge-subset variables s_e), not just clique
replacements:

Synthesis SAT instance over s_e (edge kept), t_T (triangle T fully kept):
  - K4-freeness: for each of the 9576 K4s of H_3, not all 6 edges kept.
  - t_T <-> (all 3 edges of T kept), for all 5376 triangles.
  - WLOG core conditions (sound: removing an edge in <=1 triangle, or a
    vertex of degree <8 in a K4-free graph, preserves arrowing — Appendix A
    of the paper / Bikov–Nenov):
      * each kept edge lies in >= 2 kept triangles,
      * each vertex has degree 0 or >= 8.
  - For every counterexample coloring Delta (a full 2-coloring of E(H_3)):
      some triangle monochromatic under Delta must be fully kept.

Loop: solve synthesis -> candidate G -> SAT arrowing check (kissat).
  colorable => extract coloring, extend to E(H_3), add blocking clause;
  UNSAT => G is a K4-free Folkman graph on <=63 vertices (Graham prize).
Synthesis UNSAT => PROOF that H_3 has no K4-free arrowing subgraph
(resolves Problem 5.1 in the negative).
"""
import random, sys, time, json
from itertools import combinations
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from h3 import adj, edges as h3_edges
from arrow import cnf_for_arrowing, solve as kissat_solve, verify_coloring, has_k4
from aut import generate_group

N = 63
ADJ = [set(j for j in range(N) if adj[i][j]) for i in range(N)]
EDGES = sorted((min(i, j), max(i, j)) for i, j in h3_edges)
E_IDX = {e: k for k, e in enumerate(EDGES)}

# triangles and K4s of H_3
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
assert len(TRIS) == 5376 and len(K4S) == 9576

pool = IDPool()
def S(e):  # edge var
    return pool.id(("s", e))
def T(t):  # triangle var
    return pool.id(("t", t))

solver = Cadical153()

# K4-freeness
for (i, j, k, l) in K4S:
    es = [S(e) for e in combinations((i, j, k, l), 2)]
    solver.add_clause([-v for v in es])

# t_T <-> edges
tri_edges = {t: [(t[0], t[1]), (t[0], t[2]), (t[1], t[2])] for t in TRIS}
tris_of_edge = {e: [] for e in EDGES}
for t in TRIS:
    tv = T(t)
    evs = [S(e) for e in tri_edges[t]]
    for ev in evs:
        solver.add_clause([-tv, ev])
    solver.add_clause([tv] + [-ev for ev in evs])
    for e in tri_edges[t]:
        tris_of_edge[e].append(tv)

# each kept edge in >= 2 kept triangles: s_e -> sum(t_T) >= 2
for e in EDGES:
    tvs = tris_of_edge[e]  # 16 each
    # s_e -> at least 2 of tvs:  equivalently  ~s_e OR atleast2(tvs)
    # encode: for the "at most len-2 false" formulation use CardEnc.atleast with conditional
    cnf = CardEnc.atleast(lits=tvs, bound=2, vpool=pool, encoding=EncType.seqcounter)
    se = S(e)
    for cl in cnf.clauses:
        solver.add_clause([-se] + cl)

# degree 0 or >= 8
for v in range(N):
    evs = [S((min(v, u), max(v, u))) for u in sorted(ADJ[v])]
    uv = pool.id(("used", v))
    for ev in evs:
        solver.add_clause([-ev, uv])          # any edge -> used
    cnf = CardEnc.atleast(lits=evs, bound=8, vpool=pool, encoding=EncType.seqcounter)
    for cl in cnf.clauses:
        solver.add_clause([-uv] + cl)

# require a non-empty graph (at least one triangle kept)
solver.add_clause([T(t) for t in TRIS])

GROUP = generate_group()  # 192 automorphisms of H_3 (as perms of vertices)
# sanity: each is a graph automorphism
for g in GROUP[:5] + GROUP[-5:]:
    for (a, b) in EDGES[:50]:
        assert g[b] in ADJ[g[a]]

def mono_tris(color):  # color: dict edge->0/1
    out = []
    for t in TRIS:
        c = [color[e] for e in tri_edges[t]]
        if c[0] == c[1] == c[2]:
            out.append(t)
    return out

def add_blocking(color):
    solver.add_clause([T(t) for t in mono_tris(color)])

TRI_IDX = {t: n for n, t in enumerate(TRIS)}
def tri_perm(g):
    out = []
    for (a, b, c) in TRIS:
        out.append(TRI_IDX[tuple(sorted((g[a], g[b], g[c])))])
    return out
TRI_PERMS = None  # built lazily after GROUP

def add_blocking_orbit(color, group):
    """Block the coloring and its images under all vertex automorphisms.
    If T is mono under c, then g(T) is mono under c_g; so the mono set of c_g
    is the g-image of the mono set of c."""
    global TRI_PERMS
    if TRI_PERMS is None:
        TRI_PERMS = [tri_perm(g) for g in group]
    mono = [TRI_IDX[t] for t in mono_tris(color)]
    seen = set()
    for tp in TRI_PERMS:
        img = frozenset(tp[m] for m in mono)
        if img in seen:
            continue
        seen.add(img)
        solver.add_clause([T(TRIS[m]) for m in img])

# seed with random full colorings
rng = random.Random(2026)
NSEED = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
for _ in range(NSEED):
    add_blocking({e: rng.getrandbits(1) for e in EDGES})

# resume: reload previously found counterexample colorings (with orbits)
CEX_FILE = "out/cegar_cex.txt"
import os
nloaded = 0
if os.path.exists(CEX_FILE):
    with open(CEX_FILE) as f:
        for line in f:
            bits = line.strip()
            if len(bits) == len(EDGES):
                add_blocking_orbit({e: int(bits[k]) for k, e in enumerate(EDGES)},
                                   GROUP)
                nloaded += 1
print(f"resumed {nloaded} counterexamples", flush=True)
cex_out = open(CEX_FILE, "a")

log = []
t0 = time.time()
it = 0
while True:
    it += 1
    ok = solver.solve()
    if not ok:
        print(f"[{time.time()-t0:.0f}s] SYNTHESIS UNSAT after {it-1} counterexamples "
              f"(+{NSEED} seeds): H_3 has NO K4-free arrowing subgraph satisfying the "
              f"WLOG core conditions => Problem 5.1 answered NO.")
        break
    model = set(l for l in solver.get_model() if l > 0)
    kept = [e for e in EDGES if S(e) in model]
    adjset = [set() for _ in range(N)]
    for a, b in kept:
        adjset[a].add(b); adjset[b].add(a)
    assert has_k4(N, adjset) is None
    # arrowing check
    tris = [t for t in TRIS if all(b in adjset[a] for a, b in tri_edges[t])]
    var, clauses = cnf_for_arrowing(kept, tris)
    status, cmodel, _ = kissat_solve(len(var), clauses)
    if status == "UNSAT":
        print(f"!!! [{time.time()-t0:.0f}s] iter {it}: FOLKMAN GRAPH FOUND: "
              f"{len(kept)} edges")
        json.dump({"edges": kept}, open("out/FOLKMAN_cegar.json", "w"))
        break
    bad = verify_coloring(kept, tris, var, cmodel)
    assert bad is None
    # extend coloring to all of E(H_3): unused edges colored randomly
    color = {}
    for e in EDGES:
        if e in var:
            color[e] = 1 if var[e] in cmodel else 0
        else:
            color[e] = rng.getrandbits(1)
    add_blocking_orbit(color, GROUP)
    cex_out.write("".join(str(color[e]) for e in EDGES) + "\n")
    cex_out.flush()
    if it % 25 == 0:
        print(f"[{time.time()-t0:.0f}s] iter {it}: candidate {len(kept)} edges, "
              f"{len(tris)} tris — colorable; blocked", flush=True)
