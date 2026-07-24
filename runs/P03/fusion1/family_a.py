"""Family A: targeted reduced-shape search for tau=4.

The smallest role profile allowed by the two rho(4) bounds and the
source/sink safe-class exclusion is (2,2,3,3), with n=10 and 17 arcs.
This module derives profiles, generates random acyclic degree-constrained
instances, and exact-checks every instance reaching the out-of-safe-class
region.
"""

import random
import time

import networkx as nx

from harness import (has_k_disjoint_dijoins, is_planar,
                     is_source_sink_connected, minimal_dicuts, rho, tau)


def role_profiles(max_n=20):
    """Return feasible (s,t,a,b) profiles through max_n vertices."""
    result = []
    for s in range(2, max_n):
        for t in range(2, max_n):
            for a in range(max_n):
                for b in range(max_n):
                    n = s + t + a + b
                    if n > max_n:
                        continue
                    if a - b != 4 * (t - s):
                        continue
                    if a + 3 * b < 12 or 3 * a + b < 12:
                        continue
                    result.append((n, s, t, a, b))
    return sorted(result)


def random_reduced(rng, s, t, a, b, retries=100):
    """Generate a random simple-ish DAG with the requested role profile."""
    n = s + a + b + t
    sources = list(range(s))
    internals = list(range(s, s + a + b))
    sinks = list(range(s + a + b, n))
    types = ["A"] * a + ["B"] * b
    for _ in range(retries):
        rng.shuffle(types)
        order = sources + internals[:] + sinks
        rng.shuffle(order[s:s + a + b])
        pos = {v: i for i, v in enumerate(order)}
        indeg = [0] * n
        outdeg = [0] * n
        for v in sources:
            outdeg[v] = 4
        for i, v in enumerate(internals):
            indeg[v], outdeg[v] = ((1, 2) if types[i] == "A" else (2, 1))
        for v in sinks:
            indeg[v] = 4
        outs = [v for v in range(n) for _ in range(outdeg[v])]
        ins = [v for v in range(n) for _ in range(indeg[v])]
        rng.shuffle(outs)
        rng.shuffle(ins)
        arcs = []
        used = set()
        ok = True
        for u in outs:
            choices = [i for i, v in enumerate(ins)
                       if pos[v] > pos[u] and (u, v) not in used]
            if not choices:
                ok = False
                break
            i = rng.choice(choices)
            v = ins.pop(i)
            used.add((u, v))
            arcs.append((u, v))
        if ok and not ins:
            return n, arcs
    return None


def weakly_k_arc_connected(n, arcs, k):
    for mask in range(1, (1 << n) - 1):
        cut = sum(((mask >> u) & 1) != ((mask >> v) & 1)
                   for u, v in arcs)
        if cut < k:
            return False
    return True


def in_region(n, arcs):
    rev = [(v, u) for u, v in arcs]
    return (tau(n, arcs) == 4
            and not is_source_sink_connected(n, arcs)
            and not is_planar(n, arcs)
            and rho(n, arcs, 4) >= 3
            and rho(n, rev, 4) >= 3)


def search(seconds=600, seed=0, profile=(2, 2, 3, 3)):
    rng = random.Random(seed)
    t0 = time.time()
    generated = region = packed = 0
    slowest = (0.0, None)
    while time.time() - t0 < seconds:
        instance = random_reduced(rng, *profile)
        if instance is None:
            continue
        generated += 1
        n, arcs = instance
        if not in_region(n, arcs):
            continue
        region += 1
        start = time.time()
        packed_ok = has_k_disjoint_dijoins(n, arcs, 4)
        elapsed = time.time() - start
        if elapsed > slowest[0]:
            slowest = (elapsed, (n, arcs))
        if not packed_ok:
            print("NONPACKING", n, arcs, flush=True)
            return
        packed += 1
    print({"profile": profile, "generated": generated, "region": region,
           "packed": packed, "slowest_exact_seconds": slowest[0]},
          flush=True)


if __name__ == "__main__":
    print("profiles <=", 20, ":", role_profiles(20)[:10])
    search(int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1
           else 60, int(__import__("sys").argv[2]) if len(__import__("sys").argv) > 2
           else 0)
