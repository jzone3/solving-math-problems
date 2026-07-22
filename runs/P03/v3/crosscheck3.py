"""Cross-check exhaustive3-style filter pipeline against core.py on sampled digraph6."""
import random
import sys

from exhaustive2 import parse_digraph6
from core import (enumerate_dicuts, minimal_dicuts, tau as tau_f, rho3,
                  is_source_sink_connected, pack3_sat)

rng = random.Random(0)
sample = []
for line in sys.stdin:
    line = line.strip()
    if line and rng.random() < float(sys.argv[1]):
        sample.append(line)

n_full = 0
for line in sample:
    n, arcs = parse_digraph6(line)
    d = enumerate_dicuts(n, arcs)
    t = tau_f(d) if d else None
    passes = (t == 3 and rho3(n, arcs) >= 4
              and not is_source_sink_connected(n, arcs))
    if passes:
        n_full += 1
        assert pack3_sat(arcs, minimal_dicuts(d)), f"UNSAT?! {line}"
print(f"sampled={len(sample)} full_pass={n_full} (core.py pipeline) — "
      "compare with exhaustive3 counts on same slice")
