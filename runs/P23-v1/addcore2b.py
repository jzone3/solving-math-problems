"""Continuation of addcore2: pairs [400:1597].
Usage: POOL=pool_mink.pkl addcore2b.py <nworkers> <worker_id>
"""
import pickle, random, sys
from coremin import solve_core

g509 = set(range(509))
pairs = pickle.load(open('cand_pairs.pkl', 'rb'))[400:]

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return (st == 'UNSAT'), keep

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    tag = f'b2_{wid}'
    rnd = random.Random(1000 + wid)
    for k, (w1, w2) in enumerate(pairs):
        if k % nw != wid:
            continue
        S = g509 | {int(w1), int(w2)}
        improved = True
        while improved:
            improved = False
            order = sorted(S)
            rnd.shuffle(order)
            for u in order:
                if u not in S:
                    continue
                ok, keep = unsat(S - {u}, tag)
                if ok:
                    S = set(keep) if keep and len(keep) <= len(S) - 1 else S - {u}
                    improved = True
                    if len(S) <= 508:
                        print(f'!!! <=508 FOUND: pair ({w1},{w2}) -> {len(S)}', flush=True)
                        pickle.dump(sorted(S), open(f'FOUND508b2_{w1}_{w2}.pkl', 'wb'))
                    break
        print(f'pair {k}/{len(pairs)} ({w1},{w2}): bottom {len(S)}', flush=True)
    print(f'worker{wid}: ALL DONE', flush=True)
