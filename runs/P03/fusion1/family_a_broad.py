"""Structured broader tau=4 search with a forced blocked source/sink pair."""

import random
import time

import networkx as nx

from family_a import rho
from harness import (has_k_disjoint_dijoins, is_planar,
                     minimal_dicuts, tau)


def structured_reduced(rng, s, t, a, b, retries=80):
    """Layered degree-sequence generator with source 0 unable to reach sink 0.

    R contains source 0 and sink 0; N contains the other sources and sinks.
    Arcs from R to N are forbidden, so source 0 cannot reach sink 0. N->R
    arcs preserve weak connectivity in many samples.
    """
    n = s + a + b + t
    sources = list(range(s))
    internals = list(range(s, s + a + b))
    sinks = list(range(s + a + b, n))
    for _ in range(retries):
        types = ["A"] * a + ["B"] * b
        rng.shuffle(types)
        indeg = [0] * n
        outdeg = [0] * n
        for v in sources:
            outdeg[v] = 4
        for i, v in enumerate(internals):
            indeg[v], outdeg[v] = ((1, 2) if types[i] == "A" else (2, 1))
        for v in sinks:
            indeg[v] = 4
        R = {sources[0], sinks[0]}
        # Put enough internal vertices on each side to permit the stubs.
        R.update(internals[::2])
        N = set(range(n)) - R
        order = ([sources[0]] + sources[1:] +
                 [v for v in internals if v in N] +
                 [v for v in sinks if v in N] +
                 [v for v in internals if v in R] + [sinks[0]])
        pos = {v: i for i, v in enumerate(order)}
        outs = [v for v in range(n) for _ in range(outdeg[v])]
        ins = [v for v in range(n) for _ in range(indeg[v])]
        rng.shuffle(outs)
        rng.shuffle(ins)
        arcs = []
        used = set()
        ok = True
        for u in outs:
            choices = [i for i, v in enumerate(ins)
                       if pos[v] > pos[u]
                       and not (u in R and v in N)
                       and (u, v) not in used]
            if not choices:
                ok = False
                break
            i = rng.choice(choices)
            v = ins.pop(i)
            used.add((u, v))
            arcs.append((u, v))
        if ok and not ins:
            G = nx.Graph()
            G.add_nodes_from(range(n))
            G.add_edges_from(arcs)
            if nx.is_connected(G):
                return n, arcs
    return None


def score(n, arcs):
    cuts = minimal_dicuts(n, arcs)
    return sum(len(c) == 4 for c in cuts), -len(cuts)


def anneal(rng, n, arcs, steps=12):
    """Degree-preserving head swaps, retaining only DAG/profile instances."""
    best = list(arcs)
    best_score = score(n, best)
    current = list(best)
    for _ in range(steps):
        i, j = rng.sample(range(len(current)), 2)
        (u, v), (x, y) = current[i], current[j]
        candidate = list(current)
        candidate[i], candidate[j] = (u, y), (x, v)
        if len(set(candidate)) != len(candidate):
            continue
        G = nx.DiGraph()
        G.add_nodes_from(range(n))
        G.add_edges_from(candidate)
        if not nx.is_directed_acyclic_graph(G):
            continue
        if score(n, candidate) > best_score:
            best, best_score = candidate, score(n, candidate)
            current = candidate
    return best


def in_region(n, arcs):
    rev = [(v, u) for u, v in arcs]
    return (tau(n, arcs) == 4 and not is_planar(n, arcs)
            and rho(n, arcs, 4) >= 3 and rho(n, rev, 4) >= 3)


def search(seconds=600, seed=0):
    rng = random.Random(seed)
    profiles = [(2, 2, 4, 4), (3, 3, 3, 3), (4, 4, 4, 4)]
    started = time.time()
    generated = region = packed = annealed = 0
    slowest = 0.0
    while time.time() - started < seconds:
        p = rng.choice(profiles)
        rec = structured_reduced(rng, *p)
        if rec is None:
            continue
        generated += 1
        n, base_arcs = rec
        arcs = anneal(rng, n, base_arcs)
        annealed += 1
        if not in_region(n, arcs):
            continue
        region += 1
        begin = time.time()
        ok = has_k_disjoint_dijoins(n, arcs, 4)
        slowest = max(slowest, time.time() - begin)
        if not ok:
            print("NONPACKING", n, arcs, flush=True)
            return
        packed += 1
    print({"generated": generated, "annealed": annealed, "region": region,
           "packed": packed, "slowest_exact_seconds": slowest}, flush=True)


if __name__ == "__main__":
    import sys
    search(int(sys.argv[1]) if len(sys.argv) > 1 else 600,
           int(sys.argv[2]) if len(sys.argv) > 2 else 0)
