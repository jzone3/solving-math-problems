"""
Optimized version of orient_exhaust.py for n=14/16 (see that file for the
justification chain). Differences:
- tau == 3 is guaranteed: the underlying graph is 3-edge-connected, so every
  cut has >= 3 edges; a dicut's arcs all cross one way, so every dicut has
  size >= 3; and any degree-3 source gives a dicut of size exactly 3.
  (Asserted on a 1/500 sample.)
- acyclicity via Kahn's algorithm on plain arc lists;
- source-sink connectivity via bitmask reachability;
- SAT check unchanged (harness.has_k_disjoint_dijoins).

Usage: python3 orient_fast.py n start end < cubicN.g6
"""

import sys
import time
from collections import Counter

import networkx as nx

from harness import tau, has_k_disjoint_dijoins
from orient_exhaust import PROFILES, orientations, g6_to_edges


def is_acyclic_fast(n, arcs):
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        indeg[v] += 1
        adj[u].append(v)
    stack = [v for v in range(n) if indeg[v] == 0]
    seen = 0
    while stack:
        u = stack.pop()
        seen += 1
        for w in adj[u]:
            indeg[w] -= 1
            if indeg[w] == 0:
                stack.append(w)
    return seen == n


def ss_connected_fast(n, arcs):
    """True iff every source reaches every sink (bitmask DFS)."""
    adj = [0] * n
    ind = [0] * n
    outd = [0] * n
    for (u, v) in arcs:
        adj[u] |= (1 << v)
        outd[u] += 1
        ind[v] += 1
    reach = [0] * n
    # process in reverse topological order via repeated relaxation (n small)
    for _ in range(n):
        changed = False
        for v in range(n):
            r = adj[v]
            m = adj[v]
            while m:
                w = (m & -m).bit_length() - 1
                r |= reach[w]
                m &= m - 1
            if r != reach[v]:
                reach[v] = r
                changed = True
        if not changed:
            break
    sinks = 0
    for v in range(n):
        if outd[v] == 0:
            sinks |= (1 << v)
    for v in range(n):
        if ind[v] == 0:
            if (reach[v] & sinks) != sinks:
                return False
    return True


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
        for arcs in orientations(n, edges, profiles):
            stats['profile_orientations'] += 1
            if not is_acyclic_fast(n, arcs):
                continue
            stats['dags'] += 1
            if stats['dags'] % 500 == 0:
                assert tau(n, arcs) == 3, f"tau != 3: {arcs}"
            if ss_connected_fast(n, arcs):
                stats['ss_connected_skip'] += 1
                continue
            stats['checked'] += 1
            if not has_k_disjoint_dijoins(n, arcs, 3):
                stats['NONPACKING'] += 1
                print("NONPACKING:", line.strip(), arcs, flush=True)
        if (gi + 1) % 5 == 0:
            print(f"[{gi+1}/{len(lines)}] {dict(stats)} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print("DONE", dict(stats), f"wall={time.time()-t0:.0f}s", flush=True)
