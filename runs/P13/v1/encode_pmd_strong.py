#!/usr/bin/env python3
"""Strengthened SAT encoding for (v,6,1)-PMDs.

Same base encoding as encode_pmd.py plus implied (theorem-backed) constraints:
  - membership vars m[b][s] <-> symbol s occurs in block b;
  - every unordered pair of symbols co-occurs in EXACTLY 5 blocks
    (counting theorem: each co-occurrence realizes exactly one distance for
    each orientation of the pair, and each ordered pair realizes each of the
    5 distances exactly once);
  - each symbol in exactly r = 6b/v blocks (on membership vars).
An UNSAT result refutes the original definition MODULO these counting
theorems (proved in NOTES.md); a SAT model is checked by verify.py directly.

Usage: python3 encode_pmd_strong.py v out.cnf
"""
import sys

K = 6

def encode(v):
    b = v * (v - 1) // K
    r = K * b // v
    clauses = []
    nv = 0
    def new():
        nonlocal nv
        nv += 1
        return nv
    X = [[[new() for s in range(v)] for p in range(K)] for bl in range(b)]
    def x(bl, p, s):
        return X[bl][p % K][s]
    M = [[new() for s in range(v)] for bl in range(b)]

    for bl in range(b):
        for p in range(K):
            clauses.append([x(bl, p, s) for s in range(v)])
            for s1 in range(v):
                for s2 in range(s1 + 1, v):
                    clauses.append([-x(bl, p, s1), -x(bl, p, s2)])
        for s in range(v):
            for p1 in range(K):
                for p2 in range(p1 + 1, K):
                    clauses.append([-x(bl, p1, s), -x(bl, p2, s)])
            # membership definition
            clauses.append([-M[bl][s]] + [x(bl, p, s) for p in range(K)])
            for p in range(K):
                clauses.append([M[bl][s], -x(bl, p, s)])
    for t in range(1, K):
        for xs in range(v):
            for ys in range(v):
                if xs == ys:
                    continue
                lits = []
                for bl in range(b):
                    for p in range(K):
                        z = new()
                        clauses.append([-z, x(bl, p, xs)])
                        clauses.append([-z, x(bl, p + t, ys)])
                        lits.append(z)
                clauses.append(lits)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    pool = IDPool(start_from=nv + 1)
    # replication on membership
    for s in range(v):
        cnf = CardEnc.equals(lits=[M[bl][s] for bl in range(b)], bound=r,
                             vpool=pool, encoding=EncType.seqcounter)
        clauses.extend(cnf.clauses)
    # pair co-occurrence exactly 5
    for s1 in range(v):
        for s2 in range(s1 + 1, v):
            both = []
            for bl in range(b):
                w = pool.id(('w', bl, s1, s2))
                clauses.append([-w, M[bl][s1]])
                clauses.append([-w, M[bl][s2]])
                clauses.append([w, -M[bl][s1], -M[bl][s2]])
                both.append(w)
            cnf = CardEnc.equals(lits=both, bound=5, vpool=pool,
                                 encoding=EncType.seqcounter)
            clauses.extend(cnf.clauses)
    nv = pool.top
    # symmetry breaking: block 0 = (0..5); min-rotation; sorted first symbols
    for p in range(K):
        clauses.append([x(0, p, p)])
    for bl in range(1, b):
        for s in range(v):
            for p in range(1, K):
                for s2 in range(s):
                    clauses.append([-x(bl, 0, s), -x(bl, p, s2)])
    for bl in range(1, b - 1):
        for s in range(v):
            for s2 in range(s):
                clauses.append([-x(bl, 0, s), -x(bl + 1, 0, s2)])
    return nv, clauses, b

def main():
    v = int(sys.argv[1])
    nv, clauses, b = encode(v)
    with open(sys.argv[2], 'w') as f:
        f.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            f.write(' '.join(map(str, c)) + ' 0\n')
    print('v=%d blocks=%d vars=%d clauses=%d' % (v, b, nv, len(clauses)))

if __name__ == '__main__':
    main()
