"""Random sample of the block construction at p=15, q=20 (5 blocks of 3
sources, each fully covering 3 private sinks; the 15 leftover arcs form 5
extra sinks). Each instance has 5 disjoint nontrivial tight 3-cuts."""
import random
import sys
import time
from bipsearch import min_dicuts_bip, packs3

P = 15


def main(seconds, seed):
    rng = random.Random(seed)
    base = []
    for b in range(5):
        blk = [3 * b, 3 * b + 1, 3 * b + 2]
        base += [blk, blk, blk]
    n = tau3 = 0
    t0 = time.time()
    seen = set()
    while time.time() - t0 < seconds:
        perm = list(range(P))
        rng.shuffle(perm)
        extra = sorted(tuple(sorted(perm[3 * i:3 * i + 3])) for i in range(5))
        key = tuple(extra)
        if key in seen:
            continue
        seen.add(key)
        if any(len(set(t)) < 3 for t in extra):
            continue
        sinks = base + [list(t) for t in extra]
        n += 1
        cuts, tau = min_dicuts_bip(P, sinks)
        if cuts is None or tau != 3:
            continue
        tau3 += 1
        if not packs3(sinks, cuts):
            print("UNSAT COUNTEREXAMPLE", sinks, flush=True)
            with open("counterexample.txt", "a") as f:
                f.write("BLOCK15 %r\n" % (sinks,))
        if n % 500 == 0:
            print(f"[block15] n={n} tau3={tau3}", flush=True)
    print(f"[block15] DONE n={n} tau3={tau3}", flush=True)


if __name__ == "__main__":
    main(float(sys.argv[1]), int(sys.argv[2]))
