"""Transplant the record's combinatorial structure onto the new rotation omega_16.

The 509 record is L374 union rho*S136 with rho = omega_4.  omega_16 is the only
other rotation (with omega_28) for which the type-M union W_t is non-4-colorable.
This asks the direct question: do the *same lattice sets* L and S, re-joined with
omega_16 instead of omega_4, still give a 5-chromatic graph?  If yes we get a
509-vertex graph at a brand-new rotation whose cross-edge kinds differ, i.e. a
different graph of the same size and a fresh starting point for reduction.

Also tries orbit-closures / small perturbations of L and S at t = 16, 28.
"""
import itertools
import pickle
import subprocess
import sys

import lattice as L
from sat import color_cnf, write_cnf, KISSAT

LS = pickle.load(open('LS.pkl', 'rb'))
Lset = [tuple(x) for x in LS['L']]
Sset = [tuple(x) for x in LS['S']]


def build(Lpts, Spts, t):
    """Exact graph on Lpts (base copy) + omega_t * Spts."""
    e, s = L.squarefree_split(4 * t - 1)
    pts = [('A', p) for p in Lpts] + [('B', p) for p in Spts]
    nL = len(Lpts)
    edges = []
    for i in range(nL):
        for j in range(i + 1, nL):
            if L.is_unit(Lpts[i], Lpts[j]):
                edges.append((i, j))
    for i in range(len(Spts)):
        for j in range(i + 1, len(Spts)):
            if L.is_unit(Spts[i], Spts[j]):
                edges.append((nL + i, nL + j))
    cross = 0
    for i, u in enumerate(Lpts):
        for j, v in enumerate(Spts):
            if L.cross_is_unit(u, v, t, (e, s)):
                edges.append((i, nL + j))
                cross += 1
    return pts, edges, cross


def is_5chrom(n, edges, tag):
    nvars, cls = color_cnf(n, edges, 4)
    cnf = f'/tmp/tp_{tag}.cnf'
    write_cnf(cnf, nvars, cls)
    r = subprocess.run([KISSAT, '-q', cnf], capture_output=True, text=True)
    return 's UNSATISFIABLE' in r.stdout


def main():
    for t in (4, 16, 28):
        pts, edges, cross = build(Lset, Sset, t)
        ok = is_5chrom(len(pts), edges, f't{t}')
        print(f't={t}: {len(pts)} vtx, {len(edges)} edges ({cross} cross) -> '
              f'{"NON-4-COLORABLE" if ok else "4-colorable"}', flush=True)


if __name__ == '__main__':
    main()
