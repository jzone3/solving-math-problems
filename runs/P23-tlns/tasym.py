"""Asymmetric-radius scan for the smallest obstructing translated universe.

E45 of runs/P23-fusion1 found rA = 1.6 / rB = 1.3 to be the smallest
non-4-colorable pair over its base set; this run's base (3 Minkowski layers of
the 30 unit vectors, `lattice.build_base`) is slightly different, so the frontier
has to be re-measured here.  A smaller universe means a lower greedy floor and a
cheaper exact search, so this is the cheapest available win.

Every universe is built exactly (tuniv.build) before it is tested.

Env: PAIRS, TIME.
"""
import os
import pickle

from check import is_colorable
import tuniv

PAIRS = os.environ.get('PAIRS', '1.6:1.3,1.6:1.25,1.6:1.2,1.55:1.3,1.5:1.3,'
                                '1.6:1.35,1.7:1.2,1.7:1.1,1.65:1.25')

if __name__ == '__main__':
    for spec in PAIRS.split(','):
        ra, rb = (float(x) for x in spec.split(':'))
        pts, E, tags = tuniv.build(ra, rb)
        col = is_colorable(len(pts), E, tag=f'asym{ra}_{rb}')
        print(f'rA={ra} rB={rb}: {len(pts)} vtx, {len(E)} exact edges -> '
              f'{"SAT" if col else "UNSAT"}', flush=True)
        if not col:
            out = f'tuniv_{ra}_{rb}.pkl'
            pickle.dump((pts, E), open(out, 'wb'))
            pickle.dump(tags, open(out.replace('.pkl', '') + '_tags.pkl', 'wb'))
