"""
Saturation sampling at the minimal counterexample shape (2 sources, 2 sinks,
8 internal deg-3 vertices; n=12, 18 arcs). Samples random shape DAGs, keeps
those in the full target region, dedupes by Weisfeiler-Lehman hash of the
arc-labeled digraph, SAT-checks each new distinct instance, and reports the
distinct/seen curve so we can judge how close to exhausting the region we get.

Usage: python3 saturation.py seconds seed
"""

import sys
import time
import random
import json
from collections import Counter

import networkx as nx

from harness import (tau, has_k_disjoint_dijoins, rho, is_planar,
                     is_source_sink_connected, is_chordal_underlying)
from search import random_shape_dag

K = 3


def wl_hash(n, arcs):
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for (u, v) in arcs:
        if G.has_edge(u, v):
            G[u][v]['mult'] += 1
        else:
            G.add_edge(u, v, mult=1)
    return nx.weisfeiler_lehman_graph_hash(G, edge_attr='mult', iterations=4)


if __name__ == "__main__":
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    rng = random.Random(seed)
    seen = set()
    stats = Counter()
    t0 = time.time()
    next_report = 300
    while time.time() - t0 < seconds:
        g = random_shape_dag(2, 2, 8, rng)
        if g is None:
            continue
        n, arcs = g
        stats['generated'] += 1
        if tau(n, arcs) != K:
            continue
        if (is_source_sink_connected(n, arcs) or rho(n, arcs, K) < 4
                or is_planar(n, arcs) or is_chordal_underlying(n, arcs)):
            continue
        stats['region'] += 1
        h = wl_hash(n, arcs)
        if h in seen:
            stats['dup'] += 1
            continue
        seen.add(h)
        stats['distinct'] += 1
        if not has_k_disjoint_dijoins(n, arcs, K):
            stats['NONPACKING'] += 1
            print("NONPACKING:", n, arcs, flush=True)
        if time.time() - t0 > next_report:
            next_report += 300
            print(json.dumps(dict(stats)), flush=True)
    stats['wall_seconds'] = int(time.time() - t0)
    print("FINAL", json.dumps(dict(stats)), flush=True)
