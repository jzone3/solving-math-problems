"""Vary the Minkowski *base*, not just the rotation.

Every type-M experiment so far (Parts' own, and the omega_t survey that found
t = 16 and t = 28) keeps his base B = (+)^4 H^2 fixed and only moves the
rotation.  The base is a free parameter too: (+)^n H^m for m = 1, 2 (m >= 3
leaves the lattice) and any n, clipped to a disk of radius r.  A different base
changes which pairs of the two rotated copies are at unit distance, i.e. exactly
the cross-edge structure that all the non-4-colorability comes from.

Scan: for each (m, n, r, t) build P u omega_t*P and ask kissat for a 4-colouring
with a short cap.  Floats are a prefilter only -- a hit is re-verified exactly
before anything is claimed.  Env: MS, NS, RS, TS, NMAX, CAP, PART/NPART.
"""
import itertools
import math
import os
import pickle
import subprocess
import time

import numpy as np

import lattice
from sat import color_cnf, write_cnf, KISSAT

MS = [int(x) for x in os.environ.get('MS', '1,2').split(',')]
NS = [int(x) for x in os.environ.get('NS', '3,4,5,6').split(',')]
RS = [float(x) for x in os.environ.get('RS', '1.5,2.0,2.5').split(',')]
TS = [int(x) for x in os.environ.get('TS', '2,3,4,5,6,7,8,9,10,12,13,16,'
                                           '21,25,28').split(',')]
NMAX = int(os.environ.get('NMAX', '9000'))
CAP = int(os.environ.get('CAP', '120'))
PART = int(os.environ.get('PART', '0'))
NPART = int(os.environ.get('NPART', '1'))


def base(m, n, r):
    Hm = lattice.Hm(m)
    lim = 144.0 * (r + 1e-9) ** 2
    cur = {(0, 0, 0, 0)}
    for k in range(n):
        slack = n - (k + 1)
        klim = 144.0 * (r + slack) ** 2 + 1e-6
        cur = {lattice.add(p, q) for p in cur for q in Hm
               if min(lattice.radius2_144(lattice.add(p, q))) <= klim}
    return sorted(p for p in cur if min(lattice.radius2_144(p)) <= lim)


def union_pts(P, w):
    z = np.array([lattice.to_complex(p) for p in P])
    Z = np.concatenate([z, z * w])
    keep, seen = [], set()
    for x in Z:
        k = (round(x.real, 9), round(x.imag, 9))
        if k not in seen:
            seen.add(k)
            keep.append(x)
    return np.array(keep)


def edges_of(Z):
    E = []
    for i0 in range(0, len(Z), 512):
        D = np.abs(Z[i0:i0 + 512, None] - Z[None, :])
        ii, jj = np.nonzero(np.abs(D - 1.0) < 1e-9)
        for i, j in zip(ii, jj):
            i, j = i0 + int(i), int(j)
            if i < j:
                E.append((i, j))
    return E


def colorable(n, E, tag):
    nvars, cls = color_cnf(n, E, 4)
    cnf = f'/tmp/bs_{tag}_{os.getpid()}.cnf'
    write_cnf(cnf, nvars, cls)
    try:
        r = subprocess.run([KISSAT, f'--time={CAP}', cnf],
                           capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return False
        if 's SATISFIABLE' in r.stdout:
            return True
        return None
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def main():
    jobs = [j for j in itertools.product(MS, NS, RS) ]
    for k, (m, n, r) in enumerate(jobs):
        if k % NPART != PART:
            continue
        P = base(m, n, r)
        if not P or len(P) > NMAX:
            print(f'm={m} n={n} r={r}: base {len(P)} skipped', flush=True)
            continue
        print(f'm={m} n={n} r={r}: base {len(P)} points', flush=True)
        for t in TS:
            w = lattice.omega_t_complex(t)
            Z = union_pts(P, w)
            if len(Z) > NMAX:
                continue
            E = edges_of(Z)
            if not E:
                continue
            t0 = time.time()
            st = colorable(len(Z), E, f'{PART}_{m}{n}{t}')
            tag = {True: '4-colorable', False: 'NOT 4-colorable',
                   None: 'unknown'}[st]
            print(f'  t={t}: {len(Z)} vtx {len(E)} edges -> {tag} '
                  f'({round(time.time()-t0,1)}s)', flush=True)
            if st is False:
                pickle.dump((m, n, r, t, P), open(
                    f'basehit_{m}_{n}_{r}_{t}.pkl', 'wb'))
                print('  *** HIT saved', flush=True)


if __name__ == '__main__':
    main()
