"""Greedy destructive minimization with core jumps."""
import pickle, random, sys, time
from coremin import solve_core, NALL

def greedy(S, seed, log):
    rnd = random.Random(seed)
    S = set(S)
    passno = 0
    while True:
        passno += 1
        removed = 0
        order = sorted(S)
        rnd.shuffle(order)
        for v in order:
            if v not in S or len(S) <= 4:
                continue
            cand = S - {v}
            try:
                st, keep = solve_core(cand, seed=rnd.randrange(10**6), timeout=1800, tag=f'g{seed}')
            except Exception as ex:
                print(f'seed{seed}: err {ex}', file=log, flush=True)
                continue
            if st == 'UNSAT':
                S = keep
                removed += 1
                print(f'seed{seed} pass{passno}: del {v} -> {len(S)}', file=log, flush=True)
                pickle.dump(sorted(S), open(f'greedy_seed{seed}.pkl', 'wb'))
        print(f'seed{seed} pass{passno} done, removed {removed}, n={len(S)}', file=log, flush=True)
        if removed == 0:
            break
    print(f'seed{seed} FINAL {len(S)}', file=log, flush=True)
    pickle.dump(sorted(S), open(f'greedy_seed{seed}.pkl', 'wb'))

if __name__ == '__main__':
    seed = int(sys.argv[1])
    start = pickle.load(open(sys.argv[2], 'rb'))
    greedy(start, seed, sys.stdout)
