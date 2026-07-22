"""Sweep all pattern graphs on <=7 vertices (networkx atlas), all {K,I} type
assignments, hill-climb integer weights to maximize
score = l1^2 + l2^2 - 2m(1-1/w).  Exact spectra via quotient matrix.
"""
import itertools
import random
import sys
import networkx as nx
from common import blowup_score

random.seed(0)

MAX_N = int(sys.argv[1]) if len(sys.argv) > 1 else 240
KMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 7


def hill_climb(F_adj, types, k, restarts=6, iters=400):
    best = None
    for r in range(restarts):
        w = [random.randint(1, 12) for _ in range(k)]
        cur = blowup_score(F_adj, w, types)
        stall = 0
        for _ in range(iters):
            i = random.randrange(k)
            d = random.choice([-3, -1, -1, 1, 1, 3])
            if w[i] + d < 1 or sum(w) + d > MAX_N:
                continue
            w2 = w[:]
            w2[i] += d
            s2 = blowup_score(F_adj, w2, types)
            if s2 is not None and (cur is None or s2[0] > cur[0]):
                w, cur = w2, s2
                stall = 0
            else:
                stall += 1
                if stall > 120:
                    break
        if cur is not None and (best is None or cur[0] > best[0][0]):
            best = (cur, w[:])
    return best


KMIN = int(sys.argv[3]) if len(sys.argv) > 3 else 2
RESTARTS = int(sys.argv[4]) if len(sys.argv) > 4 else 6
ITERS = int(sys.argv[5]) if len(sys.argv) > 5 else 400


def work(job):
    F, types, k, edges = job
    best = hill_climb(F, list(types), k, restarts=RESTARTS, iters=ITERS)
    if best is None:
        return None
    (s, l1, l2, m, w), wts = best
    return (s, k, edges, types, wts, l1, l2, m, w)


def main():
    import multiprocessing as mp
    atlas = nx.graph_atlas_g()
    jobs = []
    for G in atlas:
        k = G.number_of_nodes()
        if k < KMIN or k > KMAX:
            continue
        F = [[0] * k for _ in range(k)]
        for u, v in G.edges():
            F[u][v] = F[v][u] = 1
        for types in itertools.product('KI', repeat=k):
            jobs.append((F, types, k, tuple(G.edges())))
    results = []
    count = 0
    with mp.Pool(8) as pool:
        for res in pool.imap_unordered(work, jobs, chunksize=16):
            if res is None:
                continue
            results.append(res)
            count += 1
            if count % 2000 == 0:
                print(f"...{count}/{len(jobs)} done", flush=True)
            if res[0] > 1e-9:
                print("VIOLATION?", res, flush=True)
    results.sort(key=lambda t: -t[0])
    print(f"\nswept {count} (pattern,type) combos, MAX_N={MAX_N}")
    print("top 20 scores:")
    for s, k, e, ty, wts, l1, l2, m, w in results[:20]:
        print(f"score={s:+.6f} k={k} edges={list(e)} types={''.join(ty)} "
              f"wts={wts} l1={l1:.4f} l2={l2:.4f} m={m} omega={w}")


if __name__ == "__main__":
    main()
