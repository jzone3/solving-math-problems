"""Endgame CEGAR driver using native kissat via DIMACS files.

Used when the incremental pysat/Cadical loop stalls: re-solving the full
accumulated formula with kissat's preprocessing is often much faster for the
hard tail (final UNSAT proof / last few models).

Optionally warm-starts from a blocking-set JSON dumped by cegar.py
(--dump-on-stall).
"""

import argparse
import json
import subprocess
import sys
import tempfile
import time

from cegar import build_encoding, blocking_clauses_for
from hc import find_second_hc, count_hcs


def write_dimacs(path, nvars, clause_lists):
    with open(path, "w") as f:
        total = sum(len(c) for c in clause_lists)
        f.write(f"p cnf {nvars} {total}\n")
        for cls in clause_lists:
            for cl in cls:
                f.write(" ".join(map(str, cl)) + " 0\n")


def kissat_solve(cnf_path, timeout=None):
    cmd = ["kissat", "-q", cnf_path]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    pos = set()
    status = None
    for line in p.stdout.splitlines():
        if line.startswith("s "):
            status = line[2:].strip()
        elif line.startswith("v "):
            for tok in line[2:].split():
                v = int(tok)
                if v > 0:
                    pos.add(v)
    return status, pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--min-dist", type=int, default=2)
    ap.add_argument("--blocking", type=str, default=None,
                    help="JSON dump from cegar.py --dump-on-stall")
    ap.add_argument("--seconds", type=float, default=43200)
    ap.add_argument("--notes", type=str, default=None)
    a = ap.parse_args()
    n = a.n

    chords, var, base_clauses = build_encoding(n, a.min_dist)
    nvars = max(max(abs(l) for l in cl) for cl in base_clauses)
    blocking = []
    if a.blocking:
        with open(a.blocking) as f:
            d = json.load(f)
        assert d["n"] == n and d["min_dist"] == a.min_dist
        blocking = d["blocking"]

    def log(msg):
        print(msg, flush=True)
        if a.notes:
            with open(a.notes, "a") as f:
                f.write(msg + "\n")

    t0 = time.time()
    models = 0
    status = "running"
    witness = None
    cnf_path = tempfile.mktemp(suffix=".cnf")
    while True:
        if time.time() - t0 > a.seconds:
            status = "timeout"
            break
        write_dimacs(cnf_path, nvars, [base_clauses, blocking])
        st = time.time()
        remaining = a.seconds - (time.time() - t0)
        try:
            sat, pos = kissat_solve(cnf_path, timeout=max(60, remaining))
        except subprocess.TimeoutExpired:
            status = "timeout"
            break
        stime = time.time() - st
        if sat == "UNSATISFIABLE":
            status = "exhausted-unsat"
            break
        assert sat == "SATISFIABLE", sat
        X = [e for e in chords if var[e] in pos]
        adj = [[(i + 1) % n, (i - 1) % n] for i in range(n)]
        for (i, j) in X:
            adj[i].append(j)
            adj[j].append(i)
        models += 1
        second = find_second_hc(n, adj, limit=4)
        if not second:
            cnt, capped = count_hcs(n, adj, cap=3)
            if cnt == 1 and not capped:
                status = "FOUND"
                witness = X
                break
            second = find_second_hc(n, adj, limit=16)
            assert second
        chordset = set(X)
        added = 0
        seen = set()
        for cyc in second:
            for lits in blocking_clauses_for(n, cyc, chordset, var):
                key = tuple(sorted(lits))
                if key not in seen:
                    seen.add(key)
                    blocking.append(lits)
                    added += 1
        log(f"n={n} endgame model {models}: solve {stime:.1f}s, "
            f"+{added} clauses (total {len(blocking)})")

    result = {"n": n, "min_dist": a.min_dist, "mode": "kissat-endgame",
              "status": status, "models": models, "blocking": len(blocking),
              "seconds": round(time.time() - t0, 1), "witness": witness}
    log(json.dumps(result))
    return 0 if status in ("exhausted-unsat", "FOUND") else 2


if __name__ == "__main__":
    sys.exit(main())
