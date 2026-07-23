#!/usr/bin/env python3
"""Cube-and-conquer for the BTD SAT encoding.

Cubes = full assignments of row 1 (the second row), enumerated up to the
symmetry already broken in encode.py:
  - row 0 is fixed: segments seg0=[0,p2) all 2s, seg1=[p2,p2+p1) all 1s, seg2 rest 0s;
  - columns within each segment are lex-decreasing over rows 1..V-1, whose most
    significant entry is row 1 ⇒ row 1 is non-increasing within each segment.
So a cube is (a2,a1,b2,b1,c2,c1): counts of 2s/1s of row 1 in each segment, with
  a1+b1+c1 = p1, a2+b2+c2 = p2, and pair(0,1) coverage 4*a2+2*a1+2*b2+b1 = L,
row 1 laid out canonically (2s then 1s then 0s per segment). The cube set covers
all row-1 possibilities modulo broken symmetry ⇒ UNSAT of all cubes = UNSAT.

Usage: cube.py V B p1 p2 R K L basename [--nolex]

With --nolex: base encoding has NO lex/double-lex constraints (sym=False); row 0 is
fixed here by unit clauses (WLOG) and cubes fix row 1 as above. Soundness then rests
only on elementary column-permutation arguments — used to cross-check UNSAT results
independently of the double-lex machinery.
Writes basename-cube<k>.cnf for each cube (encode.py's CNF + unit clauses).
"""
import sys
from encode import encode

V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
base = sys.argv[8]
nolex = '--nolex' in sys.argv

cls, pool, x1, x2 = encode(V, B, p1, p2, R, K, L, sym=not nolex)
if nolex:
    for b in range(B):
        if b < p2:
            cls.append([x2[0][b]])
        elif b < p2 + p1:
            cls.append([x1[0][b]])
            cls.append([-x2[0][b]])
        else:
            cls.append([-x1[0][b]])
nv = pool.top

seg = [(0, p2), (p2, p2 + p1), (p2 + p1, B)]
cubes = []
for a2 in range(0, p2 + 1):
    for b2 in range(0, p2 - a2 + 1):
        c2 = p2 - a2 - b2
        for a1 in range(0, p1 + 1):
            for b1 in range(0, p1 - a1 + 1):
                c1 = p1 - a1 - b1
                if a2 + a1 > seg[0][1] - seg[0][0]:
                    continue
                if b2 + b1 > seg[1][1] - seg[1][0]:
                    continue
                if c2 + c1 > seg[2][1] - seg[2][0]:
                    continue
                if 4 * a2 + 2 * a1 + 2 * b2 + b1 != L:
                    continue
                cubes.append((a2, a1, b2, b1, c2, c1))

print(f'{len(cubes)} cubes')
for k, (a2, a1, b2, b1, c2, c1) in enumerate(cubes):
    units = []
    counts = [(a2, a1), (b2, b1), (c2, c1)]
    for (lo, hi), (n2, n1) in zip(seg, counts):
        for j, b in enumerate(range(lo, hi)):
            if j < n2:
                units.append([x2[1][b]])
            elif j < n2 + n1:
                units.append([x1[1][b]])
                units.append([-x2[1][b]])
            else:
                units.append([-x1[1][b]])
    fn = f'{base}-cube{k}.cnf'
    with open(fn, 'w') as f:
        f.write(f'p cnf {nv} {len(cls) + len(units)}\n')
        for v in range(V):
            f.write('c map %d %s\n' % (v, ' '.join(f'{x1[v][b]},{x2[v][b]}' for b in range(B))))
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')
        for c in units:
            f.write(' '.join(map(str, c)) + ' 0\n')
    print(fn, (a2, a1, b2, b1, c2, c1))
