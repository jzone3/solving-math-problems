#!/usr/bin/env python3
"""SAT and exact graph helpers for Parts-style fine searches."""
import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from fractions import Fraction as F
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)),
                                "runs", "P23-fusion1"))

from mfield import MField
from mring import tuple_to_mfield

KISSAT = os.environ.get("KISSAT", "/home/ubuntu/tools/kissat/build/kissat")
DRATTRIM = os.environ.get("DRATTRIM", "/home/ubuntu/tools/drat-trim/drat-trim")
FIELD = MField((3, 5, 11))
ZERO = (FIELD.ZERO, FIELD.ZERO)
ONE = (FIELD.ONE, FIELD.ZERO)


def cmul(z, w):
    return (FIELD.sub(FIELD.mul(z[0], w[0]), FIELD.mul(z[1], w[1])),
            FIELD.add(FIELD.mul(z[0], w[1]), FIELD.mul(z[1], w[0])))


def csub(z, w):
    return (FIELD.sub(z[0], w[0]), FIELD.sub(z[1], w[1]))


def cinv(z):
    n = FIELD.add(FIELD.mul(z[0], z[0]), FIELD.mul(z[1], z[1]))
    ni = FIELD.inv(n)
    return (FIELD.mul(z[0], ni), FIELD.scal(-1, FIELD.mul(z[1], ni)))


RHO = (
    (F(7, 8), F(0), F(0), F(0), F(0), F(0), F(0), F(0)),
    (F(0), F(0), F(0), F(1, 8), F(0), F(0), F(0), F(0)),
)


def var(vertex, color, colors=4):
    return vertex * colors + color + 1


def implication_chain(vertices, colors=4):
    """Clauses forcing all vertices in a set to have the same color."""
    clauses = []
    if len(vertices) < 2:
        return clauses
    for color in range(colors):
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            clauses.append([-var(a, color, colors), var(b, color, colors)])
    return clauses


def color_common(n, edges, colors=4, sym_clique=()):
    """Return common clauses and per-vertex positive clauses.

    At-most-one clauses, edge clauses, and symmetry breaking are common to all
    reduction checks.  Only the positive ``vertex must receive a color``
    clauses belong to the variable part.
    """
    common = []
    vertex = {v: [var(v, c, colors) for c in range(colors)] for v in range(n)}
    for v in range(n):
        for a in range(colors):
            for b in range(a + 1, colors):
                common.append([-var(v, a, colors), -var(v, b, colors)])
    for u, v in edges:
        for c in range(colors):
            common.append([-var(u, c, colors), -var(v, c, colors)])
    symmetry = [[var(v, i, colors)] for i, v in enumerate(sym_clique)]
    return 4 * n, common, vertex, symmetry


@dataclass
class CheckResult:
    status: str
    seconds: float
    model: set | None = None
    proof: str | None = None


class CNFTemplate:
    def __init__(self, n, edges, companion=(), sym_clique=(), colors=4):
        self.n = n
        self.colors = colors
        self.companion = frozenset(companion)
        self.nvars, self.common, self.vertex, self.symmetry = color_common(
            n, edges, colors, sym_clique)
        self.edge_count = len(edges)

    def clauses(self, active):
        active = set(active) | self.companion
        clauses = self.common + [self.vertex[v] for v in sorted(active)]
        clauses.extend(c for c in self.symmetry
                      if (c[0] - 1) // self.colors in active)
        return clauses

    def solve(self, active, proof=False, timeout=None):
        clauses = self.clauses(active)
        with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
            cnf = f.name
        proof_path = None
        try:
            write_cnf(cnf, self.nvars, clauses)
            if proof:
                proof_path = tempfile.mktemp(suffix=".drat")
            cmd = [KISSAT, "-q", cnf]
            if proof_path:
                cmd.append(proof_path)
            start = time.perf_counter()
            try:
                run = subprocess.run(cmd, capture_output=True, text=True,
                                     timeout=timeout)
            except subprocess.TimeoutExpired:
                return CheckResult("UNKNOWN", time.perf_counter() - start)
            elapsed = time.perf_counter() - start
            if "s UNSATISFIABLE" in run.stdout:
                status = "UNSAT"
            elif "s SATISFIABLE" in run.stdout:
                status = "SAT"
            else:
                status = "UNKNOWN"
            result = CheckResult(status, elapsed, proof=proof_path)
            if proof and status == "UNSAT":
                trim = subprocess.run([DRATTRIM, cnf, proof_path],
                                      capture_output=True, text=True)
                if "s VERIFIED" not in trim.stdout:
                    raise RuntimeError("drat-trim did not verify Kissat proof")
            return result
        finally:
            for path in (cnf, proof_path):
                if path:
                    try:
                        os.unlink(path)
                    except FileNotFoundError:
                        pass


def write_cnf(path, nvars, clauses):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


@dataclass
class PartsGraph:
    points: list
    edges: frozenset
    W: frozenset
    C: frozenset
    ring_points: dict
    working: str = "L"

    @classmethod
    def from_decomposition(cls, decomposition, working="L"):
        L = sorted(decomposition["L"])
        S = sorted(decomposition["S"])
        ring_points = {"L": list(L), "S": list(S)}
        physical = {
            "L": [tuple_to_mfield(v, FIELD) for v in L],
            "S": [cmul(RHO, tuple_to_mfield(v, FIELD)) for v in S],
        }
        other = "S" if working == "L" else "L"
        w_points = physical[working]
        c_points = [p for v, p in zip(ring_points[other], physical[other])
                    if v != (0, 0, 0, 0)]
        points = w_points + c_points
        W = frozenset(range(len(w_points)))
        C = frozenset(range(len(w_points), len(points)))
        edges = exact_edges(points)
        if working == "L":
            clique = tuple(L.index(v) for v in
                           ((0, 0, 0, 0), (12, 0, 0, 0), (6, 0, 6, 0)))
        else:
            clique_points = [tuple_to_mfield(v, FIELD) for v in
                             ((12, 0, 0, 0), (6, 0, 6, 0))]
            clique = (0,) + tuple(points.index(p) for p in clique_points)
        return cls(points, frozenset(edges), W, C,
                   {"W": ring_points[working], "L": L, "S": S,
                    "clique": clique}, working)

    @property
    def full_template(self):
        clique = self.symmetry_clique()
        return CNFTemplate(len(self.points), self.edges, self.C, clique)

    def symmetry_clique(self):
        return self.ring_points.get("clique", ())

    def subgraph_edges(self, active):
        active = set(active)
        return frozenset((u, v) for u, v in self.edges
                         if u in active and v in active)

    def template(self):
        return self.full_template


def exact_edges(points):
    """Exact strict-unit edge set, with a float prefilter only for speed."""
    floats = [(FIELD.to_float(p[0]), FIELD.to_float(p[1])) for p in points]
    edges = set()
    for i, (xi, yi) in enumerate(floats):
        for j in range(i + 1, len(points)):
            dx, dy = xi - floats[j][0], yi - floats[j][1]
            if abs(dx * dx + dy * dy - 1.0) > 1e-7:
                continue
            if FIELD.norm2(points[i], points[j]) == FIELD.ONE:
                edges.add((i, j))
    return edges


def verify_drat(template, active, timeout=None):
    return template.solve(active, proof=True, timeout=timeout)


def mono_set_clauses(vertices, colors=4):
    return implication_chain(list(vertices), colors)


def check_mono_set(template, active, vertices, timeout=None):
    clauses = template.clauses(active) + mono_set_clauses(list(vertices))
    with tempfile.NamedTemporaryFile("w", suffix=".cnf", delete=False) as f:
        path = f.name
    try:
        write_cnf(path, template.nvars, clauses)
        start = time.perf_counter()
        run = subprocess.run([KISSAT, "-q", path], capture_output=True,
                             text=True, timeout=timeout)
        elapsed = time.perf_counter() - start
        status = ("UNSAT" if "s UNSATISFIABLE" in run.stdout else
                  "SAT" if "s SATISFIABLE" in run.stdout else "UNKNOWN")
        return CheckResult(status, elapsed)
    finally:
        os.unlink(path)
