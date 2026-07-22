"""
P03 V5 search driver.

Literature-derived target region (any tau=3 counterexample D to Woodall,
minimal or otherwise, that we most want to sample):
  - DAG (WLOG; strong components contracted)
  - tau(D) = 3
  - NOT source-sink connected            (else Schrijver 1982 / FY 1987 => packs)
  - rho(3, D) >= 4                       (else Abdi-Cornuejols-Zlatin 2023 => packs)
  - underlying graph non-planar          (planar case known)
  - underlying graph not chordal         (Cornuejols-Liu-Ravi 2025 => packs)
Shape prior from Schrijver's reduction notes: in a minimal counterexample all
sources/sinks have degree k=3 and every internal vertex has degree 3
(in,out) in {(1,2),(2,1)}.

Two phases per size:
  A. random shape-constrained DAGs, SAT-check every tau=3 sample (broad stats)
  B. simulated annealing on rewiring moves toward the target region; SAT-check
     everything in region.
Any non-packing instance is dumped to counterexample_*.json (and would be
verified independently by solutions/P03/verify.py).
"""

import json
import random
import sys
import time
from collections import Counter

from harness import (tau, has_k_disjoint_dijoins, rho, is_planar,
                     is_source_sink_connected, is_chordal_underlying,
                     is_dag, check_candidate)

K = 3


def random_shape_dag(n_src, n_snk, n_int, rng):
    """Random DAG: sources outdeg 3, sinks indeg 3, internal deg-3 vertices
    with (in,out) in {(1,2),(2,1)}. Returns (n, arcs) or None."""
    n = n_src + n_int + n_snk
    # choose internal types s.t. stub counts balance:
    # out-stubs: 3*n_src + sum(out_i); in-stubs: 3*n_snk + sum(in_i)
    # type A=(in1,out2), B=(in2,out1). #A + 2#B + 3 n_snk = 2#A + #B + 3 n_src
    # => #A - #B = 3(n_snk - n_src)
    diff = 3 * (n_snk - n_src)
    if (n_int - diff) % 2 != 0 or abs(diff) > n_int:
        return None
    nB = (n_int - diff) // 2
    nA = n_int - nB
    if nA < 0 or nB < 0:
        return None
    types = ['A'] * nA + ['B'] * nB
    rng.shuffle(types)
    # topological order: sources, shuffled internals, sinks
    order = (list(range(n_src)) +
             list(range(n_src, n_src + n_int)) +
             list(range(n_src + n_int, n)))
    internals = order[n_src:n_src + n_int]
    rng.shuffle(internals)
    order[n_src:n_src + n_int] = internals
    pos = {v: i for i, v in enumerate(order)}
    outdeg = {}
    indeg = {}
    for i in range(n_src):
        outdeg[i] = 3
        indeg[i] = 0
    for j, v in enumerate(range(n_src, n_src + n_int)):
        if types[j] == 'A':
            indeg[v], outdeg[v] = 1, 2
        else:
            indeg[v], outdeg[v] = 2, 1
    for v in range(n_src + n_int, n):
        indeg[v], outdeg[v] = 3, 0
    out_stubs = [v for v in range(n) for _ in range(outdeg[v])]
    in_stubs = [v for v in range(n) for _ in range(indeg[v])]
    assert len(out_stubs) == len(in_stubs)
    # greedy random matching respecting topological order, retry a few times
    for _ in range(60):
        rng.shuffle(out_stubs)
        rng.shuffle(in_stubs)
        arcs = []
        used = [False] * len(in_stubs)
        ok = True
        for u in out_stubs:
            cands = [i for i, w in enumerate(in_stubs)
                     if not used[i] and pos[w] > pos[u]]
            if not cands:
                ok = False
                break
            i = rng.choice(cands)
            used[i] = True
            arcs.append((u, in_stubs[i]))
        if ok:
            return n, arcs
    return None


def region_score(n, arcs):
    """0 iff in the target region; positive penalties otherwise."""
    t = tau(n, arcs)
    if t is None:
        return 1000
    s = 10 * abs(t - K)
    if t == 0:
        return 1000
    s += 3 * (1 if is_source_sink_connected(n, arcs) else 0)
    s += 2 * max(0, 4 - rho(n, arcs, K))
    s += 2 * (1 if is_planar(n, arcs) else 0)
    s += 1 * (1 if is_chordal_underlying(n, arcs) else 0)
    return s


def rewire_move(n, arcs, rng):
    """Rewire one arc endpoint, keeping the digraph a DAG (checked after)."""
    arcs = list(arcs)
    i = rng.randrange(len(arcs))
    u, v = arcs[i]
    if rng.random() < 0.5:
        u2 = rng.randrange(n)
        if u2 != v:
            arcs[i] = (u2, v)
    else:
        v2 = rng.randrange(n)
        if v2 != u:
            arcs[i] = (u, v2)
    return arcs


def dump_counterexample(n, arcs, tag, stats):
    fname = f"counterexample_{tag}_{int(time.time())}.json"
    props = check_candidate(n, arcs, K, verbose=True)
    with open(fname, "w") as f:
        json.dump({"n": n, "arcs": arcs, "k": K, "props": {
            kk: (vv if not isinstance(vv, frozenset) else sorted(vv))
            for kk, vv in props.items()}}, f, indent=1)
    print(f"*** NON-PACKING INSTANCE dumped to {fname}: {props}", flush=True)
    return fname


def phase_a(sizes, seconds, rng, stats):
    """Random screening."""
    t_end = time.time() + seconds
    while time.time() < t_end:
        n_src, n_snk, n_int = rng.choice(sizes)
        g = random_shape_dag(n_src, n_snk, n_int, rng)
        if g is None:
            continue
        n, arcs = g
        stats['generated'] += 1
        t = tau(n, arcs)
        stats[f'tau={t}'] += 1
        if t != K:
            continue
        in_region = (not is_source_sink_connected(n, arcs)
                     and rho(n, arcs, K) >= 4
                     and not is_planar(n, arcs)
                     and not is_chordal_underlying(n, arcs))
        stats['tau3_checked'] += 1
        if in_region:
            stats['tau3_in_region'] += 1
        if not has_k_disjoint_dijoins(n, arcs, K):
            stats['NONPACKING'] += 1
            dump_counterexample(n, arcs, "phaseA", stats)


def phase_b(sizes, seconds, rng, stats):
    """Anneal toward region, SAT-check members of region."""
    t_end = time.time() + seconds
    while time.time() < t_end:
        n_src, n_snk, n_int = rng.choice(sizes)
        g = random_shape_dag(n_src, n_snk, n_int, rng)
        if g is None:
            continue
        n, arcs = g
        cur = region_score(n, arcs)
        temp = 3.0
        for step in range(400):
            if time.time() > t_end:
                break
            cand = rewire_move(n, arcs, rng)
            if not is_dag(n, cand):
                continue
            sc = region_score(n, cand)
            if sc <= cur or rng.random() < pow(2.718, -(sc - cur) / max(temp, 0.05)):
                arcs, cur = cand, sc
            temp *= 0.985
            if cur == 0:
                stats['anneal_region_hits'] += 1
                stats['tau3_checked'] += 1
                stats['tau3_in_region'] += 1
                if not has_k_disjoint_dijoins(n, arcs, K):
                    stats['NONPACKING'] += 1
                    dump_counterexample(n, arcs, "phaseB", stats)
                # perturb and continue searching nearby
                for _ in range(6):
                    arcs2 = rewire_move(n, arcs, rng)
                    if is_dag(n, arcs2):
                        arcs = arcs2
                cur = region_score(n, arcs)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "a"
    seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    rng = random.Random(seed)
    # (n_src, n_snk, n_int) combos; n_int - 3(n_snk-n_src) must be even>=0
    sizes = []
    for s in range(1, 4):
        for t in range(1, 4):
            for m in range(2, 11):
                if abs(3 * (t - s)) <= m and (m - 3 * (t - s)) % 2 == 0:
                    if s + t + m <= 16:
                        sizes.append((s, t, m))
    stats = Counter()
    t0 = time.time()
    if mode == "a":
        phase_a(sizes, seconds, rng, stats)
    else:
        phase_b(sizes, seconds, rng, stats)
    stats['wall_seconds'] = int(time.time() - t0)
    print(json.dumps(dict(stats), indent=1, sort_keys=True), flush=True)
