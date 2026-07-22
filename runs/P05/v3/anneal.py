"""Stage B: simulated annealing on graphs, minimizing min-triple-intersection
of longest paths. Seeds: 3-leg spider score-1 graphs / Stage-A near-misses /
random family members.

Usage: pypy3 anneal.py <n> <iters> <seed> [edges_python_literal_file]
"""
import ast
import random
import sys
import time

from lp_core import analyze, edges_to_adj, is_connected


def score_graph(n, edges):
    adj = edges_to_adj(n, edges)
    if not is_connected(n, adj):
        return 999, None
    try:
        res = analyze(n, adj, cap=1200)
    except RecursionError:
        return 999, None
    return res["score"], res


def random_seed_graph(n, rng):
    # random spanning tree + a few extra edges
    edges = set()
    verts = list(range(n))
    rng.shuffle(verts)
    for i in range(1, n):
        edges.add(tuple(sorted((verts[i], verts[rng.randrange(i)]))))
    for _ in range(n // 3):
        u, v = rng.sample(range(n), 2)
        edges.add(tuple(sorted((u, v))))
    return edges


def main():
    n = int(sys.argv[1]); iters = int(sys.argv[2]); seed = int(sys.argv[3])
    rng = random.Random(seed)
    if len(sys.argv) > 4:
        edges = set(tuple(sorted(e)) for e in ast.literal_eval(open(sys.argv[4]).read()))
        n = max(max(e) for e in edges) + 1
    else:
        edges = random_seed_graph(n, rng)
    cur, res = score_graph(n, list(edges))
    best = cur
    best_edges = set(edges)
    T = 2.0
    t0 = time.time()
    out = open("anneal_hits.log", "a")
    for it in range(iters):
        T = max(0.05, 2.0 * (1 - it / iters))
        new = set(edges)
        move = rng.random()
        if move < 0.45 or len(new) <= n - 1:
            u, v = rng.sample(range(n), 2)
            new.add(tuple(sorted((u, v))))
        elif move < 0.9:
            new.discard(rng.choice(sorted(new)))
        else:  # swap
            u, v = rng.sample(range(n), 2)
            new.add(tuple(sorted((u, v))))
            new.discard(rng.choice(sorted(new)))
        sc, res2 = score_graph(n, list(new))
        if cur <= 1:
            # plateau mode: random-walk among score<=1 graphs hunting a hole to 0
            accept = sc <= 1
        else:
            accept = sc <= cur or rng.random() < pow(2.718, -(sc - cur) / T)
        if accept:
            edges, cur = new, sc
            if sc < best:
                best, best_edges = sc, set(new)
                msg = "it=%d best=%d n=%d L=%s edges=%s" % (
                    it, best, n, res2["L"] if res2 else "?", sorted(new))
                print(msg); sys.stdout.flush()
                out.write(msg + "\n"); out.flush()
                if sc == 0:
                    with open("WITNESS_anneal.txt", "w") as f:
                        f.write(msg + "\nwitness=%s\n" % (res2["witness"],))
                    print("WITNESS FOUND"); return
        if it % 200 == 0:
            print("it=%d cur=%d best=%d T=%.2f elapsed=%.0fs" % (it, cur, best, T, time.time() - t0))
            sys.stdout.flush()
    print("DONE n=%d best=%d" % (n, best))


if __name__ == "__main__":
    main()
