"""Stage-A sweep for P05 V3: central 2-connected block + 3 rooted arms.

Usage: pypy3 search.py <block_nmin> <block_nmax> <max_arm_size> <max_total_n> [seed]

Logs near-misses (score <= 1) to hits.log; a score-0 witness is a counterexample
candidate and is dumped in full for solutions/P05/verify.py.
"""
import random
import sys
import time
from itertools import combinations, combinations_with_replacement

from lp_core import analyze, longest_path, is_connected
from families import default_arm_library, geng_graphs, assemble


def main():
    nmin, nmax, max_arm, max_total = (int(x) for x in sys.argv[1:5])
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    random.seed(seed)
    lib = default_arm_library(max_size=max_arm)
    print("arm library size:", len(lib))
    blocks = []
    for bn in range(nmin, nmax + 1):
        blocks.extend(geng_graphs(bn))
    print("blocks:", len(blocks))

    jobs = []
    for bi, (nb, bedges) in enumerate(blocks):
        for attach in combinations(range(nb), 3):
            for arms in combinations_with_replacement(range(len(lib)), 3):
                sz = nb + sum(lib[a][1] - 1 for a in arms)
                if sz > max_total:
                    continue
                jobs.append((bi, attach, arms))
    random.shuffle(jobs)
    print("jobs:", len(jobs))
    sys.stdout.flush()

    t0 = time.time()
    best_seen = 99
    hits = open("hits.log", "a")
    for cnt, (bi, attach, arm_idx) in enumerate(jobs):
        nb, bedges = blocks[bi]
        arms = [lib[a] for a in arm_idx]
        n, adj, edges, desc = assemble((nb, bedges), attach, arms)
        try:
            res = analyze(n, adj, cap=1500)
        except RecursionError:
            continue
        sc = res["score"]
        if sc is not None and sc < best_seen:
            best_seen = sc
        if sc == 0:
            msg = "WITNESS n=%d block=%d %s attach=%s edges=%s L=%d triple=%s" % (
                n, nb, desc, attach, edges, res["L"], res["witness"])
            print(msg); hits.write(msg + "\n"); hits.flush()
            with open("WITNESS.txt", "w") as f:
                f.write(msg + "\n")
        elif sc is not None and sc <= 1:
            msg = "nearmiss score=%d n=%d block=%d(%s) %s attach=%s L=%d npaths=%d trunc=%s edges=%s" % (
                sc, n, nb, bedges, desc, attach, res["L"], res["num_paths"], res["truncated"], edges)
            hits.write(msg + "\n"); hits.flush()
        if cnt % 500 == 0:
            print("progress %d/%d best=%d elapsed=%.0fs" % (cnt, len(jobs), best_seen, time.time() - t0))
            sys.stdout.flush()
    print("DONE jobs=%d best=%d elapsed=%.0fs" % (len(jobs), best_seen, time.time() - t0))


if __name__ == "__main__":
    main()
