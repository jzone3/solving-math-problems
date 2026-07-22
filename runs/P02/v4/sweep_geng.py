"""Phase A: direct sweep. Enumerate triangle-free graphs with delta >= ceil(n/3)
via nauty-geng, filter maximal triangle-free, run LP1 oracle.

Any LP1-infeasible instance is a counterexample to Brandt's conjecture.
Usage: python3 sweep_geng.py n [res mod]   (geng -X res/mod splitting for parallelism)
"""
import math
import subprocess
import sys

from oracle import lp1_multiplication_feasible, is_maximal_tf
from test_oracle import g6_to_edges


def main():
    n = int(sys.argv[1])
    res, mod = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, 1)
    mindeg = math.ceil(n / 3)
    cmd = ["nauty-geng", "-q", "-t", "-c", f"-d{mindeg}", str(n)]
    if mod > 1:
        cmd.append(f"{res}/{mod}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    total = mtf = infeasible = 0
    for line in proc.stdout:
        total += 1
        nn, edges = g6_to_edges(line.strip())
        if not is_maximal_tf(nn, edges):
            continue
        mtf += 1
        feas, cert = lp1_multiplication_feasible(nn, edges)
        if not feas:
            infeasible += 1
            print(f"COUNTEREXAMPLE n={nn} g6={line.strip()} farkas={cert}", flush=True)
    print(f"n={n} part={res}/{mod} mindeg={mindeg}: geng_tf={total} maximalTF={mtf} "
          f"infeasible={infeasible}", flush=True)


if __name__ == "__main__":
    main()
