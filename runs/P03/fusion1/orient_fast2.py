"""
Fast exhaustive orientation search for n=14/16 cubic graphs (justification:
see orient_exhaust.py docstring). Direct recursion (no generators), with:
- incremental reachability => cycles never created (DAG guaranteed);
- role-count pruning as vertices complete (bounded by allowed profiles);
- tau == 3 guaranteed by 3-edge-connectivity (sampled assert);
- source-sink-connectivity skip at leaves; SAT check for the rest.

Usage: python3 orient_fast2.py n start end < cubicN.g6
"""

import sys
import time
from collections import Counter

import networkx as nx

from harness import tau, has_k_disjoint_dijoins
from orient_exhaust import PROFILES, g6_to_edges
from orient_fast import ss_connected_fast


def search_graph(n, edges, profiles, stats, line):
    m = len(edges)
    max_s = max(p[0] for p in profiles)
    max_t = max(p[1] for p in profiles)
    max_a = max(p[2] for p in profiles)
    max_b = max(p[3] for p in profiles)
    inc = [[] for _ in range(n)]
    for i, (u, v) in enumerate(edges):
        inc[u].append(i)
        inc[v].append(i)
    outd = [0] * n
    ind = [0] * n
    done = [0] * n
    reach = [0] * n           # reach[v]: bitmask reachable FROM v (strict)
    arcs = []
    counts = {'s': 0, 't': 0, 'a': 0, 'b': 0}
    caps = {'s': max_s, 't': max_t, 'a': max_a, 'b': max_b}

    def role(v):
        if ind[v] == 0:
            return 's'
        if outd[v] == 0:
            return 't'
        return 'a' if ind[v] == 1 else 'b'

    def leaf():
        stats['dags'] += 1
        if stats['dags'] % 500 == 1:
            assert tau(n, arcs) == 3, f"tau!=3: {arcs}"
        prof = (counts['s'], counts['t'], counts['a'], counts['b'])
        if prof not in profiles:
            return
        stats['profile_dags'] += 1
        if ss_connected_fast(n, arcs):
            stats['ss_connected_skip'] += 1
            return
        stats['checked'] += 1
        if not has_k_disjoint_dijoins(n, arcs, 3):
            stats['NONPACKING'] += 1
            print("NONPACKING:", line.strip(), list(arcs), flush=True)

    def rec(i):
        if i == m:
            leaf()
            return
        u, v = edges[i]
        for (x, y) in ((u, v), (v, u)):
            if outd[x] >= 3 or ind[y] >= 3:
                continue
            if reach[y] & (1 << x):
                continue                      # would create a cycle
            outd[x] += 1
            ind[y] += 1
            done[x] += 1
            done[y] += 1
            finals = []
            ok = True
            for w in (x, y):
                if done[w] == 3:
                    r = role(w)
                    counts[r] += 1
                    finals.append(r)
                    if counts[r] > caps[r]:
                        ok = False
            if ok:
                saved = reach[:]
                add = reach[y] | (1 << y)
                for w in range(n):
                    if w == x or (reach[w] & (1 << x)):
                        reach[w] |= add
                arcs.append((x, y))
                rec(i + 1)
                arcs.pop()
                reach[:] = saved
            for r in finals:
                counts[r] -= 1
            outd[x] -= 1
            ind[y] -= 1
            done[x] -= 1
            done[y] -= 1

    rec(0)


if __name__ == "__main__":
    n = int(sys.argv[1])
    lines = [l for l in sys.stdin if l.strip()]
    if len(sys.argv) > 3:
        lines = lines[int(sys.argv[2]):int(sys.argv[3])]
    profiles = PROFILES[n]
    stats = Counter()
    t0 = time.time()
    for gi, line in enumerate(lines):
        G, edges = g6_to_edges(line)
        stats['graphs'] += 1
        if nx.check_planarity(G)[0]:
            stats['skip_planar'] += 1
            continue
        if nx.edge_connectivity(G) < 3:
            stats['skip_not_3ec'] += 1
            continue
        stats['graphs_kept'] += 1
        search_graph(n, edges, profiles, stats, line)
        if (gi + 1) % 5 == 0:
            print(f"[{gi+1}/{len(lines)}] {dict(stats)} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print("DONE", dict(stats), f"wall={time.time()-t0:.0f}s", flush=True)
