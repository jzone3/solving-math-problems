"""P05 V1 wave 4: C3-symmetric 'triangle of hubs' targeted search.

Motivation: any TWO longest paths share a vertex (classical), so a t=0 triple needs
three longest-path families meeting pairwise in three DIFFERENT regions. The natural
shape is Z3-symmetric: three hubs h0,h1,h2 arranged in a triangle, three identical
weighted arms A_i joining h_i to h_{i+1}; each longest path should traverse exactly two
hubs (miss the third), so the triple rotated by the symmetry has empty intersection iff
no vertex lies on all three.

Encoding: quotient gadget = arm graph on k vertices with weighted internal edges plus
weighted attachments from arm vertices to the left hub (h_i) and right hub (h_{i+1}).
The full skeleton is 3 hubs + 3 arm copies; realization subdivides each weighted edge
(weight w -> path of w unit edges). Exact scoring via the C scanner (./lp, LP_NOEXIT).
Annealing mutates the quotient only, so Z3 symmetry is preserved throughout.

Usage: python3 c3sym.py --iters 20000 --k 4 --kmax 8 --wmax 6 --nmax 58 --restarts 200 --tag c3
"""
import argparse, json, random, time
import core
from weighted import LP, realize

def build(k, arm_e, la, ra, hp=0, hh=0):
    """Full skeleton adjacency-weight dict from quotient.
    arm_e: {(u,v): w} internal arm edges (0<=u<v<k)
    la: {u: w} attachments arm vertex u -> left hub; ra: same -> right hub.
    hp: hub pendant weight (0=none): pendant vertex hanging off each hub.
    hh: hub-hub chord weight (0=none): direct weighted triangle edges."""
    w = {}
    def add(a, b, wt):
        e = (min(a, b), max(a, b))
        w[e] = wt
    npend = 3 if hp else 0
    for i in range(3):
        off = 3 + npend + i * k
        for (u, v), wt in arm_e.items():
            add(off + u, off + v, wt)
        for u, wt in la.items():
            add(i, off + u, wt)
        for u, wt in ra.items():
            add((i + 1) % 3, off + u, wt)
        if hp:
            add(i, 3 + i, hp)
        if hh:
            add(i, (i + 1) % 3, hh)
    n = 3 + npend + 3 * k
    adj = [[] for _ in range(n)]
    for (u, v) in w:
        adj[u].append(v); adj[v].append(u)
    return adj, w

def rand_quotient(k, wmax):
    # random connected arm
    arm_e = {}
    order = list(range(k)); random.shuffle(order)
    for i in range(1, k):
        u, v = order[i], order[random.randrange(i)]
        arm_e[(min(u, v), max(u, v))] = random.randint(1, wmax)
    for _ in range(random.randint(0, k)):
        u, v = random.sample(range(k), 2)
        arm_e.setdefault((min(u, v), max(u, v)), random.randint(1, wmax))
    la = {random.randrange(k): random.randint(1, wmax)}
    ra = {random.randrange(k): random.randint(1, wmax)}
    hp = random.choice([0, random.randint(1, wmax)])
    hh = random.choice([0, 0, random.randint(1, wmax)])
    return arm_e, la, ra, hp, hh

def mutate(k, kmax, arm_e, la, ra, hp, hh, wmax):
    arm_e = dict(arm_e); la = dict(la); ra = dict(ra)
    r = random.random()
    if r < 0.12:  # hub pendant / chord move
        if random.random() < 0.6:
            hp = max(0, min(2 * wmax, hp + random.choice([-2, -1, 1, 2])))
        else:
            hh = max(0, min(wmax, hh + random.choice([-1, 1])))
        return k, arm_e, la, ra, hp, hh
    if r < 0.45:  # weight move on a random weighted item
        pool = [('e', e) for e in arm_e] + [('l', u) for u in la] + [('r', u) for u in ra]
        kind, key = random.choice(pool)
        d = random.choice([-2, -1, 1, 2])
        tgt = {'e': arm_e, 'l': la, 'r': ra}[kind]
        tgt[key] = max(1, min(wmax, tgt[key] + d))
        return k, arm_e, la, ra, hp, hh
    if r < 0.6:  # toggle attachment
        side = random.choice([la, ra])
        u = random.randrange(k)
        if u in side and len(side) > 1:
            del side[u]
        else:
            side[u] = random.randint(1, wmax)
        return k, arm_e, la, ra, hp, hh
    if r < 0.75:  # add arm edge
        if k >= 2:
            u, v = random.sample(range(k), 2)
            arm_e.setdefault((min(u, v), max(u, v)), random.randint(1, wmax))
        return k, arm_e, la, ra, hp, hh
    if r < 0.87:  # delete arm edge
        if arm_e:
            del arm_e[random.choice(list(arm_e))]
        return k, arm_e, la, ra, hp, hh
    if k < kmax:  # grow arm: new vertex attached to 1-2 arm vertices
        u = random.randrange(k)
        arm_e[(u, k)] = random.randint(1, wmax)
        if random.random() < 0.5 and k >= 2:
            v = random.randrange(k)
            if v != u:
                arm_e[(min(v, k), max(v, k))] = random.randint(1, wmax)
        return k + 1, arm_e, la, ra, hp, hh
    return k, arm_e, la, ra, hp, hh

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iters', type=int, default=20000)
    ap.add_argument('--k', type=int, default=4)
    ap.add_argument('--kmax', type=int, default=8)
    ap.add_argument('--wmax', type=int, default=6)
    ap.add_argument('--nmax', type=int, default=58)
    ap.add_argument('--restarts', type=int, default=200)
    ap.add_argument('--tag', default='c3')
    args = ap.parse_args()
    lp = LP()
    logf = open(f'log_{args.tag}.txt', 'a')
    def log(s):
        print(s, flush=True); print(s, file=logf, flush=True)
    for rr in range(args.restarts):
        k = args.k
        arm_e, la, ra, hp, hh = rand_quotient(k, args.wmax)
        adj, w = build(k, arm_e, la, ra, hp, hh)
        if not core.is_connected(adj):
            continue
        radj = realize(adj, w)
        if len(radj) > args.nmax:
            continue
        ev = lp.score(radj)
        best = ev
        cur = (k, arm_e, la, ra, hp, hh)
        for it in range(args.iters):
            T = 2.0 * (1 - it / args.iters) + 0.05
            cur2 = mutate(cur[0], args.kmax, cur[1], cur[2], cur[3], cur[4], cur[5], args.wmax)
            k2 = cur2[0]
            adj2, w2 = build(*cur2)
            if not core.is_connected(adj2):
                continue
            radj2 = realize(adj2, w2)
            if len(radj2) > args.nmax:
                continue
            try:
                ev2 = lp.score(radj2)
            except Exception:
                lp = LP()
                continue
            d = (ev2[0] - ev[0]) + 0.01 * (ev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                cur, ev = cur2, ev2
            if ev[0] < best[0]:
                best = ev
                log(f'[{args.tag}r{rr}] it={it} best t={ev[0]} L={ev[1]}v realn={len(radj2)} masks={ev[2]} ovf={ev[3]}')
                if ev[0] == 0 and ev[3] == 0:
                    fn = f'HIT_{args.tag}_{int(time.time())}.json'
                    json.dump({'quotient': {'k': cur[0], 'arm_e': {str(e): v for e, v in cur[1].items()},
                                            'la': cur[2], 'ra': cur[3], 'hp': cur[4], 'hh': cur[5]},
                               'adj': realize(*build(*cur))}, open(fn, 'w'))
                    log(f'*** t=0 HIT written to {fn} — verify independently! ***')
                    return
        log(f'[{args.tag}r{rr}] done best t={best[0]} L={best[1]}')

if __name__ == '__main__':
    main()
