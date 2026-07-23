#!/usr/bin/env python3
"""Strengthened SAT encoding for the Z/L covering question (Erdos #273, run v2, round 2).

Additions over sat_cover.py, all *provably sound* (they only exclude non-solutions):

1. used-modulus indicator u_m <-> OR_a y[m][a].
2. FORCED-USE units: a covering needs total density Sum_{used} 1/m >= 1 (union bound).
   Let slack = Sum_{pool} 1/m - 1 (exact Fraction). Any m with 1/m > slack MUST be used:
   leaving it out caps the achievable density below 1. Unit clause u_m.
3. PAIR clauses: for m1 < m2 (both optional) with 1/m1 + 1/m2 > slack: (u_m1 OR u_m2).
4. Same translation symmetry breaking as before (a_4 = 0, a_6 in {0,1}).

Emits DIMACS + map. Usage: python3 sat_cover2.py L out.cnf out.map
"""
import sys
from fractions import Fraction
from sympy import isprime, divisors
from pysat.card import CardEnc, EncType

def pool_for(L):
    return sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)

def build(L):
    P = pool_for(L)
    slack = sum(Fraction(1, m) for m in P) - 1
    assert slack >= 0
    var, nv = {}, 0
    def newvar():
        nonlocal nv
        nv += 1
        return nv
    allowed = {}
    for m in P:
        if m == P[0]:
            allowed[m] = [0]
        elif len(P) > 1 and m == P[1] and P[0] == 4 and P[1] == 6:
            allowed[m] = [0, 1]
        else:
            allowed[m] = list(range(m))
        for a in allowed[m]:
            var[(m, a)] = newvar()
    used = {m: newvar() for m in P}
    clauses = []
    top = nv
    for m in P:
        lits = [var[(m, a)] for a in allowed[m]]
        # u_m <-> OR lits
        clauses.append([-used[m]] + lits)
        for l in lits:
            clauses.append([-l, used[m]])
        if len(lits) > 1:
            cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top, encoding=EncType.seqcounter)
            top = max(top, cnf.nv)
            clauses.extend(cnf.clauses)
    forced = [m for m in P if Fraction(1, m) > slack]
    for m in forced:
        clauses.append([used[m]])
    optional = [m for m in P if Fraction(1, m) <= slack]
    npair = 0
    for i in range(len(optional)):
        for j in range(i + 1, len(optional)):
            if Fraction(1, optional[i]) + Fraction(1, optional[j]) > slack:
                clauses.append([used[optional[i]], used[optional[j]]])
                npair += 1
    for x in range(L):
        clauses.append([var[(m, x % m)] for m in P if (m, x % m) in var])
    print(f"L={L} |pool|={len(P)} slack={float(slack):.6f} forced={forced} pair_clauses={npair} "
          f"vars={top} clauses={len(clauses)}")
    return P, var, clauses, top

def main():
    L = int(sys.argv[1])
    out, mp = sys.argv[2], sys.argv[3]
    P, var, clauses, top = build(L)
    with open(out, "w") as f:
        f.write(f"p cnf {top} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    with open(mp, "w") as f:
        for (m, a), v in sorted(var.items(), key=lambda kv: kv[1]):
            f.write(f"{v} {m} {a}\n")

if __name__ == "__main__":
    main()
