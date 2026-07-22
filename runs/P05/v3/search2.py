"""Stage A2: two-level block-tree cores.

Core = two 2-connected blocks B1, B2 glued at a cut vertex; three arms attached
at vertices spread across both blocks (at least one arm per block, none at the
glue vertex). This gives block trees of diameter >= 4 with three long arms
through distinct cut vertices — outside every proved class' comfort zone.

Usage: pypy3 search2.py <bmin> <bmax> <max_arm> <max_total> <seed> [max_jobs]
"""
import random
import sys
import time
from itertools import combinations, combinations_with_replacement

from lp_core import analyze, edges_to_adj
from families import default_arm_library, geng_graphs


def glue(b1, b2):
    """Glue vertex 0 of b2 onto vertex 0 of b1. Returns (n, edges)."""
    n1, e1 = b1
    n2, e2 = b2
    edges = list(e1)
    off = n1 - 1
    for (x, y) in e2:
        xx = 0 if x == 0 else x + off
        yy = 0 if y == 0 else y + off
        edges.append((xx, yy))
    return n1 + n2 - 1, edges


def assemble_core(core, attach, arms):
    nb, bedges = core
    edges = list(bedges)
    n = nb
    for v, (name, k, aedges) in zip(attach, arms):
        for (x, y) in aedges:
            xx = v if x == 0 else n + x - 1
            yy = v if y == 0 else n + y - 1
            edges.append((xx, yy))
        n += k - 1
    return n, edges


def main():
    bmin, bmax, max_arm, max_total, seed = (int(x) for x in sys.argv[1:6])
    max_jobs = int(sys.argv[6]) if len(sys.argv) > 6 else 4000000
    rng = random.Random(seed)
    lib = default_arm_library(max_size=max_arm)
    blocks = []
    for bn in range(bmin, bmax + 1):
        blocks.extend(geng_graphs(bn))
    print("blocks:", len(blocks), "arms:", len(lib))

    # random sampling of the (huge) configuration space
    def sample_job():
        i1 = rng.randrange(len(blocks)); i2 = rng.randrange(len(blocks))
        n1 = blocks[i1][0]; n2 = blocks[i2][0]
        nc = n1 + n2 - 1
        if nc + 3 > max_total:
            return None
        side1 = list(range(1, n1)); side2 = list(range(n1, nc))
        if rng.random() < 0.5:
            attach = tuple(rng.sample(side1, 2)) + (rng.choice(side2),)
        else:
            attach = (rng.choice(side1),) + tuple(rng.sample(side2, 2))
        arms = tuple(rng.randrange(len(lib)) for _ in range(3))
        sz = nc + sum(lib[a][1] - 1 for a in arms)
        if sz > max_total:
            return None
        return (i1, i2, attach, arms)

    jobs = []
    seen = set()
    tries = 0
    while len(jobs) < max_jobs and tries < max_jobs * 20:
        tries += 1
        j = sample_job()
        if j and j not in seen:
            seen.add(j); jobs.append(j)
    print("jobs:", len(jobs)); sys.stdout.flush()

    t0 = time.time(); best = 99
    hits = open("hits2.log", "a")
    for cnt, (i1, i2, attach, arm_idx) in enumerate(jobs):
        core = glue(blocks[i1], blocks[i2])
        arms = [lib[a] for a in arm_idx]
        n, edges = assemble_core(core, attach, arms)
        adj = edges_to_adj(n, edges)
        try:
            res = analyze(n, adj, cap=1500)
        except RecursionError:
            continue
        sc = res["score"]
        if sc is not None and sc < best:
            best = sc
        if sc == 0:
            msg = "WITNESS n=%d edges=%s L=%d triple=%s" % (n, edges, res["L"], res["witness"])
            print(msg); hits.write(msg + "\n"); hits.flush()
            with open("WITNESS2.txt", "w") as f:
                f.write(msg + "\n")
        elif sc is not None and sc <= 1:
            hits.write("nearmiss score=%d n=%d L=%d npaths=%d trunc=%s edges=%s\n" % (
                sc, n, res["L"], res["num_paths"], res["truncated"], edges))
            hits.flush()
        if cnt % 500 == 0:
            print("progress %d/%d best=%d elapsed=%.0fs" % (cnt, len(jobs), best, time.time() - t0))
            sys.stdout.flush()
    print("DONE jobs=%d best=%d elapsed=%.0fs" % (len(jobs), best, time.time() - t0))


if __name__ == "__main__":
    main()
