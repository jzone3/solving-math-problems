# Provenance: new standalone exact verifier for stage-3 universe subsets.
"""Independently verify an exact cached universe subset.

Usage:
  python3 verify.py CACHE [--vertices IDS.pkl] [--record-s] [--drat]

The verifier recomputes all unit edges from the field coordinates, writes a
fresh 4-coloring CNF, and optionally checks the kissat proof with drat-trim.
"""

from __future__ import annotations

import argparse
import os
import pickle
import shutil
import subprocess
import tempfile

import numpy as np

import univ


def load(cache, record_s=False):
    points, _, _, metadata = pickle.load(open(cache, "rb"))
    points = list(points)
    if record_s:
        D = pickle.load(open(univ.DECOMP, "rb"))
        have = set(points)
        for p in D["S"]:
            q = univ.complex_mul(univ.OMEGA, univ.lattice_field(p))
            if q not in have:
                points.append(q)
                have.add(q)
    return points, metadata


def exact_edges(points):
    fl = np.array(
        [[univ.FIELD.to_float(p[0]), univ.FIELD.to_float(p[1])] for p in points],
        dtype=float,
    )
    edges = []
    for i in range(len(points)):
        d2 = np.sum((fl[i + 1 :] - fl[i]) ** 2, axis=1)
        for j in np.flatnonzero(np.abs(d2 - 1.0) < 1e-7):
            j = i + 1 + int(j)
            if univ.FIELD.norm2(points[i], points[j]) == univ.FIELD.ONE:
                edges.append((i, j))
    return edges


def cnf(n, edges):
    clauses = []
    for v in range(n):
        vars_ = [4 * v + c + 1 for c in range(4)]
        clauses.append(vars_)
        for c in range(4):
            for d in range(c + 1, 4):
                clauses.append([-vars_[c], -vars_[d]])
    for u, v in edges:
        for c in range(4):
            clauses.append([-(4 * u + c + 1), -(4 * v + c + 1)])
    return clauses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("--vertices", default=None)
    ap.add_argument("--record-s", action="store_true")
    ap.add_argument("--drat", action="store_true")
    args = ap.parse_args()
    points, metadata = load(args.cache, args.record_s)
    if args.vertices:
        ids = pickle.load(open(args.vertices, "rb"))
        points = [points[i] for i in sorted(ids)]
    if len(set(points)) != len(points):
        raise SystemExit("FAIL: duplicate exact coordinates")
    edges = exact_edges(points)
    print(f"[1] exact distinct vertices: {len(points)} ... PASS")
    print(f"[2] exact recomputed unit edges: {len(edges)}")
    KISSAT = os.environ.get("KISSAT") or shutil.which("kissat")
    DRAT = os.environ.get("DRATTRIM") or shutil.which("drat-trim")
    with tempfile.TemporaryDirectory() as d:
        cnf_path = os.path.join(d, "graph.cnf")
        proof = os.path.join(d, "graph.drat")
        cls = cnf(len(points), edges)
        with open(cnf_path, "w") as f:
            f.write(f"p cnf {4 * len(points)} {len(cls)}\n")
            for clause in cls:
                f.write(" ".join(map(str, clause)) + " 0\n")
        r = subprocess.run([KISSAT, "-q", cnf_path, proof], capture_output=True, text=True)
        if "s UNSATISFIABLE" not in r.stdout:
            print("[3] kissat UNSAT ... FAIL")
            return 1
        print("[3] kissat UNSAT ... PASS")
        if args.drat:
            q = subprocess.run([DRAT, cnf_path, proof], capture_output=True, text=True)
            if "s VERIFIED" not in q.stdout:
                print("[4] drat-trim VERIFIED ... FAIL")
                return 1
            print("[4] drat-trim VERIFIED ... PASS")
    print("OVERALL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
