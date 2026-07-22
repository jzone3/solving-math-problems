#!/usr/bin/env python3
"""
P03 V1 phase 2: search restricted to acyclic multi-digraphs (multi-DAGs).

Reduction: dicuts of D only contain arcs between strong components and
correspond exactly to dicuts of the condensation (a DAG, with arc
multiplicities). Arcs inside strong components lie in no dicut, so a dijoin
packing of the condensation lifts to D and vice versa. Hence WLOG a minimal
counterexample is a multi-DAG.

Modes:
  random NLO NHI MLO MHI MAXMULT SECONDS SEED  - random multi-DAGs
  anneal N M SECONDS SEED  - anneal maximizing dicut tightness at tau>=3
"""
import random, sys, time
from search import dicuts_and_tau, packs_into, report_counterexample


def rand_multidag(rng, n, m, maxmult):
    """Random DAG on topological order 0..n-1 with m arcs, mult <= maxmult."""
    arcs = []
    while len(arcs) < m:
        u = rng.randrange(n); v = rng.randrange(n)
        if u == v:
            continue
        if u > v:
            u, v = v, u
        mult = rng.randint(1, maxmult)
        for _ in range(min(mult, m - len(arcs))):
            arcs.append((u, v))
    return arcs


def analyze(n, arcs):
    cuts, tau = dicuts_and_tau(n, arcs)
    if cuts is None or tau < 2:
        return None
    ok, st = packs_into(len(arcs), cuts, tau)
    return cuts, tau, ok, st


def mode_random(nlo, nhi, mlo, mhi, maxmult, seconds, seed):
    rng = random.Random(seed)
    t0 = time.time(); cnt = 0; bytau = {}
    while time.time() - t0 < seconds:
        n = rng.randint(nlo, nhi)
        m = rng.randint(max(mlo, n - 1), mhi)
        arcs = rand_multidag(rng, n, m, maxmult)
        r = analyze(n, arcs)
        if r is None:
            continue
        cuts, tau, ok, st = r
        cnt += 1; bytau[tau] = bytau.get(tau, 0) + 1
        if not ok:
            report_counterexample(n, arcs, tau)
        if cnt % 20000 == 0:
            print(f"[dagrand seed={seed}] checked={cnt} bytau={sorted(bytau.items())} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[dagrand seed={seed}] DONE checked={cnt} bytau={sorted(bytau.items())}", flush=True)


def tightness(cuts, tau, m):
    """Score how constrained the packing is: many minimal dicuts, many of them
    tight (= tau), few arcs to spare."""
    tight = sum(1 for c in cuts if len(c) == tau)
    slack = sum(len(c) - tau for c in cuts)
    return 100 * tight + 5 * len(cuts) - slack - m


def mode_anneal(n, mmax, seconds, seed):
    rng = random.Random(seed)
    t0 = time.time(); steps = 0
    cur = None; cur_s = -10**9; best_s = -10**9
    while time.time() - t0 < seconds:
        steps += 1
        if cur is None or rng.random() < 0.001:
            cand = rand_multidag(rng, n, rng.randint(n, mmax), 3)
        else:
            cand = list(cur)
            op = rng.random()
            if op < 0.35 and len(cand) > n - 1:
                cand.pop(rng.randrange(len(cand)))
            elif op < 0.75 and len(cand) < mmax:
                u = rng.randrange(n); v = rng.randrange(n)
                if u == v:
                    continue
                cand.append((min(u, v), max(u, v)))
            else:
                i = rng.randrange(len(cand))
                u = rng.randrange(n); v = rng.randrange(n)
                if u == v:
                    continue
                cand[i] = (min(u, v), max(u, v))
        r = analyze(n, cand)
        if r is None:
            continue
        cuts, tau, ok, st = r
        if not ok:
            report_counterexample(n, cand, tau)
            continue
        if tau < 3:
            continue
        s = tightness(cuts, tau, len(cand))
        if s >= cur_s or rng.random() < 0.03:
            cur, cur_s = cand, s
        if s > best_s:
            best_s = s
            print(f"[daganneal seed={seed}] step={steps} best={s} tau={tau} m={len(cand)} "
                  f"cuts={len(cuts)} tight={sum(1 for c in cuts if len(c)==tau)} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[daganneal seed={seed}] DONE steps={steps} best={best_s}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    a = sys.argv[2:]
    if mode == "random":
        mode_random(int(a[0]), int(a[1]), int(a[2]), int(a[3]), int(a[4]),
                    float(a[5]), int(a[6]))
    elif mode == "anneal":
        mode_anneal(int(a[0]), int(a[1]), float(a[2]), int(a[3]))
