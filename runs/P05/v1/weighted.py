"""P05 V1 escalation: weighted-skeleton (subdivision) search.

A weighted skeleton = small simple connected graph + integer edge weights w_e >= 1.
Realization = subdivide each edge e into w_e unit edges. Longest paths of the realized
graph correspond to max-weight paths of the skeleton; Walther/Zamfirescu-type extremal
graphs are exactly such subdivisions of small cubic skeletons. Searching (topology,
weights) space concentrates the search on the structurally interesting family and lets
one weight mutation move the whole longest-path landscape.

Score: exact min-triple-intersection t of the REALIZED graph, computed by the C scanner
(./lp, exact, overflow-flagged). Anneal to t=0.

Usage: python3 weighted.py --iters N --ns 8..12 --wmax 9 --nmax 48 --tag wsk
"""
import argparse, json, random, subprocess, time
import core
import search as S

def g6_encode(adj):
    n = len(adj)
    assert n <= 62
    out = [chr(n + 63)]
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if j in adj[i] else 0)
    while len(bits) % 6:
        bits.append(0)
    for i in range(0, len(bits), 6):
        v = 0
        for b in bits[i:i + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return ''.join(out)

def realize(skel_adj, w):
    """Subdivide edge (u,v) with weight w[(u,v)] into w unit edges."""
    n = len(skel_adj)
    adj = [[] for _ in range(n)]
    def add(a, b):
        adj[a].append(b); adj[b].append(a)
    for (u, v), wt in w.items():
        prev = u
        for _ in range(wt - 1):
            adj.append([])
            nv = len(adj) - 1
            add(prev, nv)
            prev = nv
        add(prev, v)
    return adj

class LP:
    """Persistent exact scanner subprocess (LP_NOEXIT so HITs don't kill it)."""
    def __init__(self):
        self.p = subprocess.Popen(['./lp', '64'], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True, bufsize=1,
                                  env={'LP_NOEXIT': '1', 'PATH': '/usr/bin:/bin'})
    def score(self, adj):
        g6 = g6_encode(adj)
        self.p.stdin.write(g6 + '\n'); self.p.stdin.flush()
        line = self.p.stdout.readline().split()
        if line[0] == 'HIT':
            line = self.p.stdout.readline().split()  # should not happen (t printed first)
        t, L, nm, ovf = int(line[0]), int(line[1]), int(line[2]), int(line[3])
        if line[4:] and line[4] != g6:
            raise RuntimeError('desync')
        return t, L, nm, ovf

def rand_skel(ns):
    while True:
        adj = S.random_connected_graph(ns, ns + random.randint(0, ns // 2))
        if S.is_biconnected(adj) or random.random() < 0.3:
            return adj

def edges(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]

def mutate(skel, w, ns_max, wmax):
    skel = [list(x) for x in skel]
    w = dict(w)
    r = random.random()
    E = edges(skel)
    if r < 0.55:  # weight move
        e = random.choice(E)
        w[e] = max(1, min(wmax, w[e] + random.choice([-2, -1, 1, 2])))
        return skel, w
    if r < 0.7 and len(skel) < ns_max:  # add vertex on two random vertices
        u, v = random.sample(range(len(skel)), 2)
        skel.append([])
        nv = len(skel) - 1
        skel[u].append(nv); skel[nv].append(u)
        skel[v].append(nv); skel[nv].append(v)
        w[(u, nv)] = random.randint(1, wmax); w[(v, nv)] = random.randint(1, wmax)
        return skel, w
    if r < 0.85:  # add edge
        for _ in range(20):
            u, v = random.sample(range(len(skel)), 2)
            if v not in skel[u]:
                skel[u].append(v); skel[v].append(u)
                w[(min(u, v), max(u, v))] = random.randint(1, wmax)
                return skel, w
        return None
    # delete edge (keep connected)
    random.shuffle(E)
    for u, v in E:
        skel[u].remove(v); skel[v].remove(u)
        if core.is_connected(skel):
            del w[(u, v)]
            return skel, w
        skel[u].append(v); skel[v].append(u)
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iters', type=int, default=20000)
    ap.add_argument('--ns', type=int, default=10)
    ap.add_argument('--nsmax', type=int, default=14)
    ap.add_argument('--wmax', type=int, default=7)
    ap.add_argument('--nmax', type=int, default=48)
    ap.add_argument('--restarts', type=int, default=20)
    ap.add_argument('--tag', default='wsk')
    args = ap.parse_args()
    lp = LP()
    logf = open(f'log_{args.tag}.txt', 'a')
    def log(s):
        print(s, flush=True); print(s, file=logf, flush=True)
    for rr in range(args.restarts):
        skel = rand_skel(args.ns)
        w = {e: random.randint(1, args.wmax) for e in edges(skel)}
        cur = (skel, w)
        adj = realize(skel, w)
        if len(adj) > args.nmax:
            continue
        ev = lp.score(adj)
        best = ev
        for it in range(args.iters):
            T = 2.0 * (1 - it / args.iters) + 0.05
            m = mutate(cur[0], cur[1], args.nsmax, args.wmax)
            if m is None:
                continue
            adj2 = realize(m[0], m[1])
            if len(adj2) > args.nmax:
                continue
            try:
                ev2 = lp.score(adj2)
            except Exception:
                lp = LP()
                continue
            d = (ev2[0] - ev[0]) + 0.01 * (ev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                cur, ev = m, ev2
            if ev[0] < best[0]:
                best = ev
                log(f'[{args.tag}r{rr}] it={it} best t={ev[0]} L={ev[1]}v realn={len(adj2)} masks={ev[2]} ovf={ev[3]}')
                if ev[0] == 0 and ev[3] == 0:
                    fn = f'HIT_{args.tag}_{int(time.time())}.json'
                    json.dump({'skel': cur[0], 'w': {str(k): v for k, v in cur[1].items()},
                               'adj': realize(cur[0], cur[1])}, open(fn, 'w'))
                    log(f'*** t=0 HIT written to {fn} — verify independently! ***')
                    return
        log(f'[{args.tag}r{rr}] done best t={best[0]} L={best[1]}')

if __name__ == '__main__':
    main()
