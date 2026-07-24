"""Cross-check the reduced size-4 dicut filter against direct enumeration."""

import random
import sys

sys.path.insert(0, ".")
from family_a import random_reduced
from harness import closed_sets, dicut_arcs
from enum_tau4 import reduced_dicut_ok


def brute(n, arcs):
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in arcs:
        indeg[v] += 1
        outdeg[u] += 1
    for mask in closed_sets(n, arcs):
        cut = dicut_arcs(mask, arcs)
        if len(cut) != 4:
            continue
        tails = {arcs[i][0] for i in cut}
        heads = {arcs[i][1] for i in cut}
        if len(tails) == 1:
            v = next(iter(tails))
            if indeg[v] == 0 and outdeg[v] == 4:
                continue
        if len(heads) == 1:
            v = next(iter(heads))
            if outdeg[v] == 0 and indeg[v] == 4:
                continue
        return False
    return True


rng = random.Random(404)
agree = 0
for _ in range(300):
    rec = random_reduced(rng, 2, 2, 4, 4)
    if rec is None:
        continue
    n, arcs = rec
    assert reduced_dicut_ok(n, arcs) == brute(n, arcs), arcs
    agree += 1
print(f"PASS tau=4 reduced-dicut filter: {agree}/{agree} agree")
