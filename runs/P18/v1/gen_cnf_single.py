#!/usr/bin/env python3
"""
Generic single-family covering SAT: cover Z/N with distinct moduli from an
explicit comma-separated pool (sanity/testing tool for the encoding used by
gen_cnf_b.py / gen_cnf_m.py).

Usage: gen_cnf_single.py N m1,m2,... > cnf  (map to map_s_N{N}.json)
"""
import json
import sys


def main():
    N = int(sys.argv[1])
    M = sorted(set(int(t) for t in sys.argv[2].split(",")))
    assert all(N % m == 0 for m in M)
    var = {}
    nv = 0
    for m in M:
        for a in range(m):
            nv += 1
            var[(m, a)] = nv
    clauses = []
    for m in M:
        xs = [var[(m, a)] for a in range(m)]
        s_prev = None
        for i, x in enumerate(xs):
            if i == len(xs) - 1:
                if s_prev is not None:
                    clauses.append((-s_prev, -x))
                break
            nv += 1
            s = nv
            clauses.append((-x, s))
            if s_prev is not None:
                clauses.append((-s_prev, s))
                clauses.append((-s_prev, -x))
            s_prev = s
    out = sys.stdout
    out.write("p cnf %d %d\n" % (nv, len(clauses) + N))
    for c in clauses:
        out.write(" ".join(map(str, c)) + " 0\n")
    for r in range(N):
        out.write(" ".join(str(var[(m, r % m)]) for m in M) + " 0\n")
    json.dump({"N": N, "vars": {"%d,%d" % k: v for k, v in var.items()}},
              open("map_s_N%d.json" % N, "w"))


if __name__ == "__main__":
    main()
