"""Count n=6 skeleton candidates for the multigraph (mult<=2) tau=3 exhaustion.

A minimal tau=3 counterexample has arc multiplicities <= 2 (contract a >=3-bundle:
rainbow-color the bundle; remaining dicuts are exactly the dicuts of the contraction,
which is a smaller counterexample). At n=6, ACZ forces rho=4 exactly, i.e. EVERY vertex
has (outdeg-indeg) mod 3 == 2 (multiplicity-weighted). Skeleton requirements
(multiplicity-independent): weakly connected, NOT source-sink connected (reachability is
skeleton-invariant), and every skeleton dicut has size >= 2 (a size-1 dicut caps at
weight 2 < 3), and at least one dicut exists.
Reads digraph6 on stdin, writes qualifying skeleton lines to stdout, stats to stderr.
"""
import sys

from exhaustive2 import parse_digraph6
from core import (enumerate_dicuts, tau as tauf, is_source_sink_connected)

tot = kept = 0
mdist = {}
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    tot += 1
    n, arcs = parse_digraph6(line)
    d = enumerate_dicuts(n, arcs)
    if not d:
        continue
    t = tauf(d)
    if t < 2:
        continue
    if is_source_sink_connected(n, arcs):
        continue
    kept += 1
    m = len(arcs)
    mdist[m] = mdist.get(m, 0) + 1
    print(line)
print(f"total={tot} kept={kept} m_dist={sorted(mdist.items())}", file=sys.stderr)
