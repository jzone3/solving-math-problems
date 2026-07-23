#!/usr/bin/env python3
"""Star-tree DFS prover for G127 -> (3,3)^e.

Key observation: fixing all 42 star-edge colors of vertex 0 makes the residual
formula (empirically) trivially UNSAT for kissat. So we run a DFS over the 42
star variables with an incremental CaDiCaL solver: at each node, solve under
assumptions with a conflict budget; UNSAT prunes the subtree, SAT means a good
coloring of the WHOLE graph exists (verified independently), unknown branches.

Soundness of symmetry breaking (coloring side only):
 - unit var(0,1)=red (global color flip),
 - lex-leader clauses over the 42-star-edge vector under Stab(0) x {id,flip}
   (Stab(0) = multiplications by cubic residues, which permute star edges).
Both are the same sound constraints as in sb.cnf (Crawford et al. 1996).

If DFS completes with no SAT leaf => plain instance UNSAT => G127 arrows (3,3)^e.
(DRAT for the final claim is produced separately by replaying the refuted tree
as cube-and-conquer with kissat + drat-trim; see star_cnc.py.)
"""
import sys, time
from pysat.solvers import Cadical195

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)

edges_star = sorted((0, c) for c in C)
edges_rest = sorted((u, v) for u in range(1, p) for v in adj[u] if u < v)
edges = edges_star + edges_rest
var = {e: i + 1 for i, e in enumerate(edges)}
nv = len(edges)

tris = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tris.append((u, v, w))
assert len(tris) == 9779

clauses = []
for (u, v, w) in tris:
    a, b, c = var[(u, v)], var[(u, w)], var[(v, w)]
    clauses.append([a, b, c])
    clauses.append([-a, -b, -c])

# NOTE: color flip is part of the lex-leader group below; do NOT also add a
# unit clause fixing an edge color (the flip lex constraint at position 0
# forces var(0,1)=False, so a red unit would be contradictory).


def ev(e):
    u, v = e
    return var[(u, v) if u < v else (v, u)]


def lex_clauses(seq_pairs, next_var):
    cls = []
    yprev = None
    for i, (x, y) in enumerate(seq_pairs):
        if yprev is None:
            cls.append([-x, y])
            if i == len(seq_pairs) - 1:
                break
            ynew = next_var; next_var += 1
            cls.append([-ynew, -x, y]); cls.append([-ynew, x, -y])
            cls.append([ynew, -x, -y]); cls.append([ynew, x, y])
        else:
            cls.append([-yprev, -x, y])
            if i == len(seq_pairs) - 1:
                break
            ynew = next_var; next_var += 1
            cls.append([-ynew, yprev])
            cls.append([-ynew, -x, y]); cls.append([-ynew, x, -y])
            cls.append([ynew, -yprev, -x, -y]); cls.append([ynew, -yprev, x, y])
        yprev = ynew
    return cls, next_var

next_var = nv + 1
for a in C:
    for flip in (False, True):
        if a == 1 and not flip:
            continue
        pairs = []
        for e in edges_star:
            x = var[e]
            u, v = e
            y = ev(((a * u) % p, (a * v) % p))
            pairs.append((x, -y if flip else y))
        cls, next_var = lex_clauses(pairs, next_var)
        clauses.extend(cls)

BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
NSTAR = 42
starvars = [var[e] for e in edges_star]  # 1..42

solver = Cadical195(bootstrap_with=clauses)
stats = {"unsat": 0, "nodes": 0, "sat": 0, "deep": 0}
t0 = time.time()


def report():
    print(f"t={time.time()-t0:.0f}s nodes={stats['nodes']} unsat_leaves={stats['unsat']} deep={stats['deep']}", flush=True)


def dfs(assump):
    stats["nodes"] += 1
    if stats["nodes"] % 1000 == 0:
        report()
    d = len(assump)
    solver.conf_budget(BUDGET if d < NSTAR else 10**9)
    r = solver.solve_limited(assumptions=assump)
    if r is False:
        stats["unsat"] += 1
        return False
    if r is True:
        stats["sat"] += 1
        model = solver.get_model()
        with open("star_tree_SAT_model.txt", "w") as f:
            f.write(" ".join(map(str, model[:nv])) + "\n")
        print("SAT! good coloring found; model written", flush=True)
        return True
    if d == NSTAR:
        stats["deep"] += 1
        print(f"WARN: unresolved full-star node {assump}", flush=True)
        return None
    v = starvars[d]
    for lit in (v, -v):
        res = dfs(assump + [lit])
        if res is True:
            return True
    return False


res = dfs([])
report()
if stats["sat"]:
    print("RESULT: SAT (candidate coloring found — verify independently)")
elif stats["deep"] == 0:
    print("RESULT: UNSAT — G127 arrows (3,3)^e (modulo replay certification)")
else:
    print("RESULT: incomplete (unresolved deep nodes)")
