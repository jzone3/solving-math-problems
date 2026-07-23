#!/usr/bin/env python3
"""Kramer-Mesner style orbit-reduction SAT for CW(n,k=s^2).

For a multiplier subgroup H = <gens> <= Z_n^*, any H-fixed ternary sequence is
constant x_o in {-1,0,+1} on each orbit O_o. Encode existence as SAT:
  vars P_o ("x_o=+1"), M_o ("x_o=-1"), at most one of each;
  weight:  sum |O_o| (P_o + M_o) = k          (PB equality)
  DC:      sum |O_o| (P_o - M_o) = +s         (negation symmetry fixes +s)
  R(t)=0:  sum_o C[o][o][t](P_o+M_o)
           + sum_{o<p} w_{op,t} (PP+MM-PM-MP)_{op} = 0   for t=1..n//2
  where C[o][p][t] = #{(i,j) in O_o x O_p : j-i=t mod n}, w = C[o][p][t]+C[p][o][t],
  and PP_{op} <-> P_o & P_p etc. (Tseitin AND vars, shared across shifts).
R(t)=R(n-t) so shifts t=1..floor(n/2) suffice; R(0)=k follows from the weight.
UNSAT is a definitive proof that no CW(n,k) is fixed by H.

Usage: orbit_sat.py n s g1 [g2 ...] [--dimacs FILE] [--enc E]
Exit: 0 SAT (prints SOLUTION + vec, verify externally) / 2 UNSAT / 3 skip
"""
import sys
from math import gcd
import numpy as np
from pysat.formula import IDPool, CNF
from pysat.pb import PBEnc, EncType
from pysat.solvers import Cadical195


def subgroup(n, gens):
    g = {1}
    frontier = list(gens)
    for t in gens:
        if gcd(t, n) != 1:
            raise ValueError(f"{t} not a unit mod {n}")
    changed = True
    while changed:
        changed = False
        for a in list(g):
            for b in gens:
                v = (a * b) % n
                if v not in g:
                    g.add(v)
                    changed = True
    return sorted(g)


def orbits_of(n, H):
    seen = [False] * n
    parts = []
    for i in range(n):
        if not seen[i]:
            comp = []
            stack = [i]
            seen[i] = True
            while stack:
                j = stack.pop()
                comp.append(j)
                for t in H:
                    v = (j * t) % n
                    if not seen[v]:
                        seen[v] = True
                        stack.append(v)
            parts.append(sorted(comp))
    return parts


def main():
    args = [a for a in sys.argv[1:]]
    enc = EncType.bdd
    dimacs = None
    if '--dimacs' in args:
        i = args.index('--dimacs')
        dimacs = args[i + 1]
        del args[i:i + 2]
    if '--enc' in args:
        i = args.index('--enc')
        enc = getattr(EncType, args[i + 1])
        del args[i:i + 2]
    n = int(args[0]); s = int(args[1]); gens = [int(x) for x in args[2:]]
    k = s * s
    H = subgroup(n, gens)
    parts = orbits_of(n, H)
    m = len(parts)
    sizes = [len(p) for p in parts]
    print(f"n={n} k={k} gens={gens} |H|={len(H)} m={m} sizes={sorted(sizes)}", flush=True)

    # cross-correlation tables via FFT
    ind = np.zeros((m, n), dtype=np.int64)
    for o, p in enumerate(parts):
        ind[o, p] = 1
    F = np.fft.rfft(ind, axis=1)
    C = np.empty((m, m, n), dtype=np.int64)
    for o in range(m):
        cc = np.fft.irfft(np.conj(F[o])[None, :] * F, n, axis=1)
        C[o] = np.rint(cc).astype(np.int64)

    pool = IDPool()
    P = [pool.id(('P', o)) for o in range(m)]
    M = [pool.id(('M', o)) for o in range(m)]
    cnf = CNF()
    for o in range(m):
        cnf.append([-P[o], -M[o]])

    # product AND vars for pairs (shared across all shifts)
    PP = {}; MM = {}; PM = {}; MP = {}
    half = n // 2
    need = set()
    for o in range(m):
        for p in range(o + 1, m):
            if any(C[o, p, t] + C[p, o, t] for t in range(1, half + 1)):
                need.add((o, p))
    for (o, p) in need:
        for name, d, a, b in (('PP', PP, P[o], P[p]), ('MM', MM, M[o], M[p]),
                              ('PM', PM, P[o], M[p]), ('MP', MP, M[o], P[p])):
            v = pool.id((name, o, p))
            d[(o, p)] = v
            cnf.append([-v, a]); cnf.append([-v, b]); cnf.append([-a, -b, v])
    print(f"pairs={len(need)} base_vars={pool.top}", flush=True)

    def add_pb(lits, wts, bound):
        c = PBEnc.equals(lits=lits, weights=wts, bound=bound, vpool=pool, encoding=enc)
        cnf.extend(c.clauses)

    # weight and DC
    lits = []; wts = []
    for o in range(m):
        lits += [P[o], M[o]]; wts += [sizes[o], sizes[o]]
    add_pb(lits, wts, k)
    lits = []; wts = []
    for o in range(m):
        lits += [P[o], M[o]]; wts += [sizes[o], -sizes[o]]
    add_pb(lits, wts, s)

    # autocorrelation shifts
    for t in range(1, half + 1):
        lits = []; wts = []
        for o in range(m):
            w = int(C[o, o, t])
            if w:
                lits += [P[o], M[o]]; wts += [w, w]
        for (o, p) in need:
            w = int(C[o, p, t] + C[p, o, t])
            if w:
                lits += [PP[(o, p)], MM[(o, p)], PM[(o, p)], MP[(o, p)]]
                wts += [w, w, -w, -w]
        add_pb(lits, wts, 0)
    print(f"CNF: vars={pool.top} clauses={len(cnf.clauses)}", flush=True)

    if dimacs:
        cnf.to_file(dimacs)
        print(f"wrote {dimacs}", flush=True)
        return 3

    with Cadical195(bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        if not sat:
            print(f"UNSAT n={n} k={k} gens={gens} m={m}: no H-fixed CW exists", flush=True)
            return 2
        model = set(l for l in solver.get_model() if l > 0)
        x = np.zeros(n, dtype=int)
        for o in range(m):
            if P[o] in model:
                x[parts[o]] = 1
            elif M[o] in model:
                x[parts[o]] = -1
        vec = ''.join('+' if v > 0 else ('-' if v < 0 else '0') for v in x)
        # exact check
        a = np.array(x)
        Rv = [int(sum(a[i] * a[(i + t) % n] for i in range(n))) for t in range(n)]
        ok = Rv[0] == k and all(r == 0 for r in Rv[1:])
        print(f"SOLUTION n={n} k={k} gens={gens} check={'OK' if ok else 'BAD'} vec={vec}", flush=True)
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
