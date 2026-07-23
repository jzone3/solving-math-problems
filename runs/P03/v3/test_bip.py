"""Validate bip.py dicut enumeration & packing vs core.py on random bipartite digraphs."""
import random

from bip import all_min_dicuts, pack3, gen_random
from core import enumerate_dicuts, minimal_dicuts, tau as tauf, pack3_sat

rng = random.Random(5)
agree = 0
for trial in range(120):
    n4 = 3 * rng.randint(0, 1)  # narcs = 4*n4 + 3*n3 divisible by 3 => n4 multiple of 3
    n3 = rng.randint(4, 6)  # keep nT = (4*n4+3*n3)/3 >= 4 so degree-4 sources fit
    nbrs, nT = gen_random(rng, n4, n3)
    nS = len(nbrs)
    arcs = [(i, nS + t) for i, nb in enumerate(nbrs) for t in nb]
    n = nS + nT
    t1, md1 = all_min_dicuts(nbrs, nT)
    d2 = enumerate_dicuts(n, arcs)
    t2 = tauf(d2) if d2 else None
    md2 = minimal_dicuts(d2) if d2 else []
    assert t1 == t2, (nbrs, t1, t2)
    assert set(md1) == set(md2), (nbrs, md1, md2)
    if t1 is not None and t1 >= 3:
        p1 = pack3(nbrs, md1)
        p2 = pack3_sat(arcs, md2)
        assert p1 == p2
    agree += 1
print(f"PASS: bip vs core agreement on {agree} random bipartite instances")
