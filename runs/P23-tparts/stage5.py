# Provenance: new stage-5 proof-guided B minimizer built on stage4.py/cegar.py.
"""Proof-guided pattern pruning and efficient alternating B minimisation."""

from __future__ import annotations

import argparse
import os
import pickle
import random
import shutil
import subprocess
import tempfile
import time
from collections import Counter

import cegar
import gadget
import stage4


class BIncremental:
    """One gated B SAT instance supporting cheap vertex-deletion queries."""

    def __init__(self, S, b_edges, cross):
        self.bverts = sorted(S)
        self.cross = [(a, b) for a, b in cross if b in S]
        allverts = set(self.bverts) | {a for a, _ in self.cross}
        self.order = sorted(allverts)
        self.idx = {v: i for i, v in enumerate(self.order)}
        self.bidx = {v: i for i, v in enumerate(self.bverts)}
        self.n = len(self.order)
        self.selector_base = 4 * self.n + 1
        clauses = []
        def sel(v):
            return (
                self.selector_base + self.bidx[v]
                if v in self.bidx else None
            )
        for v in self.order:
            i = self.idx[v]
            s = sel(v)
            gate = [-s] if s is not None else []
            colors = [gadget.color_var(i, c) for c in range(4)]
            clauses.append(gate + colors)
            for c in range(4):
                for d in range(c + 1, 4):
                    clauses.append(gate + [
                        -colors[c], -colors[d]
                    ])
        for u, v in b_edges:
            if u not in self.idx or v not in self.idx:
                continue
            gate = [
                -s for s in (sel(u), sel(v)) if s is not None
            ]
            for c in range(4):
                clauses.append(gate + [
                    -gadget.color_var(self.idx[u], c),
                    -gadget.color_var(self.idx[v], c),
                ])
        for a, b in self.cross:
            gate = [-sel(b)] if sel(b) is not None else []
            for c in range(4):
                clauses.append(gate + [
                    -gadget.color_var(self.idx[a], c),
                    -gadget.color_var(self.idx[b], c),
                ])
        self.solver = __import__("pysat.solvers", fromlist=["Cadical153"]).Cadical153(
            bootstrap_with=clauses
        )

    def query(self, active, pattern):
        assumptions = [
            self.selector_base + i
            for i, v in enumerate(self.bverts) if v in active
        ] + [
            -(self.selector_base + i)
            for i, v in enumerate(self.bverts) if v not in active
        ]
        vs, cs = pattern
        assumptions += [
            gadget.color_var(self.idx[v], c)
            for v, c in zip(vs, cs)
            if v in self.idx
        ]
        return self.solver.solve(assumptions=assumptions)

    def close(self):
        self.solver.delete()


def _core_file(n, edges, props):
    """Return the DRAT core clauses for a fresh property CNF."""
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, "f.cnf")
        proof = os.path.join(d, "f.drat")
        core = os.path.join(d, "f.core")
        cls = gadget.build_cnf(n, edges, props)
        gadget.write_cnf(cls, 4 * n, cnf)
        kissat = os.environ.get("KISSAT") or shutil.which("kissat")
        drat = os.environ.get("DRATTRIM") or shutil.which("drat-trim")
        r = subprocess.run(
            [kissat, "-q", cnf, proof], capture_output=True, text=True
        )
        if r.returncode == 10:
            return None
        if r.returncode != 20:
            raise RuntimeError(r.stderr[-500:])
        r = subprocess.run(
            [drat, cnf, proof, "-c", core],
            capture_output=True,
            text=True,
        )
        if r.returncode != 0 and not os.path.exists(core):
            raise RuntimeError(r.stderr[-500:])
        clauses = []
        if os.path.exists(core):
            for line in open(core):
                if line.startswith(("p", "c")):
                    continue
                vals = tuple(sorted(int(x) for x in line.split() if int(x)))
                if vals:
                    clauses.append(vals)
        return clauses


def prune_patterns_a(L, a_edges, patterns):
    """Keep only pattern clauses occurring in the A-side DRAT core."""
    order, edges = cegar.relabel(L, a_edges)
    idx = {v: i for i, v in enumerate(order)}
    usable = [
        p for p in patterns if all(v in idx for v in p[0])
    ]
    props = [stage4.pattern_clause(p, idx) for p in usable]
    core = _core_file(len(order), edges, props)
    if core is None:
        return [], "SAT"
    core_set = {frozenset(c) for c in core}
    kept = [
        p for p, clause in zip(usable, props)
        if frozenset(clause) in core_set
    ]
    # Be conservative if drat-trim emitted a reduced/non-original clause file.
    if not kept:
        kept = list(usable)
        return kept, "UNMAPPED_CORE"
    return kept, "CORE"


def valid_patterns(S, b_edges, cross, patterns):
    theory = cegar.BTheory(S, cross, b_edges)
    kept = []
    for p in patterns:
        if not theory.query(dict(zip(*p))):
            kept.append(p)
    theory.close()
    return kept


def b_greedy_batches(S, b_edges, cross, patterns, seed=1, batch=16,
                     repair=True):
    """Batch deletion with failed-pattern-first repair ordering."""
    rng = random.Random(seed)
    current = set(S)
    theory = BIncremental(current, b_edges, cross)
    failures = list(range(len(patterns)))
    removed = 0
    while True:
        changed = False
        candidates = list(current)
        rng.shuffle(candidates)
        for start in range(0, len(candidates), batch):
            group = set(candidates[start:start + batch])
            trial = current - group
            failed = []
            for i in failures + [
                i for i in range(len(patterns)) if i not in failures
            ]:
                vs, cs = patterns[i]
                if theory.query(trial, (vs, cs)):
                    failed.append(i)
                    break
            if not failed:
                current = trial
                removed += len(group)
                changed = True
                continue
            if not repair:
                failures = failed + [
                    i for i in failures if i not in failed
                ]
                continue
            # Destroy-and-repair: restore the batch, then try individual
            # vertices in the order that exposed the first failure.
            for v in group:
                trial = current - {v}
                failed_one = []
                for i in failures + [
                    i for i in range(len(patterns)) if i not in failures
                ]:
                    vs, cs = patterns[i]
                    if theory.query(trial, (vs, cs)):
                        failed_one.append(i)
                        break
                if not failed_one:
                    current = trial
                    removed += 1
                    changed = True
                else:
                    failures = failed_one + [
                        i for i in failures if i not in failed_one
                    ]
        if not changed:
            theory.close()
            return current, removed


def refresh(L, S, a_pool, a_edges, b_edges, cross, patterns):
    """Refresh lazy P after S changes, retaining only valid clauses first."""
    patterns = valid_patterns(S, b_edges, cross, patterns)
    L, patterns, hist, status = cegar.run_cegar(
        L, S, a_pool, a_edges, b_edges, cross, patterns
    )
    if status == "UNSAT":
        patterns, prune_status = prune_patterns_a(L, a_edges, patterns)
        return L, S, patterns, status, prune_status
    return L, S, patterns, status, "NO_CORE"


def run(cache, initial_ids, pattern_pickle, rounds=3, seed=1, greedy=True,
        greedy_batch=16, repair=True):
    points, labels, metadata, a_pool, b_pool, _, _ = cegar.side_sets(
        cache, "full"
    )
    b_edges, cross = cegar.split_edges(labels, metadata)
    ids = pickle.load(open(initial_ids, "rb"))
    L = set(ids["L"] if isinstance(ids, dict) else ids[0])
    S = set(ids["S"] if isinstance(ids, dict) else ids[1])
    result = pickle.load(open(pattern_pickle, "rb"))
    if isinstance(result, tuple):
        patterns = list(result[1])
    elif isinstance(result, dict):
        patterns = list(result["patterns"])
    else:
        patterns = list(result)
    trajectory = []
    for rno in range(rounds):
        started = time.time()
        patterns = valid_patterns(S, b_edges, cross, patterns)
        if not patterns:
            trajectory.append({
                "round": rno, "status": "NO_VALID_PATTERNS",
                "L": len(L), "S": len(S),
            })
            break
        L, patterns, hist, status = cegar.run_cegar(
            L, S, a_pool, labels["AA"], b_edges, cross, patterns
        )
        if status != "UNSAT":
            trajectory.append({
                "round": rno, "status": status,
                "L": len(L), "S": len(S),
                "patterns": len(patterns),
            })
            break
        patterns, pstatus = prune_patterns_a(L, labels["AA"], patterns)
        S, removed_core = stage4.b_core_reduce(
            S, b_edges, cross, patterns
        )
        if greedy:
            S, removed_greedy = b_greedy_batches(
                S, b_edges, cross, patterns, seed=seed + rno,
                batch=greedy_batch, repair=repair,
            )
        else:
            removed_greedy = 0
        trajectory.append({
            "round": rno,
            "status": "UNSAT",
            "L": len(L),
            "S": len(S),
            "patterns": len(patterns),
            "orders": dict(Counter(len(vs) for vs, _ in patterns)),
            "pattern_core": pstatus,
            "removed_core": removed_core,
            "removed_greedy": removed_greedy,
            "seconds": time.time() - started,
        })
        print(trajectory[-1], flush=True)
        # The next round refreshes P against the smaller B and re-solves A.
    return {
        "L": sorted(L),
        "S": sorted(S),
        "patterns": patterns,
        "trajectory": trajectory,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("initial_ids")
    ap.add_argument("patterns")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-greedy", action="store_true")
    ap.add_argument("--greedy-batch", type=int, default=16)
    ap.add_argument("--batch-only", action="store_true")
    args = ap.parse_args()
    result = run(
        args.cache, args.initial_ids, args.patterns,
        rounds=args.rounds, seed=args.seed, greedy=not args.no_greedy,
        greedy_batch=args.greedy_batch,
        repair=not args.batch_only,
    )
    pickle.dump(result, open(args.out, "wb"), protocol=pickle.HIGHEST_PROTOCOL)
    print(result["trajectory"])


if __name__ == "__main__":
    main()
