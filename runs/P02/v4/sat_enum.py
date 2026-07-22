"""V4 two-level search: SAT outer enumeration of {maximal triangle-free,
delta >= ceil(n/3)} graphs, LP inner oracle (exact rational) per model.

Written independently of the geng pipeline as a cross-check and to reach
sizes/shapes geng can't. Models are canonicalized with nauty-labelg to count
isomorphism classes.

Usage: python3 sat_enum.py n [--twinfree]
"""
import math
import subprocess
import sys
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical153

from oracle import lp1_multiplication_feasible, is_maximal_tf, is_triangle_free


def edges_to_g6(n, edges):
    es = {frozenset(e) for e in edges}
    bits = []
    for v in range(1, n):
        for u in range(v):
            bits.append(1 if frozenset((u, v)) in es else 0)
    while len(bits) % 6:
        bits.append(0)
    s = chr(n + 63)
    for i in range(0, len(bits), 6):
        s += chr(63 + int("".join(map(str, bits[i:i + 6])), 2))
    return s


def canon(g6):
    return subprocess.run(["nauty-labelg", "-q"], input=g6 + "\n",
                          capture_output=True, text=True).stdout.strip()


def main():
    n = int(sys.argv[1])
    twinfree = "--twinfree" in sys.argv
    mindeg = math.ceil(n / 3)
    pool = IDPool()
    e = {}
    for u, v in combinations(range(n), 2):
        e[(u, v)] = pool.id(("e", u, v))

    def E(a, b):
        return e[(min(a, b), max(a, b))]

    clauses = []
    # triangle-free
    for a, b, c in combinations(range(n), 3):
        clauses.append([-E(a, b), -E(b, c), -E(a, c)])
    # maximality: non-edge uv -> some common neighbour w
    for u, v in combinations(range(n), 2):
        lits = [E(u, v)]
        for w in range(n):
            if w in (u, v):
                continue
            t = pool.id(("t", u, v, w))
            clauses.append([-t, E(u, w)])
            clauses.append([-t, E(v, w)])
            lits.append(t)
        clauses.append(lits)
    # twin-freeness (optional): for each pair some w (!=u,v) with e(u,w) XOR e(v,w)
    if twinfree:
        for u, v in combinations(range(n), 2):
            lits = [E(u, v)]  # adjacent => not twins (twins are non-adjacent here)
            for w in range(n):
                if w in (u, v):
                    continue
                d = pool.id(("d", u, v, w))
                # d -> e(u,w) != e(v,w)
                clauses.append([-d, E(u, w), E(v, w)])
                clauses.append([-d, -E(u, w), -E(v, w)])
                lits.append(d)
            clauses.append(lits)
    # min degree
    for v in range(n):
        lits = [E(v, u) for u in range(n) if u != v]
        cnf = CardEnc.atleast(lits=lits, bound=mindeg, vpool=pool,
                              encoding=EncType.seqcounter)
        clauses.extend(cnf.clauses)

    solver = Cadical153(bootstrap_with=clauses)
    seen = {}
    models = 0
    while solver.solve():
        model = set(l for l in solver.get_model() if l > 0)
        edges = [(u, v) for (u, v), lit in e.items() if lit in model]
        models += 1
        assert is_triangle_free(n, edges) and is_maximal_tf(n, edges)
        c = canon(edges_to_g6(n, edges))
        if c not in seen:
            feas, cert = lp1_multiplication_feasible(n, edges)
            seen[c] = feas
            if not feas:
                print(f"COUNTEREXAMPLE n={n} g6={c} farkas={cert}", flush=True)
        # block this labelled model (block edge set exactly)
        solver.add_clause([-lit if lit in model else lit for lit in e.values()])
        if models % 5000 == 0:
            print(f"...{models} labelled models, {len(seen)} classes", flush=True)
    infeas = sum(1 for v in seen.values() if not v)
    print(f"n={n} mindeg={mindeg} twinfree={twinfree}: labelled_models={models} "
          f"iso_classes={len(seen)} infeasible={infeas}", flush=True)


if __name__ == "__main__":
    main()
