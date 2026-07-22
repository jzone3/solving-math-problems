"""Phase 2 of V2: anneal AROUND the subdivided/parallelized seeds.

Start points: random subdivision-transforms of D1/D2 (and the tau>=3 middle
multiplied variant).  Local moves: reroute an arc endpoint, add / delete an
arc, subdivide an arc, smooth a subdivision vertex.  Constraints kept: weakly
connected, tau >= 3, |A| <= max_arcs.

Objective (maximize): primarily the ACZ parameter rho (a counterexample needs
rho >= 3, rho >= 4 if tau=3), secondarily the CBC solve time of the packing
ILP (hard-to-pack instances are "closer" to failure).  Any instance where the
packing ILP is INFEASIBLE is a candidate counterexample: dumped to JSON and
printed loudly.
"""
import json
import random
import time

import core
import seeds
from search_subdiv import transform


def random_start(rng):
    which = rng.random()
    if which < 0.4:
        n, arcs, w = seeds.D1_n, seeds.D1_arcs, seeds.D1_w
        sm = None
        if rng.random() < 0.5:
            sm = [rng.choice((2, 3)) if j in (1, 4, 7) else 1 for j in range(9)]
        nc = [rng.choice((1, 2, 3)) for _ in range(w.count(0))]
        return transform(n, arcs, w, nc, solid_mult=sm)
    elif which < 0.8:
        n, arcs, w = seeds.D2_n, seeds.D2_arcs, seeds.D2_w
        nc = [rng.choice((1, 2, 3)) for _ in range(w.count(0))]
        return transform(n, arcs, w, nc)
    else:
        # random digraph, same scale
        nn = rng.randint(8, 16)
        m = rng.randint(nn + 4, min(30, 2 * nn + 6))
        arcs = []
        while len(arcs) < m:
            u, v = rng.randrange(nn), rng.randrange(nn)
            if u != v:
                arcs.append((u, v))
        return nn, arcs


def weakly_connected(n, arcs):
    if n == 0:
        return False
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    st = [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def mutate(n, arcs, rng, max_arcs=34):
    arcs = list(arcs)
    op = rng.random()
    if op < 0.3 and arcs:  # reroute
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        if rng.random() < 0.5:
            u = rng.randrange(n)
        else:
            v = rng.randrange(n)
        if u != v:
            arcs[i] = (u, v)
    elif op < 0.5 and len(arcs) < max_arcs:  # add
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            arcs.append((u, v))
    elif op < 0.65 and len(arcs) > n:  # delete
        arcs.pop(rng.randrange(len(arcs)))
    elif op < 0.85 and len(arcs) < max_arcs and arcs:  # subdivide
        i = rng.randrange(len(arcs))
        u, v = arcs.pop(i)
        arcs.append((u, n))
        arcs.append((n, v))
        n += 1
    else:  # smooth a vertex with indeg=outdeg=1
        cand = []
        for x in range(n):
            ins = [i for i, a in enumerate(arcs) if a[1] == x]
            outs = [i for i, a in enumerate(arcs) if a[0] == x]
            if len(ins) == 1 and len(outs) == 1:
                cand.append((x, ins[0], outs[0]))
        if cand:
            x, i_in, i_out = rng.choice(cand)
            u = arcs[i_in][0]
            v = arcs[i_out][1]
            if u != v:
                newarcs = [a for j, a in enumerate(arcs)
                           if j not in (i_in, i_out)]
                newarcs.append((u, v))
                # relabel to drop x
                relab = {y: (y if y < x else y - 1) for y in range(n)}
                arcs = [(relab[a], relab[b]) for (a, b) in newarcs]
                n -= 1
    return n, arcs


def evaluate(n, arcs, ilp_budget=60):
    """Return (feasible_packing, score tuple, tau, rho)."""
    if not weakly_connected(n, arcs):
        return None
    t, _ = core.tau(n, arcs)
    if t is None or t < 3:
        return None
    r = core.rho(n, arcs, t)
    need = 4 if t == 3 else 3
    if r < need:
        return (True, (r, 0.0), t, r)  # provably packs; keep rho as score
    cuts = core.minimal_dicuts(core.all_dicuts(n, arcs))
    t0 = time.time()
    ok = core.packing_exists(n, arcs, t, cuts=cuts, time_limit=ilp_budget)
    dt = time.time() - t0
    if ok is False:
        return (False, (r, dt), t, r)
    if ok is None:
        return (True, (r, dt), t, r)  # timeout: suspicious, treat as hot
    return (True, (r, dt), t, r)


def main(iters=200000, wall=3600 * 3, seed=1, ilp_budget=60):
    rng = random.Random(seed)
    t_end = time.time() + wall
    best_ever = None
    stats = {"steps": 0, "evals": 0, "fails": 0, "restarts": 0}
    while time.time() < t_end:
        stats["restarts"] += 1
        state = random_start(rng)
        ev = evaluate(*state, ilp_budget)
        tries = 0
        cur_score = ev[1] if ev else (-1, 0)
        while tries < 400 and time.time() < t_end:
            tries += 1
            stats["steps"] += 1
            cand = mutate(state[0], state[1], rng)
            ev = evaluate(*cand, ilp_budget)
            if ev is None:
                continue
            stats["evals"] += 1
            feas, score, t, r = ev
            if not feas:
                stats["fails"] += 1
                rec = {"n": cand[0], "arcs": cand[1], "tau": t, "rho": r}
                print("!!! PACKING FAILURE:", json.dumps(rec), flush=True)
                with open("hits_anneal.json", "a") as f:
                    f.write(json.dumps(rec) + "\n")
            # simulated-annealing-lite: accept improving or with small prob
            if score >= cur_score or rng.random() < 0.15:
                state, cur_score = cand, score
            if best_ever is None or score > best_ever[0]:
                best_ever = (score, cand[0], len(cand[1]), t, r)
            if stats["steps"] % 2000 == 0:
                print(f"[anneal seed={seed}] {stats} best={best_ever}",
                      flush=True)
    print(f"FINAL [anneal seed={seed}] {stats} best={best_ever}", flush=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--wall", type=int, default=10800)
    ap.add_argument("--ilp-budget", type=int, default=60)
    a = ap.parse_args()
    main(wall=a.wall, seed=a.seed, ilp_budget=a.ilp_budget)
