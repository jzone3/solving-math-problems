#!/usr/bin/env python3
"""Configurable implementation of Parts' two-phase fine-search reduction."""
import argparse
import itertools
import os
import pickle
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

from mring import TAUS, base_graph, orbit, orbit_representative, tau
from sat_parts import CNFTemplate, PartsGraph


@dataclass
class FineConfig:
    working: str = "L"
    max_degree: int = 3
    workers: int = 8
    timeout: float | None = None
    max_checks: int | None = None
    grouped: bool = True
    symmetry: bool = True
    current_min: int | None = None
    expansion: bool = False
    orbit_additions: list = field(default_factory=list)


@dataclass
class FineResult:
    baseline: object
    hyperedges: dict
    phase2_candidates: list
    minima: list
    timings: dict


class FineSearch:
    def __init__(self, graph, config):
        self.graph = graph
        self.config = config
        self.template = graph.template()
        self.W = tuple(sorted(graph.W))
        self.C = graph.C
        self.check_count = 0
        self.timings = {"SAT": [], "UNSAT": [], "UNKNOWN": []}
        self._stats_lock = threading.Lock()
        self._permutations = self._build_permutations()

    def _build_permutations(self):
        if not self.config.symmetry or self.graph.working != "L":
            return []
        coords = self.graph.ring_points["W"]
        by_coord = {v: i for i, v in enumerate(coords)}
        generators = []
        for matrix in TAUS[1:]:
            image = []
            for v in coords:
                w = tuple(int(x) for x in tau(v, matrix))
                if w not in by_coord:
                    break
                image.append(by_coord[w])
            else:
                generators.append(tuple(image))
        identity = tuple(range(len(coords)))
        seen, queue = {identity}, [identity]
        while queue:
            p = queue.pop()
            for g in generators:
                q = tuple(p[g[i]] for i in range(len(p)))
                if q not in seen:
                    seen.add(q)
                    queue.append(q)
        return list(seen)

    def canonical_deleted(self, deleted):
        deleted = frozenset(deleted)
        if not self._permutations:
            return deleted
        return min(frozenset(p[i] for i in deleted) for p in self._permutations)

    def check_deleted(self, deleted, proof=False):
        with self._stats_lock:
            self.check_count += 1
        result = self.template.solve(set(self.W) - set(deleted), proof,
                                     self.config.timeout)
        with self._stats_lock:
            self.timings.setdefault(result.status, []).append(result.seconds)
        return result

    def baseline_check(self):
        return self.check_deleted(())

    def _candidate_test(self, deleted):
        return deleted, self.check_deleted(deleted)

    def find_hyperedges(self):
        """Find critical deletion sets, increasing degree, with minimality."""
        found = {d: [] for d in range(1, self.config.max_degree + 1)}
        for degree in range(1, self.config.max_degree + 1):
            if degree == 1:
                candidates = [(v,) for v in self.W]
            else:
                candidates = itertools.combinations(self.W, degree)
            for deleted in candidates:
                if self.config.max_checks and self.check_count >= self.config.max_checks:
                    return found
                # No hyperedge may contain a previously found lower-degree
                # hyperedge, per Parts' definition.
                if any(set(h).issubset(deleted)
                       for lower in range(1, degree) for h in found[lower]):
                    continue
                result = self.check_deleted(deleted)
                if result.status == "SAT":
                    found[degree].append(tuple(deleted))
            if degree > 1 and not found[degree]:
                continue
        return found

    def grouped_hyperedges(self, degree=1):
        """Parts' 8-4-2-1 grouped deletion accelerator.

        A group is used only as a screening operation.  If group deletion is
        SAT, the group is recursively split; if UNSAT, every member is known
        to be individually safe to delete.
        """
        items = [(v,) for v in self.W] if degree == 1 else list(
            itertools.combinations(self.W, degree))
        found = []

        def split(batch, known=None):
            if not batch:
                return
            deleted = set().union(*batch)
            if len(batch) == 1:
                result = known or self.check_deleted(batch[0])
                if result.status == "SAT":
                    d = batch[0]
                    found.append(d)
                return
            result = known or self.check_deleted(deleted)
            if result.status == "UNSAT":
                return
            mid = len(batch) // 2
            split(batch[:mid])
            split(batch[mid:])

        batches = [items[i:i + 8] for i in range(0, len(items), 8)]
        with ThreadPoolExecutor(max_workers=self.config.workers) as pool:
            results = list(pool.map(
                lambda batch: self.check_deleted(set().union(*batch)), batches))
        for batch, result in zip(batches, results):
            split(batch, result)
        return found

    def discover_hyperedges(self):
        found = {d: [] for d in range(1, self.config.max_degree + 1)}
        if self.config.grouped:
            found[1] = self.grouped_hyperedges(1)
        else:
            found[1] = [(v,) for v in self.W
                        if self.check_deleted((v,)).status == "SAT"]
        for degree in range(2, self.config.max_degree + 1):
            # Lower-degree critical sets cannot be contained in a new set.
            lower = [set(h) for d in found if d < degree for h in found[d]]
            for deleted in itertools.combinations(self.W, degree):
                if self.config.max_checks and self.check_count >= self.config.max_checks:
                    return found
                if any(h.issubset(deleted) for h in lower):
                    continue
                if self.check_deleted(deleted).status == "SAT":
                    found[degree].append(deleted)
        return found

    def phase2_candidates(self, hyperedges):
        """Build deletion candidates from independent sets and higher splits."""
        pairs = [set(h) for h in hyperedges.get(2, [])]
        blocked = set().union(*pairs) if pairs else set()
        free = set(self.W) - blocked
        # Enumerate maximal independent sets for the degree-2 graph.  This is
        # exponential in general; the cap is intentional and configurable.
        independent = []
        for r in range(len(pairs) + 1):
            for subset in itertools.combinations(blocked, r):
                s = set(subset)
                if all(not (s >= p) for p in pairs):
                    if not any(s < q for q in independent):
                        independent = [q for q in independent if not q < s]
                        independent.append(s)
        if not pairs:
            independent = [set()]
        candidates = [set(s) | free for s in independent]
        for degree in sorted(k for k in hyperedges if k >= 3):
            for h in hyperedges[degree]:
                candidates = [c - {h[0]} | set() for c in candidates
                              if set(h).issubset(c)] + [
                                  c for c in candidates if not set(h).issubset(c)]
        candidates.sort(key=lambda x: (-len(x), tuple(sorted(x))))
        unique = {}
        for candidate in candidates:
            unique.setdefault(self.canonical_deleted(candidate), candidate)
        return list(unique.values())

    def reduce(self, hyperedges):
        candidates = self.phase2_candidates(hyperedges)
        minimum = self.config.current_min or len(self.W)
        minima = []
        for deleted in candidates:
            if len(self.W) - len(deleted) > minimum:
                continue
            result = self.check_deleted(deleted)
            if result.status != "UNSAT":
                continue
            size = len(self.W) - len(deleted)
            if size < minimum:
                proof_result = self.check_deleted(deleted, proof=True)
                if proof_result.status != "UNSAT":
                    raise RuntimeError("candidate failed exact DRAT-backed recheck")
            if size < minimum:
                minimum, minima = size, []
            if size == minimum:
                minima.append(frozenset(set(self.W) - set(deleted)))
        return candidates, minima


def expansion_reserve(A, radius=2):
    """Build Parts' reserve orbit list from B=⊕⁴H²."""
    B = base_graph(4, 2)
    disk = set()
    for v in B:
        a, b, c, d = v
        norm_a = a * a + 33 * b * b + 3 * c * c + 11 * d * d
        q = a * b + c * d
        t = (12 * radius) ** 2
        delta = norm_a - t
        if q >= 0:
            inside = delta <= 0 or delta * delta <= 132 * q * q
        else:
            aq = -q
            inside = delta <= 0 and delta * delta >= 132 * aq * aq
        if inside:
            disk.add(v)
    orbits = {}
    for v in disk:
        r = orbit_representative(v)
        orbits.setdefault(r, set()).update(orbit(v) & disk)
    scored = []
    for r, vertices in orbits.items():
        added = vertices - set(A)
        if not added:
            continue
        degree = sum(1 for x in added for y in A
                     if x != y and abs((x[0] - y[0]) ** 2 +
                                       33 * (x[1] - y[1]) ** 2 +
                                       3 * (x[2] - y[2]) ** 2 +
                                       11 * (x[3] - y[3]) ** 2 - 144) < 1e-9)
        scored.append((degree, len(added), r, frozenset(added)))
    return sorted(scored, key=lambda x: (-x[0], x[1], x[2]))


def run(config, cache="decomp509.pkl"):
    with open(cache, "rb") as f:
        decomposition = pickle.load(f)
    graph = PartsGraph.from_decomposition(decomposition, config.working)
    search = FineSearch(graph, config)
    baseline = search.baseline_check()
    hyperedges = search.discover_hyperedges()
    candidates, minima = search.reduce(hyperedges)
    return FineResult(baseline, hyperedges, candidates, minima, search.timings)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--working", choices=("L", "S"), default="L")
    ap.add_argument("--max-degree", type=int, default=3)
    ap.add_argument("--ungrouped", action="store_true")
    ap.add_argument("--max-checks", type=int)
    ap.add_argument("--timeout", type=float)
    args = ap.parse_args()
    config = FineConfig(working=args.working, max_degree=args.max_degree,
                        grouped=not args.ungrouped,
                        max_checks=args.max_checks, timeout=args.timeout)
    started = time.perf_counter()
    result = run(config, os.path.join(os.path.dirname(__file__), "decomp509.pkl"))
    elapsed = time.perf_counter() - started
    print("baseline:", result.baseline.status, f"{result.baseline.seconds:.3f}s")
    print("hyperedges:", {k: len(v) for k, v in result.hyperedges.items()})
    print("phase2 candidates:", len(result.phase2_candidates))
    print("minima:", [len(x) for x in result.minima])
    print("checks:", sum(map(len, result.timings.values())), "elapsed:", f"{elapsed:.3f}s")
    for status, values in result.timings.items():
        if values:
            print(status, "count", len(values), "mean", f"{sum(values)/len(values):.4f}s",
                  "min", f"{min(values):.4f}s", "max", f"{max(values):.4f}s")


if __name__ == "__main__":
    main()
