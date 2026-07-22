"""Hill-climb directly on mincyc(G) over Eulerian graphs with a max-degree cap
(dmax < 2K so tightness cannot be degree-forced).  Moves: parity-preserving
toggles of closed pair-sets.  Accept if mincyc does not decrease; restart with
random kicks on stagnation.  Witness condition: mincyc > K = floor((n-1)/2).
"""
import random, time, argparse
import mincyc as M
from structural_tight import random_eulerian


def degs(n, E):
    d = [0] * n
    for u, v in E:
        d[u] += 1
        d[v] += 1
    return d


def toggle(n, E, rng, Lmax=6):
    S = set((min(u, v), max(u, v)) for u, v in E)
    L = rng.choice([3, 4, 5, 6][:Lmax - 2])
    vs = rng.sample(range(n), L)
    T = [(min(a, b), max(a, b)) for a, b in zip(vs, vs[1:] + vs[:1])]
    if len(set(T)) != L:
        return None
    return list(S.symmetric_difference(T))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--dmax", type=int, default=10)
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--time-limit", type=float, default=180.0)
    ap.add_argument("--start", default="random",
                    help="random | splitK (split of K_{n-1}, n even)")
    args = ap.parse_args()
    n, dmax = args.n, args.dmax
    K = (n - 1) // 2
    rng = random.Random(args.seed)
    lf = open(f"climb_{args.start}_n{n}_d{dmax}_s{args.seed}.txt", "a")

    def log(m):
        print(m, flush=True)
        lf.write(m + "\n")
        lf.flush()

    def fresh():
        if args.start == "splitK":
            assert n % 2 == 0
            base = n - 1
            a = rng.choice(range(2, base - 2, 2))
            E = []
            for i in range(base):
                for j in range(i + 1, base):
                    if i == 0 and j <= a:
                        E.append((base, j))
                    else:
                        E.append((i, j))
            assert M.is_eulerian_simple(n, E)
            return E
        while True:
            E = random_eulerian(n, dmax, (n * dmax) // 2, rng)
            if E and M.is_eulerian_simple(n, E) and max(degs(n, E)) <= dmax:
                return E

    cur = fresh()
    cur_mc = M.min_cycles(n, cur, args.time_limit)
    best = cur_mc
    stall = 0
    log(f"=== climb n={n} dmax={dmax} K={K} start mincyc={cur_mc} m={len(cur)} ===")
    for it in range(args.iters):
        cand = toggle(n, cur, rng)
        if (cand is None or not M.is_eulerian_simple(n, cand)
                or (args.start != "splitK" and max(degs(n, cand)) > dmax)):
            continue
        mc = M.min_cycles(n, cand, args.time_limit)
        if mc is None:
            continue
        if mc >= cur_mc:
            if mc > cur_mc:
                log(f"it={it} up {cur_mc}->{mc} m={len(cand)}")
                stall = 0
            cur, cur_mc = cand, mc
        else:
            stall += 1
        if cur_mc > best:
            best = cur_mc
            log(f"it={it} BEST mincyc={best} (K={K}) m={len(cur)} edges={sorted(cur)}")
        if cur_mc > K:
            log(f"*** WITNESS *** n={n} edges={sorted(cur)}")
            import json
            with open("witness_climb.json", "w") as f:
                json.dump({"n": n, "edges": sorted(cur)}, f)
            break
        if stall > 300:
            log(f"it={it} restart (stalled at {cur_mc})")
            cur = fresh()
            cur_mc = M.min_cycles(n, cur, args.time_limit)
            stall = 0
        if it % 200 == 0:
            log(f"it={it} cur={cur_mc} best={best} m={len(cur)}")
    log(f"=== done: best={best} K={K} ===")


if __name__ == "__main__":
    main()
