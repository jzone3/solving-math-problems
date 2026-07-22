"""V1 annealed edge-flip search for a Bollobas-Nikiforov counterexample.

Maximizes ratio = (l1^2+l2^2) / (2m(1-1/omega)); a counterexample has ratio > 1.
Runs many restarts across n and edge density, in parallel worker processes.
Each worker appends its best-found states to results.jsonl.

Usage: python3 anneal.py <seed> <hours> [nmin nmax]
"""
import json
import math
import os
import random
import sys
import time
from multiprocessing import Process

from bn_core import evaluate, adj_to_g6

RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.jsonl")
EPS = 1e-6  # score must exceed this to count as a counterexample (guards float noise)


def random_graph(n, p, rng):
    adj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
    return adj


def flip(adj, i, j):
    adj[i] ^= 1 << j
    adj[j] ^= 1 << i


def objective(ratio, l1, l2, mode):
    if mode == "l2bias":
        # small bonus for a large second eigenvalue: violations (if any) need two
        # big eigenvalues, while the ratio-1 attractor (complete multipartite,
        # lambda2 = 0) is a proved-safe class. Bonus keeps the search away from it.
        return ratio + 0.03 * (l2 / l1 if l1 > 0 else 0.0)
    return ratio


def anneal_once(n, p, steps, rng, t0=0.02, t1=0.0005, mode="ratio"):
    adj = random_graph(n, p, rng)
    score, ratio, l1, l2, m, w = evaluate(n, adj)
    cur = objective(ratio, l1, l2, mode)
    best = (ratio, adj_to_g6(n, adj), score, l1, l2, m, w)
    for step in range(steps):
        T = t0 * (t1 / t0) ** (step / steps)
        nflips = 1 if rng.random() < 0.8 else 2
        pairs = []
        for _ in range(nflips):
            i = rng.randrange(n)
            j = rng.randrange(n)
            while j == i:
                j = rng.randrange(n)
            pairs.append((i, j))
            flip(adj, i, j)
        score, ratio, l1, l2, m, w = evaluate(n, adj)
        obj = objective(ratio, l1, l2, mode)
        if obj >= cur or rng.random() < math.exp((obj - cur) / T):
            cur = obj
            if ratio > best[0]:
                best = (ratio, adj_to_g6(n, adj), score, l1, l2, m, w)
                if score > EPS:
                    return best, True
        else:
            for i, j in reversed(pairs):
                flip(adj, i, j)
    return best, False


def worker(wid, seed, hours, nmin, nmax):
    rng = random.Random(seed * 10007 + wid)
    deadline = time.time() + hours * 3600
    while time.time() < deadline:
        n = rng.randrange(nmin, nmax + 1)
        p = rng.uniform(0.15, 0.9)
        steps = rng.choice([3000, 8000, 20000])
        mode = rng.choice(["ratio", "l2bias", "l2bias"])
        t_start = time.time()
        best, found = anneal_once(n, p, steps, rng, mode=mode)
        rec = {
            "worker": wid, "n": n, "p0": round(p, 3), "steps": steps, "mode": mode,
            "ratio": best[0], "score": best[2], "l1": best[3], "l2": best[4],
            "m": best[5], "omega": best[6], "g6": best[1],
            "secs": round(time.time() - t_start, 1), "counterexample": found,
        }
        with open(RESULTS, "a") as f:
            f.write(json.dumps(rec) + "\n")
        if found:
            print("COUNTEREXAMPLE FOUND", rec, flush=True)
            return


def main():
    seed = int(sys.argv[1])
    hours = float(sys.argv[2])
    nmin = int(sys.argv[3]) if len(sys.argv) > 3 else 15
    nmax = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    nproc = os.cpu_count() or 4
    procs = [Process(target=worker, args=(w, seed, hours, nmin, nmax)) for w in range(nproc)]
    for pr in procs:
        pr.start()
    for pr in procs:
        pr.join()


if __name__ == "__main__":
    main()
