"""Small hyperedges for the hitting-set bank (min-conflicts + conflict cover).

The clause a maximal colour extension produces is the complement of a 4-colorable
set and runs ~660 literals wide on the 2581-vertex universe, which makes the
lower bound crawl (same failure as E17).  A near-proper colouring of the *whole*
universe gives a far smaller clause: colour everything with min-conflicts/tabu,
then delete a vertex cover of the surviving conflicting edges.  The rest is
properly 4-coloured, so the cover is a hyperedge -- every witness must contain
one of its vertices -- and it is typically tens of vertices, not hundreds.

Writes clauses into the same append-only bank the `hsfull.py` workers read.

Env: POOL, BANK, SEED, STEPS, NOISE, ROUNDS.
"""
import json
import os
import pickle
import random

POOL = os.environ.get('POOL', 'tasym_1.6_1.3.pkl')
BANK = os.environ.get('BANK', 'hsfull_' + os.path.basename(POOL) + '.jsonl')
SEED = int(os.environ.get('SEED', '1'))
STEPS = int(os.environ.get('STEPS', '400000'))
NOISE = float(os.environ.get('NOISE', '0.02'))
ROUNDS = int(os.environ.get('ROUNDS', '10000'))

pts, E = pickle.load(open(POOL, 'rb'))
N = len(pts)
adj = [[] for _ in range(N)]
for a, b in E:
    adj[a].append(b)
    adj[b].append(a)
rng = random.Random(SEED)
print(f'pool {N} vertices, {len(E)} edges', flush=True)


def tabu():
    col = [rng.randrange(4) for _ in range(N)]
    cnt = [[0, 0, 0, 0] for _ in range(N)]
    for v in range(N):
        for u in adj[v]:
            cnt[v][col[u]] += 1
    bad = [v for v in range(N) if cnt[v][col[v]]]
    best = None
    for step in range(STEPS):
        if not bad:
            return col, []
        v = bad[rng.randrange(len(bad))]
        if cnt[v][col[v]] == 0:
            bad.remove(v)
            continue
        if rng.random() < NOISE:
            c = rng.randrange(4)
        else:
            m = min(cnt[v])
            c = rng.choice([k for k in range(4) if cnt[v][k] == m])
        if c == col[v]:
            continue
        old = col[v]
        col[v] = c
        for u in adj[v]:
            cnt[u][old] -= 1
            cnt[u][c] += 1
            if cnt[u][col[u]] and u not in bad:
                bad.append(u)
        if cnt[v][c] and v not in bad:
            bad.append(v)
        if step % 20000 == 0:
            live = sum(1 for x in range(N) if cnt[x][col[x]])
            if best is None or live < best:
                best = live
    return col, [v for v in range(N) if cnt[v][col[v]]]


def cover(col):
    """Greedy max-degree vertex cover of the conflicting edges."""
    conf = [(a, b) for a, b in E if col[a] == col[b]]
    deg = {}
    for a, b in conf:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    out = set()
    rest = list(conf)
    while rest:
        v = max(deg, key=lambda x: deg.get(x, 0))
        out.add(v)
        keep = []
        for a, b in rest:
            if a == v or b == v:
                deg[a] = deg.get(a, 0) - 1
                deg[b] = deg.get(b, 0) - 1
            else:
                keep.append((a, b))
        rest = keep
        deg.pop(v, None)
    return sorted(out)


def main():
    bank = open(BANK, 'a')
    for r in range(ROUNDS):
        col, _ = tabu()
        D = cover(col)
        if not D:
            print('!!! universe 4-colored -- impossible', flush=True)
            return
        bank.write(json.dumps(D) + '\n')
        bank.flush()
        print(f'round {r}: hyperedge |D| = {len(D)}', flush=True)


if __name__ == '__main__':
    main()
