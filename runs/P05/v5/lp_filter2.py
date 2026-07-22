#!/usr/bin/env python3
"""Fast stage-2 filter: dedupes candidate feasibility systems before z3.

Feasibility depends only on (relabeled M matrix over union U, chosen pairs,
their M values). Dedupe on that canonical key; z3-check each unique system
once. Feasible systems are rare (none so far); each feasible candidate line
is then verified directly like lp_filter.py.
"""
import sys
import re
from itertools import combinations
from z3 import Ints, Solver, sat


def feasible(k, chosen_idx, Mmat):
    Lv = [Ints(f'L{i}')[0] for i in range(k)]
    s = Solver()
    for v in range(k):
        s.add(Lv[v] >= 1)
    (x1, y1, M1), (x2, y2, M2), (x3, y3, M3) = chosen_idx
    S1 = Lv[x1] + Lv[y1] + M1
    s.add(S1 == Lv[x2] + Lv[y2] + M2)
    s.add(S1 == Lv[x3] + Lv[y3] + M3)
    ch = {(x1, y1), (x2, y2), (x3, y3)}
    for x, y in combinations(range(k), 2):
        if (x, y) in ch:
            continue
        s.add(Lv[x] + Lv[y] + Mmat[(x, y)] <= S1)
    return s.check() == sat


def main():
    pat = re.compile(
        r'CAND (\S+) pairs=(\d+),(\d+);(\d+),(\d+);(\d+),(\d+) '
        r'lens=(\d+),(\d+),(\d+) p1=(\d+) p2=(\d+) p3=(\d+) M=(\S+)')
    seen = {}
    n_lines = n_unique = n_feas = 0
    for line in sys.stdin:
        if not line.startswith('CAND '):
            continue
        n_lines += 1
        m = pat.match(line)
        assert m, line
        u1, v1, u2, v2, u3, v3 = (int(m.group(i)) for i in range(2, 8))
        M1, M2, M3 = (int(m.group(i)) for i in range(8, 11))
        Mall = {}
        for ent in m.group(14).rstrip(';').split(';'):
            x, y, l = map(int, ent.split(','))
            Mall[(x, y)] = Mall[(y, x)] = l
        U = sorted(set([u1, v1, u2, v2, u3, v3]))
        idx = {v: i for i, v in enumerate(U)}
        k = len(U)
        Mmat = {}
        for x, y in combinations(range(k), 2):
            Mmat[(x, y)] = Mall[(U[x], U[y])]
        chosen = tuple(sorted(
            (min(idx[a], idx[b]), max(idx[a], idx[b]), M)
            for a, b, M in ((u1, v1, M1), (u2, v2, M2), (u3, v3, M3))))
        key = (k, chosen, tuple(sorted(Mmat.items())))
        if key in seen:
            if seen[key]:
                print('FEASIBLE-DUP', line.strip(), flush=True)
            continue
        n_unique += 1
        f = feasible(k, chosen, Mmat)
        seen[key] = f
        if f:
            n_feas += 1
            print('FEASIBLE', line.strip(), flush=True)
        if n_lines % 1000000 == 0:
            print(f'# ...{n_lines} lines, {n_unique} unique, {n_feas} feasible',
                  file=sys.stderr, flush=True)
    print(f'# {n_lines} candidates, {n_unique} unique systems, {n_feas} feasible',
          file=sys.stderr)


if __name__ == '__main__':
    main()
