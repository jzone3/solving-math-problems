#!/usr/bin/env python3
"""Deep corrected-freed greedy expansion sweep for S, L, and the joint union."""
import argparse
import datetime
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor

from mring import orbit
from sat_parts import CNFTemplate, PartsGraph
from screening import append_note, screen_one

HERE = os.path.dirname(os.path.abspath(__file__))
DECOMP = os.path.join(HERE, "decomp509.pkl")

S_REPS = [(12, 2, 2, 0), (6, 2, 4, 0), (1, 1, 3, 5),
          (4, 0, 2, 2), (6, 0, 4, 6), (2, 0, 4, 2),
          (12, 0, 2, 6), (0, 0, 6, 6)]
L_REPS = [(4, 0, 4, 4), (1, 1, 3, 5), (2, 0, 2, 4),
          (10, 0, 8, 2), (6, 2, 4, 0), (6, 2, 8, 0)]
START = (6, 2, 4, 0)


def log_row(row):
    append_note(row)


def run_side(leg, steps, workers):
    d = pickle.load(open(DECOMP, "rb"))
    reps = S_REPS if leg == "S" else L_REPS
    selected = [START]
    for step in range(steps):
        choices = [rep for rep in reps if rep not in selected]
        scored = []
        for rep in choices:
            started = time.perf_counter()
            graph, baseline, indispensable, checks, _ = screen_one(
                d, leg, [orbit(x) for x in selected + [rep]], workers)
            wall = time.perf_counter() - started
            freed = len(d[leg]) - indispensable
            label = f"deep-greedy{step + 1} {tuple(selected + [rep])}"
            log_row((
                datetime.datetime.now().isoformat(timespec="seconds"),
                leg, label, len(graph.W),
                f"indispensable={indispensable};freed={freed}",
                indispensable, checks, f"{wall:.1f}s", baseline.status,
            ))
            print(leg, label, "freed", freed, "wall", round(wall, 1),
                  flush=True)
            if baseline.status == "UNSAT":
                scored.append((freed, rep))
        if not scored:
            break
        best = max(scored)
        selected.append(best[1])
        print(leg, "SELECT", selected, "freed", best[0], flush=True)
    out = os.path.join(HERE, f"deep_{leg.lower()}_decomp.pkl")
    result = {
        "L": d["L"] if leg == "S" else frozenset(
            set(d["L"]) | set().union(*(orbit(x) for x in selected))),
        "S": d["S"] if leg == "L" else frozenset(
            set(d["S"]) | set().union(*(orbit(x) for x in selected))),
        "selected": selected,
    }
    pickle.dump(result, open(out, "wb"))
    print(leg, "FINAL_SELECTION", selected, "vertices",
          len(result[leg]), "output", out, flush=True)


def joint_screen(d, l_selected, s_selected, workers):
    data = {
        "L": frozenset(set(d["L"]) |
                       set().union(*(orbit(x) for x in l_selected))),
        "S": frozenset(set(d["S"]) |
                       set().union(*(orbit(x) for x in s_selected))),
    }
    expanded = PartsGraph.from_decomposition(data, "L")
    old_graph = PartsGraph.from_decomposition(d, "L")
    old_indices = [expanded.points.index(p) for p in old_graph.points]
    clique = tuple(expanded.points.index(p) for p in (
        old_graph.points[0],
        old_graph.points[old_graph.ring_points["clique"][1]],
        old_graph.points[old_graph.ring_points["clique"][2]],
    ))
    template = CNFTemplate(len(expanded.points), expanded.edges,
                           sym_clique=clique)
    baseline = template.solve(range(len(expanded.points)))

    def check(i):
        return template.solve(set(range(len(expanded.points))) - {i})

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(check, old_indices))
    indispensable = sum(r.status == "SAT" for r in results)
    freed = sum(r.status == "UNSAT" for r in results)
    return (data, expanded, baseline, indispensable, freed, len(results),
            time.perf_counter() - started)


def run_joint(steps, workers):
    d = pickle.load(open(DECOMP, "rb"))
    l_selected = [(4, 0, 4, 4)]
    s_selected = [(12, 2, 2, 0)]
    l_choices = [x for x in L_REPS if x not in l_selected]
    s_choices = [x for x in S_REPS if x not in s_selected]
    for step in range(steps):
        scored = []
        for side, choices in (("L", l_choices), ("S", s_choices)):
            for rep in choices:
                ls = l_selected + [rep] if side == "L" else l_selected
                ss = s_selected + [rep] if side == "S" else s_selected
                data, expanded, baseline, indispensable, freed, checks, wall = (
                    joint_screen(d, ls, ss, workers))
                label = f"joint-deep{step + 1} L{tuple(ls)} S{tuple(ss)}"
                log_row((
                    datetime.datetime.now().isoformat(timespec="seconds"),
                    "joint", label, len(expanded.points),
                    f"indispensable={indispensable};freed={freed}",
                    indispensable, checks, f"{wall:.1f}s", baseline.status,
                ))
                print("joint", label, "freed", freed, "wall", round(wall, 1),
                      flush=True)
                if baseline.status == "UNSAT":
                    scored.append((freed, side, rep))
        if not scored:
            break
        best = max(scored)
        _, side, rep = best
        (l_selected if side == "L" else s_selected).append(rep)
        if side == "L":
            l_choices.remove(rep)
        else:
            s_choices.remove(rep)
        print("joint SELECT", side, rep, "freed", best[0],
              "L", l_selected, "S", s_selected, flush=True)
    out = os.path.join(HERE, "deep_joint_decomp.pkl")
    result = {
        "L": frozenset(set(d["L"]) |
                       set().union(*(orbit(x) for x in l_selected))),
        "S": frozenset(set(d["S"]) |
                       set().union(*(orbit(x) for x in s_selected))),
        "L_selected": l_selected,
        "S_selected": s_selected,
    }
    pickle.dump(result, open(out, "wb"))
    print("joint FINAL_SELECTION", l_selected, s_selected,
          "vertices", len(result["L"]) + len(result["S"]) - 1,
          "output", out, flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", choices=("S", "L", "joint"), required=True)
    ap.add_argument("--steps", type=int, default=7)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()
    if args.leg == "joint":
        run_joint(args.steps, args.workers)
    else:
        run_side(args.leg, args.steps, args.workers)


if __name__ == "__main__":
    main()
