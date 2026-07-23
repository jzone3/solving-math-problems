#!/usr/bin/env python3
"""
Single-family phase-B SAT: cover Z/N with distinct moduli from
(M \ {2}) cap divisors(N), M = {m : 2m+1 prime}. Same encoding as
gen_cnf_m.py but one family and modulus 2 banned.

Usage: gen_cnf_b.py N [cap] > cnf.dimacs (map to map_b_N{N}_c{cap}.json)
"""
import json
import sys

from gen_cnf_m import is_prime, divisors


def main():
    N = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else N
    M = [d for d in divisors(N) if 3 <= d <= cap and is_prime(2 * d + 1)]
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
    buf = []
    for r in range(N):
        buf.append(" ".join(str(var[(m, r % m)]) for m in M) + " 0\n")
        if len(buf) >= 10000:
            out.writelines(buf)
            buf = []
    out.writelines(buf)
    json.dump({"N": N, "cap": cap,
               "vars": {"%d,%d" % k: v for k, v in var.items()}},
              open("map_b_N%d_c%d.json" % (N, cap), "w"))
    sys.stderr.write("N=%d cap=%d |M\\2|=%d vars=%d\n" % (N, cap, len(M), nv))


if __name__ == "__main__":
    main()
