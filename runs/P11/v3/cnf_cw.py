#!/usr/bin/env python3
"""CNF encodings (for kissat) of CW existence instances.

Ternary variable v_i in {-1,0,1} -> booleans pos_i, neg_i, not both.
Products p = v_i * v_j -> booleans pp (p=+1), pn (p=-1) with full Tseitin
equivalences:
  pp <-> (pos_i & pos_j) | (neg_i & neg_j)
  pn <-> (pos_i & neg_j) | (neg_i & pos_j)
Weighted equality  sum_r c_r x_r  =  sum_s d_s y_s  (all c,d > 0) is encoded as
cardinality-equals over duplicated literals:
  sum c_r x_r + sum d_s (~y_s) = sum d_s.
Cardinality equals via pysat CardEnc (totalizer supports duplicated lits).
"""
import subprocess
import tempfile
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, CNF

KISSAT = "/home/ubuntu/kissat/build/kissat"


class Builder:
    def __init__(self):
        self.pool = IDPool()
        self.cnf = CNF()

    def var(self, name):
        return self.pool.id(name)

    def add(self, *cl):
        self.cnf.append(list(cl))

    def and2(self, a, b):
        """aux <-> a & b"""
        x = self.pool.id(("and", a, b))
        self.add(-x, a)
        self.add(-x, b)
        self.add(x, -a, -b)
        return x

    def or2(self, a, b):
        x = self.pool.id(("or", a, b))
        self.add(x, -a)
        self.add(x, -b)
        self.add(-x, a, b)
        return x

    def eq_sums(self, pos_terms, neg_terms):
        """sum_{(c,x) in pos_terms} c*x - sum_{(d,y) in neg_terms} d*y = 0."""
        lits = []
        bound = 0
        for c, x in pos_terms:
            lits.extend([x] * c)
        for d, y in neg_terms:
            lits.extend([-y] * d)
            bound += d
        enc = CardEnc.equals(lits=lits, bound=bound, vpool=self.pool,
                             encoding=EncType.totalizer)
        self.cnf.extend(enc.clauses)

    def solve(self, timeout=None, extra=()):
        with tempfile.NamedTemporaryFile("w", suffix=".cnf",
                                         delete=False) as f:
            self.cnf.to_fp(f)
            path = f.name
        cmd = [KISSAT, "-q", *extra, path]
        if timeout:
            cmd = ["timeout", str(timeout)] + cmd
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = r.stdout
        if "s SATISFIABLE" in out:
            model = set()
            for line in out.splitlines():
                if line.startswith("v "):
                    for tok in line[2:].split():
                        v = int(tok)
                        if v > 0:
                            model.add(v)
            return "SAT", model
        if "s UNSATISFIABLE" in out:
            return "UNSAT", None
        return "UNKNOWN", None


def ternary(b, name):
    p = b.var(("pos", name))
    q = b.var(("neg", name))
    b.add(-p, -q)
    return p, q


def product_lits(b, pi, ni, pj, nj):
    pp = b.or2(b.and2(pi, pj), b.and2(ni, nj))
    pn = b.or2(b.and2(pi, nj), b.and2(ni, pj))
    return pp, pn
