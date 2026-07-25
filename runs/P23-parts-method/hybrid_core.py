"""Corrected adapter of the fusion1 SAT-core jump for Parts pools."""
import os
import pickle
import subprocess
import tempfile

from sat import color_cnf, write_cnf

POOL = os.environ["POOL"]
allpts, E = pickle.load(open(POOL, "rb"))
NALL = len(allpts)
adj = [set() for _ in range(NALL)]
for u, v in E:
    adj[u].add(v)
    adj[v].add(u)

KISSAT = os.environ.get("KISSAT", "/home/ubuntu/tools/kissat/build/kissat")
DRATTRIM = os.environ.get("DRATTRIM", "/home/ubuntu/tools/drat-trim/drat-trim")


def find_triangle(active):
    aset = set(active)
    for u in sorted(aset):
        for v in sorted(adj[u] & aset):
            if v <= u:
                continue
            for w in sorted(adj[u] & adj[v] & aset):
                if w > v:
                    return u, v, w
    return None


def solve_core(active, seed=0, timeout=3600, tag="cm"):
    active = sorted(active)
    remap = {x: i for i, x in enumerate(active)}
    edges = [(remap[u], remap[v]) for u, v in E
             if u in remap and v in remap]
    triangle = find_triangle(active)
    if triangle is None:
        return "UNKNOWN", None
    triangle2 = tuple(remap[x] for x in triangle)
    nvars, clauses = color_cnf(len(active), edges, 4,
                                sym_clique=triangle2)
    tmpdir = tempfile.gettempdir()
    base = os.path.join(tmpdir, f"parts_{os.getpid()}_{tag}_{seed}")
    cnf, drat, core = base + ".cnf", base + ".drat", base + ".core"
    try:
        write_cnf(cnf, nvars, clauses)
        run = subprocess.run(
            [KISSAT, "-q", f"--seed={seed}", cnf, drat],
            capture_output=True, text=True, timeout=timeout)
        if "s UNSATISFIABLE" not in run.stdout:
            if "s SATISFIABLE" in run.stdout:
                return "SAT", None
            return "UNKNOWN", None
        trim = subprocess.run([DRATTRIM, cnf, drat, "-c", core],
                              capture_output=True, text=True, timeout=timeout)
        if "VERIFIED" not in trim.stdout:
            return "NOVERIFY", None
        keep = set()
        with open(core) as stream:
            stream.readline()
            for line in stream:
                for token in line.split()[:-1]:
                    literal = abs(int(token))
                    keep.add(active[(literal - 1) // 4])
        keep |= set(triangle)
        return "UNSAT", keep
    finally:
        for path in (cnf, drat, core):
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
