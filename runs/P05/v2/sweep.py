#!/usr/bin/env python3
"""Sweep (n, L) pairs in increasing cost order.
L range for a minimal witness: n <= 3(L+1) (R1: coverage) and 3(L+1) <= 2n (empty
common intersection => each vertex on <=2 paths). So ceil(n/3)-1 <= L <= (2n-3)//3.
"""
import math, sys, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
start_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
end_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
tl = float(sys.argv[3]) if len(sys.argv) > 3 else 7200

done = set()
logf = os.path.join(HERE, "results.log")
if os.path.exists(logf):
    for line in open(logf):
        p = dict(kv.split("=") for kv in line.split() if "=" in kv)
        if p.get("status") in ("UNSAT", "COUNTEREXAMPLE"):
            done.add((int(p["n"]), int(p["L"])))

for n in range(start_n, end_n + 1):
    lo = math.ceil(n / 3) - 1
    hi = (2 * n - 3) // 3
    for L in range(lo, hi + 1):
        if (n, L) in done:
            print(f"skip n={n} L={L} (done)", flush=True)
            continue
        print(f"=== n={n} L={L} (time limit {tl}s) ===", flush=True)
        r = subprocess.run([sys.executable, os.path.join(HERE, "sat_cegar.py"),
                            str(n), str(L), "--time-limit", str(tl)])
        if r.returncode != 0:
            print(f"ERROR n={n} L={L} rc={r.returncode}", flush=True)
