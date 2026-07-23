#!/usr/bin/env python3
"""
P18 (Erdos #273) joint two-family SAT encoding in m-space.

By the parity decomposition (see NOTES.md sec. 2), a witness exists iff
M = {m >= 2 : 2m+1 prime} contains two disjoint subsets each carrying a
distinct-moduli covering of Z. This encodes BOTH families jointly over Z/N:

  vars x_{m,a,f} : family f in {A=0 (evens), B=1 (odds)} contains b=a mod m,
  for each m | N, m in M, a in 0..m-1.
  * coverage: for every family f and residue r: OR_m x_{m, r mod m, f};
  * at-most-one over the 2m vars of each modulus m (a modulus is used at most
    once, by at most one family) -- sequential (Sinz) encoding;
  * symmetry break: modulus 2, if in the pool, is reserved to family A
    (x_{2,a,B} = false); WLOG since families are exchangeable and only one
    can hold m=2.

SAT => witness (decode_m.py lifts to n-space congruences; re-verified by
solutions/P18/verify.py). UNSAT => no witness whose per-parity moduli all
divide N (negative for this pool only).

Usage: gen_cnf_m.py N [cap] > cnf.dimacs   (mapping to map_m_N{N}_c{cap}.json)
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
    M = [d for d in divisors(N) if 2 <= d <= cap and is_prime(2 * d + 1)]
    var = {}
    nv = 0
    for m in M:
        for a in range(m):
            for f in (0, 1):
                nv += 1
                var[(m, a, f)] = nv
    clauses = []
    if 2 in M:
        clauses.append((-var[(2, 0, 1)],))
        clauses.append((-var[(2, 1, 1)],))
    # at-most-one per modulus (across residues AND families)
    for m in M:
        xs = [var[(m, a, f)] for a in range(m) for f in (0, 1)]
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
    out.write("p cnf %d %d\n" % (nv, len(clauses) + 2 * N))
    for c in clauses:
        out.write(" ".join(map(str, c)) + " 0\n")
    buf = []
    for f in (0, 1):
        for r in range(N):
            buf.append(" ".join(str(var[(m, r % m, f)]) for m in M) + " 0\n")
            if len(buf) >= 10000:
                out.writelines(buf)
                buf = []
    out.writelines(buf)
    json.dump({"N": N, "cap": cap,
               "vars": {"%d,%d,%d" % k: v for k, v in var.items()}},
              open("map_m_N%d_c%d.json" % (N, cap), "w"))
    sys.stderr.write("N=%d cap=%d |M|=%d vars=%d\n" % (N, cap, len(M), nv))


if __name__ == "__main__":
    main()
