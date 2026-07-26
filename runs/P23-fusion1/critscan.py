"""Vertex-criticality scan: which single deletions leave the graph 5-chromatic.

A SAT answer (the graph minus v is 4-colorable) means v is critical; UNSAT means
v is redundant and the graph shrinks for free.  Env: G, PART, NPART, CAP.
"""
import os
import pickle
import subprocess
import time

from sat import color_cnf, write_cnf, KISSAT

G = os.environ.get('G', 'h510e.pkl')
PART = int(os.environ.get('PART', '0'))
NPART = int(os.environ.get('NPART', '1'))
CAP = int(os.environ.get('CAP', '600'))
pts, E = pickle.load(open(G, 'rb'))
N = len(pts)


def colorable(keep, tag):
    rm = {x: i for i, x in enumerate(sorted(keep))}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nvars, cls = color_cnf(len(rm), E2, 4)
    cnf = f'/tmp/cs_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, f'--time={CAP}', cnf],
                           capture_output=True, text=True)
        if 's SATISFIABLE' in r.stdout:
            return True
        if 's UNSATISFIABLE' in r.stdout:
            return False
        return None
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


t0 = time.time()
red = 0
for v in range(N):
    if v % NPART != PART:
        continue
    st = colorable(set(range(N)) - {v}, f'{PART}_{v}')
    if st is False:
        red += 1
        print(f'*** REDUNDANT {v}: graph shrinks to {N-1}', flush=True)
        pickle.dump(sorted(set(range(N)) - {v}), open(f'red_{v}.pkl', 'wb'))
    elif st is None:
        print(f'  {v}: unknown within {CAP}s', flush=True)
    if v % 50 == 0:
        print(f'  ..{v}/{N}, {red} redundant, {round(time.time()-t0)}s',
              flush=True)
print(f'done: {red} redundant vertices', flush=True)
