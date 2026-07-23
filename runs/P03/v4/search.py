"""V4 search: maximize integrality gap tau - nu of the dijoin-packing ILP.

Background (why this IS the LP gap): the dicut clutter is ideal (Lucchesi-
Younger), hence its blocker, the dijoin clutter, is ideal (Lehman). Idealness
of the dijoin clutter gives that the fractional covering LP min{1x : x(J)>=1
for all dijoins J} has an integral optimum, i.e. equals tau. By LP duality
the fractional dijoin-packing LP therefore has value exactly tau on EVERY
digraph. So the LP/ILP integrality gap of dijoin packing is tau - nu, and
Woodall's conjecture is exactly "the gap is always 0". Any instance found
with nu <= tau - 1 is a counterexample.

Search: plateau-accepting hill climb (annealing-lite) over small multi-
digraphs, score = (tau - nu, tau, -m). Restricted to tau >= 3 (tau <= 2 is
settled). Parallel arcs allowed; weak connectivity enforced; isomorph-ish
rejection by cheap canonical key.
"""

import json
import os
import random
import sys
import time
from collections import Counter

from woodall import (min_dicut, max_packing, canon_key, all_dicuts,
                     is_strongly_connected, pack, condense_multi,
                     min_dicut_flow)

RESULTS = os.path.join(os.path.dirname(__file__), "results.jsonl")


def weakly_connected(n, arcs):
    if n == 0:
        return False
    adj = [[] for _ in range(n)]
    for (u, v) in arcs:
        adj[u].append(v)
        adj[v].append(u)
    seen = [False] * n
    stack = [0]
    seen[0] = True
    c = 1
    while stack:
        v = stack.pop()
        for w in adj[v]:
            if not seen[w]:
                seen[w] = True
                c += 1
                stack.append(w)
    return c == n


def random_digraph(rng, nmin=4, nmax=10, mmin=8, mmax=26):
    while True:
        n = rng.randint(nmin, nmax)
        m = rng.randint(max(mmin, n - 1), mmax)
        arcs = []
        for _ in range(m):
            u = rng.randrange(n)
            v = rng.randrange(n)
            while v == u:
                v = rng.randrange(n)
            arcs.append((u, v))
        if not weakly_connected(n, arcs):
            continue
        if is_strongly_connected(n, arcs):
            continue
        return n, tuple(arcs)


def mutate(rng, n, arcs, nmax=12, mmax=30):
    arcs = list(arcs)
    op = rng.random()
    if op < 0.30 and len(arcs) < mmax:
        u = rng.randrange(n)
        v = rng.randrange(n)
        while v == u:
            v = rng.randrange(n)
        arcs.append((u, v))
    elif op < 0.55 and len(arcs) > 4:
        arcs.pop(rng.randrange(len(arcs)))
    elif op < 0.80:  # rewire an endpoint
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        if rng.random() < 0.5:
            u = rng.randrange(n)
        else:
            v = rng.randrange(n)
        if u != v:
            arcs[i] = (u, v)
    elif op < 0.92 and n < nmax and len(arcs) < mmax:  # subdivide an arc
        i = rng.randrange(len(arcs))
        u, v = arcs.pop(i)
        w = n
        n += 1
        arcs.append((u, w))
        arcs.append((w, v))
    else:  # reverse an arc
        i = rng.randrange(len(arcs))
        u, v = arcs[i]
        arcs[i] = (v, u)
    return n, tuple(arcs)


def evaluate(n, arcs, time_limit=30, tau_lo=3, tau_hi=6):
    """Returns (tau, nu, n_min_dicuts) or None if tau outside [tau_lo,tau_hi].
    tau <= 2 is settled; very large tau instances are dense near-bipartite
    graphs that decompose trivially -- not the counterexample region."""
    try:
        cuts = all_dicuts(n, arcs)
        if not cuts:
            return None
        tau = min(len(c) for c in cuts)
        nmin = sum(1 for c in cuts if len(c) == tau)
    except ValueError:  # >20 condensation components: flow-based tau
        tau = min_dicut_flow(n, arcs)
        if tau is None:
            return None
        nmin = 1
    if tau < tau_lo or tau > tau_hi:
        return None
    tau2, nu = max_packing(n, arcs, tau=tau, time_limit=time_limit)
    return tau, nu, nmin


def log_result(rec):
    with open(RESULTS, "a") as f:
        f.write(json.dumps(rec) + "\n")


def run(seconds=3600, seed=0, tau_lo=3, tau_hi=6, nmax=12, mmax=30,
        log_every=200, init=None):
    rng = random.Random(seed)
    t0 = time.time()
    score_cache = {}
    stats = Counter()
    best_score = (-1,)
    cur = init
    cur_score = None
    evals = 0
    while time.time() - t0 < seconds:
        if cur is None or (init is None and rng.random() < 0.05):
            cand = random_digraph(rng, mmax=min(mmax, 26))
        elif rng.random() < 0.02 and init is not None:
            cand = init  # restart from the structured seed
        else:
            cand = mutate(rng, cur[0], cur[1], nmax=nmax, mmax=mmax)
        n, arcs = cand
        if not weakly_connected(n, arcs) or is_strongly_connected(n, arcs):
            continue
        # WLOG normalize to the multi-DAG condensation (tau and nu invariant)
        n, arcs = condense_multi(n, arcs)
        cand = (n, arcs)
        if not weakly_connected(n, arcs):
            continue
        key = canon_key(n, arcs)
        if key in score_cache:
            stats["dupe"] += 1
            cached = score_cache[key]
            # allow plateau movement onto already-seen states (no re-eval)
            if cached is not None and cur_score is not None \
                    and cached >= cur_score and rng.random() < 0.25:
                cur, cur_score = cand, cached
            continue
        res = evaluate(n, arcs, tau_lo=tau_lo, tau_hi=tau_hi)
        evals += 1
        if res is None:
            stats["tau_out_of_range"] += 1
            if len(score_cache) > 2_000_000:
                score_cache.clear()  # bound memory on multi-hour runs
            score_cache[key] = None
            # still allow moving there occasionally to escape
            if cur is None:
                cur = cand
                cur_score = (-1, 0, 0)
            continue
        tau, nu, nmin = res
        gap = tau - nu
        stats[f"tau{tau}gap{gap}"] += 1
        # hardness surrogate: many minimum dicuts, few arcs per unit tau --
        # tight instances where the packing ILP is most constrained.
        score = (gap, nmin, -len(arcs) / tau)
        if len(score_cache) > 2_000_000:
            score_cache.clear()
        score_cache[key] = score
        if gap >= 1:
            rec = {"event": "COUNTEREXAMPLE?", "n": n, "arcs": list(arcs),
                   "tau": tau, "nu": nu}
            log_result(rec)
            print("!!! GAP >= 1 FOUND:", rec, flush=True)
        if cur_score is None or score >= cur_score or rng.random() < 0.05:
            cur, cur_score = cand, score  # 5%: accept downhill (escape traps)
        if score > best_score:
            best_score = score
            log_result({"event": "best", "n": n, "arcs": list(arcs),
                        "tau": tau, "nu": nu, "t": round(time.time() - t0)})
        if evals % log_every == 0:
            print(f"[{time.time()-t0:8.0f}s] evals={evals} "
                  f"stats={dict(stats)} best={best_score}", flush=True)
    log_result({"event": "run_end", "seed": seed, "evals": evals,
                "seconds": seconds, "stats": dict(stats),
                "best_score": list(best_score)})
    print("DONE", evals, dict(stats), flush=True)


if __name__ == "__main__":
    seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 3600
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    tau_lo = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    tau_hi = int(sys.argv[4]) if len(sys.argv) > 4 else 6
    nmax = int(sys.argv[5]) if len(sys.argv) > 5 else 12
    mmax = int(sys.argv[6]) if len(sys.argv) > 6 else 30
    init = None
    if len(sys.argv) > 7:
        if sys.argv[7] == "schrijver":
            from schrijver_instance import N, ARCS
            init = (N, tuple(ARCS))
        elif sys.argv[7].startswith("ring"):
            from ring_family import ring_instance, scale_instance
            r = int(sys.argv[7][4:] or 5)
            n0, solid, dashed = ring_instance(r)
            nn, arcs0 = scale_instance(n0, solid, dashed, 1)
            init = (nn, tuple(arcs0))
    run(seconds=seconds, seed=seed, tau_lo=tau_lo, tau_hi=tau_hi,
        nmax=nmax, mmax=mmax, init=init)
