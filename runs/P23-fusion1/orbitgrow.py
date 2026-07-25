"""Constructive orbit filling (Parts-style) instead of deletion.

Deletion from the raw type-M union is provably weak: on W_4, which contains
Parts' 509, both 8-4-2-1 greedy and iterated DRAT core jumping stall around
~1850 vertices.  Parts does not delete -- he *fills orbits*: he keeps the
configuration symmetric under the base group and adds whole orbits until the
union stops being 4-colorable.

This implements that in the orbit space of W_t = P_t u omega_t P_t under the
verified automorphisms <tau3, tau4, conj33, neg> (orbit sizes 1/2/4/8):

  grow:   while 4-colorable, add the orbit whose vertices are most often
          "blocked" (see all four colors) under the solver's own colorings --
          column generation lifted from vertices to orbits;
  shrink: delete whole orbits while it stays non-4-colorable, then individual
          vertices (symmetry is only a search bias, the witness need not be
          symmetric).

Usage: POOL=wt_16.pkl python3 orbitgrow.py <seed> [<tag>]
"""
import os
import pickle
import random
import subprocess
import sys
import time

import coremin
from sat import color_cnf, write_cnf, KISSAT
from symgreedy import orbits

E, adj = coremin.E, coremin.adj
NP = len(coremin.allpts)
SEEDPTS = int(os.environ.get('SEEDPTS', '40'))
CAP = int(os.environ.get('CAP', '4000'))


def solve(S, seed, timeout=1800):
    """(True, None) if non-4-colorable, else (False, coloring dict)."""
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/og_{os.getpid()}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=timeout)
        if 's UNSATISFIABLE' in r.stdout:
            return True, None
        pos = {int(t) for line in r.stdout.splitlines() if line.startswith('v ')
               for t in line[2:].split() if int(t) > 0}
        col = {v: c for i, v in enumerate(S) for c in range(4)
               if 4 * i + c + 1 in pos}
        return False, col
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def grow(orbs, rnd, tag):
    """Fill orbits until the configuration is no longer 4-colorable."""
    oid = {}
    for i, o in enumerate(orbs):
        for v in o:
            oid[v] = i
    # seed: a random connected clump, closed under orbits
    start = rnd.randrange(NP)
    S, frontier = set(), [start]
    while frontier and len(S) < SEEDPTS:
        v = frontier.pop()
        for w in orbs[oid[v]]:
            S.add(w)
        frontier.extend(sorted(adj[v])[:4])
    used = {oid[v] for v in S}
    acc = {}
    t0 = time.time()
    while True:
        ok, col = solve(S, rnd.randrange(10 ** 6))
        if ok:
            print(f'{tag} grew to {len(S)} non-4-colorable '
                  f'({round(time.time()-t0)}s)', flush=True)
            return S
        if len(S) > CAP:
            print(f'{tag} cap hit at {len(S)}', flush=True)
            return None
        best, bs = None, -1.0
        for i, o in enumerate(orbs):
            if i in used:
                continue
            sc = acc.get(i, 0.0)
            touch = 0
            for w in o:
                nb = adj[w] & S
                if len(nb) < 3:
                    continue
                k = len({col[u] for u in nb})
                sc += 1.0 if k == 4 else 0.25 * k
                touch += 1
            if not touch:
                continue
            sc = sc / len(o) + 0.01 * touch
            if sc > bs:
                best, bs = i, sc
        if best is None:
            print(f'{tag} stuck at {len(S)}', flush=True)
            return None
        acc[best] = acc.get(best, 0.0) + 1.0
        used.add(best)
        S |= set(orbs[best])
        if len(S) % 200 < 8:
            print(f'{tag} ... {len(S)} vertices', flush=True)


def shrink(S, orbs, rnd, tag):
    oid = {}
    for i, o in enumerate(orbs):
        for v in o:
            oid[v] = i
    changed = True
    while changed:
        changed = False
        for i in rnd.sample(sorted({oid[v] for v in S}),
                            len({oid[v] for v in S})):
            g = [v for v in orbs[i] if v in S]
            if g and solve(S - set(g), rnd.randrange(10 ** 6))[0]:
                S -= set(g)
                changed = True
        for v in sorted(S, key=lambda v: len(adj[v] & S)):
            if v in S and solve(S - {v}, rnd.randrange(10 ** 6))[0]:
                S.discard(v)
                changed = True
        print(f'{tag} shrink pass -> {len(S)}', flush=True)
    return S


def main():
    seed = int(sys.argv[1])
    tag = sys.argv[2] if len(sys.argv) > 2 else f'og{seed}'
    rnd = random.Random(seed)
    orbs = orbits(coremin.allpts)
    print(f'{tag}: {len(orbs)} orbits', flush=True)
    best = None
    for rep in range(100):
        S = grow(orbs, rnd, f'{tag}r{rep}')
        if S is None:
            continue
        S = shrink(set(S), orbs, rnd, f'{tag}r{rep}')
        st, keep = coremin.solve_core(S, seed=rnd.randrange(10 ** 6), tag=tag)
        if st == 'UNSAT' and len(keep) < len(S):
            S = set(keep)
        print(f'{tag}r{rep} RESULT {len(S)}', flush=True)
        if best is None or len(S) < len(best):
            best = set(S)
            pickle.dump(sorted(best), open(f'og_{tag}.pkl', 'wb'))
            print(f'{tag} *** best {len(best)}', flush=True)


if __name__ == '__main__':
    main()
