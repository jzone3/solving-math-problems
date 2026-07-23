"""Z3 voltage-graph search: ALL graphs with a free Z3 action.

A quotient graph Q on q vertices with edges (u,v,g) labeled by a voltage g in {0,1,2}
and an integer weight lifts to the 3q-vertex graph with vertices (u,i) and edges
(u,i)-(v,(i+g) mod 3). Every graph admitting a free Z3 action arises this way, so this
strictly generalizes the triangle-of-hubs family (c3sym.py). Free action => symmetric
longest-path triples have |P ∩ sP ∩ s2P| divisible by 3: only the 3->0 quantum matters.
Weights realized by subdivision (weight w edge -> path of w unit edges); note w
subdivision vertices split across lifted edges keep the action free. Exact scoring ./lp.

Usage: python3 voltage3.py --iters 40000 --q 4 --qmax 8 --wmax 6 --nmax 57 --restarts 300 --tag v3
"""
import argparse, json, random, time
import core
from weighted import LP

def lift(q, ed):
    """ed: dict {(u,v,g): w} with u<=v; returns (adj, weights) of the lifted graph.
    Vertex (u,i) -> index 3*u+i."""
    w = {}
    for (u, v, g), wt in ed.items():
        for i in range(3):
            a, b = 3 * u + i, 3 * v + (i + g) % 3
            if a == b:
                return None
            e = (min(a, b), max(a, b))
            if e in w:
                return None
            w[e] = wt
    n = 3 * q
    adj = [[] for _ in range(n)]
    for (a, b) in w:
        adj[a].append(b); adj[b].append(a)
    return adj, w

def realize(adj, w):
    adj = [list(x) for x in adj]
    def add(a, b):
        adj[a].append(b); adj[b].append(a)
    for (u, v), wt in w.items():
        if wt == 1:
            continue
        adj[u].remove(v); adj[v].remove(u)
        prev = u
        for _ in range(wt - 1):
            adj.append([])
            nv = len(adj) - 1
            add(prev, nv)
            prev = nv
        add(prev, v)
    return adj

def rand_quotient(q, wmax):
    ed = {}
    for i in range(1, q):
        u = random.randrange(i)
        ed[(u, i, random.randrange(3))] = random.randint(1, wmax)
    for _ in range(random.randint(1, q)):
        u, v = sorted(random.sample(range(q), 2))
        ed.setdefault((u, v, random.randrange(3)), random.randint(1, wmax))
    return ed

def mutate(q, qmax, ed, wmax):
    ed = dict(ed)
    r = random.random()
    if r < 0.4 and ed:  # weight move
        k = random.choice(list(ed))
        ed[k] = max(1, min(wmax, ed[k] + random.choice([-2, -1, 1, 2])))
        return q, ed
    if r < 0.55 and ed:  # voltage move
        k = random.choice(list(ed))
        u, v, g = k
        wt = ed.pop(k)
        ed[(u, v, (g + random.choice([1, 2])) % 3)] = wt
        return q, ed
    if r < 0.7:  # add edge
        u, v = sorted(random.sample(range(q), 2)) if q >= 2 else (0, 0)
        if u != v:
            ed.setdefault((u, v, random.randrange(3)), random.randint(1, wmax))
        return q, ed
    if r < 0.85 and len(ed) > q:  # delete edge
        del ed[random.choice(list(ed))]
        return q, ed
    if q < qmax:  # grow
        u = random.randrange(q)
        ed[(u, q, random.randrange(3))] = random.randint(1, wmax)
        if random.random() < 0.5:
            v = random.randrange(q)
            if v != q:
                ed[(min(v, q), max(v, q), random.randrange(3))] = random.randint(1, wmax)
        return q + 1, ed
    return q, ed

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iters', type=int, default=40000)
    ap.add_argument('--q', type=int, default=4)
    ap.add_argument('--qmax', type=int, default=8)
    ap.add_argument('--wmax', type=int, default=6)
    ap.add_argument('--nmax', type=int, default=57)
    ap.add_argument('--restarts', type=int, default=300)
    ap.add_argument('--tag', default='v3')
    args = ap.parse_args()
    lp = LP()
    logf = open(f'log_{args.tag}.txt', 'a')
    def log(s):
        print(s, flush=True); print(s, file=logf, flush=True)
    for rr in range(args.restarts):
        q = args.q
        ed = rand_quotient(q, args.wmax)
        cur = (q, ed)
        lf = lift(q, ed)
        if lf is None or not core.is_connected(lf[0]):
            continue
        radj = realize(*lf)
        if len(radj) > args.nmax:
            continue
        ev = lp.score(radj)
        best = ev
        for it in range(args.iters):
            T = 2.0 * (1 - it / args.iters) + 0.05
            q2, ed2 = mutate(cur[0], args.qmax, cur[1], args.wmax)
            lf2 = lift(q2, ed2)
            if lf2 is None or not core.is_connected(lf2[0]):
                continue
            radj2 = realize(*lf2)
            if len(radj2) > args.nmax:
                continue
            try:
                ev2 = lp.score(radj2)
            except Exception:
                lp = LP()
                continue
            d = (ev2[0] - ev[0]) + 0.01 * (ev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                cur, ev = (q2, ed2), ev2
            if ev[0] < best[0]:
                best = ev
                log(f'[{args.tag}r{rr}] it={it} best t={ev[0]} L={ev[1]}v realn={len(radj2)} masks={ev[2]} ovf={ev[3]}')
                if ev[0] == 0 and ev[3] == 0:
                    fn = f'HIT_{args.tag}_{int(time.time())}.json'
                    lfh = lift(*cur)
                    json.dump({'q': cur[0], 'edges': {str(k): v for k, v in cur[1].items()},
                               'adj': realize(*lfh)}, open(fn, 'w'))
                    log(f'*** t=0 HIT written to {fn} — verify independently! ***')
                    return
        log(f'[{args.tag}r{rr}] done best t={best[0]} L={best[1]}')

if __name__ == '__main__':
    main()
