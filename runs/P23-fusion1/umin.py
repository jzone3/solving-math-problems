"""Batched greedy minimisation (Parts' 8-4-2-1 scheme) of an explicit vertex set."""
import os, pickle, random, subprocess, sys, time
import numpy as np
import mfield
from sat import color_cnf, write_cnf, KISSAT

SEED = int(os.environ.get('SEED', '1'))
OUT = os.environ.get('OUT', f'umin_{SEED}.pkl')
F = mfield.MField([3, 5, 11])
h = mfield.load_vtx(F, '/home/ubuntu/p23heule/vtx/510.vtx')
p = mfield.load_vtx(F, '/home/ubuntu/solving-math-problems/solutions/P23/v509e2442.vtx')
pts = sorted(set(h) | set(p), key=lambda q: (F.to_float(q[0]), F.to_float(q[1])))
N = len(pts)
z = np.array([complex(F.to_float(x), F.to_float(y)) for x, y in pts])
E = []
for i in range(N):
    for k in np.nonzero(np.abs(np.abs(z[i+1:] - z[i]) - 1.0) < 1e-7)[0]:
        j = i + 1 + int(k)
        dx = F.sub(pts[i][0], pts[j][0]); dy = F.sub(pts[i][1], pts[j][1])
        if F.add(F.mul(dx, dx), F.mul(dy, dy)) == F.ONE:
            E.append((i, j))
print(f'union {N} vertices, {len(E)} edges', flush=True)
rng = random.Random(SEED)

def colorable(vs, tag):
    vs = sorted(vs); rm = {x: i for i, x in enumerate(vs)}
    E2 = [(rm[u], rm[v]) for u, v in E if u in rm and v in rm]
    nv, cls = color_cnf(len(vs), E2, 4)
    cnf = f'/tmp/um_{tag}_{os.getpid()}.cnf'; write_cnf(cnf, nv, cls)
    try:
        r = subprocess.run([KISSAT, '--time=900', cnf], capture_output=True, text=True)
        if 's SATISFIABLE' in r.stdout: return True
        if 's UNSATISFIABLE' in r.stdout: return False
        return None
    finally:
        if os.path.exists(cnf): os.unlink(cnf)

cur = set(range(N))
assert colorable(cur, 'start') is False
t0 = time.time(); n = 0
for bs in (8, 4, 2, 1):
    again = True
    while again:
        again = False
        order = sorted(cur); rng.shuffle(order)
        for k in range(0, len(order), bs):
            batch = set(order[k:k+bs])
            if not batch <= cur: continue
            n += 1
            if colorable(cur - batch, f'{SEED}_{n}') is False:
                cur -= batch
                again = bs > 1
                print(f'  |cur|={len(cur)} (bs={bs}, {round(time.time()-t0)}s)', flush=True)
                pickle.dump(sorted(cur), open(OUT, 'wb'))
print(f'FLOOR {len(cur)}', flush=True)
