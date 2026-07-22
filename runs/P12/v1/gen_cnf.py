"""SAT encoding generator for Tuscan-2 squares T2(n).

Definition (Golomb-Taylor 1985; CPro1 problem_def.py):
  n x n array, each row a permutation of {0..n-1};
  every ordered pair (a,b), a!=b, appears with b directly right of a in EXACTLY one row;
  and with b two positions right of a in AT MOST one row.

Key counting fact used in the encoding: if every row is a permutation, there are
exactly n(n-1) distance-1 slots and n(n-1) ordered pairs, so AT-MOST-ONCE for
distance-1 pairs already forces EXACTLY-ONCE. Hence we only need at-most-one
constraints for both distances.

Variables:
  x[r][c][s] : symbol s sits at row r, column c.
  y1[r][c][(a,b)] aux: pair (a,b) realized at distance 1 at (r,c)-(r,c+1).
  y2 analogous for distance 2.
AMO over each pair's indicator list via sequential counter (pysat CardEnc).

Symmetry breaking ("standard form", cf. Kapralov ACCT 2012):
  - Counting argument: each symbol a needs its n-1 distance-1 pairs (a,b) exactly
    once; a appears n times (once per row) and contributes a distance-1 pair from
    every appearance not in the last column, so a is in the last column EXACTLY
    once. Symmetrically (pairs (.,a)) a is in the first column exactly once.
    Hence first and last columns are permutations of the symbols.
  - So w.l.o.g. (symbol relabeling + row permutation): row 0 = identity and
    column 0 = (0,1,...,n-1) top to bottom. Last column gets alldifferent as an
    implied constraint.

Usage: python3 gen_cnf.py n out.cnf
"""
import sys
from itertools import permutations
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType


def build(n: int) -> CNF:
    pool = IDPool()
    x = lambda r, c, s: pool.id(("x", r, c, s))
    cnf = CNF()

    # cell exactly-one symbol; row: each symbol exactly once
    for r in range(n):
        for c in range(n):
            lits = [x(r, c, s) for s in range(n)]
            cnf.append(lits)
            for i in range(n):
                for j in range(i + 1, n):
                    cnf.append([-lits[i], -lits[j]])
        for s in range(n):
            lits = [x(r, c, s) for c in range(n)]
            cnf.append(lits)
            for i in range(n):
                for j in range(i + 1, n):
                    cnf.append([-lits[i], -lits[j]])

    # pair indicators + AMO per ordered pair per distance
    for d in (1, 2):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                ys = []
                for r in range(n):
                    for c in range(n - d):
                        yv = pool.id(("y", d, r, c, a, b))
                        ys.append(yv)
                        # x[r][c][a] & x[r][c+d][b] -> y
                        cnf.append([-x(r, c, a), -x(r, c + d, b), yv])
                        # y -> both (helps propagation)
                        cnf.append([-yv, x(r, c, a)])
                        cnf.append([-yv, x(r, c + d, b)])
                amo = CardEnc.atmost(lits=ys, bound=1, vpool=pool,
                                     encoding=EncType.seqcounter)
                cnf.extend(amo.clauses)

    # symmetry: row 0 = identity, column 0 = identity (standard form)
    for c in range(n):
        cnf.append([x(0, c, c)])
    for r in range(1, n):
        cnf.append([x(r, 0, r)])
    # implied: last column is a permutation (exactly-one per symbol)
    for s in range(n):
        lits = [x(r, n - 1, s) for r in range(n)]
        cnf.append(lits)
        for i in range(n):
            for j in range(i + 1, n):
                cnf.append([-lits[i], -lits[j]])
    return cnf, pool


def main():
    n = int(sys.argv[1])
    out = sys.argv[2]
    cnf, pool = build(n)
    cnf.to_file(out)
    # var map for decoding: x vars are ("x",r,c,s)
    with open(out + ".map", "w") as f:
        for r in range(n):
            for c in range(n):
                for s in range(n):
                    f.write(f"{pool.id(('x', r, c, s))} {r} {c} {s}\n")
    print(f"n={n} vars={cnf.nv} clauses={len(cnf.clauses)}")


if __name__ == "__main__":
    main()
