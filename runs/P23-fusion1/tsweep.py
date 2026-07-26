"""Find the translation whose universe obstructs at the smallest radius.

Parts' placement needs radius 2.0 (4033 vertices) to stop being 4-colorable.
Two translated placements already do it in less: score-63 at 1.8 and score-65 at
**1.6** (2917 vertices). Smaller universe means cheaper exact search and, more
to the point, is where a witness smaller than 509 would have to live -- so this
sweeps many translations downward in radius.

Env: IN, START, STEP, RADII, TIME, OUT.
"""
import os
import pickle

import tradius as TR

IN = os.environ.get('IN', 'tscan2.pkl')
START = int(os.environ.get('START', '0'))
STEP = int(os.environ.get('STEP', '1'))
RADII = [float(x) for x in os.environ.get('RADII', '1.6,1.5,1.4,1.3').split(',')]
OUT = os.environ.get('OUT', f'tsweep_{START}.pkl')

cands = pickle.load(open(IN, 'rb'))
best = []
for k in range(START, len(cands), STEP):
    n, T = cands[k]
    hit = None
    for rad in RADII:
        pts, E = TR.build(T, rad)
        st = TR.decide(pts, E)
        print(f'#{k} score {n} r={rad}: {len(pts)} vtx {len(E)} edges -> {st}',
              flush=True)
        if st != 'UNSAT':
            break
        hit = (rad, len(pts), len(E))
        pickle.dump((pts, E), open(f'tu_{k}_{rad}.pkl', 'wb'))
    if hit:
        best.append((hit[0], k, n, hit[1], hit[2]))
        best.sort()
        pickle.dump(best, open(OUT, 'wb'))
        print(f'  --> #{k} obstructs down to radius {hit[0]} '
              f'({hit[1]} vertices)', flush=True)
