"""Find pool vertices that every non-4-colorable subset must contain.

If pool - {v} is 4-colorable then v lies in *every* witness inside the pool,
including any hypothetical sub-509 one.  A SAT answer is cheap (~2 s) while
UNSAT costs minutes, so scan with a short cap: a hit is conclusive, a timeout
merely uninformative.

Env: POOL, PART/NPART (shard), CAP, OUT.
"""
import os
import pickle
import subprocess
import sys
import time

from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4d.pkl')
PART = int(os.environ.get('PART', '0'))
NPART = int(os.environ.get('NPART', '1'))
CAP = int(os.environ.get('CAP', '25'))
OUT = os.environ.get('OUT', f'forced_{PART}.txt')
pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)


def colorable(drop, tag):
    S = [v for v in range(N) if v not in drop]
    rm = {x: i for i, x in enumerate(S)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/fs_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, f'--time={CAP}', cnf],
                           capture_output=True, text=True)
        return 's SATISFIABLE' in r.stdout
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def main():
    deg = {}
    for u, v in E:
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    order = sorted(range(N), key=lambda v: -deg.get(v, 0))
    hits = 0
    t0 = time.time()
    with open(OUT, 'a') as f:
        for k, v in enumerate(order):
            if k % NPART != PART:
                continue
            if colorable({v}, f'{PART}_{v}'):
                hits += 1
                f.write(f'{v}\n')
                f.flush()
                print(f'FORCED {v} (deg {deg.get(v, 0)}) '
                      f'[{hits} so far, {round(time.time()-t0)}s]', flush=True)
            if k % 200 == 0:
                print(f'  ..{k}/{N} scanned, {hits} forced, '
                      f'{round(time.time()-t0)}s', flush=True)
    print(f'done: {hits} forced vertices', flush=True)


if __name__ == '__main__':
    sys.exit(main())
