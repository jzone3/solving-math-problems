"""Plateau random walk at fixed size starting from G509, within union pool.
Move: delete random v, add random w (pool neighbor), require still UNSAT.
Whenever UNSAT with size n, also try a pure deletion to n-1 via core jump.
"""
import pickle, random, sys, time
from coremin import solve_core, allpts, adj, NALL

def load_g509_indices():
    pts509 = pickle.load(open('g509.pkl', 'rb'))[0]
    idx = {p: i for i, p in enumerate(allpts)}
    return [idx[p] for p in pts509]

def is_unsat(S, rnd, tag):
    st, keep = solve_core(S, seed=rnd.randrange(10**6), timeout=1800, tag=tag)
    return st == 'UNSAT', keep

if __name__ == '__main__':
    seed = int(sys.argv[1])
    rnd = random.Random(seed)
    S = set(load_g509_indices())
    best = len(S)
    tag = f'pl{seed}'
    t0 = time.time()
    step = 0
    fails_since_improve = 0
    while True:
        step += 1
        # candidate add: pool vertex with >=3 neighbors in S
        outside = [w for w in range(NALL) if w not in S and len(adj[w] & S) >= 3]
        v = rnd.choice(sorted(S))
        w = rnd.choice(outside)
        cand = (S - {v}) | {w}
        ok, keep = is_unsat(cand, rnd, tag)
        if ok:
            S = set(keep) if keep and len(keep) <= len(cand) else cand
            if len(S) < best:
                best = len(S)
                pickle.dump(sorted(S), open(f'plateau_seed{seed}_best.pkl', 'wb'))
                print(f'seed{seed} step{step}: NEW BEST {best}', flush=True)
            # try pure deletions occasionally
            for u in rnd.sample(sorted(S), 8):
                ok2, keep2 = is_unsat(S - {u}, rnd, tag)
                if ok2:
                    S = set(keep2) if keep2 else S - {u}
                    best = min(best, len(S))
                    pickle.dump(sorted(S), open(f'plateau_seed{seed}_best.pkl', 'wb'))
                    print(f'seed{seed} step{step}: DELETION -> {len(S)} !!', flush=True)
        if step % 20 == 0:
            print(f'seed{seed} step{step}: n={len(S)} best={best} elapsed={int(time.time()-t0)}s', flush=True)
