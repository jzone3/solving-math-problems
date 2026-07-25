"""Parallel generator of small hyperedges (complements of 4-colorable sets).

D is a hyperedge of the pool iff pool \\ D is 4-colorable: every non-4-colorable
subset must intersect D.  Small hyperedges are exactly what Parts' minimal-graph
search needs and what all previous refinement loops in this run lacked.

Method per worker: fix a proper colouring of the frozen half (kissat), then run
incremental min-conflicts/tabu on the free candidates and read off one endpoint
per surviving conflicting edge.  Typical output |D| ~ 60-220 out of 2839, versus
~850 for greedy colour extension.

Env: POOL, FROZEN, FREEHALF, NPROC, NHYP (per worker), TABU, NOISE, OUT.
"""
import os
import pickle
import random
import subprocess
import time
from multiprocessing import Pool

import coremin
from sat import color_cnf, write_cnf, KISSAT

POOL = os.environ.get('POOL', 'w4x.pkl')
FROZEN = os.environ.get('FROZEN', 'rec_w4x.pkl')
FREEHALF = int(os.environ.get('FREEHALF', '1'))
NPROC = int(os.environ.get('NPROC', '5'))
NHYP = int(os.environ.get('NHYP', '20'))
TABU = int(os.environ.get('TABU', '4000000'))
NOISE = float(os.environ.get('NOISE', '0.02'))
OUT = os.environ.get('OUT', 'hyp_w4x.pkl')
SHRINK = int(os.environ.get('SHRINK', '0'))

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]

LNSFIX = os.environ.get('LNSFIX', '')        # exact large-neighbourhood search
LNSK = int(os.environ.get('LNSK', '450'))    # how many of them to freeze
LNSSEED = int(os.environ.get('LNSSEED', '1'))

fro = set(pickle.load(open(FROZEN, 'rb'))) if FROZEN and not LNSFIX else set()
if LNSFIX:
    # Freeze a random K-subset of a known witness and let the hitting set pick
    # the rest from the *whole* pool: outer UNSAT then proves no <= 508-vertex
    # non-4-colorable set of the pool contains that core, which is a complete
    # statement about a neighbourhood of the record rather than a search floor.
    base = sorted(pickle.load(open(LNSFIX, 'rb')))
    r = random.Random(LNSSEED)
    FIX = sorted(r.sample(base, min(LNSK, len(base))))
    fixs = set(FIX)
    CAND = sorted(v for v in range(NP) if v not in fixs)
    # Restrict the free side to the pool around the hole we punched in the
    # witness: with the whole 5.2k pool free the outer solver can never be
    # driven to UNSAT, whereas a few hundred candidates make each neighbourhood
    # decidable, which is what makes this LNS *exact* rather than heuristic.
    LNSHOPS = int(os.environ.get('LNSHOPS', '0'))
    if LNSHOPS:
        near = set(base) - fixs
        for _ in range(LNSHOPS):
            near |= {u for v in near for u in adj[v]}
        CAND = sorted(near - fixs)
    # A minimum witness is vertex-critical, hence of min degree >= 4, so any
    # candidate that cannot reach degree 4 inside FIX u CAND is useless; the
    # prune is a fixpoint because dropping one candidate can starve another.
    LNSDEG = int(os.environ.get('LNSDEG', '4'))
    if LNSDEG:
        live = set(CAND)
        while True:
            drop = {v for v in live if len(adj[v] & (live | fixs)) < LNSDEG}
            if not drop:
                break
            live -= drop
        CAND = sorted(live)
elif FROZEN:
    FIX = sorted(v for v in fro if HALF[v] != FREEHALF)
    CAND = sorted(v for v in range(NP) if HALF[v] == FREEHALF)
else:
    FIX = []
    CAND = list(range(NP))
CANDS = set(CAND)
NBR = {v: sorted(adj[v] & (CANDS | set(FIX))) for v in CAND}


def kissat_color(S, tag):
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    nvars, cls = color_cnf(len(S), E2, 4)
    cnf = f'/tmp/hp_{tag}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, cnf], capture_output=True, text=True)
        if 's UNSATISFIABLE' in r.stdout:
            return None
        pos = {int(x) for line in r.stdout.splitlines() if line.startswith('v ')
               for x in line[2:].split() if int(x) > 0}
        return {v: c for i, v in enumerate(S) for c in range(4)
                if 4 * i + c + 1 in pos}
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def tabu_hyperedge(fixed_col, movable, rng, tabu=TABU):
    col = dict(fixed_col)
    mv = set(movable)
    for v in movable:
        col[v] = rng.randrange(4)
    cnt = {v: [0, 0, 0, 0] for v in movable}
    for v in movable:
        for u in NBR[v]:
            if u in col:
                cnt[v][col[u]] += 1
    bad = {v for v in movable if cnt[v][col[v]]}
    best = None
    for it in range(tabu):
        if not bad:
            break
        v = rng.choice(tuple(bad))
        old = col[v]
        c = (rng.randrange(4) if rng.random() < NOISE
             else min(range(4), key=lambda k: (cnt[v][k], rng.random())))
        if c == old:
            continue
        col[v] = c
        for u in NBR[v]:
            if u in mv:
                cnt[u][old] -= 1
                cnt[u][c] += 1
                (bad.add if cnt[u][col[u]] else bad.discard)(u)
        (bad.add if cnt[v][c] else bad.discard)(v)
        if it % 200000 == 0:
            cur = sum(cnt[u][col[u]] for u in movable)
            if best is None or cur < best[0]:
                best = (cur, dict(col))
    cur = sum(cnt[u][col[u]] for u in movable)
    if best is None or cur < best[0]:
        best = (cur, dict(col))
    col = best[1]
    D = set()
    for u, v in E:
        if u in col and v in col and col[u] == col[v]:
            if u in D or v in D:
                continue
            if u in mv:
                D.add(u)
            elif v in mv:
                D.add(v)
            else:
                return None
    return D


def shrink(D, rng, tag):
    """Remove vertices from D while pool \\ D stays 4-colorable (exact, kissat).

    Tabu only certifies that pool \\ D is colorable; it says nothing about
    minimality, and minimal hyperedges are the strong constraints.  Each test is
    a satisfiable colouring instance, so kissat answers quickly.
    """
    D = list(D)
    rng.shuffle(D)
    keep = set(D)
    for v in D:
        trial = keep - {v}
        rest = [u for u in CAND if u not in trial]
        if kissat_color(FIX + rest, tag) is not None:
            keep = trial
    return keep


def worker(seed):
    rng = random.Random(seed)
    col0 = kissat_color(FIX, f'w{seed}') if FIX else {}
    out = []
    for i in range(NHYP):
        D = tabu_hyperedge(col0, CAND, rng)
        if not D:
            continue
        n0 = len(D)
        if SHRINK:
            D = shrink(D, rng, f's{seed}')
        out.append(sorted(D))
        print(f'[{seed}] {i}: |D|={n0}' +
              (f' -> {len(D)} after shrink' if SHRINK else ''), flush=True)
    return out


def main():
    t0 = time.time()
    with Pool(NPROC) as p:
        res = p.map(worker, list(range(1, NPROC + 1)))
    hyps = [d for r in res for d in r]
    old = []
    if os.path.exists(OUT):
        old = pickle.load(open(OUT, 'rb'))
    pickle.dump(old + hyps, open(OUT, 'wb'))
    sz = sorted(len(d) for d in hyps)
    print(f'{len(hyps)} hyperedges, min {sz[0]} median {sz[len(sz)//2]} '
          f'max {sz[-1]}, {round(time.time()-t0)}s -> {OUT} '
          f'(total {len(old)+len(hyps)})', flush=True)


if __name__ == '__main__':
    main()
