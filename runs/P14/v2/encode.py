#!/usr/bin/env python3
"""SAT encoder for Balanced Ternary Designs BTD(V,B; p1,p2,R; K,L).

Variables per cell (v,b):
  x1[v][b] : multiplicity >= 1
  x2[v][b] : multiplicity == 2   (x2 -> x1)
So m_{vb} = x1 + x2 (as 0/1 ints), m in {0,1,2}.

Constraints (all via cardinality networks, pysat CardEnc):
  row v:    sum_b x1 = p1 + p2,  sum_b x2 = p2      (=> row sum = R)
  col b:    sum_v (x1 + x2) = K                     (2VB literals? no: 2V per col)
  pair v<w: sum_b m_vb * m_wb = L. Expand product:
            m_v*m_w = x1v*x1w + x1v*x2w + x2v*x1w + x2v*x2w  (each an AND var)
            -> plain cardinality: sum of 4B AND-literals == L.

Symmetry breaking:
  - Row 0 fixed to canonical pattern: p2 twos, then p1 ones, then zeros.
  - Column lex-decreasing within each constant segment of row 0.
  - Row lex-decreasing among rows 1..V-1 (adjacent rows), comparing cell values.

Usage: encode.py V B p1 p2 R K L out.cnf [--nosym]
Writes DIMACS; a comment line "c map v b var1 var2" documents cell vars.
"""
import sys
from pysat.formula import IDPool
from pysat.card import CardEnc, EncType


def encode(V, B, p1, p2, R, K, L, sym=True):
    assert R == p1 + 2 * p2
    pool = IDPool()
    x1 = [[pool.id(('x1', v, b)) for b in range(B)] for v in range(V)]
    x2 = [[pool.id(('x2', v, b)) for b in range(B)] for v in range(V)]
    cls = []
    # x2 -> x1
    for v in range(V):
        for b in range(B):
            cls.append([-x2[v][b], x1[v][b]])

    def card_eq(lits, bound):
        cnf = CardEnc.equals(lits=lits, bound=bound, vpool=pool,
                             encoding=EncType.cardnetwrk)
        cls.extend(cnf.clauses)

    # rows
    for v in range(V):
        card_eq(x1[v][:], p1 + p2)
        card_eq(x2[v][:], p2)
    # cols
    for b in range(B):
        card_eq([x1[v][b] for v in range(V)] + [x2[v][b] for v in range(V)], K)

    # AND helper
    def AND(a, bb):
        t = pool.id(('and', a, bb))
        # define once
        if getattr(pool, '_defined', None) is None:
            pool._defined = set()
        if t not in pool._defined:
            pool._defined.add(t)
            cls.append([-t, a])
            cls.append([-t, bb])
            cls.append([t, -a, -bb])
        return t

    # pairs
    for v in range(V):
        for w in range(v + 1, V):
            lits = []
            for b in range(B):
                lits.append(AND(x1[v][b], x1[w][b]))
                lits.append(AND(x1[v][b], x2[w][b]))
                lits.append(AND(x2[v][b], x1[w][b]))
                lits.append(AND(x2[v][b], x2[w][b]))
            card_eq(lits, L)

    if sym:
        # fix row 0: first p2 cells =2, next p1 cells =1, rest 0
        for b in range(B):
            if b < p2:
                cls.append([x2[0][b]])
            elif b < p2 + p1:
                cls.append([x1[0][b]])
                cls.append([-x2[0][b]])
            else:
                cls.append([-x1[0][b]])

        # Simpler & fully correct lex: implement lex >= directly with prefix
        # "equal so far" chain variables.
        def lex_ge(cellsA, cellsB, tag):
            # cells: list of (x1,x2) pairs; enforce value-vector A >=lex B.
            n = len(cellsA)
            # e[i]: prefix equal through i (0-based). gt[i]: A>B at pos i.
            prev_e = None
            for i in range(n):
                a1, a2 = cellsA[i]
                b1, b2 = cellsB[i]
                gt = pool.id(('lexgt', tag, i))
                eq = pool.id(('lexeq', tag, i))
                t1 = AND(a1, -b1)
                t2 = AND(a2, -b2)
                # gt <-> t1 | t2
                cls.append([-t1, gt]); cls.append([-t2, gt])
                cls.append([-gt, t1, t2])
                # eq -> pairwise equal (one direction suffices; also need
                # equality -> eq for completeness of the chain constraint,
                # otherwise the break could be unsound? No: constraint is
                # prev_e -> (gt | (eq & continue)). We must allow eq to be
                # set true when equal; add both directions to be safe.
                cls.append([-eq, -a1, b1]); cls.append([-eq, a1, -b1])
                cls.append([-eq, -a2, b2]); cls.append([-eq, a2, -b2])
                cls.append([eq, a1, b1])  # a1=b1=0 and a2=b2=0 -> need eq
                # full CNF for eq <- (a1<->b1)&(a2<->b2):
                # (~(a1<->b1) | ~(a2<->b2) | eq) expands to 4 clauses:
                cls.append([eq, a1, b1, a2, b2])
                cls.append([eq, a1, b1, -a2, -b2])
                cls.append([eq, -a1, -b1, a2, b2])
                cls.append([eq, -a1, -b1, -a2, -b2])
                # chain: prefix-equal-before -> gt or eq
                if prev_e is None:
                    cls.append([gt, eq])
                    e_here = eq
                else:
                    cls.append([-prev_e, gt, eq])
                    e_here = pool.id(('lexE', tag, i))
                    cls.append([-e_here, prev_e])
                    cls.append([-e_here, eq])
                    cls.append([e_here, -prev_e, -eq])
                prev_e = e_here
            # if fully equal that's fine (>=)

        # rows 1..V-1 lex-decreasing
        for v in range(1, V - 1):
            lex_ge([(x1[v][b], x2[v][b]) for b in range(B)],
                   [(x1[v + 1][b], x2[v + 1][b]) for b in range(B)],
                   ('row', v))
        # columns within row-0 segments lex-decreasing (rows 1..V-1)
        segs = [(0, p2), (p2, p2 + p1), (p2 + p1, B)]
        for lo, hi in segs:
            for b in range(lo, hi - 1):
                lex_ge([(x1[v][b], x2[v][b]) for v in range(1, V)],
                       [(x1[v][b + 1], x2[v][b + 1]) for v in range(1, V)],
                       ('col', b))

    return cls, pool, x1, x2


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    sym = '--nosym' not in sys.argv
    V, B, p1, p2, R, K, L = map(int, args[:7])
    out = args[7]
    cls, pool, x1, x2 = encode(V, B, p1, p2, R, K, L, sym)
    nv = pool.top
    with open(out, 'w') as f:
        f.write(f'p cnf {nv} {len(cls)}\n')
        for v in range(V):
            f.write('c map %d %s\n' % (v, ' '.join(f'{x1[v][b]},{x2[v][b]}' for b in range(B))))
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')
    print(f'wrote {out}: {nv} vars {len(cls)} clauses')


if __name__ == '__main__':
    main()
