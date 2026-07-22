"""V4 symbolic scan: parameterized join families with sympy.

For each family the Laplacian spectrum is a short list of (value, multiplicity) pairs in
the parameters. Inside a constant-eigenvalue block the deficit
    f(t) = m + t(t+1)/2 - S_t
is a convex quadratic in t, so its minimum over the block is attained at the block
endpoints or at t* = v - 1/2 (v = block eigenvalue). We form all candidate minima
symbolically and try to prove each is >= 0 on the parameter domain; where sympy cannot
decide, we fall back to a large exact integer grid (a,b,c <= 300).

Families (n, m, blocks sorted descending):
  F1: K_a v (b*K_c)         (a>=1,b>=1,c>=1)
  F2: (b*K_c) v E_a         complete-multipartite-like with clique parts
  F3: K_a v (K_b u E_c)     split-ish with one big clique + independent part
  F4: cone^r over b*K_c     = K_r v bK_c is F1; instead do E_r v (K_b u K_c)
"""
import sys, time
from fractions import Fraction
import sympy as sp
sys.path.insert(0, '.')

a, b, c, r, t = sp.symbols('a b c r t', positive=True, integer=True)

def family_F1():
    n = a + b * c
    m = a * (a - 1) / 2 + b * c * (c - 1) / 2 + a * b * c
    blocks = [(a + b * c, a), (a + c, b * (c - 1)), (a, b - 1), (0, 1)]
    dom = [(a, 1, None), (b, 1, None), (c, 2, None)]
    return "K_a v bK_c", n, m, blocks, dom

def family_F2():
    # (b*K_c) v E_a : join spectrum: bK_c nonzero part shifted by a: c+a x b(c-1),
    # a x (b-1); E_a minus one zero shifted by bc: bc x (a-1); plus n, 0.
    n = a + b * c
    m = b * c * (c - 1) / 2 + a * b * c
    blocks = [(a + b * c, 1), (b * c, a - 1), (a + c, b * (c - 1)), (a, b - 1), (0, 1)]
    dom = [(a, 1, None), (b, 1, None), (c, 2, None)]
    return "bK_c v E_a", n, m, blocks, dom

def family_F3():
    # K_a v (K_b u E_c): K_b u E_c spectrum: b x(b-1), 0 x(c+1)... minus one zero,
    # shifted by a: a+b x(b-1), a x c ; K_a nonzero shifted by b+c: a+b+c x(a-1);
    # plus n=a+b+c, 0.
    n = a + b + c
    m = a * (a - 1) / 2 + b * (b - 1) / 2 + a * (b + c)
    blocks = [(a + b + c, a), (a + b, b - 1), (a, c), (0, 1)]
    dom = [(a, 1, None), (b, 2, None), (c, 1, None)]
    return "K_a v (K_b u E_c)", n, m, blocks, dom

def family_F4():
    # E_r v (K_b u K_c), b >= c: K_b u K_c minus one zero shifted r: b+r x(b-1),
    # c+r x(c-1), r x1; E_r minus one zero shifted (b+c): b+c x(r-1); plus n, 0
    n = r + b + c
    m = b * (b - 1) / 2 + c * (c - 1) / 2 + r * (b + c)
    blocks = [(r + b + c, 1), (b + r, b - 1), (b + c, r - 1), (c + r, c - 1), (r, 1), (0, 1)]
    # NOTE: sort order b+r vs b+c vs c+r depends on parameters; deficit-minimum over a
    # DESCENDING sort is what the conjecture needs. We handle order by checking S_t for
    # the true sorted order only in the grid; symbolically we restrict to r >= c
    # (=> b+r >= b+c >= c+r when b >= r?) -- messy; grid is authoritative for F4.
    dom = [(r, 1, None), (b, 2, None), (c, 2, None)]
    return "E_r v (K_b u K_c)", n, m, blocks, dom

def block_candidates(name, n, m, blocks, dom):
    """Return list of (label, expr, extra_conditions) deficit candidates."""
    out = []
    T0 = sp.Integer(0)
    S0 = sp.Integer(0)
    for i, (v, mult) in enumerate(blocks):
        # t in (T0, T0+mult]; f(t) = m + t(t+1)/2 - S0 - v*(t-T0)
        f = m + t * (t + 1) / 2 - S0 - v * (t - T0)
        # integer params => v integer => interior minimizer candidates are t = v-1, v
        for lbl, tt in (("start", T0 + 1), ("end", T0 + mult),
                        ("int(v-1)", v - 1), ("int(v)", v)):
            out.append((f"{name} blk{i} {lbl}", sp.expand(f.subs(t, tt)), (v, mult, T0)))
        S0 = S0 + v * mult
        T0 = T0 + mult
    return out

def try_prove_nonneg(expr, dom):
    """Attempt to prove expr >= 0 for all integer params in domain via polynomial
    substitution x = xmin + x' (x' >= 0) and checking all coefficients >= 0."""
    e = sp.expand(sp.together(expr))
    subs = {}
    prim = {}
    for (sym, lo, hi) in dom:
        s2 = sp.Symbol(sym.name + "p", nonnegative=True)
        subs[sym] = lo + s2
        prim[sym] = s2
    e2 = sp.expand(e.subs(subs))
    e2 = sp.nsimplify(e2)
    poly = sp.Poly(e2, *[prim[s] for s, _, _ in dom]) if not e2.free_symbols - set(prim.values()) else None
    if poly is None:
        return None
    return all(co >= 0 for co in poly.coeffs())

def grid_check(name, n, m, blocks, dom, LIM=300):
    """Exact integer grid check with true sorting of blocks."""
    from itertools import product
    syms = [s for s, _, _ in dom]
    lows = [lo for _, lo, _ in dom]
    worst = None
    fn = sp.lambdify(syms, [n, m] + [x for blk in blocks for x in blk], "math")
    for vals in product(*[range(lo, LIM + 1, max(1, (LIM - lo) // 60)) for lo in lows]):
        out = fn(*vals)
        N, M = int(out[0]), Fraction(out[1]).limit_denominator(1)
        pairs = []
        it = iter(out[2:])
        for v, mult in zip(it, it):
            v, mult = Fraction(v).limit_denominator(1), int(mult)
            if mult > 0:
                pairs.append((v, mult))
        pairs.sort(key=lambda x: -x[0])
        # block-wise min
        S0 = Fraction(0); T0 = 0; best = None
        import math
        for v, mult in pairs:
            cand = {T0 + 1, T0 + mult}
            ts = v - Fraction(1, 2)
            for x in (math.floor(ts), math.ceil(ts)):
                if T0 + 1 <= x <= T0 + mult:
                    cand.add(x)
            for tt in cand:
                d = M + Fraction(tt * (tt + 1), 2) - (S0 + v * (tt - T0))
                if best is None or d < best[0]:
                    best = (d, tt)
            S0 += v * mult; T0 += mult
        assert T0 == N, (name, vals, T0, N)
        if best[0] < 0:
            print(f"!!! COUNTEREXAMPLE {name} params={vals} t={best[1]} d={best[0]}")
        if worst is None or best[0] < worst[0]:
            worst = (best[0], vals, best[1])
    return worst

for fam in (family_F1, family_F2, family_F3, family_F4):
    name, n, m, blocks, dom = fam()
    print(f"== {name}")
    w = grid_check(name, n, m, blocks, dom)
    print(f"   grid (params to 300, ~60 pts/axis, exact): min deficit {w[0]} at {w[1]} t={w[2]}")
    if fam in (family_F1, family_F3):  # listed block order = true descending sort
        all_proved = True
        for lbl, expr, (v, mult, T0) in block_candidates(name, n, m, blocks, dom):
            res = try_prove_nonneg(expr, dom)
            if res is not True and "int(" in lbl:
                # interior candidate t in {v-1, v}: only relevant if T0+1 <= t <= T0+mult.
                # Prove vacuity: show t < T0+1 always, or t > T0+mult always
                # (strict positivity via coeff test on expr - 1, integer-valued exprs).
                tt = v - 1 if "v-1" in lbl else v
                below = try_prove_nonneg(sp.expand((T0 + 1) - tt - 1), dom)  # T0+1-t >= 1
                above = try_prove_nonneg(sp.expand(tt - (T0 + mult) - 1), dom)
                if below or above:
                    res = True
                    lbl += " [out-of-block, vacuous]"
            all_proved = all_proved and (res is True)
            tag = {True: "PROVED>=0", False: "coeff-test inconclusive", None: "skip"}[res]
            print(f"   {lbl}: {tag}   f = {sp.simplify(expr)}")
        print(f"   ==> family {'FULLY PROVED >= 0 symbolically' if all_proved else 'NOT fully proved (grid only)'}")
    sys.stdout.flush()
