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
from symbolic import symbolic_verify, _subtract


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


class WinR(Expr):
    """Descend into the sub-cell with a specific residue r mod q^e
    (q coprime to the current modulus): residue-aligned window choice,
    needed when later sections must line up with inherited coverage."""

    def __init__(self, q, r, expr):
        self.q, self.r, self.expr = q, r, expr

    def eval(self, ctx, a, M, path=""):
        sa, sm = crt(a, M, self.r, self.q)
        self.expr.eval(ctx, sa, sm, f"{path}/w{self.r}%{self.q}")


def _erel(inp):
    """Dyadic relaxation depth of an expression, or None if it does not
    spill outside its cell (One/Split/Hole).  An arrow whose inputs are
    all relaxed covers its cell relaxed to the LARGEST input 2-part
    (Nielsen: '4^ = 2( ,2^) ... applies to the entire class 2 (mod 2)')."""
    if isinstance(inp, Relax) and inp.q == 2:
        return inp.e
    if isinstance(inp, Arrow):
        es = [_erel(i) for i in inp.inputs if i is not None]
        if es and all(e is not None for e in es):
            return max(es)
    return None


def _relax_cell(a, M, e):
    v = qval(M, 2)
    if e >= v:
        return a % M, M
    M2 = M // 2 ** (v - e)
    return a % M2, M2


def _spill_regions(ctx):
    """Covered regions implied by pending arrows: relaxed arrow cells
    (when every input is a relaxed class/arrow) plus level-1 input
    classes.  Expanded in a shadow context; nothing is committed."""
    sh = Ctx(1)
    sh.shadow = True
    sh.pending = [dict(r) for r in ctx.pending]
    regions = []
    guard = 0
    while sh.pending:
        guard += 1
        assert guard < 10 ** 5
        rec = sh.pending.pop()
        es = [_erel(i) for i in rec["inputs"] if i is not None]
        if es and all(e is not None for e in es):
            regions.append(_relax_cell(rec["a"], rec["M"], max(es)))
        else:
            regions.append((rec["a"] % rec["M"], rec["M"]))
        for j, inp in enumerate(rec["inputs"], 1):
            if inp is None or isinstance(inp, (Hole, X)):
                continue
            sa, sm = subcell(rec["a"], rec["M"], rec["q"], j)
            inp.eval(sh, sa, sm, f"spill{rec['path']}#{j}")
    regions += [(r % m, m) for r, m in sh.out]
    return regions


def _covered_in(regions, a, M):
    rem = [(a % M, M)]
    for r, m in regions:
        rem = _subtract(rem, r, m)
        if not rem:
            return True
    return False


def _materialize_regions(ctx, depth=4):
    """Concrete covered regions of the system so far: placed classes,
    arrow levels 1..depth (recursively), and each arrow's leftover chain
    cell after `depth` levels (closed later by the multiplier tail)."""
    regions = [(r % m, m) for r, m in ctx.out] + list(ctx.assumed)
    sh = Ctx(1)
    sh.shadow = True
    sh.pending = [dict(r) for r in ctx.pending]
    guard = 0
    while sh.pending:
        guard += 1
        assert guard < 10 ** 5
        rec = sh.pending.pop()
        ca, cm = rec["a"], rec["M"]
        for _k in range(depth):
            for j, inp in enumerate(rec["inputs"], 1):
                if inp is None or isinstance(inp, (Hole, X)):
                    continue
                sa, sm = subcell(ca, cm, rec["q"], j)
                inp.eval(sh, sa, sm, "mat")
            ca, cm = subcell(ca, cm, rec["q"], rec["q"])
        # leftover chain -> multiplier tail; when every input is relaxed
        # the tail classes are relaxed too (Nielsen: the arrow "applies
        # to the entire congruence class 2 (mod 2)"), so the leftover
        # region spills to the relaxed cell
        es = [_erel(i) for i in rec["inputs"] if i is not None]
        if es and all(e is not None for e in es):
            regions.append(_relax_cell(ca, cm, max(es)))
        else:
            regions.append((ca % cm, cm))
    regions += [(r % m, m) for r, m in sh.out]
    return regions


def _cell_covered(ctx, a, M):
    return _covered_in(_materialize_regions(ctx), a, M)


def _probe_xcells(inp, ca, cm):
    """Dry-run inp on cell (ca, cm); return the X cells it would claim."""
    sh = Ctx(1)
    sh.shadow = True
    inp.eval(sh, ca, cm, "probe")
    guard = 0
    while sh.pending:
        guard += 1
        assert guard < 10 ** 4
        rec = sh.pending.pop()
        for j, sub in enumerate(rec["inputs"], 1):
            if sub is None or isinstance(sub, Hole):
                continue
            sa, sm = subcell(rec["a"], rec["M"], rec["q"], j)
            sub.eval(sh, sa, sm, "probe")
    return [(xa, xm) for xa, xm, _ in sh.xcells]


class ASplit(Expr):
    """Split whose X inputs are routed onto the subcells that are
    ALREADY covered by earlier sections (Nielsen's inherited x marks
    land on specific residues; window order in the notation is
    diagram-relative, so we align by actual coverage)."""

    def __init__(self, q, inputs):
        assert len(inputs) == q
        self.q, self.inputs = q, inputs

    def eval(self, ctx, a, M, path=""):
        cells = [subcell(a, M, self.q, j) for j in range(1, self.q + 1)]
        if ctx.shadow:
            for i, inp in enumerate(self.inputs):
                if inp is None or isinstance(inp, X):
                    continue
                ca, cm = cells[i]
                inp.eval(ctx, ca, cm, f"{path}/s{self.q}#{i + 1}")
            return
        regions = _materialize_regions(ctx)
        # feasible windows per input: every X cell the input would claim
        # at that window must already be covered
        feas = []
        for i, inp in enumerate(self.inputs):
            if inp is None:
                feas.append(set(range(self.q)))
                continue
            ok = set()
            for j in range(self.q):
                xc = _probe_xcells(inp, *cells[j])
                if all(_covered_in(regions, xa, xm) for xa, xm in xc):
                    ok.add(j)
            feas.append(ok)
        # backtracking perfect matching, most-constrained input first
        order = sorted(range(self.q), key=lambda i: len(feas[i]))
        assign = {}

        def bt(k):
            if k == self.q:
                return True
            i = order[k]
            for j in feas[i]:
                if j in assign.values():
                    continue
                assign[i] = j
                if bt(k + 1):
                    return True
                del assign[i]
            return False

        assert bt(0), \
            f"{path}: no x-consistent window assignment (mod {M * self.q})"
        for i, inp in enumerate(self.inputs):
            if inp is None:
                continue
            ca, cm = cells[assign[i]]
            inp.eval(ctx, ca, cm, f"{path}/a{self.q}#{assign[i] + 1}")


class Add(Expr):
    """Nielsen's '+': several partial sets evaluated on the same cell."""

    def __init__(self, exprs):
        self.exprs = exprs

    def eval(self, ctx, a, M, path=""):
        for i, e in enumerate(self.exprs, 1):
            e.eval(ctx, a, M, f"{path}/+{i}")


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
                    Arrow(3, [R1(0)(), R1(1)()])])
    in4 = Arrow(3, [One(), A2()])
    in5 = Arrow(5, [R1(1)(), RA(1)(), Arrow(3, [R1(0)(), R1(1)()]),
                    Arrow(3, [R1(2)(), RA(2)()])])
    e = Split(5, [One(), A2(), in3, in4, in5])
    e.eval(ctx, a, M, "4.3")
    # the extra 125^*1: bare 5-power classes covering, at every 25^ level
    # k >= 2, the window-4 cell (whose 3^(4,8^) only applies to 0 mod 4)
    # relaxed to its 5-part -- "we place it to cover the higher powers of
    # 5 in the set 25^*3^(4,8^)".  Family {5^a : a >= 3}; levels beyond
    # the truncation are an assumed region (paper's arrow portion).
    lev = subcell(a, M, 5, 5)
    for k in range(1, 4):
        w4 = subcell(*lev, 5, 4)
        if k >= 2:
            v = 5 ** qval(w4[1], 5)
            ctx.take(w4[0] % v, v, f"4.3/125up1/k{k}")
        lev = subcell(*lev, 5, 5)
    ctx.families.append((5 ** (qval(lev[1], 5) + 1), frozenset({5}),
                         "4.3/125up1/family"))
    # induction: at every 25^ level >= 4 the windows 1-3 are covered by
    # the relaxed 25^ inputs on every branch, window 4 by the 125^*1
    # family, and window 5 descends -- so the whole deep tower is covered
    v = 5 ** qval(lev[1], 5)
    ctx.assumed.append((lev[0] % v, v))


def A31_2():
    """3^(1, 2): 3-arrow with dyadically relaxed inputs 1 and 2."""
    return Arrow(3, [R1(0)(), R1(1)()])


def A34_8a():
    """3^(4, 8^)."""
    return Arrow(3, [R1(2)(), RA(2)()])


def Alist():
    """Nielsen's ordered set A = {2, 4, 3^(1,2), 1, 8^, 3^(4,8^)}."""
    return [R1(1)(), R1(2)(), A31_2(), R1(0)(), A2(), A34_8a()]


def sec44(ctx):
    """4.4: the prime 7 on hole m4 (branch '2 mod 4').
    7( , 8^, 3(2, 4, 3^(1,2)),
       5(5^(1,2,4,8^), 2, 3(1,2,x), 4, 5(x,x,x,3^(1,2),x)),
       3(8^, 3^(4,8^), ) + 5(3.4, 9^(1,2), x, 9^(4,8^),
                             5(x,x,x,5^(3.1,3.2,3.4,3.8^),x)),
       5(8^, , 3(8^, , x), , 5(x,x,x,3^(4,8^),x)), )
    then 49^(A) in the last window, 49^*5*A in the gray window-4 blank,
    and 49^*25*A on the class 20 mod 25 of the first window."""
    (a, M), = ctx.holes.pop("m4")
    in1 = Add([Hole("h44_left"),  # empty except 20 mod 25 (see 4.10)
               WinR(25, 20, Arrow(7, Alist()))])
    in3 = Split(3, [R1(1)(), R1(2)(), A31_2()])
    in4 = ASplit(5, [Arrow(5, [R1(0)(), R1(1)(), R1(2)(), A2()]),
                     R1(1)(),
                     ASplit(3, [R1(0)(), R1(1)(), X()]),
                     R1(2)(),
                     ASplit(5, [X(), X(), X(), A31_2(), X()])])
    in5 = Split(3, [A2(), A34_8a(),
                    ASplit(5, [R1(2)(),
                               A31_2(),  # 9^(1,2): 3-part 3 inherited
                               X(),
                               A34_8a(),  # 9^(4,8^)
                               ASplit(5, [X(), X(), X(),
                                          Arrow(5, [R1(0)(), R1(1)(),
                                                    R1(2)(), A2()]),
                                          X()])])])
    in6 = ASplit(5, [A2(), Hole("h44_g5"),
                     ASplit(3, [A2(), Hole("h44_g15"), X()]),
                     Arrow(7, Alist()),  # 49^*5*A fills '4 mod 5'
                     ASplit(5, [X(), X(), X(), A34_8a(), X()])])
    in7 = Arrow(7, Alist())  # 49^(A)
    e = Split(7, [in1, A2(), in3, in4, in5, in6, in7])
    e.eval(ctx, a, M, "4.4")


def report(ctx, label):
    hm = sum(measure(cells) for cells in ctx.holes.values())
    print(f"after {label}: {len(ctx.out)} classes, "
          f"{sum(len(c) for c in ctx.holes.values())} hole-cells "
          f"(measure {float(hm):.6f}) : "
          f"{sorted(ctx.holes.keys())}")


# holes that remain open after the sections transcribed so far (they are
# consumed by later, not-yet-transcribed subsections of the paper)
OPEN_HOLES = ("m6", "m12", "m16", "m18a", "m18b", "m24", "m32",
              "m36", "c27a", "c27b", "m18rem", "h43_9",
              "h44_left", "h44_g5", "h44_g15")


def main():
    ctx = Ctx(40)
    sec41(ctx)
    report(ctx, "4.1")
    sec42(ctx)
    report(ctx, "4.2")
    sec43(ctx)
    report(ctx, "4.3")
    sec44(ctx)
    report(ctx, "4.4")
    ok, lines = symbolic_verify(ctx, expect_holes=OPEN_HOLES,
                                regions=_materialize_regions(ctx, depth=6))
    for l in lines:
        print(l)
    print("SYMBOLIC VERIFY:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()
