"""Cross-check enum_pypy.exact_pack against harness SAT on candidates and on
random small DAGs (where non-packing may genuinely occur for tau<3 reasons the
pipeline never sees, this still validates the coloring logic)."""
import json
import random
from enum_pypy import exact_pack
from harness import has_k_disjoint_dijoins, tau

cands = [json.loads(l) for l in open("/tmp/cand_test3.jsonl")]
random.seed(7)
sample = random.sample(cands, 300)
for rec in sample:
    arcs = [tuple(a) for a in rec["arcs"]]
    assert exact_pack(14, arcs) == has_k_disjoint_dijoins(14, arcs, 3), rec
print("PASS exact_pack crosscheck on 300 n=14 candidates")

# random DAGs, various sizes, including some that do NOT pack
agree = npk = 0
for it in range(300):
    n = random.randrange(4, 9)
    arcs = []
    for u in range(n):
        for v in range(u + 1, n):
            for _ in range(random.randrange(3)):
                if random.random() < 0.5:
                    arcs.append((u, v))
    if not arcs:
        continue
    t = tau(n, arcs)
    if t is None or t == 0:
        continue
    a = exact_pack(n, arcs) if t >= 3 else None
    if t >= 3:
        b = has_k_disjoint_dijoins(n, arcs, 3)
        assert a == b, (n, arcs, t, a, b)
        agree += 1
        if not b:
            npk += 1
print(f"PASS random-DAG crosscheck: {agree} agree ({npk} non-packing)")
