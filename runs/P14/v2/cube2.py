#!/usr/bin/env python3
"""Two-row cubing for BTD SAT cross-checks, using ONLY elementary symmetry.

Row 0 fixed WLOG (p2 twos, p1 ones, zeros). Row 1: enumerate per-segment count
tuples (as cube.py --nolex) and lay out canonically; this refines the columns into
up to 9 runs ("refined segments") on which (row0,row1) is constant and inside which
columns remain freely permutable. Row 2: enumerate per-refined-segment counts
(n2_i, n1_i) with
    sum n2 = p2, sum n1 = p1, n2_i+n1_i <= size_i,
    sum_i r0_i*(2*n2_i+n1_i) = L   (pair 0,2)
    sum_i r1_i*(2*n2_i+n1_i) = L   (pair 1,2)
and lay row 2 out canonically inside each refined segment. Every BTD (if any) has a
column permutation matching one cube => UNSAT of all cubes proves nonexistence,
with no reliance on lex/double-lex constraints.

Usage:
  cube2.py V B p1 p2 R K L --count            # just print number of cubes
  cube2.py V B p1 p2 R K L basename [--emit]  # write basename-cube<k>.cnf
"""
import sys
from encode import encode

V, B, p1, p2, R, K, L = map(int, sys.argv[1:8])
count_only = '--count' in sys.argv
base = None
if not count_only:
    base = sys.argv[8]

seg = [(0, p2, 2), (p2, p2 + p1, 1), (p2 + p1, B, 0)]  # (lo, hi, row0val)


def row1_cubes():
    out = []
    for a2 in range(p2 + 1):
        for b2 in range(p2 - a2 + 1):
            c2 = p2 - a2 - b2
            for a1 in range(p1 + 1):
                for b1 in range(p1 - a1 + 1):
                    c1 = p1 - a1 - b1
                    caps = [s[1] - s[0] for s in seg]
                    if a2 + a1 > caps[0] or b2 + b1 > caps[1] or c2 + c1 > caps[2]:
                        continue
                    if 4 * a2 + 2 * a1 + 2 * b2 + b1 != L:
                        continue
                    out.append(((a2, a1), (b2, b1), (c2, c1)))
    return out


def refined(counts):
    """Given row-1 per-segment counts, return list of (lo, hi, r0, r1)."""
    runs = []
    for (lo, hi, r0), (n2, n1) in zip(seg, counts):
        pos = lo
        for val, n in ((2, n2), (1, n1), (0, hi - lo - n2 - n1)):
            if n > 0:
                runs.append((pos, pos + n, r0, val))
                pos += n
    return runs


def row2_dists(runs):
    """Enumerate (n2_i, n1_i) per run meeting all constraints (DFS with pruning)."""
    res = []
    m = len(runs)

    def dfs(i, rem2, rem1, s02, s12, acc):
        if s02 > L or s12 > L:
            return
        if i == m:
            if rem2 == 0 and rem1 == 0 and s02 == L and s12 == L:
                res.append(list(acc))
            return
        lo, hi, r0, r1 = runs[i]
        size = hi - lo
        for n2 in range(min(rem2, size) + 1):
            for n1 in range(min(rem1, size - n2) + 1):
                w = 2 * n2 + n1
                dfs(i + 1, rem2 - n2, rem1 - n1,
                    s02 + r0 * w, s12 + r1 * w, acc + [(n2, n1)])

    dfs(0, p2, p1, 0, 0, [])
    return res


cubes = []
for counts in row1_cubes():
    runs = refined(counts)
    for dist in row2_dists(runs):
        cubes.append((counts, runs, dist))
print(f'{len(cubes)} cubes', flush=True)
if count_only:
    sys.exit(0)

cls, pool, x1, x2 = encode(V, B, p1, p2, R, K, L, sym=False)
nv = pool.top
base_units = []
for b in range(B):
    if b < p2:
        base_units.append([x2[0][b]])
    elif b < p2 + p1:
        base_units.append([x1[0][b]])
        base_units.append([-x2[0][b]])
    else:
        base_units.append([-x1[0][b]])


def fix(v, b, val, units):
    if val == 2:
        units.append([x2[v][b]])
    elif val == 1:
        units.append([x1[v][b]])
        units.append([-x2[v][b]])
    else:
        units.append([-x1[v][b]])


for k, (counts, runs, dist) in enumerate(cubes):
    units = list(base_units)
    # row 1
    for (lo, hi, r0), (n2, n1) in zip(seg, counts):
        for j, b in enumerate(range(lo, hi)):
            fix(1, b, 2 if j < n2 else (1 if j < n2 + n1 else 0), units)
    # row 2
    for (lo, hi, r0, r1), (n2, n1) in zip(runs, dist):
        for j, b in enumerate(range(lo, hi)):
            fix(2, b, 2 if j < n2 else (1 if j < n2 + n1 else 0), units)
    fn = f'{base}-cube{k}.cnf'
    with open(fn, 'w') as f:
        f.write(f'p cnf {nv} {len(cls) + len(units)}\n')
        for v in range(V):
            f.write('c map %d %s\n' % (v, ' '.join(f'{x1[v][b]},{x2[v][b]}' for b in range(B))))
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')
        for c in units:
            f.write(' '.join(map(str, c)) + ' 0\n')
print('wrote', len(cubes), 'files', flush=True)
