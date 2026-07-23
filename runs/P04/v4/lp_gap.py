"""Wave 3a: LP/ILP duality-gap attack (METHODOLOGY V4 framing).

Fractional cycle decomposition number: min sum_C x_C s.t. for every edge e,
sum_{C ni e} x_C = 1, x >= 0 over all cycles C.  Solved by column generation:
  master LP over a restricted cycle pool; pricing = find a cycle with weight
  sum_e dual_e > 1 (positive reduced profit), i.e. a max-weight cycle w.r.t.
  duals -- found via DFS branch-and-bound (graphs here are small).
LP* <= ILP* = mincyc(G).  If we ever certify LP* > K, that graph is a
counterexample with an LP certificate.  More realistically: search (anneal) for
graphs maximizing gap = mincyc - ceil(LP*); large-gap graphs show where integer
obstructions live and are prime perturbation seeds.
"""
import itertools, random, time, argparse
import pulp
import mincyc as M
from search import toggle_even_set, valid, canon, degrees


def all_short_cycles(n, edges, maxlen=7, cap=20000):
    """Seed pool: all cycles up to maxlen (canonical: min vertex first, direction)."""
    adj = [[] for _ in range(n)]
    Eset = set(canon(edges))
    for u, v in Eset:
        adj[u].append(v)
        adj[v].append(u)
    cycles = set()

    def dfs(start, cur, path, visited):
        if len(path) > maxlen:
            return
        for w in adj[cur]:
            if w == start and len(path) >= 3:
                cyc = frozenset((min(a, b), max(a, b))
                                for a, b in zip(path, path[1:] + [start]))
                cycles.add(cyc)
                if len(cycles) >= cap:
                    return
            elif w not in visited and w > start:
                dfs(start, w, path + [w], visited | {w})

    for s in range(n):
        dfs(s, s, [s], {s})
        if len(cycles) >= cap:
            break
    return [sorted(c) for c in cycles]


def max_weight_cycle(n, edges, w, eps=1e-9):
    """Find a cycle maximizing sum of edge weights; exact DFS with an optimistic
    bound (sum of positive weights).  Returns (weight, cycle_edges) or None."""
    Eset = sorted(set(canon(edges)))
    adj = {}
    for u, v in Eset:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    wmap = {e: w[e] for e in Eset}
    best = [1.0 + 1e-7, None]  # only care about weight > 1
    pos_total = sum(x for x in w.values() if x > 0)

    def dfs(start, cur, used, weight, visited):
        if weight + (pos_total - sum(max(wmap[e], 0) for e in used)) <= best[0]:
            pass  # weak bound; rely on size limits below
        for nxt in adj[cur]:
            e = (min(cur, nxt), max(cur, nxt))
            if e in used:
                continue
            if nxt == start and len(used) >= 2:
                tw = weight + wmap[e]
                if tw > best[0] + eps:
                    best[0] = tw
                    best[1] = used | {e}
            elif nxt not in visited and nxt > start:
                dfs(start, nxt, used | {e}, weight + wmap[e], visited | {nxt})

    for s in sorted(adj):
        dfs(s, s, frozenset(), 0.0, frozenset([s]))
    if best[1] is None:
        return None
    return best[0], sorted(best[1])


def frac_cycle_decomp(n, edges, time_budget=120.0, verbose=False):
    """Column generation for the fractional cycle decomposition LP.
    Returns (lp_value, n_columns, converged)."""
    E = sorted(set(canon(edges)))
    pool = {frozenset(c) for c in all_short_cycles(n, E, maxlen=min(5, n), cap=4000)}
    t0 = time.time()
    while True:
        prob = pulp.LpProblem("fcd", pulp.LpMinimize)
        cols = [sorted(c) for c in pool]
        x = [pulp.LpVariable(f"x{i}", lowBound=0) for i in range(len(cols))]
        prob += pulp.lpSum(x)
        con = {}
        for e in E:
            c_ = pulp.lpSum(x[i] for i, c in enumerate(cols) if e in set(map(tuple, c)))
            prob += c_ == 1, f"e{e[0]}_{e[1]}"
            con[e] = f"e{e[0]}_{e[1]}"
        prob.solve(pulp.PULP_CBC_CMD(msg=0))
        if pulp.LpStatus[prob.status] != "Optimal":
            return None, len(pool), False
        duals = {e: prob.constraints[con[e]].pi for e in E}
        lp_val = pulp.value(prob.objective)
        if time.time() - t0 > time_budget:
            return lp_val, len(pool), False
        found = max_weight_cycle(n, E, duals)
        if found is None:
            return lp_val, len(pool), True
        _, cyc = found
        key = frozenset(map(tuple, cyc))
        if key in pool:
            return lp_val, len(pool), True
        pool.add(key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=13)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--iters", type=int, default=400)
    args = ap.parse_args()
    n = args.n
    K = (n - 1) // 2
    rng = random.Random(args.seed)
    lf = open(f"lp_gap_n{n}_s{args.seed}.txt", "a")

    def log(m_):
        print(m_, flush=True)
        lf.write(m_ + "\n")
        lf.flush()

    # seed: clique tree of K5s for odd n (structurally tight)
    E = []
    start = 0
    while True:
        vs = list(range(start, start + 5))
        E += [(vs[i], vs[j]) for i in range(5) for j in range(i + 1, 5)]
        start += 4
        if start + 4 >= n + 1:
            break
    cur = sorted(canon(E))
    best_gap = -1
    log(f"=== lp-gap anneal n={n} K={K} ===")
    for it in range(args.iters):
        cand = toggle_even_set(n, cur, rng, max_len=8) if it else list(cur)
        if cand is None or not valid(n, cand):
            continue
        mc = M.min_cycles(n, cand, 300)
        if mc is None:
            continue
        lp, ncols, conv = frac_cycle_decomp(n, cand)
        if lp is None:
            continue
        gap = mc - lp
        if lp > K + 1e-6:
            log(f"*** LP WITNESS *** n={n} lp={lp} edges={sorted(canon(cand))}")
            return
        if gap >= best_gap - 1e-9:
            if gap > best_gap + 1e-9:
                best_gap = gap
                log(f"it={it} BEST gap={gap:.3f} mc={mc} lp={lp:.3f} conv={conv} "
                    f"m={len(cand)} edges={sorted(canon(cand))}")
            cur = sorted(canon(cand))
        if it % 25 == 0:
            log(f"it={it} mc={mc} lp={lp:.3f} gap={gap:.3f} best={best_gap:.3f} "
                f"m={len(cand)} cols={ncols} conv={conv}")
    log(f"=== done best_gap={best_gap:.3f} ===")


if __name__ == "__main__":
    main()
