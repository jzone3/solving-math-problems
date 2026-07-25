"""Small multi-rotation unions: is a union of >=3 rotated small disks of Parts'
base lattice already non-4-colorable at fewer than 509 vertices?

Parts' type-M construction unions exactly TWO copies, P and rho*P.  Nothing in
the literature unions three or more copies at several rotations, and a union
that is non-4-colorable while having fewer than 509 vertices would beat the
record outright (any minimisation afterwards can only help).

Scan: base points = +^n H^2 (n = 2, 3) inside a disk of radius r, copies rotated
by omega_{t} for t in a candidate list (plus the identity), sharing the origin.
Floats are used as a *prefilter* only -- any non-4-colorable hit is re-verified
in exact arithmetic before anything is claimed.
"""
import itertools
import math
import os
import pickle
import sys
from multiprocessing import Pool

import numpy as np

import lattice
from sat import color_cnf, solve

NMAX = int(os.environ.get('NVTX', '520'))       # reject unions >= this
TLIM = int(os.environ.get('TLIM', '900'))
TS = [int(x) for x in os.environ.get('TS', '1,2,3,4,5,6,7,8,9,10,12,15,16,'
                                           '19,21,25,28').split(',')]
NCOPY = int(os.environ.get('NCOPY', '3'))
NPROC = int(os.environ.get('NPROC', '6'))


def base(n, r):
    H2 = lattice.Hm(2)
    cur = {(0, 0, 0, 0)}
    for _ in range(n):
        cur = {lattice.add(p, q) for p in cur for q in H2}
    out = []
    for p in cur:
        z = lattice.to_complex(p)
        if abs(z) <= r + 1e-9:
            out.append(z)
    return out


def union(pts, rots):
    Z = []
    for w in rots:
        Z.extend(z * w for z in pts)
    Z = np.array(Z)
    keep, seen = [], set()
    for z in Z:
        k = (round(z.real, 9), round(z.imag, 9))
        if k in seen:
            continue
        seen.add(k)
        keep.append(z)
    return np.array(keep)


def edges_of(Z):
    n = len(Z)
    E = []
    for i0 in range(0, n, 512):
        D = np.abs(Z[i0:i0 + 512, None] - Z[None, :])
        ii, jj = np.nonzero(np.abs(D - 1.0) < 1e-9)
        for i, j in zip(ii, jj):
            i, j = i0 + int(i), int(j)
            if i < j:
                E.append((i, j))
    return E


def rot(t):
    """omega_t, or its conjugate (rotation by -angle) for negative t."""
    a = abs(t)
    w = complex((2 * a - 1) / (2 * a), math.sqrt(4 * a - 1) / (2 * a))
    return w.conjugate() if t < 0 else w


def job(arg):
    n, r, ts = arg
    pts = base(n, r)
    if not pts:
        return None
    rots = [1 + 0j] + [rot(t) for t in ts]
    Z = union(pts, rots)
    if len(Z) >= NMAX or len(Z) < 30:
        return None
    E = edges_of(Z)
    if len(E) < 2 * len(Z):
        return None
    nvars, cls = color_cnf(len(Z), E, 4)
    st, _ = solve(nvars, cls, timeout=TLIM)
    tag = f'n={n} r={r} ts={ts}: {len(Z)} vtx {len(E)} edges -> {st}'
    print(tag, flush=True)
    if st == 'UNSAT':
        with open(f'hit_{n}_{r}_{"_".join(map(str, ts))}.pkl', 'wb') as f:
            pickle.dump((n, r, ts, [(z.real, z.imag) for z in Z], E), f)
    return tag


def main():
    jobs = []
    radii = [float(x) for x in os.environ.get('RADII', '0.6,0.8,1.0,1.2')
             .split(',')]
    for n in [int(x) for x in os.environ.get('NS', '2,3').split(',')]:
        for r in radii:
            for ts in itertools.combinations(TS, NCOPY - 1):
                jobs.append((n, r, list(ts)))
    print(f'{len(jobs)} unions to test', flush=True)
    with Pool(NPROC) as p:
        for res in p.imap_unordered(job, jobs):
            if res and 'UNSAT' in res:
                print('*** HIT ***', res, flush=True)


if __name__ == '__main__':
    main()
