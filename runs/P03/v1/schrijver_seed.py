#!/usr/bin/env python3
"""
Phase 3: mutate/anneal around Schrijver's weighted counterexample (ACZ Fig 1,
extracted from the arXiv:2202.00392 vector figure D1.pdf).

Vertices: outer hexagon O1..O6 = 0..5, inner hexagon I1..I6 = 6..11.
Solid arcs (weight 1) and dashed arcs (weight 0):
  solid: O1->O6, O3->O2, O5->O4, I6->I1, I2->I3, I4->I5, I2->O6, I6->O2, I4->O4
  dashed: O5->O6, O1->O2, O3->O4, I2->I1, I6->I5, I4->I3,
          I1->O6, I2->O5, I3->O4, I4->O3, I5->O2, I6->O1

Weighted sanity check: every dicut has solid-weight >= 2 but solid arcs cannot
be partitioned into 2 dijoins (Schrijver 1980).

Unweighted attack: replace weight-0 arcs by md parallel arcs and weight-1 arcs
by ms parallel arcs (md >> ms mimics "free" arcs); grid over (ms, md) plus the
tau>=2 extension (middle solid arcs of the three 3-arc solid paths get
multiplicity t-1); then anneal around every such seed.
"""
import random, sys, time
from search import dicuts_and_tau, packs_into, report_counterexample
from pysat.solvers import Cadical153

O1, O2, O3, O4, O5, O6 = range(6)
I1, I2, I3, I4, I5, I6 = range(6, 12)
N = 12

SOLID = [(O1, O6), (O3, O2), (O5, O4),
         (I6, I1), (I2, I3), (I4, I5),
         (I2, O6), (I6, O2), (I4, O4)]
DASHED = [(O5, O6), (O1, O2), (O3, O4),
          (I2, I1), (I6, I5), (I4, I3),
          (I1, O6), (I2, O5), (I3, O4), (I4, O3), (I5, O2), (I6, O1)]
# the three "3-arc solid paths" of the tau>=2 extension: I2->I3? The solid
# paths are I6->I1? Middle arcs per Harvey'11 extension = the inner solid arcs.
MIDDLE = [(I6, I1), (I2, I3), (I4, I5)]


def weighted_sanity():
    arcs = SOLID + DASHED
    cuts, tau = dicuts_and_tau(N, arcs)
    assert cuts is not None
    solid_idx = set(range(len(SOLID)))
    wmin = min(len(c & solid_idx) for c in cuts)
    print("num minimal dicuts:", len(cuts), "min solid weight:", wmin)
    # try to 2-color the SOLID arcs so each dicut has both colors
    k = 2
    var = lambda a, c: a * k + c + 1
    s = Cadical153()
    for a in solid_idx:
        s.add_clause([var(a, c) for c in range(k)])
        s.add_clause([-var(a, 0), -var(a, 1)])
    for cut in cuts:
        for c in range(k):
            s.add_clause([var(a, c) for a in (cut & solid_idx)])
    print("2 disjoint weighted dijoins exist:", s.solve())
    s.delete()


def expand(ms, md, ext_t=None):
    arcs = []
    for a in SOLID:
        mult = ms
        if ext_t and a in MIDDLE:
            mult = ext_t - 1
        arcs.extend([a] * mult)
    for a in DASHED:
        arcs.extend([a] * md)
    return arcs


def grid():
    for ms in range(1, 4):
        for md in range(1, 9):
            for ext in [None, 3, 4, 5]:
                arcs = expand(ms, md, ext)
                cuts, tau = dicuts_and_tau(N, arcs)
                if cuts is None or tau < 2:
                    continue
                ok, _ = packs_into(len(arcs), cuts, tau)
                tag = f"ms={ms} md={md} ext={ext} m={len(arcs)} tau={tau}"
                print(("PACKS  " if ok else "!!! UNSAT ") + tag, flush=True)
                if not ok:
                    report_counterexample(N, arcs, tau)


def mutate(rng, arcs):
    cand = list(arcs)
    op = rng.random()
    if op < 0.35 and len(cand) > 12:
        cand.pop(rng.randrange(len(cand)))
    elif op < 0.7:
        u = rng.randrange(N); v = rng.randrange(N)
        if u != v:
            cand.append((u, v))
    else:
        i = rng.randrange(len(cand))
        u = rng.randrange(N); v = rng.randrange(N)
        if u != v:
            cand[i] = (u, v)
    return cand


def anneal(seconds, seed):
    rng = random.Random(seed)
    seeds = []
    for ms in (1, 2):
        for md in (2, 3, 4):
            for ext in (None, 3):
                seeds.append(expand(ms, md, ext))
    t0 = time.time(); steps = 0
    cur = list(rng.choice(seeds)); cur_s = -10**9; best = -10**9
    while time.time() - t0 < seconds:
        steps += 1
        if rng.random() < 0.002:
            cur = list(rng.choice(seeds)); cur_s = -10**9
        cand = mutate(rng, cur)
        if len(cand) > 44:
            continue
        r = dicuts_and_tau(N, cand)
        cuts, tau = r
        if cuts is None or tau < 3:
            continue
        ok, _ = packs_into(len(cand), cuts, tau)
        if not ok:
            report_counterexample(N, cand, tau)
            print("UNSAT FOUND", flush=True)
            continue
        tight = sum(1 for c in cuts if len(c) == tau)
        s = 100 * tight + 5 * len(cuts) - len(cand)
        if s >= cur_s or rng.random() < 0.03:
            cur, cur_s = cand, s
        if s > best:
            best = s
            print(f"[schr-anneal seed={seed}] step={steps} best={s} tau={tau} "
                  f"m={len(cand)} cuts={len(cuts)} tight={tight} "
                  f"t={time.time()-t0:.0f}s", flush=True)
    print(f"[schr-anneal seed={seed}] DONE steps={steps} best={best}", flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sanity":
        weighted_sanity()
    elif cmd == "grid":
        grid()
    elif cmd == "anneal":
        anneal(float(sys.argv[2]), int(sys.argv[3]))
