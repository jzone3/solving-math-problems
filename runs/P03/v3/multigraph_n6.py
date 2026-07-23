"""Close the parallel-arc gap at n=6 for tau=3.

Reduction (documented in NOTES): a MINIMAL tau=3 counterexample has all arc
multiplicities <= 2 — if an arc bundle has >= 3 copies, color 3 of them with the 3
colors; every dicut containing the bundle is then hit by all colors, and the remaining
dicuts are exactly the dicuts of the contraction D/(uv), which must itself be a (smaller)
counterexample. Since contraction reduces n, exhausting mult<=2 at n=6 together with the
already-exhausted simple n<=6 slice rules out ALL n<=6 counterexamples (any n=6
counterexample contracts down to a minimal one on <= 6 vertices).

At n=6, ACZ forces rho(3,D,1) = 4 exactly, i.e. every vertex has
(outdeg-indeg) mod 3 == 2 (multiplicity-weighted). Skeleton must be weakly connected,
not source-sink connected (multiplicity-invariant), with every skeleton dicut >= 2
(a size-1 skeleton dicut has weight <= 2 < 3). 53 such skeletons (n6_skeletons.d6).

For each skeleton, enumerate all x in {1,2}^m; keep tau(x)=3 and all-imbalances==2 mod 3;
SAT-check 3-dijoin packing of the expanded multigraph.
"""
import sys
from itertools import product

from exhaustive2 import parse_digraph6
from core import enumerate_dicuts, minimal_dicuts, tau as tauf, pack3_sat, rho3

total_x = kept = sat_checked = cex = 0
for line in open("n6_skeletons.d6"):
    line = line.strip()
    if not line:
        continue
    n, arcs = parse_digraph6(line)
    m = len(arcs)
    d = enumerate_dicuts(n, arcs)  # arc-index sets, multiplicity applied per index
    for x in product((1, 2), repeat=m):
        total_x += 1
        # tau with multiplicities
        t = min(sum(x[i] for i in cut) for cut in d)
        if t != 3:
            continue
        # all vertex imbalances == 2 mod 3
        imb = [0] * n
        for i, (u, v) in enumerate(arcs):
            imb[u] += x[i]
            imb[v] -= x[i]
        if any(b % 3 != 2 for b in imb):
            continue
        kept += 1
        # expand multigraph and SAT-check
        earcs = []
        for i, a in enumerate(arcs):
            earcs.extend([a] * x[i])
        ed = enumerate_dicuts(n, earcs)
        assert tauf(ed) == 3 and rho3(n, earcs) == 4
        md = minimal_dicuts(ed)
        sat_checked += 1
        if not pack3_sat(earcs, md):
            cex += 1
            print(f"COUNTEREXAMPLE skeleton={line} mult={x}", flush=True)
print(f"skeletons=53 mult_patterns={total_x} full_pass={kept} "
      f"sat_checked={sat_checked} counterexamples={cex}")
