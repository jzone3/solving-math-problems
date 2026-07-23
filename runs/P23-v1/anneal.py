"""Simulated annealing over a candidate pool: maintain a non-4-colorable
induced subgraph S, minimize |S|. Moves: swap (del+add), pure delete, pure add.
Uphill (size-increasing) moves accepted with Metropolis probability to escape
the 509 basin. Core jumps applied on every UNSAT check.
"""
import math, os, pickle, random, sys, time
from coremin import solve_core, adj, NALL

def is_unsat(S, rnd, tag):
    st, keep = solve_core(S, seed=rnd.randrange(10**6), timeout=1800, tag=tag)
    return st == 'UNSAT', keep

if __name__ == '__main__':
    seed = int(sys.argv[1])
    start_file = sys.argv[2]
    rnd = random.Random(seed)
    start = pickle.load(open(start_file, 'rb'))
    if isinstance(start, tuple):
        start = start[0]
    S = set(start)
    best = len(S)
    bestS = set(S)
    tag = f'an{seed}'
    T0, Tmin, alpha = 3.0, 0.3, 0.999
    T = T0
    t0 = time.time()
    step = 0
    while True:
        step += 1
        T = max(Tmin, T * alpha)
        r = rnd.random()
        Ss = sorted(S)
        if r < 0.5:
            # swap: delete 1..2, add 1
            k = 1 if rnd.random() < 0.7 else 2
            dels = rnd.sample(Ss, k)
            base = S - set(dels)
            outside = [w for w in range(NALL) if w not in S and len(adj[w] & base) >= 4]
            if not outside:
                continue
            cand = base | {rnd.choice(outside)}
        elif r < 0.8:
            cand = S - {rnd.choice(Ss)}
        else:
            outside = [w for w in range(NALL) if w not in S and len(adj[w] & S) >= 4]
            if not outside:
                continue
            cand = S | set(rnd.sample(outside, min(2, len(outside))))
        d = len(cand) - len(S)
        if d > 0 and rnd.random() > math.exp(-d / T):
            continue
        ok, keep = is_unsat(cand, rnd, tag)
        if not ok:
            continue
        S = set(keep) if keep and len(keep) <= len(cand) else set(cand)
        if len(S) < best:
            best = len(S)
            bestS = set(S)
            pickle.dump(sorted(bestS), open(f'anneal_seed{seed}_best.pkl', 'wb'))
            print(f'seed{seed} step{step}: NEW BEST {best}', flush=True)
            if best < 509:
                print(f'seed{seed}: *** BELOW 509 ***', flush=True)
        if step % 20 == 0:
            print(f'seed{seed} step{step}: n={len(S)} best={best} T={T:.2f} '
                  f'elapsed={int(time.time() - t0)}s', flush=True)
