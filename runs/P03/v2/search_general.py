"""Phase-2 frontier push (post-negative): random search over GENERAL
digraphs — cycles allowed, parallel arcs allowed (multigraph Woodall),
2-cycles allowed — at n up to 16, tau >= 3, i.e. outside every class the
phase-1 seed-blowup search lived in (those were all DAGs derived from
planar drawings).

Pipeline per instance (fast bitmask core, no external deps until the ILP):
  1. random weakly-connected multi-digraph;
  2. dicuts via lower sets of the condensation (bitmask cuts); tau >= 3;
  3. ACZ rho filter (tau=3 needs rho>=4, else provably packs);
  4. T randomized greedy packing attempts; if any succeeds -> packs, next;
  5. exact ILP (CBC) only for greedy-resistant instances; INFEASIBLE =>
     candidate counterexample (dump + loud print).

Hardness telemetry (greedy fail fraction, ILP time) is logged to find
near-misses even if no failure occurs.
"""
import json
import random
import sys
import time

import core


def rand_instance(rng, nmax=16):
    n = rng.randint(6, nmax)
    mode = rng.random()
    if mode < 0.4:      # sparse general
        m = rng.randint(max(4, n // 2), min(32, 2 * n))
    else:               # denser general
        m = rng.randint(n + 2, min(32, 3 * n))
    dag = rng.random() < 0.4  # 40%: orient all arcs low->high (rich dicuts)
    arcs = []
    while len(arcs) < m:
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        if dag and u > v:
            u, v = v, u
        arcs.append((u, v))
    # force weak connectivity via random spanning chain
    perm = list(range(n))
    rng.shuffle(perm)
    for i in range(n - 1):
        if rng.random() < 0.5:
            arcs.append((perm[i], perm[i + 1]))
        else:
            arcs.append((perm[i + 1], perm[i]))
    return n, arcs


def dicut_masks(n, arcs, max_cuts=20000):
    """All dicuts as arc-index bitmasks (deduped); None if too many."""
    nc, carcs, orig_idx, comp = core.condense(n, arcs)
    if nc == 1:
        return []
    masks = set()
    for ls in core.lower_sets(nc, carcs):
        m = 0
        for j, (cu, cv) in enumerate(carcs):
            if (ls >> cu) & 1 and not (ls >> cv) & 1:
                m |= 1 << orig_idx[j]
        masks.add(m)
        if len(masks) > max_cuts:
            return None
    # keep only inclusion-minimal masks (sufficient for dijoin constraints,
    # and tau must be computed before this filter!)
    return list(masks)


def minimal_masks(masks):
    masks = sorted(masks, key=lambda m: bin(m).count("1"))
    out = []
    for m in masks:
        if not any(o & m == o for o in out):
            out.append(m)
    return out


def greedy_pack(masks_min, m_arcs, k, rng, tries=25):
    """Try to find k disjoint hitting sets of the dicut masks greedily."""
    for _ in range(tries):
        used = 0
        ok = True
        for _color in range(k):
            hit = 0  # set of dicuts already hit by this color
            chosen = 0
            order = list(range(len(masks_min)))
            rng.shuffle(order)
            for ci in order:
                cm = masks_min[ci]
                if cm & chosen:
                    continue
                avail = cm & ~used
                if not avail:
                    ok = False
                    break
                bits = []
                x = avail
                while x:
                    b = x & -x
                    bits.append(b)
                    x ^= b
                pick = rng.choice(bits)
                chosen |= pick
                used |= pick
            if not ok:
                break
        if ok:
            return True
    return False


def run(seed=0, wall=7200, nmax=16, ilp_budget=300):
    rng = random.Random(seed)
    t_end = time.time() + wall
    stats = {"gen": 0, "tau_ge3": 0, "rho_filtered": 0, "greedy_packed": 0,
             "ilp_tested": 0, "FAILURES": 0, "timeouts": 0, "cut_blowup": 0}
    hard = []
    while time.time() < t_end:
        stats["gen"] += 1
        n, arcs = rand_instance(rng, nmax)
        masks = dicut_masks(n, arcs)
        if masks is None:
            stats["cut_blowup"] += 1
            continue
        if not masks:
            continue
        t = min(bin(m).count("1") for m in masks)
        if t < 3 or t > 6:
            continue
        stats["tau_ge3"] += 1
        r = core.rho(n, arcs, t)
        if r <= 2 or (t == 3 and r == 3):
            stats["rho_filtered"] += 1
            continue
        mmin = minimal_masks(masks)
        if greedy_pack(mmin, len(arcs), t, rng):
            stats["greedy_packed"] += 1
            continue
        stats["ilp_tested"] += 1
        cuts = [frozenset(i for i in range(len(arcs)) if (m >> i) & 1)
                for m in mmin]
        t0 = time.time()
        ok = core.packing_exists(n, arcs, t, cuts=cuts,
                                 time_limit=ilp_budget)
        dt = time.time() - t0
        rec = {"n": n, "arcs": arcs, "tau": t, "rho": r, "ilp_time": dt}
        if ok is False:
            stats["FAILURES"] += 1
            print("!!! PACKING FAILURE:", json.dumps(rec), flush=True)
            with open(f"hits_general_{seed}.json", "a") as f:
                f.write(json.dumps(rec) + "\n")
        elif ok is None:
            stats["timeouts"] += 1
            print("ILP TIMEOUT (suspicious):", json.dumps(rec), flush=True)
        else:
            hard.append((dt, n, len(arcs), t, r))
            hard.sort(reverse=True)
            del hard[10:]
        if stats["gen"] % 20000 == 0:
            print(f"[general seed={seed}] {stats} hardest={hard[:3]}",
                  flush=True)
    print(f"FINAL [general seed={seed} nmax={nmax}] {stats} hardest={hard}",
          flush=True)


if __name__ == "__main__":
    run(seed=int(sys.argv[1]) if len(sys.argv) > 1 else 0,
        wall=int(sys.argv[2]) if len(sys.argv) > 2 else 7200,
        nmax=int(sys.argv[3]) if len(sys.argv) > 3 else 16)
