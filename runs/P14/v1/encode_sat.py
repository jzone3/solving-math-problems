#!/usr/bin/env python3
"""Third independent check: CNF encoding of BTD(V,B;p1,p2,R;K,L) for a
DRAT-certified UNSAT proof via kissat + drat-trim.

Encoding:
  vars x1[i][j], x2[i][j] booleans; not both.
  row: exactly p1 of x1, exactly p2 of x2 (seqcounter cardinality).
  col: sum x1 + 2*sum x2 = K, weighted sums done by literal duplication
       inside a seqcounter cardinality-equals (duplicating a literal w
       times contributes w to the count; verified exhaustively on small
       cases — see NOTES.md).
  pair (i,k): sum_j (a1 + 2*a2 + 2*a3 + 4*a4) = L with AND-aux vars
       a1=x1i&x1k, a2=x1i&x2k, a3=x2i&x1k, a4=x2i&x2k (3 clauses each),
       weighted by duplication as above.
  double-lex symmetry breaking (sound): rows lex non-increasing and
       columns lex non-increasing, entries ordered by value m=x1+2*x2
       (numeric order == lex order on (x2,x1) since x1,x2 exclusive).

Usage: encode_sat.py V B p1 p2 R K L out.cnf
"""
import sys
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, CNF


def main():
    V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
    assert R == p1 + 2 * p2
    out = sys.argv[8]
    pool = IDPool()
    cnf = CNF()
    X1 = [[pool.id(("x1", i, j)) for j in range(B)] for i in range(V)]
    X2 = [[pool.id(("x2", i, j)) for j in range(B)] for i in range(V)]

    def card_eq(lits, bound):
        c = CardEnc.equals(lits=lits, bound=bound, vpool=pool,
                           encoding=EncType.seqcounter)
        cnf.extend(c.clauses)

    for i in range(V):
        for j in range(B):
            cnf.append([-X1[i][j], -X2[i][j]])
        card_eq(X1[i][:], p1)
        card_eq(X2[i][:], p2)

    for j in range(B):
        lits = [X1[i][j] for i in range(V)]
        for i in range(V):
            lits += [X2[i][j], X2[i][j]]
        card_eq(lits, K)

    def AND(a, b):
        v = pool.id(("and", a, b))
        cnf.append([-v, a])
        cnf.append([-v, b])
        cnf.append([v, -a, -b])
        return v

    for i in range(V):
        for k in range(i + 1, V):
            lits = []
            for j in range(B):
                a1 = AND(X1[i][j], X1[k][j])
                a2 = AND(X1[i][j], X2[k][j])
                a3 = AND(X2[i][j], X1[k][j])
                a4 = AND(X2[i][j], X2[k][j])
                lits += [a1] + [a2] * 2 + [a3] * 2 + [a4] * 4
            card_eq(lits, L)

    # double-lex: entry comparison literals for value m = x1 + 2*x2
    def entry_eq(iu, ju, iv, jv):
        """literal true iff m[iu][ju] == m[iv][jv] (uses x1/x2 exclusivity)."""
        v = pool.id(("eq", iu, ju, iv, jv))
        u1, u2 = X1[iu][ju], X2[iu][ju]
        v1, v2 = X1[iv][jv], X2[iv][jv]
        cnf.append([-v, -u1, v1]); cnf.append([-v, u1, -v1])
        cnf.append([-v, -u2, v2]); cnf.append([-v, u2, -v2])
        cnf.append([v, u1, v1, u2, v2])  # both entries 0 -> eq
        cnf.append([v, -u1, -v1])        # both mult 1 -> eq
        cnf.append([v, -u2, -v2])        # both mult 2 -> eq
        return v

    def add_lex_ge(cells_u, cells_v):
        """cells are lists of (i,j); enforce vector_u >=lex vector_v."""
        n = len(cells_u)
        eqs = []
        for t in range(n):
            eqs.append(entry_eq(*cells_u[t], *cells_v[t]))
        # prefix-eq chain
        pre = []
        for t in range(n):
            p = pool.id(("pre", tuple(cells_u), t))
            pre.append(p)
            if t == 0:
                cnf.append([-p, eqs[0]]); cnf.append([p, -eqs[0]])
            else:
                cnf.append([-p, pre[t - 1]]); cnf.append([-p, eqs[t]])
                cnf.append([p, -pre[t - 1], -eqs[t]])
        # position 0: m_u >= m_v ; conditional positions t: pre[t-1] -> m_u >= m_v
        def ge_clauses(cu, cv, cond):
            u1, u2 = X1[cu[0]][cu[1]], X2[cu[0]][cu[1]]
            v1, v2 = X1[cv[0]][cv[1]], X2[cv[0]][cv[1]]
            # forbid m_u < m_v: (u=0,v=1),(u=0,v=2),(u=1,v=2)
            base = [] if cond is None else [-cond]
            cnf.append(base + [u1, u2, -v1])   # u=0 & v1 -> contradiction
            cnf.append(base + [u1, u2, -v2])   # u=0 & v2
            cnf.append(base + [-u1, -v2])      # u=1 & v=2
        ge_clauses(cells_u[0], cells_v[0], None)
        for t in range(1, n):
            ge_clauses(cells_u[t], cells_v[t], pre[t - 1])

    for i in range(V - 1):
        add_lex_ge([(i, j) for j in range(B)], [(i + 1, j) for j in range(B)])
    for j in range(B - 1):
        add_lex_ge([(i, j) for i in range(V)], [(i, j + 1) for i in range(V)])

    cnf.to_file(out)
    print(f"wrote {out}: {pool.top} vars, {len(cnf.clauses)} clauses")


if __name__ == "__main__":
    main()
