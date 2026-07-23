"""Cross-check exact_pack_cegar against exact_pack and the PySAT harness."""
import json
import random
from enum_pypy import exact_pack, exact_pack_cegar, star_cuts
from harness import has_k_disjoint_dijoins, tau

cands = [json.loads(l) for l in open("/tmp/cand_test3.jsonl")]
random.seed(11)
for rec in random.sample(cands, 400):
    arcs = [tuple(a) for a in rec["arcs"]]
    a = exact_pack_cegar(14, arcs, star_cuts(14, arcs))
    b = exact_pack(14, arcs)
    assert a == b, rec
print("PASS cegar vs exact_pack: 400/400 n=14 candidates agree")

agree = npk = 0
random.seed(13)
while agree < 60:
    n = random.randrange(4, 9)
    arcs = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < 0.5:
                arcs.append((u, v))
    if not arcs:
        continue
    t = tau(n, arcs)
    if t is None or t < 3:
        continue
    a = exact_pack_cegar(n, arcs, star_cuts(n, arcs))
    b = has_k_disjoint_dijoins(n, arcs, 3)
    assert a == b, (n, arcs)
    agree += 1
    npk += (not b)
print(f"PASS cegar vs PySAT on {agree} random tau>=3 DAGs ({npk} non-packing)")
