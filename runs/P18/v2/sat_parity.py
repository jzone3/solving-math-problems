#!/usr/bin/env python3
"""Parity-reduced SAT encoding (round 2).

All pool moduli are even, so a covering of Z with moduli | L splits into a covering of the
even integers and one of the odd integers; via x = 2y + r each becomes a covering of Z/(L/2)
with moduli m/2, and the two parts use *disjoint* subsets of the pool (distinct moduli).

Encoding over half-period H = L/2:
  y0[m][b] / y1[m][b]: congruence with modulus m assigned to parity class 0/1, residue b mod m/2.
  AMO over the union of y0[m][*] and y1[m][*] per m (modulus used at most once overall).
  Coverage: for each y in Z/H: OR_m y0[m][y mod m/2]  and  OR_m y1[m][y mod m/2].
  Forced-use units and pair clauses from the density slack (union bound), as in sat_cover2.
  Symmetry: swapping parity classes = translation by 1 => WLOG modulus 4 (half-mod 2), if used,
  sits in class 0; residual translations by 2 fix its residue b = 0. So y1[4][*] removed and
  y0[4] restricted to b = 0.

Usage: python3 sat_parity.py L out.cnf out.map
"""
import sys
from fractions import Fraction
from sympy import isprime, divisors
from pysat.card import CardEnc, EncType

def main():
    L = int(sys.argv[1]); out, mp = sys.argv[2], sys.argv[3]
    assert L % 2 == 0
    H = L // 2
    P = sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)
    slack = sum(Fraction(1, m) for m in P) - 1
    var, nv, clauses = {}, 0, []
    def newvar():
        nonlocal nv; nv += 1; return nv
    for m in P:
        h = m // 2
        if m == 4:
            var[(0, m, 0)] = newvar()          # class 0, residue 0 only
        else:
            for c in (0, 1):
                for b in range(h):
                    var[(c, m, b)] = newvar()
    used = {m: newvar() for m in P}
    top = nv
    for m in P:
        lits = [var[k] for k in var if k[1] == m and isinstance(k[0], int)]
        clauses.append([-used[m]] + lits)
        for l in lits:
            clauses.append([-l, used[m]])
        if len(lits) > 1:
            cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top, encoding=EncType.seqcounter)
            top = max(top, cnf.nv); clauses.extend(cnf.clauses)
    forced = [m for m in P if Fraction(1, m) > slack]
    for m in forced:
        clauses.append([used[m]])
    optional = [m for m in P if Fraction(1, m) <= slack]
    npair = 0
    for i in range(len(optional)):
        for j in range(i + 1, len(optional)):
            if Fraction(1, optional[i]) + Fraction(1, optional[j]) > slack:
                clauses.append([used[optional[i]], used[optional[j]]]); npair += 1
    for y in range(H):
        for c in (0, 1):
            cl = [var[k] for m in P for k in [(c, m, y % (m // 2))] if k in var]
            clauses.append(cl)
    print(f"L={L} H={H} |pool|={len(P)} forced={forced} pairs={npair} vars={top} clauses={len(clauses)}")
    with open(out, "w") as f:
        f.write(f"p cnf {top} {len(clauses)}\n")
        for cl in clauses:
            f.write(" ".join(map(str, cl)) + " 0\n")
    with open(mp, "w") as f:
        for k, v in sorted(((k, v) for k, v in var.items()), key=lambda kv: kv[1]):
            f.write(f"{v} {k[0]} {k[1]} {k[2]}\n")

if __name__ == "__main__":
    main()
