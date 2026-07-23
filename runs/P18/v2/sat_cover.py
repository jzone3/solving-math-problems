#!/usr/bin/env python3
"""SAT search for an Erdos #273 covering system with all moduli dividing L.

Encoding (exact, integers only):
  * Pool = {m : m | L, m > 1, m+1 prime, m+1 >= 5}.
  * Variable y[m][a] for each m in pool, a in range(m): "congruence a (mod m) selected".
  * Distinct moduli (ErGr80 convention): at most one residue selected per modulus
    (pairwise AMO per m).
  * Coverage: for each x in range(L): OR_{m in pool} y[m][x mod m].
  * Sound symmetry breaking via translation invariance of Z:
      - residues of the smallest pool modulus m0 restricted to a = 0
        (any covering using m0 can be translated so its m0-residue is 0;
         coverings not using m0 are unaffected only if we DON'T force usage --
         we merely delete y[m0][a], a != 0, which is sound),
      - residues of the second modulus m1 restricted to a in {0, ..., gcd-orbit},
        here conservatively a in {0, 1} for m1 = 6 with m0 = 4
        (residual translations are multiples of 4; {0,2,4} mod 6 acts on residues,
         orbits are the two parity classes, so every class has a representative in {0,1}).
  * If SAT: prints the witness and re-verifies it from scratch (pure integer check).

Usage: python3 sat_cover.py L [time_limit_s] [--no-symbreak]
"""
import sys, time
from fractions import Fraction
from sympy import isprime, divisors
from pysat.solvers import Cadical153
from pysat.card import CardEnc, EncType

def pool_for(L):
    return sorted(m for m in divisors(L) if m > 1 and isprime(m + 1) and m + 1 >= 5)

def build(L, symbreak=True):
    P = pool_for(L)
    var = {}
    nv = 0
    allowed = {}
    for m in P:
        if symbreak and m == P[0]:
            allowed[m] = [0]
        elif symbreak and len(P) > 1 and m == P[1] and P[0] == 4 and P[1] == 6:
            allowed[m] = [0, 1]
        else:
            allowed[m] = list(range(m))
        for a in allowed[m]:
            nv += 1
            var[(m, a)] = nv
    clauses = []
    # AMO per modulus (sequential counter, linear-size; pairwise blows up for m ~ 10^4)
    top = nv
    for m in P:
        lits = [var[(m, a)] for a in allowed[m]]
        if len(lits) > 1:
            cnf = CardEnc.atmost(lits=lits, bound=1, top_id=top, encoding=EncType.seqcounter)
            top = max(top, cnf.nv)
            clauses.extend(cnf.clauses)
    # coverage
    for x in range(L):
        cl = []
        for m in P:
            a = x % m
            v = var.get((m, a))
            if v:
                cl.append(v)
        clauses.append(cl)
    return P, var, clauses, nv

def verify(L, witness):
    """Pure-integer independent check of a witness [(a, m), ...]."""
    ms = [m for _, m in witness]
    assert len(set(ms)) == len(ms), "moduli not distinct"
    for a, m in witness:
        assert m > 1 and isprime(m + 1) and m + 1 >= 5, f"bad modulus {m}"
    covered = bytearray(L)
    for a, m in witness:
        assert L % m == 0
        for x in range(a % m, L, m):
            covered[x] = 1
    return all(covered)

def main():
    L = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 0
    symbreak = "--no-symbreak" not in sys.argv
    P, var, clauses, nv = build(L, symbreak)
    dens = sum(Fraction(1, m) for m in P)
    print(f"L={L} |pool|={len(P)} density={float(dens):.6f} vars={nv} clauses={len(clauses)} symbreak={symbreak}")
    if dens < 1:
        print("RESULT density<1 => UNSAT trivially (no covering with moduli | L)")
        return
    t0 = time.time()
    with Cadical153(bootstrap_with=clauses) as s:
        if tl:
            # cadical via pysat has no native timeout; rely on external timeout(1) instead
            pass
        res = s.solve()
        t = time.time() - t0
        if res:
            model = set(l for l in s.get_model() if l > 0)
            witness = sorted(((a, m) for (m, a), v in var.items() if v in model), key=lambda t: t[1])
            print(f"SAT in {t:.1f}s; witness ({len(witness)} congruences):")
            print(witness)
            ok = verify(L, witness)
            print("independent re-verification:", "PASS" if ok else "FAIL")
        else:
            print(f"RESULT UNSAT in {t:.1f}s: no covering system with distinct moduli of the form p-1 (p>=5 prime) all dividing {L}")

if __name__ == "__main__":
    main()
