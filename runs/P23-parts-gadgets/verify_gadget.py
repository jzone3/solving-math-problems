"""Independent verifier for a minimized gadget pkl.

Checks:
 1. all vertices distinct exact lattice points;
 2. stored edge list == exact recomputation of ALL unit pairs (strict UDG);
 3. the graph alone is 4-colorable (SAT) -- property is not vacuous;
 4. gadget property (mono / non-mono) holds: refutation CNF UNSAT by kissat
    AND the DRAT proof is verified by drat-trim (s VERIFIED).

Usage: python3 verify_gadget.py gadget_xxx.pkl
"""
import os
import pickle
import subprocess
import sys
import tempfile

from lattice import unit_edges, dist2
from gadget import (build_cnf, solve, write_cnf, prop_mono_pair,
                    prop_nonmono_set, KISSAT, DRAT)


def main(path):
    with open(path, "rb") as f:
        d = pickle.load(f)
    pts, edges, gadget, kind = d["points"], d["edges"], d["gadget"], d["kind"]
    n = len(pts)
    assert len(set(pts)) == n, "duplicate vertices"
    print("[1] %d distinct exact vertices" % n)
    exact = set(map(tuple, (tuple(sorted(e)) for e in unit_edges(pts))))
    stored = set(tuple(sorted(e)) for e in edges)
    assert exact == stored, "edge mismatch: stored %d vs exact %d" % (len(stored), len(exact))
    print("[2] edge list matches exact recomputation: %d unit edges" % len(exact))
    assert solve(build_cnf(n, list(stored), []), 4 * n) == "SAT"
    print("[3] graph alone is 4-colorable (property is not vacuous)")
    prop = prop_mono_pair(*gadget) if kind == "mono" else prop_nonmono_set(gadget)
    cls = build_cnf(n, list(stored), prop)
    with tempfile.TemporaryDirectory() as td:
        cnf = os.path.join(td, "f.cnf")
        proof = os.path.join(td, "f.drat")
        write_cnf(cls, 4 * n, cnf)
        r = subprocess.run([KISSAT, "-q", cnf, proof], capture_output=True, text=True)
        assert r.returncode == 20, "property refutation not UNSAT"
        r2 = subprocess.run([DRAT, cnf, proof], capture_output=True, text=True)
        assert "s VERIFIED" in r2.stdout, r2.stdout[-500:]
    print("[4] property (%s, gadget=%s) UNSAT, drat-trim: s VERIFIED" % (kind, gadget))
    print("PASS", path)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
