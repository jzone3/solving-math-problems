# Provenance: new stage-3 lazy CEGAR oracle for two-half interface forcing.
"""Lazy interface-pattern CEGAR and alternating-side minimisation."""

from __future__ import annotations

import argparse
import itertools
import pickle
import random
import time

from pysat.solvers import Cadical153

import gadget
import univ


def split_edges(labels, metadata):
    """Recover cross edges incident to the shared T=0 origin.

    univ.py's exclusive labels classify an origin--B edge as BB because the
    origin belongs to both memberships.  For a decomposition with the origin
    placed on A, those edges must be treated as cross edges.
    """
    a_n = metadata["A_candidates"]
    cross = list(labels["cross"])
    b_edges = []
    for e in labels["BB"]:
        u, v = e
        if (u < a_n) != (v < a_n):
            a, b = (u, v) if u < a_n else (v, u)
            cross.append((a, b))
        else:
            b_edges.append(e)
    oriented = [
        (u, v) if u < a_n else (v, u)
        for u, v in cross
    ]
    return b_edges, oriented


def clauses(n, edges, extra=()):
    return gadget.build_cnf(n, edges, extra)


def colors_from_model(model, order):
    pos = set(model)
    out = {}
    for i, v in enumerate(order):
        for c in range(4):
            if gadget.color_var(i, c) in pos:
                out[v] = c
                break
    return out


def relabel(verts, edges):
    order = sorted(verts)
    idx = {v: i for i, v in enumerate(order)}
    return order, [(idx[u], idx[v]) for u, v in edges if u in idx and v in idx]


def color_a(L, a_edges, patterns):
    order, edges = relabel(L, a_edges)
    idx = {v: i for i, v in enumerate(order)}
    props = []
    for vs, cs in patterns:
        if all(v in idx for v in vs):
            props.append([-gadget.color_var(idx[v], c) for v, c in zip(vs, cs)])
    cls = clauses(len(order), edges, props)
    with Cadical153(bootstrap_with=cls) as solver:
        if not solver.solve():
            return None
        return colors_from_model(solver.get_model(), order)


class BTheory:
    """Persistent SAT instance for B plus its selected cross edges."""

    def __init__(self, S, cross, b_edges):
        bverts = set(S)
        self.cross = [(a, b) for a, b in cross if b in bverts]
        bverts.update(b for _, b in self.cross)
        iverts = {a for a, _ in self.cross}
        self.order = sorted(bverts | iverts)
        self.idx = {v: i for i, v in enumerate(self.order)}
        edges = [(self.idx[u], self.idx[v]) for u, v in b_edges
                 if u in self.idx and v in self.idx]
        edges += [(self.idx[a], self.idx[b]) for a, b in self.cross]
        self.solver = Cadical153(bootstrap_with=clauses(len(self.order), edges))

    def query(self, assignment):
        assumptions = [
            gadget.color_var(self.idx[v], c)
            for v, c in assignment.items()
            if v in self.idx
        ]
        return self.solver.solve(assumptions=assumptions)

    def close(self):
        self.solver.delete()


def minimal_pattern(theory, assignment):
    """Deletion MUS over interface literals; returns a minimal assignment."""
    lits = list(assignment.items())
    while True:
        changed = False
        for i in range(len(lits)):
            trial = dict(lits[:i] + lits[i + 1 :])
            if not theory.query(trial):
                lits.pop(i)
                changed = True
                break
        if not changed:
            return tuple(v for v, _ in lits), tuple(c for _, c in lits)


def grow_candidates(L, a_pool, a_edges, coloring, batch=4):
    current = set(L)
    forced = []
    frontier = {}
    for v in a_pool - current:
        neigh = [
            (w if u == v else u)
            for u, w in a_edges
            if (u == v and w in current) or (w == v and u in current)
        ]
        seen = {coloring[u] for u in neigh if u in coloring}
        if len(seen) == 4:
            forced.append(v)
        elif seen:
            frontier[v] = (len(seen), len(neigh))
    if forced:
        return set(forced[:batch]), "model-conflict"
    if frontier:
        ranked = sorted(frontier, key=lambda v: frontier[v], reverse=True)
        return set(ranked[:batch]), "frontier"
    return set(sorted(a_pool - current)[:batch]), "fallback"


def run_cegar(L, S, a_pool, a_edges, b_edges, cross, patterns=None, batch=4, limit=10000):
    """Grow L and lazily discover minimal B-forbidden interface patterns."""
    L = set(L)
    patterns = list(patterns or [])
    theory = BTheory(S, cross, b_edges)
    seen = {(tuple(vs), tuple(cs)) for vs, cs in patterns}
    history = []
    for iteration in range(limit):
        coloring = color_a(L, a_edges, patterns)
        if coloring is None:
            theory.close()
            return L, patterns, history, "UNSAT"
        assignment = {a: coloring[a] for a, _ in cross if a in coloring and _ in S}
        if not theory.query(assignment):
            pattern = minimal_pattern(theory, assignment)
            if pattern not in seen:
                patterns.append(pattern)
                seen.add(pattern)
                history.append({"event": "pattern", "order": len(pattern[0]), "L": len(L)})
            else:
                # A duplicate can only occur if the A model is color-equivalent;
                # add its exact blocking clause through the same stored pattern.
                history.append({"event": "duplicate-pattern", "L": len(L)})
            continue
        if L >= a_pool:
            theory.close()
            return L, patterns, history, "EXTENDS_FULL_A"
        added, reason = grow_candidates(L, a_pool, a_edges, coloring, batch)
        if not added:
            theory.close()
            return L, patterns, history, "STALLED"
        L.update(added)
        history.append({"event": "grow", "reason": reason, "added": len(added), "L": len(L)})
    theory.close()
    return L, patterns, history, "LIMIT"


def cached_test(L, a_edges, patterns):
    return color_a(L, a_edges, patterns) is None


def core_reduce(L, a_edges, patterns, preserve):
    """Use DRAT cores before expensive individual deletion tests."""
    L = set(L)
    while True:
        order, edges = relabel(L, a_edges)
        idx = {v: i for i, v in enumerate(order)}
        props = [
            [-gadget.color_var(idx[v], c) for v, c in zip(vs, cs)]
            for vs, cs in patterns
            if all(v in idx for v in vs)
        ]
        used = gadget.core_vertices(
            len(order), edges, props,
            {idx[v] for v in preserve if v in idx},
            timeout=1800,
        )
        if used is None:
            return L
        new = {order[i] for i in used}
        if new == L:
            return L
        L = new


def _load(cache, include_record_s=False):
    points, edges, labels, metadata = pickle.load(open(cache, "rb"))
    points = list(points)
    if include_record_s:
        D = pickle.load(open(univ.DECOMP, "rb"))
        existing = set(points)
        for p in D["S"]:
            q = univ.complex_mul(univ.OMEGA, univ.lattice_field(p))
            if q not in existing:
                points.append(q)
                existing.add(q)
        if len(points) != metadata["vertices"]:
            memberships = [
                [i < metadata["A_candidates"], i >= metadata["A_candidates"]]
                for i in range(len(points))
            ]
            memberships[0] = [True, True]
            edges, labels = univ.edge_labels(points, memberships)
            metadata = dict(metadata)
            metadata["vertices"] = len(points)
            metadata["edges"] = len(edges)
    return points, labels, metadata


def side_sets(cache, mode):
    points, labels, metadata = _load(cache, include_record_s=(mode == "record"))
    a_pool = set(range(metadata["A_candidates"]))
    b_pool = set(range(metadata["A_candidates"], len(points)))
    D = pickle.load(open(univ.DECOMP, "rb"))
    amap = {p: i for i, p in enumerate(points[: metadata["A_candidates"]])}
    bmap = {p: i for i, p in enumerate(points)}
    rec_a = {amap[univ.lattice_field(p)] for p in D["L"]}
    rec_b = set()
    for p in D["S"]:
        q = univ.complex_mul(univ.OMEGA, univ.lattice_field(p))
        if q in bmap and bmap[q] >= metadata["A_candidates"]:
            rec_b.add(bmap[q])
    if mode == "record":
        return points, labels, metadata, a_pool, b_pool, rec_a, rec_b
    return points, labels, metadata, a_pool, b_pool, a_pool, b_pool


def minimise(cache, a_mode="record", b_mode="record", passes=1, seed=1):
    base_mode = "record" if b_mode == "record" else "full"
    points, labels, metadata, a_pool, b_pool, L, S = side_sets(cache, base_mode)
    if a_mode == "record":
        _, _, _, _, _, L, _ = side_sets(cache, "record")
    a_edges = labels["AA"]
    b_edges, cross = split_edges(labels, metadata)
    patterns = []
    best = {"L": len(L), "S": len(S), "total": len(L) + len(S), "patterns": 0}
    rng = random.Random(seed)
    for pidx in range(passes):
        L, patterns, hist, status = run_cegar(L, S, a_pool, a_edges, b_edges, cross, patterns)
        print(f"pass {pidx}: CEGAR {status}, |L|={len(L)} |S|={len(S)} patterns={len(patterns)}")
        if status != "UNSAT":
            break
        L = core_reduce(L, a_edges, patterns,
                        {v for vs, _ in patterns for v in vs})
        print(f"  core: |L|={len(L)} patterns={len(patterns)}", flush=True)
        changed = True
        while changed:
            changed = False
            order = list(L - {v for vs, _ in patterns for v in vs})
            rng.shuffle(order)
            for v in order:
                trial = L - {v}
                if cached_test(trial, a_edges, patterns):
                    L = trial
                    changed = True
                else:
                    trial2, patterns2, _, st = run_cegar(
                        trial, S, a_pool, a_edges, b_edges, cross, patterns
                    )
                    if st == "UNSAT":
                        L, patterns = trial2, patterns2
                        changed = True
            print(f"  L pass: |L|={len(L)} patterns={len(patterns)}")
        candidate = {"L": len(L), "S": len(S), "total": len(L) + len(S), "patterns": len(patterns)}
        if candidate["total"] < best["total"]:
            best = candidate
        # B-side deletion is intentionally conservative: cached patterns are
        # reused only when every one remains forbidden by the smaller S.
        changed = True
        while changed:
            changed = False
            order = list(S)
            rng.shuffle(order)
            for v in order:
                trial_s = S - {v}
                trial_theory = BTheory(trial_s, cross, b_edges)
                valid = all(
                    not trial_theory.query(dict(zip(vs, cs)))
                    for vs, cs in patterns
                )
                trial_theory.close()
                if valid:
                    if cached_test(L, a_edges, patterns):
                        S = trial_s
                        changed = True
                        continue
                trial_l, patterns2, _, st = run_cegar(
                    L, trial_s, a_pool, a_edges, b_edges, cross, patterns
                )
                if st == "UNSAT":
                    L, S, patterns = trial_l, trial_s, patterns2
                    changed = True
            print(f"  S pass: |L|={len(L)} |S|={len(S)} patterns={len(patterns)}")
        candidate = {"L": len(L), "S": len(S), "total": len(L) + len(S), "patterns": len(patterns)}
        if candidate["total"] < best["total"]:
            best = candidate
    return {"L": sorted(L), "S": sorted(S), "patterns": patterns, "best": best}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("--a-mode", choices=("record", "full"), default="record")
    ap.add_argument("--b-mode", choices=("record", "full"), default="record")
    ap.add_argument("--passes", type=int, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    result = minimise(args.cache, args.a_mode, args.b_mode, args.passes, args.seed)
    print(result["best"])
    if args.out:
        pickle.dump(result, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()
