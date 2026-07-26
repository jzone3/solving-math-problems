# Provenance: new stage-2 analyser based on origin/runs/P23-fusion1/ports.py and scratch/paircal2.py.
"""Interface-pattern analysis for a cached translated two-half universe."""

from __future__ import annotations

import argparse
import itertools
import pickle
import time

from pysat.solvers import Cadical153

from gadget import color_var


def canonical_patterns(k):
    """Equality types on k ordered vertices, using colors 0..3 canonically."""
    out = []

    def rec(prefix):
        if len(prefix) == k:
            out.append(tuple(prefix))
            return
        for c in range(min(4, max(prefix, default=-1) + 2)):
            rec(prefix + [c])

    rec([0])
    return out if k else [()]


def clauses_for_coloring(vertices, edges):
    cls = []
    for v in vertices:
        cls.append([color_var(v, c) for c in range(4)])
        for c1, c2 in itertools.combinations(range(4), 2):
            cls.append([-color_var(v, c1), -color_var(v, c2)])
    for u, v in edges:
        for c in range(4):
            cls.append([-color_var(u, c), -color_var(v, c)])
    return cls


def interface_data(points, edges, labels, a_n):
    cross = labels["cross"]
    oriented = [
        (u, v) if u < a_n <= v else (v, u)
        for u, v in cross
    ]
    interface_a = sorted({u for u, _ in oriented})
    interface_b = sorted({v for _, v in oriented})
    b_vertices = sorted(
        {v for e in labels["BB"] for v in e}
        | {v for _, v in oriented}
    )
    b_edges = labels["BB"]
    return interface_a, interface_b, b_vertices, b_edges, oriented


def analyse(cache, max_triples=True):
    points, edges, labels, metadata = pickle.load(open(cache, "rb"))
    ia, ib, b_vertices, b_edges, cross = interface_data(
        points, edges, labels, metadata["A_candidates"]
    )
    cls = clauses_for_coloring(b_vertices, b_edges + cross)
    base_ok = None
    pairs = []
    triples = []
    t0 = time.time()
    with Cadical153(bootstrap_with=cls) as solver:
        base_ok = solver.solve()
        if not base_ok:
            raise RuntimeError("S plus cross-edge theory is already UNSAT")

        pair_forbidden = set()
        for u, v in itertools.combinations(ia, 2):
            for pat in canonical_patterns(2):
                assumptions = [color_var(u, pat[0]), color_var(v, pat[1])]
                if not solver.solve(assumptions=assumptions):
                    item = (u, v, pat)
                    pairs.append(item)
                    pair_forbidden.add((u, v, pat))

        if max_triples:
            for triple in itertools.combinations(ia, 3):
                for pat in canonical_patterns(3):
                    covered = False
                    for i, j in itertools.combinations(range(3), 2):
                        sub = (triple[i], triple[j], (pat[i], pat[j]))
                        if sub in pair_forbidden:
                            covered = True
                            break
                    if covered:
                        continue
                    assumptions = [
                        color_var(v, c) for v, c in zip(triple, pat)
                    ]
                    if not solver.solve(assumptions=assumptions):
                        triples.append((triple, pat))

    result = {
        "cache": cache,
        "metadata": metadata,
        "interface_a": ia,
        "interface_b": ib,
        "b_vertices": b_vertices,
        "cross": cross,
        "pairs": pairs,
        "triples": triples,
        "seconds": time.time() - t0,
    }
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cache")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-triples", action="store_true")
    args = ap.parse_args()
    result = analyse(args.cache, not args.no_triples)
    print(
        f"interface A={len(result['interface_a'])} "
        f"B={len(result['interface_b'])}; cross={len(result['cross'])}; "
        f"forbidden pairs={len(result['pairs'])} "
        f"triples={len(result['triples'])}; {result['seconds']:.2f}s"
    )
    if args.out:
        with open(args.out, "wb") as f:
            pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    main()
