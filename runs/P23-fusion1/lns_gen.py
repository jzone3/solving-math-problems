"""Pool-agnostic LNS (ruin & recreate) for any (points, edges) pool pickle.

Same engine as lns508.py but (a) the ruin is a BFS ball in the graph instead of
a spatial ball, so no coordinates are needed, and (b) the start set and target
come from the command line, so it can minimize any non-4-colorable subgraph
(e.g. the W_16 cores from the new type-M rotation on runs/P23-parts-rho).

Env: POOL, START (pkl with a list of vertex indices), SEED, ITERS, KMIN, KMAX,
     GLIM (repair budget per pass), SLACK.
"""
import os, pickle, random, subprocess, time
from collections import deque

POOL = os.environ.get('POOL', 'wt_16.pkl')
os.environ['POOL'] = POOL
START = os.environ.get('START', '')
SEED = int(os.environ.get('SEED', '0'))
ITERS = int(os.environ.get('ITERS', '1000'))
KMIN = int(os.environ.get('KMIN', '10'))
KMAX = int(os.environ.get('KMAX', '60'))
GLIM = int(os.environ.get('GLIM', '400'))
SLACK = int(os.environ.get('SLACK', '80'))

import coremin
from sat import color_cnf, write_cnf, KISSAT

E, adj, NP = coremin.E, coremin.adj, len(coremin.allpts)
rng = random.Random(SEED)


def cnf_unsat(S, seed, timeout=1800):
    """Proof-free non-4-colorability test."""
    S = sorted(S)
    remap = {x: i for i, x in enumerate(S)}
    E2 = [(remap[u], remap[v]) for u, v in E if u in remap and v in remap]
    tri = coremin.find_triangle(S)
    tri2 = tuple(remap[x] for x in tri) if tri else None
    nvars, cls = color_cnf(len(S), E2, 4, sym_clique=tri2)
    d = os.path.expanduser('~/p23/tmp')
    os.makedirs(d, exist_ok=True)
    cnf = f'{d}/lg_{SEED}_{seed}.cnf'
    try:
        write_cnf(cnf, nvars, cls)
        r = subprocess.run([KISSAT, f'--seed={seed}', cnf],
                           capture_output=True, text=True, timeout=timeout)
        if 's UNSATISFIABLE' in r.stdout:
            return True, None
        pos = set()
        for line in r.stdout.splitlines():
            if line.startswith('v '):
                for tok in line[2:].split():
                    x = int(tok)
                    if x > 0:
                        pos.add(x)
        col = {}
        for i, v in enumerate(S):
            for c in range(4):
                if 4 * i + c + 1 in pos:
                    col[v] = c
                    break
        return False, col
    finally:
        if os.path.exists(cnf):
            os.unlink(cnf)


def ruin(S, k):
    """Delete a BFS ball of k vertices around a random seed vertex."""
    S = set(S)
    start = rng.choice(sorted(S))
    seen, order, q = {start}, [start], deque([start])
    while q and len(order) < k:
        u = q.popleft()
        for w in adj[u] & S:
            if w not in seen:
                seen.add(w); order.append(w); q.append(w)
                if len(order) >= k:
                    break
    return S - set(order[:k])


def recreate(S, target):
    """Conflict-driven column generation (add vertices blocked under colorings)."""
    S = set(S)
    acc = {}
    cap = target + SLACK
    while True:
        ok, col = cnf_unsat(S, rng.randrange(10**6))
        if ok:
            return S
        if len(S) >= cap:
            return None
        best, bs = None, -1.0
        for w in range(NP):
            if w in S:
                continue
            nb = adj[w] & S
            if len(nb) < 3:
                continue
            kk = len({col[u] for u in nb})
            s = acc.get(w, 0.0) + (1.0 if kk == 4 else 0.25 * kk) + 0.01 * len(nb)
            if kk == 4:
                acc[w] = acc.get(w, 0.0) + 1.0
            if s > bs:
                best, bs = w, s
        if best is None:
            return None
        S.add(best)


def repair(S):
    S = set(S)
    for _ in range(3):
        shrunk = False
        for v in sorted(S, key=lambda v: len(adj[v] & S))[:GLIM]:
            if v in S and cnf_unsat(S - {v}, rng.randrange(10**6))[0]:
                S.discard(v)
                shrunk = True
        if not shrunk:
            break
    return S


def main():
    S = set(pickle.load(open(START, 'rb'))) if START else set(range(NP))
    best = cur = set(S)
    print(f'LNS-gen seed={SEED} pool={POOL} start={len(S)}', flush=True)
    t0 = time.time()
    for it in range(ITERS):
        k = rng.randint(KMIN, KMAX)
        got = recreate(ruin(cur, k), len(cur) - 1)
        if got is None:
            print(f'  it{it} k={k}: recreate failed ({round(time.time()-t0)}s)', flush=True)
            continue
        S2 = repair(got)
        print(f'  it{it} k={k}: -> {len(S2)} (cur {len(cur)} best {len(best)}) '
              f'{round(time.time()-t0)}s', flush=True)
        if len(S2) <= len(cur):
            cur = set(S2)
        if len(S2) < len(best):
            best = set(S2)
            pickle.dump(sorted(best), open(f'lnsg_best_{SEED}.pkl', 'wb'))
            print(f'*** NEW BEST {len(best)}', flush=True)
    print(f'DONE best={len(best)}', flush=True)


if __name__ == '__main__':
    main()
