"""Iterated randomized DRAT core extraction ("core jumping").

Calibration finding: Parts' 8-4-2-1 greedy floors near ~1900 on W_4 — the pool
that provably contains a 509-vertex solution — so plain deletion greedy is ~3.5x
off the optimum and its floor on any new pool (e.g. W_16) carries no negative
information.  This tries the other lever: a DRAT proof only touches part of the
formula, so the UNSAT core of a set is often far smaller than any single
deletion sequence reaches.  Re-extracting the core with fresh solver seeds and
randomized clause order jumps between very different cores.

Usage: POOL=wt_4.pkl python3 corejump.py <seed> <start.pkl> [<tag>]
"""
import os
import pickle
import random
import sys
import time

from coremin import solve_core

STALL = int(os.environ.get('STALL', '40'))


def main():
    seed = int(sys.argv[1])
    S = set(pickle.load(open(sys.argv[2], 'rb')))
    tag = sys.argv[3] if len(sys.argv) > 3 else f'cj{seed}'
    rnd = random.Random(seed)
    best = set(S)
    print(f'{tag} start {len(S)}', flush=True)
    t0 = time.time()
    since = 0
    it = 0
    while since < STALL:
        it += 1
        st, keep = solve_core(S, seed=rnd.randrange(10 ** 6), timeout=3600, tag=tag)
        if st != 'UNSAT':
            print(f'{tag} it{it}: {st}', flush=True)
            S = set(best)
            since += 1
            continue
        if len(keep) < len(best):
            best = set(keep)
            since = 0
            pickle.dump(sorted(best), open(f'cj_{tag}.pkl', 'wb'))
            print(f'{tag} it{it}: core -> {len(best)} ({round(time.time()-t0)}s)',
                  flush=True)
        else:
            since += 1
        # perturb: drop a few random vertices from the incumbent and re-core
        S = set(best)
        for v in rnd.sample(sorted(S), min(3, len(S))):
            S.discard(v)
    print(f'{tag} FINAL {len(best)}', flush=True)


if __name__ == '__main__':
    main()
