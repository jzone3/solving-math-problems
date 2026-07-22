#!/usr/bin/env python3
"""
P03 V1 (DGG playbook): direct counterexample search for Woodall's conjecture.

Woodall: in every digraph, min size of a nonempty dicut (tau) equals the max
number of pairwise disjoint dijoins.  Since any superset of a dijoin is a
dijoin, k disjoint dijoins exist iff the arc set can be PARTITIONED into k
dijoins.  So a counterexample is a digraph where the arcs cannot be
partitioned into tau dijoins (each part hitting every dicut).

Pipeline per candidate digraph D=(V,A) (multi-arcs allowed, no loops):
  1. must be weakly connected, not strongly connected (else no dicut exists)
  2. enumerate all dicuts: U with delta^-(U)=0, dicut = delta^+(U); keep the
     inclusion-minimal ones (clauses for others are implied); tau = min size
  3. SAT feasibility: color each arc with one of tau colors, each minimal
     dicut must contain every color.  Symmetry break: the tau arcs of one
     minimum dicut get distinct fixed colors.
  4. UNSAT => COUNTEREXAMPLE (tau disjoint dijoins impossible).

Modes:
  exhaustive N        - all simple digraphs on N labeled vertices (N<=5 sane)
  random N_LO N_HI M_LO M_HI SECONDS  - random multi-digraph sampling
  anneal N M SECONDS  - hill-climb/anneal on SAT hardness at tau>=3
"""
import itertools, random, sys, time
from pysat.solvers import Cadical153


def dicuts_and_tau(n, arcs):
    """Return (list of inclusion-minimal dicuts as frozensets of arc indices, tau).
    Returns (None, None) if there is no dicut (strongly connected) or graph
    is weakly disconnected."""
    # weak connectivity
    adj = [set() for _ in range(n)]
    for (u, v) in arcs:
        adj[u].add(v); adj[v].add(u)
    seen = {0}; stack = [0]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y); stack.append(y)
    if len(seen) != n:
        return None, None
    cuts = []
    for U in range(1, (1 << n) - 1):
        indeg = 0
        cut = []
        for i, (u, v) in enumerate(arcs):
            uin = (U >> u) & 1
            vin = (U >> v) & 1
            if vin and not uin:
                indeg = 1
                break
            if uin and not vin:
                cut.append(i)
        if not indeg:
            cuts.append(frozenset(cut))
    if not cuts:
        return None, None
    # inclusion-minimal only
    cuts = sorted(set(cuts), key=len)
    minimal = []
    for c in cuts:
        if not any(m <= c for m in minimal):
            minimal.append(c)
    tau = len(minimal[0])
    return minimal, tau


def packs_into(n_arcs, min_dicuts, k):
    """SAT: can arcs be partitioned into k dijoins? Returns (bool, stats)."""
    tau_cut = min(min_dicuts, key=len)
    var = lambda a, c: a * k + c + 1
    s = Cadical153()
    for a in range(n_arcs):
        s.add_clause([var(a, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                s.add_clause([-var(a, c1), -var(a, c2)])
    for cut in min_dicuts:
        for c in range(k):
            s.add_clause([var(a, c) for a in cut])
    # symmetry break: distinct colors on one min dicut (|cut| == tau >= k)
    for c, a in enumerate(sorted(tau_cut)[:k]):
        s.add_clause([var(a, c)])
    ok = s.solve()
    st = s.accum_stats()
    s.delete()
    return ok, st


def check(n, arcs):
    """Returns (tau, packs, stats) or None if no dicut / disconnected."""
    cuts, tau = dicuts_and_tau(n, arcs)
    if cuts is None or tau == 0:
        return None
    if tau == 1:
        return (1, True, {})
    ok, st = packs_into(len(arcs), cuts, tau)
    return (tau, ok, st)


def report_counterexample(n, arcs, tau):
    print("!!! COUNTEREXAMPLE CANDIDATE !!!", flush=True)
    print("n =", n, "arcs =", sorted(arcs), "tau =", tau, flush=True)
    with open("counterexample.txt", "a") as f:
        f.write(f"n={n} tau={tau} arcs={sorted(arcs)}\n")


def mode_exhaustive(n):
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    total = 1 << len(pairs)
    t0 = time.time()
    stats = {"checked": 0, "bytau": {}}
    for mask in range(1, total):
        arcs = [pairs[i] for i in range(len(pairs)) if (mask >> i) & 1]
        r = check(n, arcs)
        if r is None:
            continue
        tau, ok, _ = r
        stats["checked"] += 1
        stats["bytau"][tau] = stats["bytau"].get(tau, 0) + 1
        if not ok:
            report_counterexample(n, arcs, tau)
        if mask % 100000 == 0:
            print(f"[exh n={n}] {mask}/{total} checked={stats['checked']} "
                  f"bytau={stats['bytau']} t={time.time()-t0:.0f}s", flush=True)
    print(f"[exh n={n}] DONE {stats} t={time.time()-t0:.0f}s", flush=True)


def rand_digraph(rng, n, m):
    arcs = []
    for _ in range(m):
        u = rng.randrange(n); v = rng.randrange(n)
        while v == u:
            v = rng.randrange(n)
        arcs.append((u, v))
    return arcs


def mode_random(nlo, nhi, mlo, mhi, seconds, seed):
    rng = random.Random(seed)
    t0 = time.time()
    cnt = 0; bytau = {}
    while time.time() - t0 < seconds:
        n = rng.randint(nlo, nhi)
        m = rng.randint(max(mlo, n - 1), mhi)
        arcs = rand_digraph(rng, n, m)
        r = check(n, arcs)
        if r is None:
            continue
        tau, ok, _ = r
        cnt += 1
        bytau[tau] = bytau.get(tau, 0) + 1
        if not ok:
            report_counterexample(n, arcs, tau)
        if cnt % 20000 == 0:
            print(f"[rand seed={seed}] checked={cnt} bytau={sorted(bytau.items())} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[rand seed={seed}] DONE checked={cnt} bytau={sorted(bytau.items())}", flush=True)


def hardness(st):
    return st.get("conflicts", 0) if st else 0


def mode_anneal(n, m, seconds, seed):
    """Hill-climb on SAT conflicts among tau>=3 instances (hard-instance hunt)."""
    rng = random.Random(seed)
    t0 = time.time()
    cur = None; cur_h = -1
    best_h = -1
    steps = 0
    while time.time() - t0 < seconds:
        steps += 1
        if cur is None:
            cand = rand_digraph(rng, n, m)
        else:
            cand = list(cur)
            op = rng.random()
            if op < 0.4 and len(cand) > n:
                cand.pop(rng.randrange(len(cand)))
            elif op < 0.8:
                u = rng.randrange(n); v = rng.randrange(n)
                if u != v:
                    cand.append((u, v))
            else:
                i = rng.randrange(len(cand))
                u = rng.randrange(n); v = rng.randrange(n)
                if u != v:
                    cand[i] = (u, v)
        r = check(n, cand)
        if r is None:
            continue
        tau, ok, st = r
        if not ok:
            report_counterexample(n, cand, tau)
            continue
        if tau < 3:
            continue
        h = hardness(st) + tau * 5
        if h >= cur_h or rng.random() < 0.05:
            cur, cur_h = cand, h
        if h > best_h:
            best_h = h
            print(f"[anneal seed={seed}] step={steps} new best hardness={h} tau={tau} "
                  f"m={len(cand)} t={time.time()-t0:.0f}s", flush=True)
    print(f"[anneal seed={seed}] DONE steps={steps} best_h={best_h}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "exhaustive":
        mode_exhaustive(int(sys.argv[2]))
    elif mode == "random":
        mode_random(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]),
                    int(sys.argv[5]), float(sys.argv[6]), int(sys.argv[7]))
    elif mode == "anneal":
        mode_anneal(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]),
                    int(sys.argv[5]))
