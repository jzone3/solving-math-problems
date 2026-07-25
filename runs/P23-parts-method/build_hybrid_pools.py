#!/usr/bin/env python3
"""Materialize exact Parts-expanded graphs for the legacy core minimizer."""
import os
import pickle

from mring import orbit
from sat_parts import PartsGraph

HERE = os.path.dirname(os.path.abspath(__file__))
D = pickle.load(open(os.path.join(HERE, "decomp509.pkl"), "rb"))


def materialize(name, decomposition, working, fixed_mode="companion"):
    graph = PartsGraph.from_decomposition(decomposition, working)
    pool = os.path.join(HERE, f"pool_{name}.pkl")
    pickle.dump((graph.points, sorted(graph.edges)), open(pool, "wb"))
    if fixed_mode == "companion":
        fixed = sorted(graph.C)
        start = list(range(len(graph.points)))
        variable = sorted(graph.W)
    else:
        fixed = []
        start = list(range(len(graph.points)))
        variable = start
    pickle.dump(start, open(os.path.join(HERE, f"start_{name}.pkl"), "wb"))
    pickle.dump(fixed, open(os.path.join(HERE, f"fixed_{name}.pkl"), "wb"))
    pickle.dump({
        "name": name,
        "working": working,
        "points": graph.points,
        "edges": graph.edges,
        "W": graph.W,
        "C": graph.C,
        "variable": variable,
        "fixed": fixed,
        "decomposition": decomposition,
    }, open(os.path.join(HERE, f"meta_{name}.pkl"), "wb"))
    print(name, "vertices", len(graph.points), "edges", len(graph.edges),
          "variable", len(variable), "fixed", len(fixed))


S_best = {
    "L": D["L"],
    "S": frozenset(set(D["S"]) | orbit((6, 2, 4, 0))
                   | orbit((6, 0, 4, 6)) | orbit((12, 0, 2, 6))),
}
L_best = {
    "L": frozenset(set(D["L"]) | orbit((6, 2, 4, 0))
                   | orbit((1, 1, 3, 5)) | orbit((6, 2, 8, 0))),
    "S": D["S"],
}
JOINT = {
    "L": frozenset(set(D["L"]) | orbit((4, 0, 4, 4))),
    "S": frozenset(set(D["S"]) | orbit((12, 2, 2, 0))),
}
S181 = {
    "L": D["L"],
    "S": frozenset(set(D["S"]) | orbit((12, 2, 2, 0))
                   | orbit((1, 1, 3, 5))),
}

materialize("sbest", S_best, "S")
materialize("lbest", L_best, "L")
materialize("joint", JOINT, "L", fixed_mode="all")
materialize("split_s181", S181, "L")
