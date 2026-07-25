"""Smallest central disk of W16 that is already non-4-colorable.

Greedy stalls at ~1924 on W16 and every UNSAT check at that size costs minutes,
so instead of shrinking the big witness, look for a *small* obstruction: sort
the pool by |z| and test prefixes.  A colorable prefix answers fast (SAT), so
the scan is cheap until it reaches the interesting radius.
"""
import os
import pickle
import subprocess
import sys
import time

import coremin
import lattice
from sat import color_cnf, write_cnf, KISSAT

TCAP = int(os.environ.get('TCAP', '300'))
PTS = coremin.allpts
om = lattice.omega_t_complex(16)
Z = [lattice.to_complex(q) * (om if t == 'B' else 1) for t, q in PTS]
order = sorted(range(len(PTS)), key=lambda v: abs(Z[v]))


def check(S, tag):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in coremin.E
          if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/ds_{tag}.cnf'
    write_cnf(cnf, nvars, cls)
    t0 = time.time()
    try:
        r = subprocess.run([KISSAT, f'--time={TCAP}', cnf],
                           capture_output=True, text=True)
    except Exception:
        return 'ERR', 0
    dt = round(time.time() - t0, 1)
    if 's UNSATISFIABLE' in r.stdout:
        return 'UNSAT', dt
    if 's SATISFIABLE' in r.stdout:
        return 'SAT', dt
    return 'UNKNOWN', dt


def main():
    for n in [int(x) for x in sys.argv[1:]] or [400, 600, 800, 1200, 1600,
                                                2400, 3200]:
        S = order[:n]
        st, dt = check(S, f'{os.getpid()}_{n}')
        ne = sum(1 for u, v in coremin.E if u in set(S) and v in set(S))
        print(f'n={n} r={abs(Z[order[n-1]]):.2f} edges={ne}: {st} ({dt}s)',
              flush=True)
        if st == 'UNSAT':
            pickle.dump(S, open(f'disk_{n}.pkl', 'wb'))
            return


if __name__ == '__main__':
    main()
