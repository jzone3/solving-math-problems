"""Faithful mechanization of Nielsen's minimum-modulus-40 construction,
subsection by subsection (Section 4 of the paper), on top of arrow_dsl.

Progress ledger: each subsection consumes named holes from the ledger and
may add new ones.  After all subsections the ledger must be empty and the
system verifies as a covering system with min modulus 40.

Extra primitives needed beyond arrow_dsl core:
  Desc(q, j, expr)   descend along a NEW prime q into branch window j
  Relax(q, e, expr)  relax the current cell's q-part to q^e (covers a
                     superset class; Nielsen's "covering more than needed")
"""
from fractions import Fraction

from arrow_dsl import (Ctx, Expr, Hole, X, One, Split, Arrow, subcell,
                       qval, crt, measure, finalize, fill_arrow)


class Desc(Expr):
    def __init__(self, q, j, expr):
        self.q, self.j, self.expr = q, j, expr

    def eval(self, ctx, a, M, path=""):
        sa, sm = subcell(a, M, self.q, self.j)
        self.expr.eval(ctx, sa, sm, f"{path}/d{self.q}#{self.j}")


class Relax(Expr):
    """Reduce the q-part of the current modulus to q**e (e < current)."""

    def __init__(self, q, e, expr):
        self.q, self.e, self.expr = q, e, expr

    def eval(self, ctx, a, M, path=""):
        cur = qval(M, self.q)
        assert self.e <= cur, f"relax {self.q}^{self.e} vs {self.q}^{cur}"
        M2 = M // self.q ** (cur - self.e)
        self.expr.eval(ctx, a % M2, M2, f"{path}/r{self.q}^{self.e}")


A2 = lambda: Arrow(2, [One()])  # noqa: E731  (2^m)^arrow in context


def R1(e):
    """bare 2-power 2^e: class covering the cell relaxed to 2-part 2^e."""
    return lambda: Relax(2, e, One())


def RA(e):
    """(2^(e+1))^arrow: dyadic arrow on the cell relaxed to 2-part 2^e."""
    return lambda: Relax(2, e, Arrow(2, [One()]))


def sec41(ctx):
    """4.1: 2^arrow minus moduli 2,4,8,16,32; 64^arrow survives."""
    e = Split(2, [Hole("m2"), Split(2, [Hole("m4"), Split(2, [
        Hole("m8"), Split(2, [Hole("m16"), Split(2, [Hole("m32"),
                                                     A2()])])])])])
    e.eval(ctx, 0, 1, "4.1")


def sec42(ctx):
    """4.2: on hole m2 (1 mod 2): 3^arrow(2, 4^arrow) minus moduli
    6,12,18,24,36 -- i.e. 3( ,2(2( ,2( ,2^)), ),3( ,2(2( ,2^), ),
    3^(2(1, ),2(2^, )))) -- plus the extra (2): 81^arrow(1,_) inside the
    m18 hole.  The deep inputs are REFINED (2(1,_), 2(2^,_)) which frees
    the moduli 2*3^n (n>=4) for the extra arrow."""
    (a, M), = ctx.holes.pop("m2")
    lvl1_in2 = Split(2, [Hole("m12"), Split(2, [Hole("m24"), A2()])])
    lvl2_in2 = Split(2, [Hole("m36"), A2()])
    # 27^arrow(2(1, ), 2(2^arrow, )): per-level half-holes shared with
    # the extra 81-arrow / later sections
    rest = Arrow(3, [Split(2, [One(), Hole("c27a")]),
                     Split(2, [A2(), Hole("c27b")])])
    # the m18 hole is immediately split: two mod-54 subcells stay holes,
    # the third ("21 mod 27") carries the extra 81^arrow(1,_)
    m18 = Split(3, [Hole("m18a"), Hole("m18b"),
                    Arrow(3, [One(), Hole("m18rem")])])
    e = Split(3, [Hole("m6"), lvl1_in2,
                  Split(3, [m18, lvl2_in2, rest])])
    e.eval(ctx, a, M, "4.2")


def sec43(ctx):
    """4.3: fill hole m8 (a mod-8 cell) with
    5(8, 16^, 3(4, 3^(4, ), 3^(1, 2)), 3^(8, 16^),
      5^(2, 4^, 3^(1, 2), 3^(4, 8^)))."""
    (a, M), = ctx.holes.pop("m8")
    in3 = Split(3, [R1(2)(), Arrow(3, [R1(2)(), Hole("h43_9")]),
                    Arrow(3, [One(), R1(1)()])])
    in4 = Arrow(3, [One(), A2()])
    in5 = Arrow(5, [R1(1)(), RA(1)(), Arrow(3, [One(), R1(1)()]),
                    Arrow(3, [R1(2)(), RA(2)()])])
    e = Split(5, [One(), A2(), in3, in4, in5])
    e.eval(ctx, a, M, "4.3")


def report(ctx, label):
    hm = sum(measure(cells) for cells in ctx.holes.values())
    print(f"after {label}: {len(ctx.out)} classes, "
          f"{sum(len(c) for c in ctx.holes.values())} hole-cells "
          f"(measure {float(hm):.6f}) : "
          f"{sorted(ctx.holes.keys())}")


def main():
    ctx = Ctx(40)
    sec41(ctx)
    report(ctx, "4.1")
    sec42(ctx)
    report(ctx, "4.2")
    sec43(ctx)
    report(ctx, "4.3")
    finalize(ctx)
    report(ctx, "finalize")
    # sanity: holes + placed classes must exactly tile Z (measure 1 if no
    # overlaps); check measure of classes+holes
    tot = measure(ctx.out) + sum(measure(c) for c in ctx.holes.values())
    print("total measure classes+holes =", tot, "(should be >= 1;"
          " == 1 iff disjoint)")


if __name__ == "__main__":
    main()
