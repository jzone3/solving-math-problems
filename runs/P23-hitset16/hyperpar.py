"""Parallel generator of small hyperedges (complements of 4-colorable sets).

D is a hyperedge of the pool iff pool \\ D is 4-colorable: every non-4-colorable
subset must intersect D.  Small hyperedges are exactly what Parts' minimal-graph
search needs and what all previous refinement loops in this run lacked.

Method per worker: fix a proper colouring of the frozen half (kissat), then run
incremental min-conflicts/tabu on the free candidates and read off one endpoint
per surviving conflicting edge.  Typical output |D| ~ 60-220 out of 2839, versus
~850 for greedy colour extension.

Env: POOL, FROZEN, FREEHALF, NPROC, NHYP (per worker), TABU, NOISE, OUT,
WHOLE, CHECK_SAMPLE.
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
WHOLE = os.environ.get('WHOLE', '0') == '1'
CHECK_SAMPLE = int(os.environ.get('CHECK_SAMPLE', '8'))

E, adj, PTS = coremin.E, coremin.adj, coremin.allpts
NP = len(PTS)
HALF = [0 if t == 'A' else 1 for t, _ in PTS]
SIDE_VERTICES = ([i for i, h in enumerate(HALF) if h == 0],
                 [i for i, h in enumerate(HALF) if h == 1])

fro = set(pickle.load(open(FROZEN, 'rb'))) if FROZEN else set()
if WHOLE:
    FIX = []
    CAND = list(range(NP))
else:
    FIX = sorted(v for v in fro if HALF[v] != FREEHALF)
    CAND = sorted(v for v in range(NP) if HALF[v] == FREEHALF)
CANDS = set(CAND)
NBR = {v: sorted(adj[v] & (CANDS | set(FIX))) for v in CAND}
UNIVERSE = set(range(NP))


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


def validate_hyperedge(D, col):
    """Assert D is sound: col colors every vertex outside D conflict-free."""
    assert set(col) == UNIVERSE, (
        f'colouring coverage failure: {len(col)} != {len(UNIVERSE)}')
    outside = UNIVERSE - set(D)
    assert all(v in col for v in outside)
    for u, v in E:
        if u not in D and v not in D:
            assert col[u] != col[v], f'conflict outside D: {(u, v)}'


def tabu_hyperedge(fixed_col, movable, rng, tabu=TABU, return_col=False):
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
    bad_edges = [(u, v) for u, v in E
                 if u in col and v in col and col[u] == col[v]]
    if any(u not in mv and v not in mv for u, v in bad_edges):
        return None
    # Turn the residual conflict graph into a vertex cover.  Choosing the
    # highest-conflict-degree endpoint first is much tighter than relying on
    # the arbitrary lattice edge order, while preserving soundness.
    conflict_adj = {}
    for u, v in bad_edges:
        conflict_adj.setdefault(u, set()).add(v)
        conflict_adj.setdefault(v, set()).add(u)
    D = set()
    while conflict_adj:
        v = max(conflict_adj, key=lambda x: len(conflict_adj[x]))
        D.add(v)
        for u in list(conflict_adj[v]):
            conflict_adj[u].discard(v)
            if not conflict_adj[u]:
                del conflict_adj[u]
        del conflict_adj[v]
    validate_hyperedge(D, col)
    return (D, col) if return_col else D


def worker(seed):
    rng = random.Random(seed)
    if WHOLE:
        ca = kissat_color(SIDE_VERTICES[0], f'a{seed}')
        cb = kissat_color(SIDE_VERTICES[1], f'b{seed}')
        assert ca and cb, 'single-copy base graph unexpectedly non-4-colorable'
        perm = list(range(4))
        rng.shuffle(perm)
        col0 = dict(ca)
        col0.update({v: perm[c] for v, c in cb.items()})
    else:
        col0 = kissat_color(FIX, f'w{seed}') if FIX else {}
    out = []
    for i in range(NHYP):
        result = tabu_hyperedge(col0, CAND, rng, return_col=True)
        D, col = result if result else (None, None)
        if D:
            validate_hyperedge(D, col)
            out.append(sorted(D))
            print(f'[{seed}] {i}: |D|={len(D)}', flush=True)
    return out


def main():
    t0 = time.time()
    old = pickle.load(open(OUT, 'rb')) if os.path.exists(OUT) else []
    all_hyps = list(old)
    with Pool(NPROC) as p:
        for result in p.imap_unordered(worker, list(range(1, NPROC + 1))):
            all_hyps.extend(result)
            pickle.dump(all_hyps, open(OUT, 'wb'))
            print(f'checkpointed {len(all_hyps)} hyperedges -> {OUT}',
                  flush=True)
    hyps = all_hyps[len(old):]
    merged = all_hyps
    if CHECK_SAMPLE and merged:
        rng = random.Random(917263)
        sample = rng.sample(merged, min(CHECK_SAMPLE, len(merged)))
        for i, D in enumerate(sample):
            st, _ = kissat_color(sorted(UNIVERSE - set(D)), f'bankcheck_{i}')
            assert st, f'banked hyperedge {i} failed SAT check'
    sz = sorted(len(d) for d in hyps)
    print(f'{len(hyps)} hyperedges, min {sz[0]} median {sz[len(sz)//2]} '
          f'max {sz[-1]}, {round(time.time()-t0)}s -> {OUT} '
          f'(total {len(old)+len(hyps)})', flush=True)


if __name__ == '__main__':
    main()
