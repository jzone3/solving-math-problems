"""V4 extremal-family perturbation search for Hajos' conjecture (P04).

Strategy: start from families achieving the bound K = floor((n-1)/2) with equality
(K_{2k+1} and dense Eulerian relatives), apply parity-preserving perturbations:
  (a) vertex splits (odd n -> n+1 keeps K constant),
  (b) toggling even-degree edge sets in the "symmetric difference" sense
      (each vertex incident to an even number of toggled pairs),
and test decomposability into <= K cycles.  Infeasible instance => counterexample.
Instances that stay tight (mincyc == K) are retained in a pool and perturbed further.
"""
import random, sys, time, json, argparse
import mincyc as M


def canon(edges):
    return tuple(sorted((min(u, v), max(u, v)) for u, v in edges))


def degrees(n, edges):
    d = [0] * n
    for u, v in edges:
        d[u] += 1
        d[v] += 1
    return d


def toggle_even_set(n, edges, rng, max_len=6):
    """Toggle a closed (even) set of vertex pairs: random closed walk on vertex
    pairs => pick a cycle v0 v1 ... vL v0 in K_n and flip each pair (vi, vi+1)."""
    E = set(canon(edges))
    L = rng.choice(list(range(3, max_len + 1)))
    vs = rng.sample(range(n), L)
    T = [(min(a, b), max(a, b)) for a, b in zip(vs, vs[1:] + vs[:1])]
    if len(set(T)) != L:
        return None
    newE = E.symmetric_difference(T)
    return list(newE)


def vertex_split(n, edges, rng):
    """Split a vertex v of degree >= 6 into v and a new vertex n, moving an even
    number (>=2, <=deg-2... keep both even and >=2... for Eulerian keep >=2) of
    its edges to the new vertex.  Optionally add edge (v, n)?  No: adding (v,n)
    would make both odd; keep them non-adjacent so parity is preserved."""
    deg = degrees(n, edges)
    cands = [v for v in range(n) if deg[v] >= 6]
    if not cands:
        return None
    v = rng.choice(cands)
    incident = [i for i, e in enumerate(edges) if v in e]
    k = rng.choice(range(2, deg[v] - 1, 2))  # move even count, leave >= 2
    moved = set(rng.sample(incident, k))
    newE = []
    for i, (a, b) in enumerate(edges):
        if i in moved:
            newE.append((n if a == v else a, n if b == v else b))
        else:
            newE.append((a, b))
    return n + 1, newE


def valid(n, edges):
    if not edges:
        return False
    try:
        return M.is_eulerian_simple(n, edges)
    except AssertionError:
        return False


def check(n, edges, time_limit, log):
    K = (n - 1) // 2
    t0 = time.time()
    ok, sol = M.decomposable_within(n, edges, K, time_limit)
    dt = time.time() - t0
    if ok is False:
        log(f"*** WITNESS CANDIDATE *** n={n} m={len(edges)} K={K} INFEASIBLE "
            f"edges={canon(edges)}")
        return "WITNESS", dt
    if ok is None:
        log(f"TIMEOUT n={n} m={len(edges)} K={K} t={dt:.0f}s edges={canon(edges)}")
        return "TIMEOUT", dt
    # feasible at K; is it tight (infeasible at K-1)?
    ok2, _ = M.decomposable_within(n, edges, K - 1, time_limit)
    return ("TIGHT" if ok2 is False else ("LOOSE" if ok2 else "TIGHT?")), dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters", type=int, default=200)
    ap.add_argument("--time-limit", type=float, default=120.0)
    ap.add_argument("--start", default="k13",
                    help="k13|k13split|k15|k11|k14mpm|k16mpm|k15split|"
                         "bouquet:7,7|cliquetree:5,5,5 (path-glued cliques)")
    ap.add_argument("--log", default="search_log.txt")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    lf = open(args.log, "a")

    def log(msg):
        print(msg, flush=True)
        lf.write(msg + "\n")
        lf.flush()

    if args.start.startswith("bouquet:") or args.start.startswith("cliquetree:"):
        sizes = [int(x) for x in args.start.split(":")[1].split(",")]
        E0 = []
        if args.start.startswith("bouquet:"):
            n0, nxt = 1 + sum(s - 1 for s in sizes), 1
            for s in sizes:
                vs = [0] + list(range(nxt, nxt + s - 1))
                nxt += s - 1
                E0 += [(vs[i], vs[j]) for i in range(s) for j in range(i + 1, s)]
        else:  # cliquetree: path of cliques, consecutive cliques share one vertex
            n0 = sum(s for s in sizes) - (len(sizes) - 1)
            start = 0
            for s in sizes:
                vs = list(range(start, start + s))
                E0 += [(vs[i], vs[j]) for i in range(s) for j in range(i + 1, s)]
                start += s - 1
    elif args.start in ("k14mpm", "k16mpm"):
        n0 = 14 if args.start == "k14mpm" else 16
        E0 = [(i, j) for i in range(n0) for j in range(i + 1, n0)
              if not (j == i + 1 and i % 2 == 0)]
    else:
        base = {"k11": 11, "k13": 13, "k15": 15, "k13split": 13,
                "k15split": 15}[args.start]
        n0, E0 = M.complete_graph(base)
    pool = [(n0, E0)]
    if args.start in ("k13split", "k15split"):
        for _ in range(50):
            r = vertex_split(n0, E0, rng)
            if r and valid(*r):
                pool = [r]
                break
    seen = set()
    stats = {"TIGHT": 0, "LOOSE": 0, "TIMEOUT": 0, "WITNESS": 0, "invalid": 0}
    log(f"=== search start seed={args.seed} start={args.start} iters={args.iters} ===")
    for it in range(args.iters):
        # bias selection toward denser (higher m) pool members
        weights = [len(e) ** 2 for _, e in pool]
        n, E = rng.choices(pool, weights=weights)[0]
        move = rng.random()
        if move < 0.25 and n % 2 == 1:
            r = vertex_split(n, E, rng)
        elif move < 0.5:
            # double toggle: two independent closed-set flips
            r1 = toggle_even_set(n, E, rng, max_len=8)
            r = toggle_even_set(n, r1, rng, max_len=8) if r1 else None
            r = (n, r) if r else None
        else:
            r = toggle_even_set(n, E, rng, max_len=8)
            r = (n, r) if r else None
        if r is None or not valid(*r):
            stats["invalid"] += 1
            continue
        nn, EE = r
        key = (nn, canon(EE))
        if key in seen:
            continue
        seen.add(key)
        res, dt = check(nn, EE, args.time_limit, log)
        stats[res if res in stats else "TIMEOUT"] = stats.get(res, 0) + 1
        deg = degrees(nn, EE)
        log(f"it={it} n={nn} m={len(EE)} deg=[{min(d for d in deg if d)}..{max(deg)}] "
            f"res={res} t={dt:.1f}s pool={len(pool)}")
        if res == "WITNESS":
            with open("witness.json", "w") as f:
                json.dump({"n": nn, "edges": canon(EE)}, f)
            log("WITNESS SAVED -- stopping")
            break
        if res in ("TIGHT", "TIGHT?"):
            if max(deg) < 2 * ((nn - 1) // 2):
                log(f"STRUCTURAL-TIGHT n={nn} m={len(EE)} edges={canon(EE)}")
            pool.append((nn, EE))
            if len(pool) > 40:
                pool.pop(1)
    log(f"=== done: {stats} pool_final={len(pool)} distinct_checked={len(seen)} ===")


if __name__ == "__main__":
    main()
