#!/usr/bin/env python3
"""
P18 (Erdos #273) SAT encoding: covering of Z/N with distinct admissible moduli.

Variables: x_{d,a} for each admissible modulus d (d | N, d >= 4, d+1 prime,
optionally d <= cap) and each residue a in 0..d-1 -- "the system contains the
congruence a mod d".
Clauses:
  * coverage: for every r in 0..N-1, OR over d of x_{d, r mod d};
  * at-most-one per modulus d (distinct-moduli convention: each modulus hosts
    at most one congruence), sequential (Sinz) encoding, O(d) aux vars/clauses.

SAT => witness (decoded by decode_model.py, re-verified by
solutions/P18/verify.py). UNSAT => no covering of Z with distinct moduli drawn
from this specific divisor pool (NOT an unconditional negative).

Usage: gen_cnf.py N [cap] > cnf.dimacs   (mapping written to map_N{N}_c{cap}.json)
"""
import json
import sys


def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def divisors(n):
    ds = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            ds.append(i)
            if i != n // i:
                ds.append(n // i)
        i += 1
    return sorted(ds)


def main():
    N = int(sys.argv[1])
    cap = int(sys.argv[2]) if len(sys.argv) > 2 else N
    D = [d for d in divisors(N) if 4 <= d <= cap and is_prime(d + 1)]
    var = {}
    nv = 0
    for d in D:
        for a in range(d):
            nv += 1
            var[(d, a)] = nv
    clauses = []
    # at-most-one per modulus, sequential encoding
    for d in D:
        xs = [var[(d, a)] for a in range(d)]
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
    ncov = N
    out.write("p cnf %d %d\n" % (nv, len(clauses) + ncov))
    for c in clauses:
        out.write(" ".join(map(str, c)) + " 0\n")
    buf = []
    for r in range(N):
        buf.append(" ".join(str(var[(d, r % d)]) for d in D) + " 0\n")
        if len(buf) >= 10000:
            out.writelines(buf)
            buf = []
    out.writelines(buf)
    json.dump({"N": N, "cap": cap,
               "vars": {"%d,%d" % k: v for k, v in var.items()}},
              open("map_N%d_c%d.json" % (N, cap), "w"))
    sys.stderr.write("N=%d cap=%d |D|=%d vars=%d\n" % (N, cap, len(D), nv))


if __name__ == "__main__":
    main()
