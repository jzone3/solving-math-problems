"""Random blow-up sampler for larger patterns k=8..10 (beyond atlas sweep):
random pattern graphs, random {K,I} types, hill-climbed integer weights.
"""
import random
import sys
import time
import multiprocessing as mp
from common import blowup_score

TIME_BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
MAX_N = 400


def hill_climb(F, types, k, rng, restarts=4, iters=500):
    best = None
    for _ in range(restarts):
        w = [rng.randint(1, 15) for _ in range(k)]
        cur = blowup_score(F, w, types)
        stall = 0
        for _ in range(iters):
            i = rng.randrange(k)
            d = rng.choice([-3, -1, -1, 1, 1, 3])
            if w[i] + d < 1 or sum(w) + d > MAX_N:
                continue
            w2 = w[:]
            w2[i] += d
            s2 = blowup_score(F, w2, types)
            if s2 is not None and (cur is None or s2[0] > cur[0]):
                w, cur, stall = w2, s2, 0
            else:
                stall += 1
                if stall > 150:
                    break
        if cur is not None and (best is None or cur[0] > best[0][0]):
            best = (cur, w[:])
    return best


def worker(seed):
    rng = random.Random(seed)
    t0 = time.time()
    top = []
    n_tried = 0
    while time.time() - t0 < TIME_BUDGET:
        k = rng.randint(8, 10)
        p = rng.choice([0.2, 0.35, 0.5, 0.65, 0.8])
        F = [[0] * k for _ in range(k)]
        for i in range(k):
            for j in range(i + 1, k):
                if rng.random() < p:
                    F[i][j] = F[j][i] = 1
        types = [rng.choice('KI') for _ in range(k)]
        best = hill_climb(F, types, k, rng)
        n_tried += 1
        if best is None:
            continue
        (s, l1, l2, m, w), wts = best
        top.append((s, k, tuple(tuple(r) for r in F), tuple(types), tuple(wts), l1, l2, m, w))
        top.sort(key=lambda t: -t[0])
        top = top[:5]
        if s > 1e-9:
            print("VIOLATION?", s, k, F, types, wts, flush=True)
    return n_tried, top


if __name__ == "__main__":
    with mp.Pool(8) as pool:
        res = pool.map(worker, range(8))
    total = sum(r[0] for r in res)
    alltop = sorted((t for r in res for t in r[1]), key=lambda t: -t[0])[:10]
    print(f"random blow-up sampler: {total} (pattern,type) combos, k=8..10, MAX_N={MAX_N}")
    for t in alltop:
        print(f"score={t[0]:+.6f} k={t[1]} types={''.join(t[3])} wts={t[4]} "
              f"l1={t[5]:.4f} l2={t[6]:.4f} m={t[7]} w={t[8]}")
