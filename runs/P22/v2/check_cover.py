#!/usr/bin/env python3
"""Verify that a march_cu cube set is a complete cover of the search space:
the CNF { (~l1 | ... | ~lk) : cube (l1..lk) } must be UNSAT (no assignment
avoids all cubes). Emits cover.cnf, solves with kissat, checks DRAT.
Usage: check_cover.py <cubes.icnf> <nvars>
"""
import subprocess, sys

cube_path, nv = sys.argv[1], int(sys.argv[2])
clauses = []
for line in open(cube_path):
    if line.startswith("a "):
        lits = [int(x) for x in line.split()[1:-1]]
        clauses.append([-l for l in lits])
with open("cover.cnf", "w") as f:
    f.write(f"p cnf {nv} {len(clauses)}\n")
    for cl in clauses:
        f.write(" ".join(map(str, cl)) + " 0\n")
r = subprocess.run(["kissat", "-q", "cover.cnf", "cover.drat"], capture_output=True)
assert r.returncode == 20, f"cover check: kissat exit {r.returncode} (expected UNSAT=20)"
v = subprocess.run(["drat-trim", "cover.cnf", "cover.drat"], capture_output=True, text=True)
assert "s VERIFIED" in v.stdout, "drat-trim failed on cover proof"
print(f"COVER VERIFIED: {len(clauses)} cubes cover all assignments (UNSAT, DRAT-checked)")
