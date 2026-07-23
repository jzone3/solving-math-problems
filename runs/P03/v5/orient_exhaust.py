"""
Exhaustive settlement of the SMALLEST POSSIBLE minimal tau=3 counterexample
cell for Woodall's conjecture, via cubic-graph orientation enumeration.

Justification chain (see NOTES.md sections 2, 3b):
- A minimal counterexample is "reduced" (Schrijver's discussion notes, Thm 3):
  acyclic, weakly 3-arc-connected, all sources/sinks have degree k=3, all
  internal vertices have degree 3. Hence its UNDERLYING GRAPH IS CUBIC and
  (weak 3-arc-connectivity) 3-edge-connected, in particular simple.
- ACZ 2023 rho bounds in both arc directions + the single-source/sink
  source-sink-connectivity argument force, per NOTES 3b:
    n=12: profile (sources, sinks, #(1,2), #(2,1)) = (2,2,4,4)
    n=14: profiles (2,2,5,5), (3,3,4,4), (2,3,6,3), (3,2,3,6)
- Planar digraphs are safe: skip planar underlying graphs.
- Source-sink connected digraphs are safe: skip those orientations.

So: enumerate all connected cubic graphs on n vertices (nauty geng), keep the
3-edge-connected non-planar ones, enumerate ALL acyclic orientations with an
allowed degree profile, and for each with tau exactly 3 that is not
source-sink connected, SAT-check the partition into 3 dijoins.

Usage: nauty-geng -c -d3 -D3 12 | python3 orient_exhaust.py 12 [start end]
(start/end slice the graph list for parallelism)
"""

import sys
import time
from collections import Counter

import networkx as nx

from harness import tau, has_k_disjoint_dijoins, is_source_sink_connected

PROFILES = {
    12: {(2, 2, 4, 4)},
    14: {(2, 2, 5, 5), (3, 3, 4, 4), (2, 3, 6, 3), (3, 2, 3, 6)},
    16: {(2, 2, 6, 6), (3, 3, 5, 5), (4, 4, 4, 4), (2, 3, 7, 4), (3, 2, 4, 7),
         (2, 4, 8, 2), (4, 2, 2, 8), (3, 4, 6, 3), (4, 3, 3, 6)},
}


def g6_to_edges(line):
    G = nx.from_graph6_bytes(line.strip().encode())
    return G, sorted(G.edges())


def profile_of(n, outd, ind):
    s = t = a = b = 0
    for v in range(n):
        if ind[v] == 0:
            s += 1
        elif outd[v] == 0:
            t += 1
        elif ind[v] == 1:
            a += 1
        else:
            b += 1
    return (s, t, a, b)


def orientations(n, edges, profiles):
    """DFS over edge orientations with degree-cap pruning; yields arc lists
    whose degree profile is allowed. Acyclicity checked by caller."""
    m = len(edges)
    outd = [0] * n
    ind = [0] * n
    arcs = []

    def rec(i):
        if i == m:
            if profile_of(n, outd, ind) in profiles:
                yield list(arcs)
            return
        u, v = edges[i]
        for (x, y) in ((u, v), (v, u)):
            if outd[x] < 3 and ind[y] < 3:
                outd[x] += 1
                ind[y] += 1
                arcs.append((x, y))
                yield from rec(i + 1)
                arcs.pop()
                outd[x] -= 1
                ind[y] -= 1

    yield from rec(0)


def is_acyclic(n, arcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    G.add_edges_from(arcs)
    return nx.is_directed_acyclic_graph(G)


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
            if not is_acyclic(n, arcs):
                continue
            stats['dags'] += 1
            if tau(n, arcs) != 3:
                continue
            stats['tau3'] += 1
            if is_source_sink_connected(n, arcs):
                stats['ss_connected_skip'] += 1
                continue
            stats['checked'] += 1
            if not has_k_disjoint_dijoins(n, arcs, 3):
                stats['NONPACKING'] += 1
                print("NONPACKING:", line.strip(), arcs, flush=True)
        if (gi + 1) % 10 == 0:
            print(f"[{gi+1}/{len(lines)}] {dict(stats)} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print("DONE", dict(stats), f"wall={time.time()-t0:.0f}s", flush=True)
