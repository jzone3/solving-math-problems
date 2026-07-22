"""P05 V1: annealed mutation search over graphs, seeded from hypotraceable /
longest-path-pathological graphs. Objective: minimize the minimum, over triples of
longest paths, of |P1 cap P2 cap P3| (target 0 = counterexample to Gallai-3).

Usage: python3 search.py [--seed NAME|random] [--iters N] [--nmax N] [--tag TAG]
"""
import argparse, json, os, random, sys, time
import core

random.seed()

def copy_adj(adj):
    return [list(x) for x in adj]

def add_edge(adj, u, v):
    adj[u].append(v); adj[v].append(u)

def del_edge(adj, u, v):
    adj[u].remove(v); adj[v].remove(u)

def edges_of(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]

def mutate(adj, nmin, nmax):
    """Return a mutated connected copy, or None."""
    adj = copy_adj(adj)
    n = len(adj)
    E = edges_of(adj)
    moves = ['add', 'del', 'subdiv', 'pendant', 'rewire', 'smooth', 'split']
    mv = random.choice(moves)
    try:
        if mv == 'add':
            for _ in range(20):
                u, v = random.sample(range(n), 2)
                if v not in adj[u]:
                    add_edge(adj, u, v)
                    return adj
            return None
        if mv == 'del':
            random.shuffle(E)
            for u, v in E:
                del_edge(adj, u, v)
                if core.is_connected(adj):
                    return adj
                add_edge(adj, u, v)
            return None
        if mv == 'subdiv':
            if n >= nmax: return None
            u, v = random.choice(E)
            del_edge(adj, u, v)
            adj.append([])
            add_edge(adj, u, n); add_edge(adj, v, n)
            return adj
        if mv == 'pendant':
            if n >= nmax: return None
            u = random.randrange(n)
            adj.append([])
            add_edge(adj, u, n)
            return adj
        if mv == 'smooth':
            if n <= nmin: return None
            cands = [v for v in range(n) if len(adj[v]) == 2 and adj[v][0] != adj[v][1]]
            random.shuffle(cands)
            for v in cands:
                a, b = adj[v]
                if a not in adj[b] or True:
                    if b in adj[a]:
                        continue
                    # remove v, join a-b
                    newadj = [[u - (u > v) for u in adj[w] if u != v] for w in range(n) if w != v]
                    aa = a - (a > v); bb = b - (b > v)
                    add_edge(newadj, aa, bb)
                    return newadj
            return None
        if mv == 'split':
            if n >= nmax: return None
            cands = [v for v in range(n) if len(adj[v]) >= 4]
            if not cands: return None
            v = random.choice(cands)
            nbs = list(adj[v]); random.shuffle(nbs)
            cut = random.randint(2, len(nbs) - 2)
            keep, move = nbs[:cut], nbs[cut:]
            for u in move:
                del_edge(adj, v, u)
            adj.append([])
            w = n
            for u in move:
                add_edge(adj, w, u)
            add_edge(adj, v, w)
            return adj
        if mv == 'rewire':
            u, v = random.choice(E)
            for _ in range(20):
                w = random.randrange(n)
                if w != u and w != v and w not in adj[u]:
                    del_edge(adj, u, v)
                    add_edge(adj, u, w)
                    if core.is_connected(adj):
                        return adj
                    del_edge(adj, u, w)
                    add_edge(adj, u, v)
            return None
    except (ValueError, IndexError):
        return None
    return None


def triple_score(paths, work_cap=200000):
    """Min |P1&P2&P3| over triples of longest-path masks (heuristic but usually exact:
    scans pairs in order of pairwise intersection size, all thirds, up to work_cap ops)."""
    ms = sorted(set(m for _, m in paths))
    k = len(ms)
    pc = core.popcount
    if len(paths) < 3:
        return pc(ms[0])
    if k == 1:
        return pc(ms[0])
    if k == 2:
        return pc(ms[0] & ms[1])
    pairs = []
    max_pairs = max(1, work_cap // max(k, 1))
    if k * (k - 1) // 2 <= max_pairs:
        it = ((i, j) for i in range(k) for j in range(i + 1, k))
    else:
        seen = set()
        def gen():
            for _ in range(max_pairs * 3):
                i = random.randrange(k); j = random.randrange(k)
                if i < j and (i, j) not in seen:
                    seen.add((i, j))
                    yield (i, j)
                    if len(seen) >= max_pairs:
                        return
        it = gen()
    for i, j in it:
        pairs.append((pc(ms[i] & ms[j]), ms[i] & ms[j]))
    pairs.sort(key=lambda x: x[0])
    best = None
    budget = work_cap
    for pcm, m in pairs:
        if best is not None and pcm >= 3 * best and best <= 2:
            break
        for l in ms:
            c = pc(m & l)
            if best is None or c < best:
                best = c
                if best == 0:
                    return 0
        budget -= k
        if budget <= 0:
            break
    return best


def is_biconnected(adj):
    n = len(adj)
    if n < 3:
        return False
    if not core.is_connected(adj):
        return False
    for v in range(n):
        sub = [[u - (u > v) for u in adj[w] if u != v] for w in range(n) if w != v]
        if not core.is_connected(sub):
            return False
    return True


def evaluate(adj, path_cap=8000, node_budget=400_000, biconn=False, max_avg_deg=3.6):
    n = len(adj)
    if max_avg_deg and sum(len(x) for x in adj) > max_avg_deg * n:
        return None
    if biconn and not is_biconnected(adj):
        return None
    r = core.longest_paths(adj, cap=path_cap, node_budget=node_budget)
    if r is None:
        return None
    L, paths = r
    t = triple_score(paths)
    k = len(set(m for _, m in paths))
    return (t, L, k)


def random_connected_graph(n, m):
    while True:
        adj = [[] for _ in range(n)]
        perm = list(range(n)); random.shuffle(perm)
        for i in range(n - 1):
            add_edge(adj, perm[i], perm[i + 1])
        E = set(map(tuple, (sorted(e) for e in edges_of(adj))))
        while len(E) < m:
            u, v = random.sample(range(n), 2)
            if (min(u, v), max(u, v)) not in E:
                add_edge(adj, u, v)
                E.add((min(u, v), max(u, v)))
        return adj


def canon_key(adj):
    return tuple(sorted((min(u, v), max(u, v)) for u in range(len(adj)) for v in adj[u] if u < v)), len(adj)


def key(ev):
    return (ev[0], -ev[1], -ev[2])


def run(seed_adj, iters, nmin, nmax, tag, log, biconn=False):
    cur = copy_adj(seed_adj)
    ev = evaluate(cur, biconn=biconn)
    tries = 0
    while ev is None and tries < 200:
        cur2 = mutate(cur, nmin, nmax)
        if cur2 is not None:
            ev2 = evaluate(cur2, biconn=biconn)
            if ev2 is not None:
                cur, ev = cur2, ev2
                break
        tries += 1
    if ev is None:
        log(f'[{tag}] seed unevaluable, abort')
        return None
    best = ev
    best_adj = copy_adj(cur)
    T0 = 2.0
    t_start = time.time()
    for it in range(iters):
        T = T0 * (1 - it / iters) + 0.05
        cand = mutate(cur, nmin, nmax)
        if cand is None:
            continue
        ev2 = evaluate(cand, biconn=biconn)
        if ev2 is None:
            continue
        d = (ev2[0] - ev[0]) + 0.02 * (ev[1] - ev2[1]) + 0.001 * (ev[2] - ev2[2])
        if d <= 0 or random.random() < pow(2.718, -d / T):
            cur, ev = cand, ev2
        if key(ev) < key(best):
            best = ev
            best_adj = copy_adj(cur)
            log(f'[{tag}] it={it} new best t={best[0]} L={best[1]}v n={len(cur)} m={len(edges_of(cur))} paths={best[2]}')
            if best[0] == 0:
                fn = f'HIT_{tag}_{int(time.time())}.json'
                json.dump({'adj': best_adj}, open(fn, 'w'))
                log(f'[{tag}] *** t=0 HIT written to {fn} ***')
                return best_adj
    log(f'[{tag}] done iters={iters} best t={best[0]} (L={best[1]}v, n={len(best_adj)}) elapsed={time.time()-t_start:.0f}s')
    json.dump({'adj': best_adj, 'score': best}, open(f'best_{tag}.json', 'w'))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', default='random')
    ap.add_argument('--iters', type=int, default=2000)
    ap.add_argument('--nmin', type=int, default=8)
    ap.add_argument('--nmax', type=int, default=24)
    ap.add_argument('--restarts', type=int, default=1)
    ap.add_argument('--tag', default='run')
    ap.add_argument('--biconn', action='store_true')
    ap.add_argument('--seedfile', default=None, help='jsonl file with {"adj":...} entries; cycles through them')
    args = ap.parse_args()
    seeds = core.load_seeds(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seeds.jsonl'))
    logf = open(f'log_{args.tag}.txt', 'a')
    def log(s):
        print(s, flush=True)
        print(s, file=logf, flush=True)
    file_seeds = None
    if args.seedfile:
        file_seeds = [json.loads(l)['adj'] for l in open(args.seedfile)]
    for r in range(args.restarts):
        if file_seeds:
            seed_adj = file_seeds[r % len(file_seeds)]
        elif args.seed == 'random':
            n = random.randint(max(10, args.nmin), args.nmax)
            m = n + random.randint(0, n // 2)
            seed_adj = random_connected_graph(n, m)
        elif True:
            seed_adj = seeds[args.seed]
        res = run(seed_adj, args.iters, args.nmin, args.nmax, f'{args.tag}r{r}', log, biconn=args.biconn)
        if res is not None:
            log('COUNTEREXAMPLE CANDIDATE FOUND — verify independently!')
            return


if __name__ == '__main__':
    main()
