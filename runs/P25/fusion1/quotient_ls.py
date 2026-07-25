#!/usr/bin/env python3
"""Two-worker Metropolis search for a 24-orbit sigma^6 cover."""
import math
import os
import random
import sys
import time

from cube_sigma_pos import digits, setup


def worker(seed, limit, outdir):
    random.seed(seed)
    orbits, _, qball, _ = setup(24)
    n = len(qball)
    covers = [set() for _ in range(n)]
    for p, cols in enumerate(qball):
        for j in cols:
            covers[j].add(p)
    selected = {0}
    selected.update(random.sample(range(1, n), 23))
    counts = [0] * n
    for j in selected:
        for p in covers[j]:
            counts[p] += 1
    best = sum(c > 0 for c in counts)
    started = time.monotonic()
    it = 0
    while time.monotonic() - started < limit:
        it += 1
        uncovered = [p for p, c in enumerate(counts) if not c]
        if not uncovered:
            words = sorted(w for j in selected for w in orbits[j])
            code = os.path.join(outdir, f"code_{seed}.txt")
            with open(code, "w") as f:
                for w in words:
                    f.write("".join(map(str, digits(w))) + "\n")
            print(f"FOUND seed={seed} iterations={it} words={len(words)} code={code}",
                  flush=True)
            return True
        p = random.choice(uncovered)
        entering = random.choice([j for j in qball[p] if j not in selected])
        leaving = random.choice(tuple(selected - {0}))
        oldscore = sum(c > 0 for c in counts)
        for q in covers[leaving]:
            counts[q] -= 1
        for q in covers[entering]:
            counts[q] += 1
        newscore = sum(c > 0 for c in counts)
        delta = newscore - oldscore
        temp = 0.35
        if delta >= 0 or random.random() < math.exp(delta / temp):
            selected.remove(leaving)
            selected.add(entering)
        else:
            for q in covers[entering]:
                counts[q] -= 1
            for q in covers[leaving]:
                counts[q] += 1
        score = sum(c > 0 for c in counts)
        if score > best:
            best = score
            if best >= n - 1:
                print(f"LS_BEST seed={seed} covered={best}/{n} iterations={it}",
                      flush=True)
    print(f"LS_TIMEOUT seed={seed} best={best}/{n} iterations={it}", flush=True)
    return False


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else os.getpid()
    limit = float(sys.argv[2]) if len(sys.argv) > 2 else 10800
    outdir = sys.argv[3] if len(sys.argv) > 3 else "logs/quotient_ls"
    os.makedirs(outdir, exist_ok=True)
    worker(seed, limit, outdir)
