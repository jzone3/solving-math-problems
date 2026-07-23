"""Random sampling extension of the gadget-ring attack for k = 7..10 (exhaustive
enumeration infeasible). Random stub placements + random simple gadget graphs;
rings m = 3..6, straight/crossed; exact HC count with cutoff 4.

Usage: python3 gadget_sample.py k samples [seed]
"""
import sys, random, itertools
from collections import Counter
from hcutil import hc_count
from gadget_ring import ring

def rand_gadget(k, rng):
    l1, l2 = rng.choice(list(itertools.combinations_with_replacement(range(k), 2)))
    r1, r2 = rng.choice(list(itertools.combinations_with_replacement(range(k), 2)))
    stub_of = Counter([l1, l2, r1, r2])
    need = [4 - stub_of.get(v, 0) for v in range(k)]
    if any(x < 0 for x in need) or sum(need) % 2:
        return None
    for _ in range(300):
        stubs = [v for v in range(k) for _ in range(need[v])]
        rng.shuffle(stubs)
        edges = set()
        ok = True
        for i in range(0, len(stubs), 2):
            u, v = stubs[i], stubs[i + 1]
            if u == v or (min(u, v), max(u, v)) in edges:
                ok = False
                break
            edges.add((min(u, v), max(u, v)))
        if ok:
            return list(edges), l1, l2, r1, r2
    return None

if __name__ == "__main__":
    k, samples = int(sys.argv[1]), int(sys.argv[2])
    rng = random.Random(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    hits = 0
    for s in range(samples):
        if s % 20 == 0:
            print(f"progress s={s}", flush=True)
        g = rand_gadget(k, rng)
        if g is None:
            continue
        gedges, l1, l2, r1, r2 = g
        for crossed in (0, 1):
            for m in range(3, 7):
                edges = ring(k, m, gedges, l1, l2, r1, r2, crossed)
                c = hc_count(k * m, edges, cutoff=4, timeout=30)
                if c == 1:
                    simple = len(set(edges)) == len(edges)
                    with open("WITNESS.txt" if simple else "gadget_multi_hits.txt", "a") as f:
                        f.write(f"GADGET-SAMPLE k={k} m={m} simple={simple} gedges={gedges} "
                                f"stubs=({l1},{l2}|{r1},{r2}) crossed={crossed} edges={sorted(edges)}\n")
                    print(f"HIT k={k} m={m} simple={simple}", flush=True)
                    hits += 1
                if c == 0:
                    break
    print(f"k={k} samples={samples} hits={hits}", flush=True)
