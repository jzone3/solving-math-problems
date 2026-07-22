"""Hunt for 'structurally tight' Hajos instances: Eulerian graphs with max degree
Dmax < 2K whose min cycle decomposition still reaches K = floor((n-1)/2).
Any such graph is tight for non-degree reasons -> prime V4 perturbation seed.
Records the max mincyc observed per (n, Dmax) regime.
"""
import random, sys, time, argparse
import mincyc as M


def random_eulerian(n, dmax, target_m, rng, tries=200):
    """Random even graph: start with random edge set near target_m via random
    T-joins: build by unioning random cycles until dense enough."""
    E = set()
    for _ in range(tries):
        L = rng.randrange(3, n + 1)
        vs = rng.sample(range(n), L)
        cyc = [(min(a, b), max(a, b)) for a, b in zip(vs, vs[1:] + vs[:1])]
        newE = E.symmetric_difference(cyc)
        deg = [0] * n
        for u, v in newE:
            deg[u] += 1
            deg[v] += 1
        if max(deg) <= dmax and len(newE) >= len(E):
            E = newE
        if len(E) >= target_m:
            break
    return list(E)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=14)
    ap.add_argument("--dmax", type=int, default=10)
    ap.add_argument("--samples", type=int, default=500)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--time-limit", type=float, default=180.0)
    ap.add_argument("--log", default=None)
    args = ap.parse_args()
    n, dmax = args.n, args.dmax
    K = (n - 1) // 2
    rng = random.Random(args.seed)
    lf = open(args.log or f"structural_n{n}_d{dmax}.txt", "a")

    def log(m):
        print(m, flush=True)
        lf.write(m + "\n")
        lf.flush()

    target_m = (n * dmax) // 2 - rng.randrange(0, 6)
    best = 0
    hist = {}
    log(f"=== structural hunt n={n} dmax={dmax} K={K} samples={args.samples} ===")
    for s in range(args.samples):
        E = random_eulerian(n, dmax, (n * dmax) // 2 - rng.randrange(0, 8) * 2, rng)
        if not E or not M.is_eulerian_simple(n, E):
            continue
        deg = [0] * n
        for u, v in E:
            deg[u] += 1
            deg[v] += 1
        if max(deg) > dmax:
            continue
        mc = M.min_cycles(n, E, args.time_limit)
        hist[mc] = hist.get(mc, 0) + 1
        if mc is not None and mc > best:
            best = mc
            log(f"s={s} NEW BEST mincyc={mc} (K={K}) m={len(E)} deg=[{min(deg)}..{max(deg)}] "
                f"edges={sorted(E)}")
            if mc > K:
                log("*** WITNESS ***")
                break
        if s % 50 == 0:
            log(f"s={s} best={best} hist={hist}")
    log(f"=== done n={n} dmax={dmax}: best={best} K={K} hist={hist} ===")


if __name__ == "__main__":
    main()
