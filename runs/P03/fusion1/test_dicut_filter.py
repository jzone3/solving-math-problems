"""Cross-check enum_pypy.dicut_structure_ok against harness brute force."""
import json
import random
from enum_pypy import dicut_structure_ok
from harness import closed_sets, dicut_arcs

def brute(n, arcs):
    ind = [0] * n
    outd = [0] * n
    for (u, v) in arcs:
        ind[v] += 1
        outd[u] += 1
    for U in closed_sets(n, arcs):
        cut = dicut_arcs(U, arcs)
        if len(cut) != 3:
            continue
        size = bin(U).count("1")
        if size == 1 and ind[U.bit_length() - 1] == 0:
            continue
        if size == n - 1:
            v = (((1 << n) - 1) ^ U).bit_length() - 1
            if outd[v] == 0:
                continue
        return False
    return True

random.seed(1)
cands = [json.loads(l) for l in open("/tmp/cand_test.jsonl")][:200]
cands += random.sample([json.loads(l) for l in open("/tmp/cand_test.jsonl")],
                       300)
agree = 0
for rec in cands:
    arcs = [tuple(a) for a in rec["arcs"]]
    n = 14
    assert dicut_structure_ok(n, arcs) == brute(n, arcs), rec
    agree += 1
print(f"PASS dicut filter crosscheck: {agree}/{agree} agree")
