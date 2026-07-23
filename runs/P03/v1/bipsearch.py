#!/usr/bin/env python3
"""
Phase 4: direct attack on the smallest open case via ACZ's reduction.

Abdi-Cornuejols-Zlatin (arXiv:2202.00392, Decompose-Lift-Reduce) prove that
unweighted Woodall for tau>=3 holds iff it holds for sink-regular
(tau,tau+1)-bipartite digraphs: arcs go source->sink, every sink has
in-degree exactly tau, every source out-degree tau or tau+1. tau=2 is
folklore-true, so tau=3 sink-regular (3,4)-bipartite digraphs are THE
smallest open case (D27 lives here: 12 sources, 15 sinks).

Structure exploited: in a bipartite source->sink digraph, every dicut
delta^+(U) is determined by S = U cap sources (U must contain every sink all
of whose in-neighbours lie in S, and may not contain any other sink for
minimality). So dicuts <-> nonempty proper subsets S of sources, and with
p sources the full dicut enumeration is a 2^p bitmask sweep - lightning fast
for p<=20. An instance is just a list of q in-neighbour triples.

check(): tau (min dicut) must be 3; SAT-check whether arcs 3-colour so every
minimal dicut contains all 3 colours (packing <-> partition into 3 dijoins,
by upward-closedness). UNSAT => counterexample to Woodall.

Modes:
  exhaustive P Q  - all multisets of Q triples over C(P,3), isomorph-reduced
                    by requiring the triple list to be lexicographically
                    minimal under source permutations (orderly-ish filter).
  random P Q SECONDS SEED
  anneal SECONDS SEED   - anneal around D27 (12 sources, 15 sinks).
"""
import random, sys, time
from itertools import combinations
from pysat.solvers import Cadical153

D27_SOLID = [(2,1),(12,1),(12,14),(15,14),(15,9),(6,9),(6,16),(6,16),(2,13),(2,13),
             (4,3),(4,17),(4,3),(18,17),(8,19),(8,20),(8,20),(0,5),(22,5),(22,23),
             (24,23),(24,7),(11,7),(0,21),(11,10),(26,19),(18,25),(26,25),(11,10),(0,21)]
D27_DASH = [(11,19),(18,10),(18,13),(12,21),(0,14),(15,5),(8,9),(6,7),(22,16),
            (22,3),(4,23),(24,17),(12,20),(2,25),(26,1)]


def d27_sinklists():
    """D27 as (p, list of per-sink in-neighbour lists)."""
    arcs = D27_SOLID + D27_DASH
    ind = {}
    for (u, v) in arcs:
        ind.setdefault(v, []).append(u)
    sources = sorted(set(u for u, _ in arcs))
    smap = {s: i for i, s in enumerate(sources)}
    return len(sources), [sorted(smap[u] for u in ins) for ins in ind.values()]


def min_dicuts_bip(p, sinks):
    """sinks: list of in-neighbour lists (each of length 3, entries < p).
    Returns (minimal dicuts as list of frozensets of arc ids, tau) or
    (None, None) if some dicut is empty / degenerate.
    Arc id = (sink index, position)."""
    q = len(sinks)
    smask = [0] * q
    for t, ins in enumerate(sinks):
        m = 0
        for u in ins:
            m |= 1 << u
        smask[t] = m
    # skip if some source unused (out-degree 0 => it is a sink-side vertex)
    allm = 0
    for m in smask:
        allm |= m
    if allm != (1 << p) - 1:
        return None, None
    # Dicuts delta^+(U): U = S cup T with S subset of sources, T subset of
    # sinks fully covered by S (no arc may enter U). For fixed S the unique
    # inclusion-minimal candidate with nonempty cut is either T = Tmax(S)
    # (all covered sinks), or - when cut(S, Tmax) is empty ("closed" U) -
    # T = Tmax minus one covered sink t, giving cut = in(t). The latter are
    # all subsumed by {in(t) : t any sink}, each of which IS a dicut
    # (U = V - {t}), so tau <= 3 always in this class.
    cuts = set(frozenset((t, pos) for pos in range(len(sinks[t]))) for t in range(q))
    for S in range(1, (1 << p) - 1):
        cut = []
        for t in range(q):
            m = smask[t]
            if m & S and (m & S) != m:
                for pos, u in enumerate(sinks[t]):
                    if (S >> u) & 1:
                        cut.append((t, pos))
        if cut:
            cuts.add(frozenset(cut))
    # S = all sources: cuts from excluding covered sinks = in(t), already added
    uniq = sorted(cuts, key=len)
    minimal = []
    for c in uniq:
        if not any(m <= c for m in minimal):
            minimal.append(c)
    return minimal, len(minimal[0])


def packs3(sinks, cuts):
    k = 3
    ids = {}
    def var(a, c):
        key = (a, c)
        if key not in ids:
            ids[key] = len(ids) + 1
        return ids[key]
    s = Cadical153()
    arcs = set()
    for c in cuts:
        arcs |= c
    for a in arcs:
        s.add_clause([var(a, c) for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                s.add_clause([-var(a, c1), -var(a, c2)])
    for cut in cuts:
        for c in range(k):
            s.add_clause([var(a, c) for a in cut])
    r = s.solve()
    s.delete()
    return r


def check(p, sinks, out=None):
    cuts, tau = min_dicuts_bip(p, sinks)
    if cuts is None or tau != 3:
        return None
    ok = packs3(sinks, cuts)
    if not ok:
        msg = f"UNSAT COUNTEREXAMPLE p={p} sinks={sinks}"
        print(msg, flush=True)
        with open("counterexample.txt", "a") as f:
            f.write(msg + "\n")
    return ok


def canonical_min(p, sinks):
    """True if the sorted triple list is lexicographically minimal under all
    source permutations. Exact for p<=8; use only in exhaustive mode."""
    from itertools import permutations
    base = sorted(tuple(t) for t in sinks)
    for perm in permutations(range(p)):
        cand = sorted(tuple(sorted(perm[u] for u in t)) for t in sinks)
        if cand < base:
            return False
    return True


def mode_exhaustive(p, q):
    triples = list(combinations(range(p), 3))
    total = 0; checked = 0; t0 = time.time()
    def rec(start, chosen):
        nonlocal total, checked
        if len(chosen) == q:
            total += 1
            if not canonical_min(p, chosen):
                return
            r = check(p, list(chosen))
            if r is not None:
                checked += 1
                if checked % 2000 == 0:
                    print(f"[bip-exh p={p} q={q}] total={total} checked={checked} "
                          f"t={time.time()-t0:.0f}s", flush=True)
            return
        for i in range(start, len(triples)):
            chosen.append(triples[i])
            rec(i, chosen)   # allow repeats (parallel sinks)
            chosen.pop()
    rec(0, [])
    print(f"[bip-exh p={p} q={q}] DONE total={total} checked={checked} "
          f"t={time.time()-t0:.0f}s", flush=True)


def mode_exhaustall(p, qmax):
    """All multisets of q<=qmax triples over C(p,3), no isomorph rejection
    (feasible for p<=6). Checks every tau=3 instance."""
    triples = list(combinations(range(p), 3))
    total = 0; checked = 0; t0 = time.time()
    def rec(start, chosen):
        nonlocal total, checked
        if chosen:
            total += 1
            r = check(p, list(chosen))
            if r is not None:
                checked += 1
                if checked % 20000 == 0:
                    print(f"[bip-exhall p={p} q<={qmax}] total={total} "
                          f"checked={checked} t={time.time()-t0:.0f}s", flush=True)
        if len(chosen) == qmax:
            return
        for i in range(start, len(triples)):
            chosen.append(list(triples[i]))
            rec(i, chosen)
            chosen.pop()
    rec(0, [])
    print(f"[bip-exhall p={p} q<={qmax}] DONE total={total} checked={checked} "
          f"t={time.time()-t0:.0f}s", flush=True)


def mode_random(p, q, seconds, seed):
    rng = random.Random(seed)
    t0 = time.time(); n = 0; ok3 = 0
    while time.time() - t0 < seconds:
        n += 1
        sinks = [sorted(rng.sample(range(p), 3)) for _ in range(q)]
        r = check(p, sinks)
        if r is not None:
            ok3 += 1
        if n % 20000 == 0:
            print(f"[bip-rand p={p} q={q} seed={seed}] tried={n} tau3={ok3} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[bip-rand p={p} q={q} seed={seed}] DONE tried={n} tau3={ok3}", flush=True)


def mode_anneal(seconds, seed):
    rng = random.Random(seed)
    p, sinks = d27_sinklists()
    cur = [list(t) for t in sinks]
    t0 = time.time(); steps = 0; checked = 0; cur_s = -1; best = -1
    while time.time() - t0 < seconds:
        steps += 1
        cand = [list(t) for t in cur]
        op = rng.random()
        if op < 0.6:  # rewire one arc of one sink
            t = rng.randrange(len(cand))
            i = rng.randrange(3)
            u = rng.randrange(p)
            if u in cand[t]:
                continue
            cand[t][i] = u; cand[t].sort()
        elif op < 0.8 and len(cand) > 8:  # delete a sink
            cand.pop(rng.randrange(len(cand)))
        else:  # add a sink
            cand.append(sorted(rng.sample(range(p), 3)))
        cuts, tau = min_dicuts_bip(p, cand)
        if cuts is None or tau != 3:
            continue
        checked += 1
        ok = packs3(cand, cuts)
        if not ok:
            msg = f"UNSAT COUNTEREXAMPLE p={p} sinks={cand}"
            print(msg, flush=True)
            with open("counterexample.txt", "a") as f:
                f.write(msg + "\n")
            continue
        tight = sum(1 for c in cuts if len(c) == 3)
        s = 100 * tight + len(cuts) - 3 * len(cand)
        if s >= cur_s or rng.random() < 0.05:
            cur, cur_s = cand, s
        if s > best:
            best = s
            print(f"[bip-anneal seed={seed}] step={steps} checked={checked} best={s} "
                  f"q={len(cand)} cuts={len(cuts)} tight={tight} "
                  f"t={time.time()-t0:.0f}s", flush=True)
        if rng.random() < 0.0005:
            cur = [list(t) for t in sinks]; cur_s = -1
    print(f"[bip-anneal seed={seed}] DONE steps={steps} checked={checked} best={best}",
          flush=True)


if __name__ == "__main__":
    m = sys.argv[1]
    if m == "exhaustall":
        mode_exhaustall(int(sys.argv[2]), int(sys.argv[3]))
    elif m == "exhaustive":
        mode_exhaustive(int(sys.argv[2]), int(sys.argv[3]))
    elif m == "random":
        mode_random(int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]))
    elif m == "anneal":
        mode_anneal(float(sys.argv[2]), int(sys.argv[3]))
