"""Step 1: verify H_3 properties + reproduce paper's quasi-Folkman UNSAT with DRAT cert."""
import subprocess, os
from h3 import adj, edges, nondegenerate_triangles, all_triangles, maximal_cliques_C
from arrow import (cnf_for_triangle_system, write_dimacs, solve, count_k4,
                   KISSAT, DRATTRIM)

n = 63
adjset = [set(j for j in range(n) if adj[i][j]) for i in range(n)]

k4 = count_k4(n, adjset)
print("K4 count in H_3:", k4)
# expected: K4s inside the 28 K9 cliques: 28*C(9,4)=3528, plus K4s with exactly 3 in a clique?
# Prop 2.2(4): every K4 has >=3 vertices in a clique of C_3.

ndt = nondegenerate_triangles()
alltri = all_triangles()
print("triangles:", len(alltri), "non-degenerate:", len(ndt))

edge_list = sorted((min(i, j), max(i, j)) for i, j in edges)
var, clauses = cnf_for_triangle_system(edge_list, ndt)
print("SAT instance: vars", len(var), "clauses", len(clauses))
os.makedirs("out", exist_ok=True)
write_dimacs("out/h3_quasi.cnf", len(var), clauses)
r = subprocess.run([KISSAT, "-q", "out/h3_quasi.cnf", "out/h3_quasi.drat"],
                   capture_output=True, text=True)
print("kissat:", [l for l in r.stdout.splitlines() if l.startswith("s")])
v = subprocess.run([DRATTRIM, "out/h3_quasi.cnf", "out/h3_quasi.drat"],
                   capture_output=True, text=True)
print("drat-trim:", v.stdout.strip().splitlines()[-1])

# Full arrowing of H_3 itself (all triangles) — trivially UNSAT given the above, but record it.
var2, clauses2 = cnf_for_triangle_system(edge_list, alltri)
write_dimacs("out/h3_full_arrow.cnf", len(var2), clauses2)
r2 = subprocess.run([KISSAT, "-q", "out/h3_full_arrow.cnf", "out/h3_full_arrow.drat"],
                    capture_output=True, text=True)
print("full arrowing kissat:", [l for l in r2.stdout.splitlines() if l.startswith("s")])
v2 = subprocess.run([DRATTRIM, "out/h3_full_arrow.cnf", "out/h3_full_arrow.drat"],
                    capture_output=True, text=True)
print("drat-trim:", v2.stdout.strip().splitlines()[-1])
