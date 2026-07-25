"""How many of the 126 cross edges does a non-4-colorable subset of W4 need?

The two halves of Parts' union are individually 4-colorable, so every witness is
forced through the cross edges, of which the whole pool has only 126 (the record
uses 54).  Relaxing the pool by *deleting* cross edges is sound in one
direction: if the pool with only the cross-edge set C left is 4-colorable, then
no witness whose cross edges lie inside C exists at all.  So greedily deleting
cross edges while the pool stays non-4-colorable yields a minimal C, i.e. a
structural lower bound on what a witness must use, and a much smaller
combinatorial object (126 elements) than the 5696-vertex search space.
"""
import os
import pickle
import random
import subprocess
import time

from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4x.pkl')
SEED = int(os.environ.get('SEED', '1'))
TCAP = int(os.environ.get('TCAP', '900'))
pts, E = pickle.load(open(POOL, 'rb'))
CROSS = [(u, v) for u, v in E if pts[u][0] != pts[v][0]]
SAME = [(u, v) for u, v in E if pts[u][0] == pts[v][0]]
rng = random.Random(SEED)


def colorable(edges, tag):
    vs = sorted({x for e in edges for x in e})
    remap = {x: i for i, x in enumerate(vs)}
    nvars, cls = color_cnf(len(vs), [(remap[u], remap[v]) for u, v in edges], 4)
    cnf = f'/tmp/cm_{tag}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, f'--time={TCAP}', cnf],
                           capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return False
        if 's SATISFIABLE' in r.stdout:
            return True
        return None                      # unknown within the cap
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def main():
    keep = list(CROSS)
    t0 = time.time()
    st = colorable(SAME + keep, f'{SEED}_0')
    print(f'pool with all {len(keep)} cross edges: '
          f'{"4-colorable" if st else "NOT 4-colorable"} '
          f'({round(time.time()-t0)}s)', flush=True)
    if st is not False:
        return
    # Parts-style 8-4-2-1 batching: each UNSAT check costs minutes, so try to
    # pay one check per eight deletions while that still succeeds.
    n = 0
    for bs in (8, 4, 2, 1):
        again = True
        while again:
            again = False
            order = [e for e in keep]
            rng.shuffle(order)
            for k in range(0, len(order), bs):
                batch = set(order[k:k + bs])
                if not batch <= set(keep):
                    continue
                trial = [x for x in keep if x not in batch]
                n += 1
                st = colorable(SAME + trial, f'{SEED}_{n}')
                if st is False:
                    keep = trial
                    again = bs > 1
                    pickle.dump(keep, open(f'crossmin_{SEED}.pkl', 'wb'))
                    print(f'  -{len(batch)} cross edges: {len(keep)} left '
                          f'({round(time.time()-t0)}s)', flush=True)
    print(f'MINIMAL cross set: {len(keep)} of {len(CROSS)} '
          f'({round(time.time()-t0)}s)', flush=True)


if __name__ == '__main__':
    main()
