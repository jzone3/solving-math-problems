#!/usr/bin/env python3
"""Specialized SAT encoding for the (9,6,1)-PMD.

Structural reduction: in a (9,6,1)-PMD every unordered pair lies in exactly 5
blocks (one per distance), so the 12 block SETS form a (9,6,5)-BIBD; blocks are
distinct as sets because the complementary design is a (9,3,1)-BIBD (12 distinct
triples), i.e. an STS(9), which is UNIQUE up to isomorphism: the lines of AG(2,3).
Hence WLOG the 12 block sets are the complements of the 12 lines of AG(2,3) on
points 0..8 (point i = (i%3, i//3)); only the cyclic orderings are free.

Vars x[j][p][s]: block j, position p in 0..5, holds symbol s (s in the fixed
6-set of block j). Rotation broken by fixing the minimal symbol at position 0.
Coverage: for each t in 1..5 and ordered pair (x,y): at-least-one over aux z
(counting argument makes it exactly-one; verifier re-checks).
"""
import sys
from itertools import combinations

K = 6
V = 9

def ag23_lines():
    pts = [(i % 3, i // 3) for i in range(9)]
    idx = {p: i for i, p in enumerate(pts)}
    lines = set()
    for a, b in combinations(range(9), 2):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        x3, y3 = (-x1 - x2) % 3, (-y1 - y2) % 3
        c = idx[(x3, y3)]
        lines.add(tuple(sorted((a, b, c))))
    assert len(lines) == 12
    return sorted(lines)

def encode():
    lines = ag23_lines()
    blocks = [sorted(set(range(V)) - set(l)) for l in lines]  # 6-sets
    nv = 0
    clauses = []
    def new():
        nonlocal nv
        nv += 1
        return nv
    X = {}
    for j, bs in enumerate(blocks):
        for p in range(K):
            for s in bs:
                X[(j, p, s)] = new()
    def x(j, p, s):
        return X[(j, p % K, s)]
    for j, bs in enumerate(blocks):
        # rotation symmetry: minimal symbol at position 0
        clauses.append([x(j, 0, bs[0])])
        for p in range(K):
            clauses.append([x(j, p, s) for s in bs])
            for s1, s2 in combinations(bs, 2):
                clauses.append([-x(j, p, s1), -x(j, p, s2)])
        for s in bs:
            for p1, p2 in combinations(range(K), 2):
                clauses.append([-x(j, p1, s), -x(j, p2, s)])
    for t in range(1, K):
        for a in range(V):
            for b in range(V):
                if a == b:
                    continue
                lits = []
                for j, bs in enumerate(blocks):
                    if a in bs and b in bs:
                        for p in range(K):
                            z = new()
                            clauses.append([-z, x(j, p, a)])
                            clauses.append([-z, x(j, p + t, b)])
                            lits.append(z)
                clauses.append(lits)
    return nv, clauses, blocks

def main():
    out = sys.argv[1]
    nv, clauses, blocks = encode()
    with open(out, 'w') as f:
        f.write('p cnf %d %d\n' % (nv, len(clauses)))
        for c in clauses:
            f.write(' '.join(map(str, c)) + ' 0\n')
    with open(out + '.blocks', 'w') as f:
        for bs in blocks:
            f.write(' '.join(map(str, bs)) + '\n')
    print('vars=%d clauses=%d' % (nv, len(clauses)))

if __name__ == '__main__':
    main()
