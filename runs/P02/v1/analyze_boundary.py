#!/usr/bin/env python3
"""Exact re-verification of every BOUNDARY-INFEAS witness found by the sweep:
checks (exactly, over Q) maximality, triangle-freeness, delta >= n/3,
multiplication-LP infeasibility, and computes exact d_f of the core.
Usage: analyze_boundary.py out/N*.txt"""
import sys
from itertools import combinations
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from exactlp import exact_max_t, exact_df
from process import graph6_to_adj


def core_of(n, adj):
    classes = {}
    for v in range(n):
        classes.setdefault(adj[v], []).append(v)
    reps = sorted(classes, key=lambda m: classes[m][0])
    m = len(reps)
    cadj = [0] * m
    for i, r in enumerate(reps):
        for j, r2 in enumerate(reps):
            if r >> classes[r2][0] & 1:
                cadj[i] |= 1 << j
    return m, cadj


def canon_key(n, adj):
    # cheap iso-invariant key (not a full canonical form): sorted refined
    # colour histogram via 3 rounds of WL
    col = [bin(a).count('1') for a in adj]
    for _ in range(3):
        new = []
        for v in range(n):
            nb = sorted(col[u] for u in range(n) if adj[v] >> u & 1)
            new.append(hash((col[v], tuple(nb))))
        col = new
    return (n, tuple(sorted(col)))


def main():
    total = 0
    keys = {}
    for path in sys.argv[1:]:
        for line in open(path):
            if not line.startswith('BOUNDARY-INFEAS'):
                continue
            parts = line.split()
            g6 = parts[2]
            n, adj = graph6_to_adj(g6)
            degs = [bin(a).count('1') for a in adj]
            assert 3 * min(degs) >= n, (g6, 'delta')
            for u, v in combinations(range(n), 2):
                if adj[u] >> v & 1:
                    assert not (adj[u] & adj[v]), (g6, 'triangle')
                else:
                    assert adj[u] & adj[v], (g6, 'not maximal')
            m, cadj = core_of(n, adj)
            t = exact_max_t(m, cadj)
            assert t == 0, (g6, 'mult system not infeasible?!', t)
            df = exact_df(m, cadj)
            assert df >= 3, (g6, 'df < 3: REAL COUNTEREXAMPLE', df)
            total += 1
            keys.setdefault(canon_key(m, cadj), []).append((n, g6, str(df)))
    print(f'verified {total} boundary-infeasible witnesses, all df >= 3 (exact)')
    print(f'~{len(keys)} distinct cores (WL-key upper bound estimate)')
    for k, v in sorted(keys.items(), key=lambda kv: (kv[0][0], -len(kv[1]))):
        n_core = k[0]
        dfs = set(x[2] for x in v)
        print(f'core_n={n_core} count={len(v)} dfs={sorted(dfs)} '
              f'example={v[0][1]} (n={v[0][0]})')


if __name__ == '__main__':
    main()
