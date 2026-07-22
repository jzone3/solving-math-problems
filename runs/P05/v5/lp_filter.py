#!/usr/bin/env python3
"""Stage-2 filter: read CAND lines from multi_search, check integer
feasibility of arm lengths with z3, and for feasible ones do a full direct
brute-force verification of the constructed multi-arm graph.

Feasibility system (arms at U = union of chosen pair vertices, arm lengths
L_v >= 1 integer, plus a global uniform shift handled implicitly):
  L_x1+L_y1+M1 == L_x2+L_y2+M2 == L_x3+L_y3+M3 == S
  for every other unordered pair (u,v) in U: L_u+L_v+M_uv <= S
One-arm/zero-arm paths are dominated after adding a large uniform shift to
all L_v (pair sums grow by 2t, one-arm by t), so they impose no constraint.

Any candidate passing z3 is then built explicitly (with shift so that
min L >= |V(H)|) and verified by exhaustive longest-path enumeration.
"""
import sys
import re
from itertools import combinations
from z3 import Ints, Solver, sat


def parse_graph6(line):
    data = [ord(ch) - 63 for ch in line.strip()]
    n = data[0]
    bits = []
    for v in data[1:]:
        bits.extend((v >> k) & 1 for k in range(5, -1, -1))
    edges = []
    idx = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                edges.append((i, j))
            idx += 1
    return n, edges


def all_longest_paths(n, adj):
    best = [0]
    paths = []
    def dfs(v, mask, ln):
        for w in range(n):
            if adj[v] >> w & 1 and not mask >> w & 1:
                dfs(w, mask | 1 << w, ln + 1)
        if ln > best[0]:
            best[0] = ln
            paths.clear()
            paths.append(mask)
        elif ln == best[0]:
            paths.append(mask)
    for s in range(n):
        dfs(s, 1 << s, 0)
    return best[0], sorted(set(paths))


def main():
    n_feas = n_checked = n_counter = 0
    for line in sys.stdin:
        if not line.startswith('CAND '):
            continue
        n_checked += 1
        m = re.match(
            r'CAND (\S+) pairs=(\d+),(\d+);(\d+),(\d+);(\d+),(\d+) '
            r'lens=(\d+),(\d+),(\d+) p1=(\d+) p2=(\d+) p3=(\d+) M=(\S+)', line)
        assert m, line
        g6 = m.group(1)
        u1, v1, u2, v2, u3, v3 = (int(m.group(i)) for i in range(2, 8))
        M1, M2, M3 = (int(m.group(i)) for i in range(8, 11))
        Mall = {}
        for ent in m.group(14).rstrip(';').split(';'):
            x, y, l = map(int, ent.split(','))
            Mall[(x, y)] = Mall[(y, x)] = l
        U = sorted(set([u1, v1, u2, v2, u3, v3]))
        Lv = {v: Ints(f'L{v}')[0] for v in U}
        s = Solver()
        for v in U:
            s.add(Lv[v] >= 1)
        chosen = {tuple(sorted(p)) for p in [(u1, v1), (u2, v2), (u3, v3)]}
        S1 = Lv[u1] + Lv[v1] + M1
        s.add(S1 == Lv[u2] + Lv[v2] + M2)
        s.add(S1 == Lv[u3] + Lv[v3] + M3)
        for x, y in combinations(U, 2):
            if (x, y) in chosen:
                continue
            s.add(Lv[x] + Lv[y] + Mall[(x, y)] <= S1)
        if s.check() != sat:
            continue
        n_feas += 1
        mod = s.model()
        Lval = {v: mod[Lv[v]].as_long() for v in U}
        nh, edges = parse_graph6(g6)
        shift = nh + max(0, *Lval.values())
        for v in U:
            Lval[v] += shift
        # build multi-arm graph
        edges2 = list(edges)
        n = nh
        for root in U:
            prev = root
            for _ in range(Lval[root]):
                edges2.append((prev, n))
                prev = n
                n += 1
        adj = [0] * n
        for a, b in edges2:
            adj[a] |= 1 << b
            adj[b] |= 1 << a
        best, paths = all_longest_paths(n, adj)
        mn = 999
        for p1, p2, p3 in combinations(paths, 3):
            sz = bin(p1 & p2 & p3).count('1')
            mn = min(mn, sz)
            if mn == 0:
                break
        tag = 'COUNTEREXAMPLE' if mn == 0 else 'direct-check-fail'
        if mn == 0:
            n_counter += 1
        print(f'FEASIBLE {line.strip()} L={Lval} spider_n={n} '
              f'longest={best} npaths={len(paths)} min_triple={mn} {tag}',
              flush=True)
    print(f'# {n_checked} candidates, {n_feas} feasible, '
          f'{n_counter} counterexamples', file=sys.stderr)


if __name__ == '__main__':
    main()
