"""P05 V1: hybridize hypotraceable / hypohamiltonian pieces.

Pieces = (adjacency list, stub vertices). A piece is obtained by deleting a cubic vertex
from a hypohamiltonian/hypotraceable graph (its 3 neighbours become 'stubs'), or by
deleting an edge (2 stubs). Hybrids wire stubs of 2-4 pieces together via random
matchings, optionally through extra hub vertices, then get scored by the longest-path
triple-intersection objective. Best hybrids are appended to hybrids.jsonl as seeds for
annealing (search.py).
"""
import json, random, sys, time
import core, search

PETERSEN = [[1,4,5],[0,2,6],[1,3,7],[2,4,8],[0,3,9],[0,7,8],[1,8,9],[2,5,9],[3,5,6],[4,6,7]]

def load_all():
    seeds = core.load_seeds('seeds.jsonl')
    seeds['Petersen'] = PETERSEN
    return seeds

def delete_vertex(adj, v):
    stubs = [u - (u > v) for u in adj[v]]
    sub = [[u - (u > v) for u in adj[w] if u != v] for w in range(len(adj)) if w != v]
    return sub, stubs

def pieces_from(adj):
    """All pieces from deleting one cubic vertex."""
    out = []
    for v in range(len(adj)):
        if len(adj[v]) == 3:
            out.append(delete_vertex(adj, v))
    return out

def shift(adj, off):
    return [[u + off for u in nb] for nb in adj]

def hybrid(pieces, extra_hubs=0):
    """Disjoint union of pieces; wire all stubs randomly (matching among stubs and hubs)."""
    adj = []
    stubs = []
    for p_adj, p_stubs in pieces:
        off = len(adj)
        adj += shift(p_adj, off)
        stubs += [s + off for s in p_stubs]
    hubs = []
    for _ in range(extra_hubs):
        adj.append([])
        hubs.append(len(adj) - 1)
    random.shuffle(stubs)
    # connect stubs: random matching among stubs across pieces; odd ones go to hubs or random
    while len(stubs) >= 2:
        a = stubs.pop()
        if hubs and random.random() < 0.4:
            h = random.choice(hubs)
            adj[a].append(h); adj[h].append(a)
            continue
        b = stubs.pop()
        adj[a].append(b); adj[b].append(a)
    for a in stubs:
        t = random.choice(hubs) if hubs else random.randrange(len(adj))
        if t != a and t not in adj[a]:
            adj[a].append(t); adj[t].append(a)
    for h in hubs:
        while len(adj[h]) < 2:
            t = random.randrange(len(adj))
            if t != h and t not in adj[h]:
                adj[h].append(t); adj[t].append(h)
    return adj

def main():
    n_iter = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    maxn = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    seeds = load_all()
    plib = []
    for name in ('Petersen', 'Van Cleemput-Zamfirescu Graph 13'):
        plib += pieces_from(seeds[name])
    # also pieces from Thomassen 34 (33-vertex pieces are large; keep a few)
    big = pieces_from(seeds['Thomassen Graph 34'])[:3]
    best = []
    logf = open('log_hybrid.txt', 'a')
    for it in range(n_iter):
        k = random.choice([2, 2, 3, 3, 4])
        ps = [random.choice(plib) for _ in range(k)]
        if random.random() < 0.15 and maxn >= 40:
            ps = [random.choice(big)] + [random.choice(plib) for _ in range(random.choice([1, 2]))]
        n_tot = sum(len(p[0]) for p in ps)
        if n_tot > maxn:
            continue
        adj = hybrid(ps, extra_hubs=random.choice([0, 0, 1, 2]))
        if not core.is_connected(adj):
            continue
        ev = search.evaluate(adj, path_cap=20000, node_budget=2_000_000)
        if ev is None:
            continue
        t, L, np_ = ev
        msg = f'[hyb] it={it} n={len(adj)} t={t} L={L}v paths={np_}'
        if t is not None and t <= 2:
            print(msg, flush=True); print(msg, file=logf, flush=True)
            best.append((t, adj))
            with open('hybrids.jsonl', 'a') as f:
                f.write(json.dumps({'t': t, 'L': L, 'adj': adj}) + '\n')
            if t == 0:
                json.dump({'adj': adj}, open(f'HIT_hyb_{int(time.time())}.json', 'w'))
                print('*** t=0 HIT (verify!) ***', flush=True)
                return
    print(f'hybridize done: {len(best)} candidates with t<=2', flush=True)

if __name__ == '__main__':
    main()
