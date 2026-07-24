"""SAT machinery for checking and minimizing Parts' gadget graphs.

Gadget properties over a unit-distance graph G with distinguished vertices T:
  mono-pair (u,v):      every proper 4-coloring gives u,v the SAME color.
        refutation CNF: 4-coloring clauses + unit clauses  u=color1, v=color2
        (sound WLOG by color permutation).  UNSAT  <=>  property holds.
  non-mono-pair (u,v):  no proper 4-coloring gives u,v the same color.
        refutation CNF: 4-coloring clauses + unit clauses  u=color1, v=color1.
        UNSAT  <=>  property holds.
  non-mono-triple (u,v,w): never all three the same color.
        refutation CNF: + unit clauses u=v=w=color1.  UNSAT <=> property.

Minimization: kissat produces a DRAT proof, drat-trim -c extracts the UNSAT
core; vertices with no clause in the core are deleted (gadget vertices are
always kept), iterate to fixpoint; then greedy single-vertex deletion with
core jumps.
"""
import os
import subprocess
import sys
import tempfile

KISSAT = os.path.expanduser("~/p23/kissat/build/kissat")
DRAT = os.path.expanduser("~/p23/drat-trim/drat-trim")


def color_var(i, k):
    return 4 * i + k + 1  # vertex i (0-based), color k in 0..3


def build_cnf(n, edges, prop_clauses):
    """Return list of clauses (lists of ints) for 4-coloring + property."""
    cls = []
    for i in range(n):
        cls.append([color_var(i, k) for k in range(4)])
    for (i, j) in edges:
        for k in range(4):
            cls.append([-color_var(i, k), -color_var(j, k)])
    cls.extend(prop_clauses)
    return cls


def prop_mono_pair(u, v):
    return [[color_var(u, 0)], [color_var(v, 1)]]


def prop_nonmono_set(vs):
    return [[color_var(v, 0)] for v in vs]


def write_cnf(cls, nvars, path):
    with open(path, "w") as f:
        f.write("p cnf %d %d\n" % (nvars, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")


def solve(cls, nvars, proof=None, timeout=None):
    """Returns 'UNSAT', 'SAT'."""
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, "f.cnf")
        write_cnf(cls, nvars, cnf)
        cmd = [KISSAT, "-q", cnf]
        if proof:
            cmd.append(proof)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 20:
            return "UNSAT"
        if r.returncode == 10:
            return "SAT"
        raise RuntimeError("kissat failed: %s %s" % (r.returncode, r.stderr[-500:]))


def core_vertices(n, edges, prop_clauses, keep):
    """Solve; if UNSAT extract drat-trim core and return the surviving vertex
    set (vertices appearing in any core clause), else None (SAT)."""
    cls = build_cnf(n, edges, prop_clauses)
    nvars = 4 * n
    with tempfile.TemporaryDirectory() as d:
        cnf = os.path.join(d, "f.cnf")
        proof = os.path.join(d, "f.drat")
        core = os.path.join(d, "f.core")
        write_cnf(cls, nvars, cnf)
        r = subprocess.run([KISSAT, "-q", cnf, proof], capture_output=True, text=True)
        if r.returncode == 10:
            return None
        assert r.returncode == 20, r.stderr[-300:]
        r2 = subprocess.run([DRAT, cnf, proof, "-c", core], capture_output=True, text=True)
        used = set(keep)
        with open(core) as f:
            for line in f:
                if line.startswith(("p", "c")):
                    continue
                for lit in map(int, line.split()):
                    if lit == 0:
                        continue
                    used.add((abs(lit) - 1) // 4)
        return used


def induced(vids, edges):
    """Relabel vertex-id set vids (iterable of old ids) -> (mapping list, edges)."""
    order = sorted(vids)
    idx = {v: i for i, v in enumerate(order)}
    es = [(idx[a], idx[b]) for (a, b) in edges if a in idx and b in idx]
    return order, es


class GadgetInstance:
    """A pool of exact lattice points with a gadget property to preserve."""

    def __init__(self, points, edges, gadget_ids, kind):
        self.points = points          # exact coordinates (frac 4-tuples)
        self.edges = edges            # list of index pairs
        self.gadget = list(gadget_ids)
        self.kind = kind              # 'mono' or 'nonmono'

    def prop(self):
        if self.kind == "mono":
            assert len(self.gadget) == 2
            return prop_mono_pair(*self.gadget)
        return prop_nonmono_set(self.gadget)

    def holds(self):
        return solve(build_cnf(len(self.points), self.edges, self.prop()),
                     4 * len(self.points)) == "UNSAT"

    def shrink_core(self):
        """Iterate drat-trim core reduction to fixpoint. Returns new instance."""
        inst = self
        while True:
            used = core_vertices(len(inst.points), inst.edges, inst.prop(),
                                 set(inst.gadget))
            assert used is not None, "property lost (SAT) during core reduction"
            if len(used) == len(inst.points):
                return inst
            order, es = induced(used, inst.edges)
            idx = {v: i for i, v in enumerate(order)}
            inst = GadgetInstance([inst.points[v] for v in order], es,
                                  [idx[g] for g in inst.gadget], inst.kind)

    def greedy(self, seed=0, log=lambda *a: None):
        """Greedy destructive deletion with core jumps. Vertices are tracked by
        exact coordinates so a pass continues after a successful deletion."""
        import random
        rng = random.Random(seed)
        inst = self.shrink_core()
        while True:
            improved = False
            coords = [inst.points[i] for i in range(len(inst.points))
                      if i not in set(inst.gadget)]
            rng.shuffle(coords)
            for pt in coords:
                loc = {p: i for i, p in enumerate(inst.points)}
                if pt not in loc:
                    continue  # already removed by a core jump
                v = loc[pt]
                vids = set(range(len(inst.points))) - {v}
                ordr, es = induced(vids, inst.edges)
                idx = {u: i for i, u in enumerate(ordr)}
                cand = GadgetInstance([inst.points[u] for u in ordr], es,
                                      [idx[g] for g in inst.gadget], inst.kind)
                used = core_vertices(len(cand.points), cand.edges, cand.prop(),
                                     set(cand.gadget))
                if used is not None:
                    ordr2, es2 = induced(used, cand.edges)
                    idx2 = {u: i for i, u in enumerate(ordr2)}
                    inst = GadgetInstance([cand.points[u] for u in ordr2], es2,
                                          [idx2[g] for g in cand.gadget], cand.kind)
                    log("greedy: %d vertices" % len(inst.points))
                    improved = True
            if not improved:
                return inst
