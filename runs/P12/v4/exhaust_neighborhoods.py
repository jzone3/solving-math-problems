#!/usr/bin/env python3
"""Exhaust all C(n,k) row-subsets of an incumbent with kissat (complete search
per neighborhood). Any SAT => full T2(n) witness. All-UNSAT => certificate that
no T2(n) agrees with the incumbent on any n-k rows.

Usage: exhaust_neighborhoods.py incumbent k [kissat_path] [jobs] [per_tl_s]
Results appended to exhaust_<incumbent>_k<k>.log
"""
import itertools
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))


def run_subset(inc, n, subset, kissat, tl):
    free = ",".join(map(str, subset))
    with tempfile.NamedTemporaryFile(suffix=".cnf", delete=False) as tf:
        cnf = tf.name
    try:
        subprocess.run([sys.executable, os.path.join(HERE, "fix_rows_cnf.py"), inc, free, cnf],
                       check=True, capture_output=True)
        p = subprocess.run([kissat, "-q", cnf], capture_output=True, text=True,
                           timeout=tl if tl > 0 else None)
        out = p.stdout
        if "s SATISFIABLE" in out:
            return subset, "SAT", out
        if "s UNSATISFIABLE" in out:
            return subset, "UNSAT", None
        return subset, "UNKNOWN", None
    except subprocess.TimeoutExpired:
        return subset, "TIMEOUT", None
    finally:
        os.unlink(cnf)


def main():
    inc = sys.argv[1]
    k = int(sys.argv[2])
    kissat = sys.argv[3] if len(sys.argv) > 3 else os.path.expanduser("~/bin/kissat")
    jobs = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    tl = float(sys.argv[5]) if len(sys.argv) > 5 else 0
    arr = [[int(x) for x in l.split()] for l in open(inc) if l.strip()]
    n = len(arr)
    log = f"exhaust_{os.path.basename(inc)}_k{k}.log"
    subsets = list(itertools.combinations(range(n), k))
    print(f"{len(subsets)} subsets of size {k}, jobs={jobs}", flush=True)
    done = unsat = 0
    with open(log, "a") as lf, ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(run_subset, inc, n, s, kissat, tl): s for s in subsets}
        for f in as_completed(futs):
            subset, verdict, out = f.result()
            done += 1
            unsat += verdict == "UNSAT"
            lf.write(f"{subset} {verdict}\n")
            lf.flush()
            if verdict == "SAT":
                sol = f"SAT_MODEL_{os.path.basename(inc)}_{'_'.join(map(str, subset))}.txt"
                with open(sol, "w") as sf:
                    sf.write(out)
                print(f"!!! SAT at subset {subset} — model dumped to {sol}", flush=True)
            if done % 20 == 0:
                print(f"progress {done}/{len(subsets)} (UNSAT {unsat})", flush=True)
    print(f"DONE k={k}: {done} subsets, UNSAT {unsat}, see {log}", flush=True)


if __name__ == "__main__":
    main()
