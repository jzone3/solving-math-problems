"""SAT arrowing utilities for P22.

G -> (3,3)^e  iff  the CNF 'exists a 2-edge-coloring with no monochromatic triangle'
is UNSAT. Variables = edges of G; for each triangle two clauses (not all red / not all blue).
"""
import subprocess, os, tempfile
from itertools import combinations

KISSAT = os.path.expanduser("~/work/kissat/build/kissat")
DRATTRIM = os.path.expanduser("~/work/drat-trim/drat-trim")

def triangles_of(n, adjset):
    tris = []
    for i in range(n):
        ni = sorted(x for x in adjset[i] if x > i)
        for a in range(len(ni)):
            for b in range(a + 1, len(ni)):
                j, k = ni[a], ni[b]
                if k in adjset[j]:
                    tris.append((i, j, k))
    return tris

def cnf_for_arrowing(edges, tris):
    var = {e: i + 1 for i, e in enumerate(sorted(edges))}
    clauses = []
    for (i, j, k) in tris:
        e1, e2, e3 = var[(i, j)], var[(i, k)], var[(j, k)]
        clauses.append([e1, e2, e3])
        clauses.append([-e1, -e2, -e3])
    return var, clauses

def cnf_for_triangle_system(edges, tris):
    # same encoding but tris may be a subset (quasi-Folkman test)
    return cnf_for_arrowing(edges, tris)

def write_dimacs(path, nvars, clauses):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for c in clauses:
            f.write(" ".join(map(str, c)) + " 0\n")

def solve(nvars, clauses, drat_path=None, timeout=3600):
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        cnf_path = f.name
    write_dimacs(cnf_path, nvars, clauses)
    cmd = [KISSAT, "-q", cnf_path]
    if drat_path:
        cmd.append(drat_path)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = r.stdout
        if "s UNSATISFIABLE" in out:
            return "UNSAT", None, cnf_path
        if "s SATISFIABLE" in out:
            model = set()
            for line in out.splitlines():
                if line.startswith("v"):
                    for tok in line.split()[1:]:
                        v = int(tok)
                        if v > 0:
                            model.add(v)
            return "SAT", model, cnf_path
        return "UNKNOWN", None, cnf_path
    finally:
        pass

def has_k4(n, adjset):
    for i in range(n):
        ni = sorted(x for x in adjset[i] if x > i)
        for a in range(len(ni)):
            j = ni[a]
            common_ij = [x for x in ni[a+1:] if x in adjset[j]]
            for b in range(len(common_ij)):
                k = common_ij[b]
                for l in common_ij[b+1:]:
                    if l in adjset[k]:
                        return (i, j, k, l)
    return None

def count_k4(n, adjset):
    c = 0
    for i in range(n):
        ni = sorted(x for x in adjset[i] if x > i)
        for a in range(len(ni)):
            j = ni[a]
            common_ij = [x for x in ni[a+1:] if x in adjset[j]]
            for b in range(len(common_ij)):
                k = common_ij[b]
                for l in common_ij[b+1:]:
                    if l in adjset[k]:
                        c += 1
    return c

def verify_coloring(edges, tris, var, model):
    """model: set of true variable indices (red edges). Check no mono triangle."""
    red = {e for e in edges if var[e] in model}
    for (i, j, k) in tris:
        e = [(i, j), (i, k), (j, k)]
        r = sum(1 for x in e if x in red)
        if r == 0 or r == 3:
            return (i, j, k)
    return None
