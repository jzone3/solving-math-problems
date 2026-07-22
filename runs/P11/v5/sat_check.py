#!/usr/bin/env python3
"""Independent SAT-based check of the orbit exhausts (second verifier).

Encodes: does a CW(n, s^2) exist that is fixed by multiplier t on Z_n
(coefficients constant on orbits, A(1)=+s)?  Uses CaDiCaL via python-sat;
completely different search machinery from the C DFS in exhaust_cw.c.

Encoding: per orbit o, vars P_o, N_o (in +1 support / in -1 support),
not both; |P| weighted = (s^2+s)/2, |N| weighted = (s^2-s)/2 (cardinality
with literal duplication for weights); for each shift g the autocorrelation
sum splits into positive part (PP+NN pairs) and negative part (PN+NP):
encode "pos + (W_neg - neg) = W_neg" as one cardinality equality over
product variables.

Usage: python3 sat_check.py n s t          e.g. sat_check.py 120 7 7
Prints UNSAT (no such CW) or SAT + a witness (then verifies it).
"""
import sys
from itertools import combinations_with_replacement
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153


def orbits(n, t):
    seen = [False] * n
    out = []
    for x in range(n):
        if seen[x]:
            continue
        orb, y = [], x
        while not seen[y]:
            seen[y] = True
            orb.append(y)
            y = y * t % n
        out.append(orb)
    return out


def main():
    n, s, t = map(int, sys.argv[1:4])
    k = s * s
    orbs = orbits(n, t)
    u = len(orbs)
    pool = IDPool()
    P = [pool.id(("P", i)) for i in range(u)]
    N = [pool.id(("N", i)) for i in range(u)]
    clauses = [[-P[i], -N[i]] for i in range(u)]

    def card_eq(lits, bound):
        cnf = CardEnc.equals(lits=lits, bound=bound, vpool=pool,
                             encoding=EncType.seqcounter)
        clauses.extend(cnf.clauses)

    # weighted |P| and |N|
    plits, nlits = [], []
    for i, o in enumerate(orbs):
        plits += [P[i]] * len(o)
        nlits += [N[i]] * len(o)
    card_eq(plits, (k + s) // 2)
    card_eq(nlits, (k - s) // 2)

    # product variables
    def prod(a, b):
        v = pool.id(("and", a, b)) if a <= b else pool.id(("and", b, a))
        return v

    defined = set()

    def define(v, a, b):
        if v in defined:
            return
        defined.add(v)
        clauses.append([-v, a])
        clauses.append([-v, b])
        clauses.append([v, -a, -b])

    # optional proven fold constraints q:j  (fold mod q equals s*delta_j)
    for arg in sys.argv[5:]:
        q, j = map(int, arg.split(":"))
        for r in range(q):
            lits = []
            for i, o in enumerate(orbs):
                w = sum(1 for x in o if x % q == r)
                lits += [P[i]] * w + [-N[i]] * w
            wneg = sum(1 for x in range(n) if x % q == r)
            # sum P - sum N = target  <=>  P-count + (wneg - N-count) = wneg + target
            card_eq(lits, wneg + (s if r == j else 0))

    # M[o][o'][g] = #{(x,y) in O_o x O_o' : x - y == g mod n}
    # build per shift g the pos/neg weighted literal lists
    idx = [None] * n
    for i, o in enumerate(orbs):
        for x in o:
            idx[x] = i
    from collections import defaultdict
    M = defaultdict(int)   # (i, j, g) -> count, i,j orbit ids
    for i, o in enumerate(orbs):
        for j, o2 in enumerate(orbs):
            for x in o:
                for y in o2:
                    g = (x - y) % n
                    if g:
                        M[(i, j, g)] += 1
    for g in range(1, n // 2 + 1):
        pos, neg = [], []
        for i in range(u):
            for j in range(u):
                c = M.get((i, j, g), 0)
                if not c:
                    continue
                pp = prod(P[i], P[j]); define(pp, min(P[i], P[j]), max(P[i], P[j]))
                nn = prod(N[i], N[j]); define(nn, min(N[i], N[j]), max(N[i], N[j]))
                pn = prod(P[i], N[j]); define(pn, min(P[i], N[j]), max(P[i], N[j]))
                np_ = prod(N[i], P[j]); define(np_, min(N[i], P[j]), max(N[i], P[j]))
                pos += [pp] * c + [nn] * c
                neg += [pn] * c + [np_] * c
        w_neg = len(neg)
        # pos - neg = 0  <=>  pos + (negated neg lits true count) == w_neg
        card_eq(pos + [-v for v in neg], w_neg)

    print(f"n={n} s={s} t={t} orbits={u} clauses={len(clauses)}", flush=True)
    if len(sys.argv) > 4:                      # dump DIMACS for kissat etc.
        top = pool.top
        with open(sys.argv[4], "w") as f:
            f.write(f"p cnf {top} {len(clauses)}\n")
            for cl in clauses:
                f.write(" ".join(map(str, cl)) + " 0\n")
        print("wrote", sys.argv[4])
        return
    with Cadical153(bootstrap_with=clauses) as slv:
        sat = slv.solve()
        if not sat:
            print("UNSAT: no CW fixed by multiplier (A(1)=+s) exists")
            return
        model = set(l for l in slv.get_model() if l > 0)
        Pset, Nset = [], []
        for i, o in enumerate(orbs):
            if P[i] in model:
                Pset += o
            if N[i] in model:
                Nset += o
        print("SAT")
        # verify
        a = [0] * n
        for x in Pset:
            a[x] = 1
        for x in Nset:
            a[x] = -1
        ok = all(sum(a[i] * a[(i + g) % n] for i in range(n)) == 0
                 for g in range(1, n)) and sum(v * v for v in a) == k
        print("witness verifies:", ok)
        print("P =", sorted(Pset))
        print("N =", sorted(Nset))


if __name__ == "__main__":
    main()
