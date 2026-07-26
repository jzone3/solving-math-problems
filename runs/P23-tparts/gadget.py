# Provenance: copied from origin/runs/P23-parts-gadgets:runs/P23-parts-gadgets/gadget.py.
"""Generic SAT/DRAT helpers for forcing-pattern subgraphs."""

import os
import shutil
import subprocess
import tempfile

KISSAT = os.environ.get("KISSAT") or shutil.which("kissat") or os.path.expanduser(
    "~/p23/kissat/build/kissat"
)
DRAT = os.environ.get("DRATTRIM") or shutil.which("drat-trim") or os.path.expanduser(
    "~/p23/drat-trim/drat-trim"
)


def color_var(i, k):
    return 4 * i + k + 1


def build_cnf(n, edges, prop_clauses=()):
    cls = []
    for i in range(n):
        cls.append([color_var(i, k) for k in range(4)])
        for c1 in range(4):
            for c2 in range(c1 + 1, 4):
                cls.append([-color_var(i, c1), -color_var(i, c2)])
    for u, v in edges:
        for c in range(4):
            cls.append([-color_var(u, c), -color_var(v, c)])
    cls.extend(prop_clauses)
    return cls


def write_cnf(cls, nvars, path):
    with open(path, "w") as f:
        f.write(f"p cnf {nvars} {len(cls)}\n")
        for clause in cls:
            f.write(" ".join(map(str, clause)) + " 0\n")


def solve(cls, nvars, timeout=None):
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, "f.cnf")
        write_cnf(cls, nvars, cnf)
        try:
            r = subprocess.run(
                [KISSAT, "-q", cnf], capture_output=True, text=True, timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return "UNKNOWN"
        if r.returncode == 10:
            return "SAT"
        if r.returncode == 20:
            return "UNSAT"
        raise RuntimeError(f"kissat failed ({r.returncode}): {r.stderr[-500:]}")


def core_vertices(n, edges, prop_clauses, keep, timeout=None):
    """Return vertices in a DRAT-trim UNSAT core, or None for SAT."""
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, "f.cnf")
        proof = os.path.join(d, "f.drat")
        core = os.path.join(d, "f.core")
        write_cnf(build_cnf(n, edges, prop_clauses), 4 * n, cnf)
        try:
            r = subprocess.run(
                [KISSAT, "-q", cnf, proof],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return None
        if r.returncode == 10:
            return None
        if r.returncode != 20:
            raise RuntimeError(f"kissat failed ({r.returncode}): {r.stderr[-500:]}")
        r2 = subprocess.run(
            [DRAT, cnf, proof, "-c", core], capture_output=True, text=True
        )
        if r2.returncode != 0 and not os.path.exists(core):
            raise RuntimeError(f"drat-trim failed: {r2.stderr[-500:]}")
        used = set(keep)
        if os.path.exists(core):
            for line in open(core):
                if line.startswith(("p", "c")):
                    continue
                for lit in map(int, line.split()):
                    if lit:
                        used.add((abs(lit) - 1) // 4)
        return used
