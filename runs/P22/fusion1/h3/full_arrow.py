#!/usr/bin/env python3
"""Decide target #1's literal question for the full graph: does H_3 arrow (3,3)^e
using ALL of its triangles?  Emits the arrowing CNF over every triangle of H_3
(not just the non-degenerate system T_3) so an UNSAT + DRAT certificate proves
H_3 -> (3,3)^e.  (H_3 is not K_4-free, so this is a decided arrowing fact, not a
Folkman bound.)  Reuses the verified constructor in build_h3.py.
"""
from pathlib import Path
import build_h3 as B

G = B.build()
tris, nondeg = B.triangles_and_system(G)
edges = G["edges"]
eidx = {e: i + 1 for i, e in enumerate(edges)}


def evar(u, v):
    return eidx[(u, v) if u < v else (v, u)]


clauses = []
for (i, j, k) in tris:
    a, b, c = evar(i, j), evar(i, k), evar(j, k)
    clauses.append((a, b, c))
    clauses.append((-a, -b, -c))

out = Path(__file__).resolve().parent / "h3_full.cnf"
with open(out, "w") as f:
    f.write(f"p cnf {len(edges)} {len(clauses)}\n")
    for cl in clauses:
        f.write(" ".join(map(str, cl)) + " 0\n")

print(f"H_3 full arrowing: {len(edges)} vars, {len(tris)} triangles "
      f"({len(nondeg)} non-degenerate), {len(clauses)} clauses -> {out.name}")
print("UNSAT <=> H_3 -> (3,3)^e over ALL triangles")
