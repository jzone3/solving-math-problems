#!/usr/bin/env python3
"""Exact-SAT verifier for ascan.c 'ACAND' candidate lines.

Each ACAND line encodes a sink-regular (3,4)-bipartite candidate that ascan's
heuristic packer failed to 3-color. Reconstruct it, recompute tau and all
minimal dicuts with the independent bip.py pipeline, and decide packability by
exact SAT. Any UNSAT here is a genuine tau=3 Woodall counterexample.

Usage: python3 averify.py aout_*.txt
"""
import sys
from bip import all_min_dicuts, pack3


def parse(line):
    nbrs_str = line.split("nbrs=", 1)[1].strip()
    return [tuple(int(x) for x in row.split(",")) for row in nbrs_str.split(";")]


def parse_dbg(line):
    toks = dict(p.split("=", 1) for p in line.split()[1:5])
    nbrs_str = line.split("nbrs=", 1)[1].strip()
    nbrs = [tuple(int(x) for x in row.split(",")) for row in nbrs_str.split(";")]
    return int(toks["tau3"]), int(toks["packed"]), nbrs


def main(paths):
    checked = unsat = dbg_ok = dbg_bad = 0
    for path in paths:
        with open(path) as f:
            for line in f:
                if line.startswith("ADBG") or line.startswith("NDBG"):
                    try:
                        c_tau3, c_packed, nbrs = parse_dbg(line)
                    except ValueError:
                        continue  # garbled partial line (killed writer)
                    if any(len(r) not in (3, 4) for r in nbrs):
                        continue
                    nT = max(t for row in nbrs for t in row) + 1
                    tau, md = all_min_dicuts(nbrs, nT)
                    py_tau3 = 1 if tau >= 3 else 0
                    ok = (py_tau3 == c_tau3)
                    if ok and c_packed:
                        ok = bool(pack3(nbrs, md))
                    if ok:
                        dbg_ok += 1
                    else:
                        dbg_bad += 1
                        print(f"MISMATCH: py_tau={tau} {line.strip()}")
                    continue
                if not (line.startswith("ACAND") or line.startswith("NCAND")):
                    continue
                nbrs = parse(line)
                nT = max(t for row in nbrs for t in row) + 1
                tau, md = all_min_dicuts(nbrs, nT)
                checked += 1
                if tau != 3:
                    print(f"NOTE tau={tau} (heuristic-only candidate): {line.strip()}")
                    continue
                if not pack3(nbrs, md):
                    unsat += 1
                    print(f"COUNTEREXAMPLE: {line.strip()}")
    print(f"checked={checked} unsat={unsat} dbg_ok={dbg_ok} dbg_bad={dbg_bad}")
    return 1 if unsat else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
