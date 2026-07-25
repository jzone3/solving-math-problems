"""Minimise vertices inside a *cross-edge-restricted* pool.

`crossmin.py` shows the pool stays non-4-colorable with far fewer than its 126
cross edges.  Deleting an edge is not legal in a unit-distance graph, but the
vertex-level version is: forbid one endpoint of every cross edge we want gone.
Each choice of endpoints (a vertex cover of the discarded cross edges) yields a
different legal sub-pool, and each sub-pool has its own minimisation floor -- a
structurally motivated diversification of a search that otherwise always lands
on the same 509.

Env: POOL, CSET (crossmin output), SEED, OUT.
"""
import json
import os
import pickle
import random
import subprocess
import time

from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4x.pkl')
CSET = os.environ.get('CSET', 'crossmin_15.pkl')
SEED = int(os.environ.get('SEED', '1'))
TCAP = int(os.environ.get('TCAP', '900'))
pts, E = pickle.load(open(POOL, 'rb'))
CROSS = [(u, v) for u, v in E if pts[u][0] != pts[v][0]]
keep = {tuple(e) for e in pickle.load(open(CSET, 'rb'))}
drop = [e for e in CROSS if tuple(e) not in keep]
rng = random.Random(SEED)


def colorable(S, tag):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/cr_{tag}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, f'--time={TCAP}', cnf],
                           capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return False
        if 's SATISFIABLE' in r.stdout:
            return True
        return None
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def cover(edges):
    """Random-ish vertex cover of the cross edges to be discarded."""
    left = list(edges)
    out = set()
    while left:
        u, v = left[rng.randrange(len(left))]
        x = u if rng.random() < 0.5 else v
        out.add(x)
        left = [(a, b) for a, b in left if a != x and b != x]
    return out


def main():
    print(f'{len(CROSS)} cross edges, keeping {len(keep)}, '
          f'discarding {len(drop)}', flush=True)
    for trial in range(100):
        cv = cover(drop)
        S = [v for v in range(len(pts)) if v not in cv]
        t0 = time.time()
        st = colorable(S, f'{SEED}_{trial}')
        print(f'  cover {len(cv)} vertices -> pool {len(S)}: '
              f'{"4-colorable" if st else "NOT 4-colorable"} '
              f'({round(time.time()-t0)}s)', flush=True)
        if st is False:
            pickle.dump(S, open(f'crossrest_{SEED}_{trial}.pkl', 'wb'))
            print('  -> usable restricted pool saved', flush=True)
            continue
        # pool minus the cover is 4-colorable, so the cover is a hyperedge:
        # every non-4-colorable subset of the pool must contain one of its
        # vertices.  Shrink it greedily -- each test is a fast SAT answer --
        # and bank it; these are by far the smallest clauses found so far.
        cv = set(cv)
        for x in sorted(cv):
            trial_cv = cv - {x}
            keep_pool = [v for v in range(len(pts)) if v not in trial_cv]
            if colorable(keep_pool, f'{SEED}_{trial}_s{x}') is True:
                cv = trial_cv
        print(f'  -> hyperedge of {len(cv)} vertices', flush=True)
        with open(os.environ.get('BANK', 'crossbank.jsonl'), 'a') as f:
            f.write(json.dumps(sorted(cv)) + chr(10))


if __name__ == '__main__':
    main()
