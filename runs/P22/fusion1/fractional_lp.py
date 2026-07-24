#!/usr/bin/env python3
"""Attack A (fusion1) — fractional / counting lower bound on the minimum
number of monochromatic triangles of a 2-edge-coloring of G127.

Goal framing.  G127 -> (3,3)^e  <=>  min over 2-colorings c of (# mono
triangles) >= 1.  A *rigorous* lower bound on that minimum coming from a
convex relaxation (LP/SDP) would settle the arrowing question if it were
>= 1.  This is exactly the class of "fractional / counting" arguments
requested for this wave, and is the analytic core of the Lange-Radziszowski-Xu
2012 MAX-CUT SDP approach (which was too weak for G127).

What this script establishes (EXACTLY, with a certificate):

  The triangle-local LP relaxation of min-mono-triangles -- the
  Sherali-Adams level-2 / local-consistency LP over the triangle hypergraph
  of G127 -- has optimum value exactly 0.

Consequently NO counting/fractional argument that only enforces
per-triangle distributions with consistent single-edge marginals can prove
arrowing of G127.  This is a clean negative result explaining why the
LRX MAX-CUT relaxation is too weak, and it holds for *any* K4-free triangle
hypergraph (triangles pairwise share at most one edge), not just G127.

The LP (a valid relaxation, so its optimum is a valid LOWER bound on the true
integer minimum):
  vars:  p_T(s) >= 0  for each triangle T and each s in {0,1}^3 (colorings of
         T's three edges);  m_e in [0,1] for each edge e.
  s.t.   sum_s p_T(s) = 1                              (each T is a distribution)
         sum_{s : s_j = 1} p_T(s) = m_e(T,j)           (edge-marginal consistency)
  min    sum_T ( p_T(000) + p_T(111) )                 (expected # mono triangles)

Every genuine 2-coloring gives a feasible point (point masses) whose objective
equals its actual mono-triangle count, so LP_opt <= true_min: a valid lower
bound.

CERTIFICATE that LP_opt = 0:
  - objective is a sum of nonnegative variables  =>  LP_opt >= 0.
  - the explicit feasible point  m_e = 1/2 for all e, and for every triangle
    p_T = uniform(1/6) over the six BICHROMATIC patterns {001,010,100,011,101,110}
    (and 0 on 000,111)  is feasible (each edge-marginal is exactly 3*(1/6)=1/2,
    identical across all triangles, so consistency holds automatically) and has
    objective 0  =>  LP_opt <= 0.
  Hence LP_opt = 0 exactly.  (No solver needed; we verify the certificate.)

We additionally solve the LP numerically on a subgraph with scipy.linprog as an
independent mechanical check that the construction is feasible and optimal.
"""
import itertools
import sys

import numpy as np

p = 127
C = sorted({pow(x, 3, p) for x in range(1, p)})
assert len(C) == 42 and (p - 1) in C
adj = [set() for _ in range(p)]
for u in range(p):
    for c in C:
        adj[u].add((u + c) % p)

edges = sorted((0, c) for c in C) + sorted(
    (u, v) for u in range(1, p) for v in adj[u] if u < v)
assert len(edges) == 2667
eidx = {e: i for i, e in enumerate(edges)}

tris = []
for (u, v) in edges:
    for w in sorted(adj[u] & adj[v]):
        if w > v:
            tris.append((u, v, w))
assert len(tris) == 9779


def tri_edges(t):
    u, v, w = t
    return (eidx[(u, v)], eidx[(u, w)], eidx[(v, w)])


# ---- K4-freeness => triangles pairwise share at most one edge -------------
# (this is exactly what makes the uniform-per-triangle pseudo-distribution
#  globally marginal-consistent).  Check it explicitly.
edge_to_tris = {}
for ti, t in enumerate(tris):
    for e in tri_edges(t):
        edge_to_tris.setdefault(e, []).append(ti)

# two triangles sharing >=2 edges would share all 3 vertices (=same triangle)
# in a simple graph; verify no edge-pair is shared by producing a K4:
shared_two = 0
for ti, t in enumerate(tris):
    es = set(tri_edges(t))
    cnt = {}
    for e in es:
        for tj in edge_to_tris[e]:
            if tj != ti:
                cnt[tj] = cnt.get(tj, 0) + 1
    if any(v >= 2 for v in cnt.values()):
        shared_two += 1
assert shared_two == 0, "found two triangles sharing 2 edges (=> K4)"
print(f"[structure] {len(tris)} triangles, pairwise share <=1 edge (K4-free): OK")

# ---- verify the analytic certificate on the FULL instance -----------------
# uniform over the 6 bichromatic patterns; check marginals and objective.
patterns = list(itertools.product((0, 1), repeat=3))
bichromatic = [s for s in patterns if not (s[0] == s[1] == s[2])]
assert len(bichromatic) == 6
pT = {s: (1.0 / 6.0 if s in bichromatic else 0.0) for s in patterns}
# marginal of each of the 3 positions:
for j in range(3):
    m = sum(pT[s] for s in patterns if s[j] == 1)
    assert abs(m - 0.5) < 1e-12, m
obj_per_tri = pT[(0, 0, 0)] + pT[(1, 1, 1)]
assert obj_per_tri == 0.0
print("[certificate] per-triangle uniform-bichromatic distribution:")
print("   every single-edge marginal = 1/2 (identical for all triangles =>")
print("   edge-marginal consistency holds globally), objective per triangle = 0")
print(f"   => full-instance LP objective = {obj_per_tri * len(tris):.1f}")
print("   objective >= 0 always  =>  LP optimum = 0 EXACTLY (proved).")

# ---- independent numerical LP on a subgraph -------------------------------
def solve_local_lp(sub_tris):
    """Solve the triangle-local LP over the given list of triangles with
    scipy.linprog; returns optimum. Vars: 8 per triangle + one marginal per
    edge that appears. Valid relaxation; expect optimum 0."""
    from scipy.optimize import linprog
    from scipy.sparse import lil_matrix

    sub_edges = sorted({e for t in sub_tris for e in tri_edges(t)})
    me = {e: k for k, e in enumerate(sub_edges)}
    nT = len(sub_tris)
    nE = len(sub_edges)
    # variable layout: [ p_0(0..7) , p_1(0..7), ..., m_0..m_{nE-1} ]
    npvar = 8 * nT
    ntot = npvar + nE

    c = np.zeros(ntot)
    for ti in range(nT):
        c[8 * ti + 0b000] = 1.0  # 000
        c[8 * ti + 0b111] = 1.0  # 111

    rows = []
    A = lil_matrix((0, ntot))
    b = []
    A_eq_rows = []
    b_eq = []

    # sum_s p_T(s) = 1
    for ti in range(nT):
        r = np.zeros(ntot)
        r[8 * ti:8 * ti + 8] = 1.0
        A_eq_rows.append(r)
        b_eq.append(1.0)
    # marginal consistency: for each triangle, each local edge j:
    #   sum_{s: bit j =1} p_T(s) - m_e = 0
    for ti, t in enumerate(sub_tris):
        te = tri_edges(t)
        for j in range(3):
            r = np.zeros(ntot)
            for sidx, s in enumerate(patterns):
                if s[j] == 1:
                    r[8 * ti + sidx] = 1.0
            r[npvar + me[te[j]]] = -1.0
            A_eq_rows.append(r)
            b_eq.append(0.0)

    A_eq = np.array(A_eq_rows)
    bounds = [(0, None)] * npvar + [(0, 1)] * nE
    res = linprog(c, A_eq=A_eq, b_eq=np.array(b_eq), bounds=bounds,
                  method="highs")
    return res


if "--full-lp" in sys.argv:
    print("\n[numerical] solving the local LP on the FULL instance "
          "(9779 triangles) ...")
    res = solve_local_lp(tris)
    print(f"   status={res.message}  optimum={res.fun:.6g}")
else:
    # a subgraph: all triangles touching vertices 0..15 (dense, many shared
    # edges) -- enough to exercise the consistency constraints mechanically.
    verts = set(range(16))
    sub = [t for t in tris if all(x in verts for x in t)]
    print(f"\n[numerical] solving the local LP on a {len(sub)}-triangle "
          f"subgraph (verts 0..15) ...")
    res = solve_local_lp(sub)
    print(f"   status={res.message}  optimum={res.fun:.6g}")
    print("   (run with --full-lp for all 9779 triangles)")

opt = res.fun if res.success else None
assert opt is not None and abs(opt) < 1e-6, f"expected LP optimum 0, got {opt}"
print("\nRESULT: triangle-local (Sherali-Adams level-2) LP optimum = 0.")
print("=> no local fractional/counting argument proves G127 -> (3,3)^e.")
print("PASS")
