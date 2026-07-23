#!/usr/bin/env python3
"""Adversarial-review INDEPENDENT CNF encoding of BTD(V,B;p1,p2,R;K,L),
written from the definition alone (CPro1 problem_def.py / Handbook VI.2),
deliberately different from runs/P14/v1/encode_sat.py:

  - order encoding per cell: t1[i][j] = (m_ij >= 1), t2[i][j] = (m_ij >= 2),
    with t2 -> t1.  Then m = t1 + t2 as a 0/1 sum (no literal duplication).
  - row i: exactly (p1+p2) of t1 true, exactly p2 of t2 true.
  - col j: exactly K of {t1[i][j], t2[i][j] : i} true (since sum m = K).
  - pair (i,k): m_i*m_k = (t1i+t2i)(t1k+t2k) = AND(t1i,t1k)+AND(t1i,t2k)
    +AND(t2i,t1k)+AND(t2i,t2k), all weight 1: exactly-L over 4B AND vars.
  - cardinalities: pysat totalizer (vs seqcounter in the reviewed encoder).
  - symmetry breaking: double-lex, rows and columns lex non-increasing
    (sound per Flener et al. CP 2002), implemented independently over
    order-encoded entry comparisons.  NOTE: a non-DEcreasing variant of
    this same encoder is dramatically slower for kissat (>5 h without a
    verdict vs ~10 min); the certified runs used this orientation.

Usage: review_encode.py V B p1 p2 R K L out.cnf [nolex]
"""
import sys
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, CNF


def build(V, B, p1, p2, R, K, L, lex=True):
    assert R == p1 + 2 * p2
    pool = IDPool()
    cnf = CNF()
    T1 = [[pool.id(("t1", i, j)) for j in range(B)] for i in range(V)]
    T2 = [[pool.id(("t2", i, j)) for j in range(B)] for i in range(V)]
    for i in range(V):
        for j in range(B):
            cnf.append([T1[i][j], -T2[i][j]])  # t2 -> t1

    def card_eq(lits, bound):
        c = CardEnc.equals(lits=lits, bound=bound, vpool=pool,
                           encoding=EncType.totalizer)
        cnf.extend(c.clauses)

    for i in range(V):
        card_eq(T1[i][:], p1 + p2)
        card_eq(T2[i][:], p2)
    for j in range(B):
        card_eq([T1[i][j] for i in range(V)] + [T2[i][j] for i in range(V)], K)

    def AND(a, b):
        v = pool.id(("A", min(a, b), max(a, b)))
        cnf.append([-v, a])
        cnf.append([-v, b])
        cnf.append([v, -a, -b])
        return v

    for i in range(V):
        for k in range(i + 1, V):
            lits = []
            for j in range(B):
                lits.append(AND(T1[i][j], T1[k][j]))
                lits.append(AND(T1[i][j], T2[k][j]))
                lits.append(AND(T2[i][j], T1[k][j]))
                lits.append(AND(T2[i][j], T2[k][j]))
            card_eq(lits, L)

    if lex:
        def le_clauses(cu, cv, cond):
            """m[cu] <= m[cv] (optionally under cond): order encoding:
            t1u -> t1v ; t2u -> t2v."""
            pre = [] if cond is None else [-cond]
            cnf.append(pre + [-T1[cu[0]][cu[1]], T1[cv[0]][cv[1]]])
            cnf.append(pre + [-T2[cu[0]][cu[1]], T2[cv[0]][cv[1]]])

        def eq_var(cu, cv):
            v = pool.id(("E", cu, cv))
            u1, u2 = T1[cu[0]][cu[1]], T2[cu[0]][cu[1]]
            v1, v2 = T1[cv[0]][cv[1]], T2[cv[0]][cv[1]]
            cnf.append([-v, -u1, v1]); cnf.append([-v, u1, -v1])
            cnf.append([-v, -u2, v2]); cnf.append([-v, u2, -v2])
            cnf.append([v, u1, v1])          # both 0 (t1 false both) -> t2 false too -> eq
            cnf.append([v, -u1, -v1, u2, v2])  # both >=1, both <2 -> eq
            cnf.append([v, -u2, -v2])        # both 2 -> eq
            return v

        def add_lex_le(cells_u, cells_v):
            n = len(cells_u)
            le_clauses(cells_u[0], cells_v[0], None)
            prev = None
            for t in range(n - 1):
                e = eq_var(cells_u[t], cells_v[t])
                p = pool.id(("P", tuple(cells_u), t))
                if prev is None:
                    cnf.append([-p, e]); cnf.append([p, -e])
                else:
                    cnf.append([-p, prev]); cnf.append([-p, e])
                    cnf.append([p, -prev, -e])
                le_clauses(cells_u[t + 1], cells_v[t + 1], p)
                prev = p

        for i in range(V - 1):
            add_lex_le([(i + 1, j) for j in range(B)], [(i, j) for j in range(B)])
        for j in range(B - 1):
            add_lex_le([(i, j + 1) for i in range(V)], [(i, j) for i in range(V)])

    return cnf, pool, T1, T2


def main():
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    out = sys.argv[8]
    lex = not (len(sys.argv) > 9 and sys.argv[9] == "nolex")
    cnf, pool, _, _ = build(V, B, p1, p2, R, K, L, lex)
    cnf.to_file(out)
    print(f"wrote {out}: {pool.top} vars, {len(cnf.clauses)} clauses, lex={lex}")


if __name__ == "__main__":
    main()
