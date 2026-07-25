"""Port/pattern decomposition of a type-M union (modern form of Parts' method).

W_t = L u omega_t S is glued by very few cross edges (66 at t=4, 66 at t=16), so
greedy growth never even crosses between the two copies and deletion has to keep
both halves whole.  The right object is the *port pattern set*:

  R_A = A-vertices incident to a cross edge, R_B likewise in the rotated copy,
  Pi_A = { c|R_A : c a proper 4-coloring of L },  Pi_B analogous.

L u omega S is 5-chromatic  <=>  for every pi_A in Pi_A, pi_B in Pi_B and every
color permutation sigma, some cross edge (u,v) has pi_A(u) = sigma(pi_B(v)).

Pi_A/Pi_B are computable by projected ALL-SAT (blocking clauses on the port
variables only) because |R| is small.  This script measures the ports and the
pattern sets of the record's own halves, which is the calibration needed before
searching for smaller halves.
"""
import itertools
import os
import pickle
import subprocess
import sys

import lattice as L
from sat import color_cnf, write_cnf, KISSAT

T = int(os.environ.get('T', '4'))


def cross_pairs(Apts, Bpts, t):
    e, s = L.squarefree_split(4 * t - 1)
    return [(i, j) for i, u in enumerate(Apts) for j, v in enumerate(Bpts)
            if L.cross_is_unit(u, v, t, (e, s))]


def within_edges(pts):
    return [(i, j) for i in range(len(pts)) for j in range(i + 1, len(pts))
            if L.is_unit(pts[i], pts[j])]


def patterns(pts, ports, tag, cap=200000):
    """Projected ALL-SAT: all colorings restricted to `ports`, mod color perm."""
    edges = within_edges(pts)
    nvars, cls = color_cnf(len(pts), edges, 4)
    cls = list(cls)
    out = set()
    cnf = f'/tmp/pt_{tag}.cnf'
    while len(out) < cap:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's SATISFIABLE' not in r.stdout:
            break
        pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
               for x in line[2:].split() if int(x) > 0}
        col = {}
        for i in range(len(pts)):
            for c in range(4):
                if 4 * i + c + 1 in pos:
                    col[i] = c
                    break
        pat = tuple(col[p] for p in ports)
        # canonical form under color permutation
        best = min(tuple(sigma[x] for x in pat)
                   for sigma in itertools.permutations(range(4)))
        out.add(best)
        # block this port pattern (all color permutations of it)
        for sigma in itertools.permutations(range(4)):
            cls.append([-(4 * p + sigma[pat[k]] + 1)
                        for k, p in enumerate(ports)])
    if os.path.exists(cnf):
        os.unlink(cnf)
    return out


def main():
    LS = pickle.load(open('LS.pkl', 'rb'))
    Lp = [tuple(x) for x in LS['L']]
    Sp = [tuple(x) for x in LS['S']]
    cp = cross_pairs(Lp, Sp, T)
    RA = sorted({i for i, _ in cp})
    RB = sorted({j for _, j in cp})
    print(f't={T}: |L|={len(Lp)} |S|={len(Sp)} cross={len(cp)} '
          f'ports A={len(RA)} B={len(RB)}', flush=True)
    pa = patterns(Lp, RA, f'A{T}')
    print(f'  |Pi_A| = {len(pa)} (canonical, mod color permutation)', flush=True)
    for p in sorted(pa)[:20]:
        print('   ', p, flush=True)
    pb = patterns(Sp, RB, f'B{T}')
    print(f'  |Pi_B| = {len(pb)}', flush=True)
    for p in sorted(pb)[:20]:
        print('   ', p, flush=True)
    pickle.dump({'RA': RA, 'RB': RB, 'cross': cp, 'PiA': pa, 'PiB': pb},
                open(f'ports_t{T}.pkl', 'wb'))


if __name__ == '__main__':
    main()
