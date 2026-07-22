#!/usr/bin/env python3
"""SAT encoder for (v,6,1)-perfect Mendelsohn designs (PMD).

A (v,k)-PMD is a collection of b = v(v-1)/k cyclically ordered k-tuples of
distinct points from a v-set such that for every t in 1..k-1, every ordered
pair (x,y) of distinct points appears t-apart in exactly one block.

Encoding (k=6):
  vars x[b][p][s] = "block b, position p holds symbol s".
  - each cell exactly one symbol (ALO + pairwise AMO)
  - each block: each symbol at most once (pairwise AMO over positions)
  - coverage: for each t in 1..5 and ordered pair (x,y), at least one
    (block,pos) realizes it. Since #slots per distance = 6b = v(v-1) equals
    #ordered pairs, at-least-one coverage implies exactly-one.
    Realization uses aux var z[b,p,t,x,y] with z -> x[b][p][x], z -> x[b][p+t][y].
  - replication: each symbol appears in exactly r = 6b/v = (v-1)... wait r = k*b/v
    blocks; encoded as an exact cardinality constraint over the 6b cells.
Symmetry breaking:
  - block 0 fixed to (0,1,2,3,4,5)  [valid WLOG: relabel points of any block]
  - each block rotated so its minimal symbol is at position 0
  - blocks sorted by first symbol (nondecreasing), implemented via
    "if block b starts with symbol s then block b+1 starts with symbol >= s".

Usage: python3 encode_pmd.py v out.cnf [--nofix]
"""
import sys

K = 6

def encode(v, fix_first=True):
    b = v * (v - 1) // K
    assert v * (v - 1) % K == 0
    r = K * b // v
    assert K * b % v == 0
    clauses = []
    nv = 0
    def new():
        nonlocal nv
        nv += 1
        return nv
    X = [[[new() for s in range(v)] for p in range(K)] for bl in range(b)]
    def x(bl, p, s):
        return X[bl][p % K][s]

    # cell exactly-one
    for bl in range(b):
        for p in range(K):
            clauses.append([x(bl, p, s) for s in range(v)])
            for s1 in range(v):
                for s2 in range(s1 + 1, v):
                    clauses.append([-x(bl, p, s1), -x(bl, p, s2)])
    # block all-different
    for bl in range(b):
        for s in range(v):
            for p1 in range(K):
                for p2 in range(p1 + 1, K):
                    clauses.append([-x(bl, p1, s), -x(bl, p2, s)])
    # coverage
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
    # replication: each symbol in exactly r blocks == exactly r cells total
    try:
        from pysat.card import CardEnc, EncType
        from pysat.formula import IDPool
        pool = IDPool(start_from=nv + 1)
        for s in range(v):
            cells = [x(bl, p, s) for bl in range(b) for p in range(K)]
            cnf = CardEnc.equals(lits=cells, bound=r, vpool=pool,
                                 encoding=EncType.seqcounter)
            clauses.extend(cnf.clauses)
        nv = pool.top
    except ImportError:
        pass
    # symmetry breaking
    if fix_first:
        for p in range(K):
            clauses.append([x(0, p, p)])
    # min-rotation: position 0 holds the minimal symbol of the block
    for bl in range(1 if fix_first else 0, b):
        for s in range(v):
            for p in range(1, K):
                for s2 in range(s):
                    clauses.append([-x(bl, 0, s), -x(bl, p, s2)])
    # sorted first symbols
    for bl in range((1 if fix_first else 0), b - 1):
        for s in range(v):
            for s2 in range(s):
                clauses.append([-x(bl, 0, s), -x(bl + 1, 0, s2)])
    return nv, clauses, b

def main():
    v = int(sys.argv[1])
    out = sys.argv[2]
    fix = '--nofix' not in sys.argv
    nv, clauses, b = encode(v, fix)
    with open(out, 'w') as f:
        f.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            f.write(' '.join(map(str, c)) + ' 0\n')
    print('v=%d blocks=%d vars=%d clauses=%d fix=%s' % (v, b, nv, len(clauses), fix))

if __name__ == '__main__':
    main()
