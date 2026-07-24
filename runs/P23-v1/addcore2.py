"""Double-addition greedy: for unit-adjacent candidate pairs (w1,w2), start from
G509 + {w1,w2} (511 vertices, UNSAT superset) and greedily delete with drat-trim
core jumps. Reaching <= 508 = new record. Pairs ranked by combined record degree.
Usage: POOL=pool_mink.pkl addcore2.py <nworkers> <worker_id> [maxpairs]
"""
import pickle, random, sys
from coremin import solve_core

g509 = set(range(509))
pairs = pickle.load(open('cand_pairs.pkl', 'rb'))

def unsat(S, tag):
    st, keep = solve_core(S, seed=random.randrange(10**6), timeout=1800, tag=tag)
    return (st == 'UNSAT'), keep

if __name__ == '__main__':
    nw, wid = int(sys.argv[1]), int(sys.argv[2])
    maxp = int(sys.argv[3]) if len(sys.argv) > 3 else len(pairs)
    tag = f'a2_{wid}'
    rnd = random.Random(wid)
    for k, (w1, w2) in enumerate(pairs[:maxp]):
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
                        pickle.dump(sorted(S), open(f'FOUND508a2_{w1}_{w2}.pkl', 'wb'))
                    break
        print(f'pair {k}/{maxp} ({w1},{w2}): bottom {len(S)}', flush=True)
