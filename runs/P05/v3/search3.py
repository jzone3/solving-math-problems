"""Stage A3: single larger central block (n=7-9), sampled, arms up to size 6.

Usage: pypy3 search3.py <bmin> <bmax> <max_arm> <max_total> <seed> <num_samples>
"""
import random
import sys
import time

from lp_core import analyze, edges_to_adj
from families import default_arm_library, geng_graphs, assemble


def main():
    bmin, bmax, max_arm, max_total, seed, num = (int(x) for x in sys.argv[1:7])
    rng = random.Random(seed)
    lib = default_arm_library(max_size=max_arm)
    blocks = []
    for bn in range(bmin, bmax + 1):
        blocks.extend(geng_graphs(bn))
    print("blocks:", len(blocks), "arms:", len(lib)); sys.stdout.flush()

    t0 = time.time(); best = 99
    hits = open("hits3.log", "a")
    seen = set()
    cnt = 0
    tries = 0
    while cnt < num and tries < num * 20:
        tries += 1
        bi = rng.randrange(len(blocks))
        nb, bedges = blocks[bi]
        attach = tuple(sorted(rng.sample(range(nb), 3)))
        arm_idx = tuple(rng.randrange(len(lib)) for _ in range(3))
        sz = nb + sum(lib[a][1] - 1 for a in arm_idx)
        if sz > max_total:
            continue
        key = (bi, attach, arm_idx)
        if key in seen:
            continue
        seen.add(key)
        cnt += 1
        arms = [lib[a] for a in arm_idx]
        n, adj, edges, desc = assemble((nb, bedges), attach, arms)
        try:
            res = analyze(n, adj, cap=1500)
        except RecursionError:
            continue
        sc = res["score"]
        if sc is not None and sc < best:
            best = sc
        if sc == 0:
            msg = "WITNESS n=%d block=%d %s attach=%s edges=%s L=%d triple=%s" % (
                n, nb, desc, attach, edges, res["L"], res["witness"])
            print(msg); hits.write(msg + "\n"); hits.flush()
            with open("WITNESS3.txt", "w") as f:
                f.write(msg + "\n")
        elif sc is not None and sc <= 1:
            hits.write("nearmiss score=%d n=%d block=%s %s attach=%s L=%d edges=%s\n" % (
                sc, n, bedges, desc, attach, res["L"], edges)); hits.flush()
        if cnt % 500 == 0:
            print("progress %d/%d best=%d elapsed=%.0fs" % (cnt, num, best, time.time() - t0))
            sys.stdout.flush()
    print("DONE cnt=%d best=%d elapsed=%.0fs" % (cnt, best, time.time() - t0))


if __name__ == "__main__":
    main()
