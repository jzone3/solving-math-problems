"""Symmetry-breaking refinement: run a Z3-voltage symmetric anneal to a t=3 optimum,
then anneal ASYMMETRIC single-edge moves on the realized graph (add/del/subdivide/
smooth), exact scoring via ./lp. Asymmetric triples are not quantized to 3Z, so the
descent 3 -> 2 -> 1 -> 0 is open; the hope is the symmetric optimum sits near an
asymmetric t=0 witness.

Usage: python3 asym.py --restarts 100 --symiters 8000 --asymiters 30000 --tag as
"""
import argparse, json, random, time
import core
from weighted import LP
import voltage3 as V

def edge_list(adj):
    return [(u, v) for u in range(len(adj)) for v in adj[u] if u < v]

def amutate(adj, nmax):
    adj = [list(x) for x in adj]
    n = len(adj)
    r = random.random()
    def add(a, b):
        adj[a].append(b); adj[b].append(a)
    if r < 0.3:  # add edge
        for _ in range(20):
            u, v = random.sample(range(n), 2)
            if v not in adj[u]:
                add(u, v)
                return adj
        return None
    if r < 0.55:  # delete edge (keep connected)
        E = edge_list(adj)
        random.shuffle(E)
        for u, v in E:
            adj[u].remove(v); adj[v].remove(u)
            if core.is_connected(adj):
                return adj
            adj[u].append(v); adj[v].append(u)
        return None
    if r < 0.8 and n < nmax:  # subdivide random edge
        E = edge_list(adj)
        u, v = random.choice(E)
        adj[u].remove(v); adj[v].remove(u)
        adj.append([])
        add(u, n); add(n, v)
        return adj
    # smooth a degree-2 vertex
    cands = [v for v in range(n) if len(adj[v]) == 2 and adj[v][0] != adj[v][1]]
    random.shuffle(cands)
    for x in cands:
        a, b = adj[x]
        if b in adj[a]:
            continue
        adj[x] = []
        adj[a].remove(x); adj[b].remove(x)
        adj[a].append(b); adj[b].append(a)
        # compact: relabel removing x
        keep = [v for v in range(n) if v != x]
        idx = {v: i for i, v in enumerate(keep)}
        return [[idx[u] for u in adj[v]] for v in keep]
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--restarts', type=int, default=100)
    ap.add_argument('--symiters', type=int, default=8000)
    ap.add_argument('--asymiters', type=int, default=30000)
    ap.add_argument('--q', type=int, default=4)
    ap.add_argument('--qmax', type=int, default=8)
    ap.add_argument('--wmax', type=int, default=6)
    ap.add_argument('--nmax', type=int, default=52)
    ap.add_argument('--tag', default='as')
    args = ap.parse_args()
    lp = LP()
    logf = open(f'log_{args.tag}.txt', 'a')
    def log(s):
        print(s, flush=True); print(s, file=logf, flush=True)
    for rr in range(args.restarts):
        # phase 1: symmetric anneal to t=3
        q = args.q
        ed = V.rand_quotient(q, args.wmax)
        lf = V.lift(q, ed)
        if lf is None or not core.is_connected(lf[0]):
            continue
        radj = V.realize(*lf)
        if len(radj) > args.nmax:
            continue
        ev = lp.score(radj)
        cur = (q, ed)
        cradj = radj
        for it in range(args.symiters):
            T = 1.5 * (1 - it / args.symiters) + 0.05
            q2, ed2 = V.mutate(cur[0], args.qmax, cur[1], args.wmax)
            lf2 = V.lift(q2, ed2)
            if lf2 is None or not core.is_connected(lf2[0]):
                continue
            radj2 = V.realize(*lf2)
            if len(radj2) > args.nmax:
                continue
            try:
                ev2 = lp.score(radj2)
            except Exception:
                lp = LP()
                continue
            d = (ev2[0] - ev[0]) + 0.01 * (ev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                cur, ev, cradj = (q2, ed2), ev2, radj2
            if ev[0] <= 3:
                break
        if ev[0] > 3:
            log(f'[{args.tag}r{rr}] sym phase stuck at t={ev[0]}, skipping')
            continue
        # phase 2: asymmetric refinement
        adj, aev = cradj, ev
        best = aev
        for it in range(args.asymiters):
            T = 1.2 * (1 - it / args.asymiters) + 0.03
            adj2 = amutate(adj, args.nmax + 6)
            if adj2 is None or not core.is_connected(adj2):
                continue
            try:
                ev2 = lp.score(adj2)
            except Exception:
                lp = LP()
                continue
            d = (ev2[0] - aev[0]) + 0.01 * (aev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                adj, aev = adj2, ev2
            if aev[0] < best[0]:
                best = aev
                log(f'[{args.tag}r{rr}] asym it={it} best t={aev[0]} L={aev[1]} n={len(adj)} masks={aev[2]} ovf={aev[3]}')
                if aev[0] == 0 and aev[3] == 0:
                    fn = f'HIT_{args.tag}_{int(time.time())}.json'
                    json.dump({'adj': adj}, open(fn, 'w'))
                    log(f'*** t=0 HIT written to {fn} — verify independently! ***')
                    return
        log(f'[{args.tag}r{rr}] done best t={best[0]} (sym start t={ev[0]})')

if __name__ == '__main__':
    main()
