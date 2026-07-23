"""Decide the minimum order of a 'quasi-Folkman' triangle system, the object from
Appendix A of arXiv:2506.14942: a set T of triples of [n] such that
  (i)  no four triples of T span only 4 vertices (T contains no 'K4', i.e. the
       4 faces of a 4-set are never all present), and
  (ii) every 2-coloring of the edges of K_n yields a triple of T whose 3 edges
       are monochromatic.
The paper found examples with n=12, then n=11 (circulant, |T|=88), leaving the
minimum open. CEGAR: synthesis over t_tau (one bool per triple), forall-side =
edge colorings; blocking clauses with S_n orbit sampling.

Usage: python3 quasi_min.py n [max_iters]
Output: 'EXISTS' with a witness T (verified independently), or 'NONE' when
synthesis goes UNSAT (=> no quasi-Folkman system on n vertices).
"""
import sys, random, time, json
from itertools import combinations, permutations
from pysat.solvers import Cadical153
from arrow import solve as kissat_solve

n = int(sys.argv[1])
MAXIT = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9

VERTS = list(range(n))
EDGES = list(combinations(VERTS, 2))
E_IDX = {e: i for i, e in enumerate(EDGES)}
TRIPLES = list(combinations(VERTS, 3))
T_IDX = {t: i for i, t in enumerate(TRIPLES)}
tri_edges = {t: [(t[0], t[1]), (t[0], t[2]), (t[1], t[2])] for t in TRIPLES}

def tvar(t):
    return T_IDX[t] + 1
NV = len(TRIPLES)

solver = Cadical153()
# (i) no 4-set has all four faces
for q in combinations(VERTS, 4):
    faces = [tvar(f) for f in combinations(q, 3)]
    solver.add_clause([-v for v in faces])
# non-empty
solver.add_clause([tvar(t) for t in TRIPLES])

rng = random.Random(42)
PERMS = [tuple(range(n))] + [tuple(rng.sample(VERTS, n)) for _ in range(199)]

def mono_triples(color):  # color: list over EDGES of 0/1
    out = []
    for t in TRIPLES:
        c = [color[E_IDX[e]] for e in tri_edges[t]]
        if c[0] == c[1] == c[2]:
            out.append(t)
    return out

def block(color):
    mono = mono_triples(color)
    seen = set()
    for p in PERMS:
        img = frozenset(tuple(sorted((p[a], p[b], p[c]))) for (a, b, c) in mono)
        if img in seen:
            continue
        seen.add(img)
        if not img:
            print("NONE trivially: a coloring with zero mono triples exists globally")
            sys.exit(0)
        solver.add_clause([tvar(t) for t in img])

# seed
for _ in range(2000):
    block([rng.getrandbits(1) for _ in EDGES])

def check(T):
    """SAT check: exists coloring of K_n edges with no mono triple in T.
    Returns None if UNSAT (T is quasi-Folkman), else the coloring."""
    clauses = []
    for t in T:
        evs = [E_IDX[e] + 1 for e in tri_edges[t]]
        clauses.append(evs)
        clauses.append([-v for v in evs])
    status, model, _ = kissat_solve(len(EDGES), clauses)
    if status == "UNSAT":
        return None
    color = [1 if (i + 1) in model else 0 for i in range(len(EDGES))]
    # independent verification
    for t in T:
        c = [color[E_IDX[e]] for e in tri_edges[t]]
        assert not (c[0] == c[1] == c[2])
    return color

t0 = time.time()
it = 0
while it < MAXIT:
    it += 1
    if not solver.solve():
        print(f"[{time.time()-t0:.0f}s] n={n}: SYNTHESIS UNSAT after {it-1} iters "
              f"=> NO quasi-Folkman system on {n} vertices.")
        sys.exit(0)
    model = set(l for l in solver.get_model() if l > 0)
    T = [t for t in TRIPLES if tvar(t) in model]
    color = check(T)
    if color is None:
        print(f"[{time.time()-t0:.0f}s] n={n}: EXISTS — quasi-Folkman system with "
              f"|T|={len(T)} found and verified (kissat UNSAT).")
        json.dump({"n": n, "T": T}, open(f"out/quasi_n{n}.json", "w"))
        sys.exit(0)
    block(color)
    if it % 200 == 0:
        print(f"[{time.time()-t0:.0f}s] n={n} iter {it}: |T|={len(T)} colorable",
              flush=True)
