# Provenance: copied from origin/runs/P23-parts-gadgets:runs/P23-parts-gadgets/mfield.py
"""Exact arithmetic in an arbitrary real multi-quadratic field Q(sqrt p1, ..., sqrt pk).

An element is a tuple of Fractions indexed by subset-masks over the chosen
squarefree generators PRIMES. value = sum_mask coef[mask] * sqrt(prod primes in mask).

This generalizes runs/P23-v1/field.py (which hard-codes Q(sqrt3,sqrt5,sqrt11)) to
any generator set, so we can explore *different field extensions* -- e.g.
Q(sqrt3,sqrt5,sqrt11,sqrt2) or Q(sqrt3,sqrt5,sqrt11,sqrt13) -- and generate apex
vertices whose completing radical falls outside the original Parts field.

No floating point is used in any decision; to_float is only a prefilter.
"""
from fractions import Fraction as F
import sympy as sp
from sympy.parsing.mathematica import parse_mathematica as _pm
from sympy.simplify.sqrtdenest import sqrtdenest


class MField:
    def __init__(self, primes):
        # primes: sorted tuple of distinct squarefree integers > 1 (usually primes)
        self.primes = tuple(primes)
        self.k = len(self.primes)
        self.N = 1 << self.k
        self.ZERO = tuple(F(0) for _ in range(self.N))
        one = [F(0)] * self.N
        one[0] = F(1)
        self.ONE = tuple(one)
        # radicand value of a mask
        self._radval = [self._rv(m) for m in range(self.N)]
        # multiplication table: (m1,m2) -> (int factor, result mask)
        self.MUL = {}
        for m1 in range(self.N):
            for m2 in range(self.N):
                common = m1 & m2
                self.MUL[(m1, m2)] = (self._radval[common], m1 ^ m2)
        self._rads = {m: sp.sqrt(self._radval[m]) for m in range(1, self.N)}

    def _rv(self, m):
        v = 1
        for i, p in enumerate(self.primes):
            if m >> i & 1:
                v *= p
        return v

    def add(self, x, y):
        return tuple(x[i] + y[i] for i in range(self.N))

    def sub(self, x, y):
        return tuple(x[i] - y[i] for i in range(self.N))

    def mul(self, x, y):
        out = [F(0)] * self.N
        MUL = self.MUL
        for m1 in range(self.N):
            c1 = x[m1]
            if not c1:
                continue
            for m2 in range(self.N):
                c2 = y[m2]
                if not c2:
                    continue
                f, b = MUL[(m1, m2)]
                out[b] += c1 * c2 * f
        return tuple(out)

    def scal(self, r, x):
        r = F(r)
        return tuple(r * c for c in x)

    def inv(self, x):
        N = self.N
        M = [[F(0)] * N for _ in range(N)]
        for j in range(N):
            for m1 in range(N):
                if not x[m1]:
                    continue
                f, b = self.MUL[(m1, j)]
                M[b][j] += x[m1] * f
        A = [row[:] + [F(1) if i == 0 else F(0)] for i, row in enumerate(M)]
        for col in range(N):
            piv = next(r for r in range(col, N) if A[r][col] != 0)
            A[col], A[piv] = A[piv], A[col]
            pv = A[col][col]
            A[col] = [a / pv for a in A[col]]
            for r in range(N):
                if r != col and A[r][col]:
                    fac = A[r][col]
                    A[r] = [a - fac * b for a, b in zip(A[r], A[col])]
        return tuple(A[i][N] for i in range(N))

    def to_sympy(self, x):
        return sum(sp.Rational(c.numerator, c.denominator) * (self._rads[b] if b else 1)
                   for b, c in enumerate(x) if c)

    def to_float(self, x):
        import math
        return sum(float(c) * math.sqrt(self._radval[b]) for b, c in enumerate(x) if c)

    def parse_sympy(self, e):
        """Convert an expanded sympy radical expression to a field element, or None
        if it uses a radical outside this field."""
        e = sp.expand(e)
        coeffs = [sp.Integer(0)] * self.N
        terms = e.as_ordered_terms() if e.is_Add else [e]
        for t in terms:
            c, rad_mask = sp.Integer(1), 0
            for f in t.as_ordered_factors():
                if f.is_Rational:
                    c *= f
                elif f.is_Pow and f.exp == sp.Rational(1, 2) and f.base.is_Integer:
                    base = int(f.base)
                    mask = 0
                    left = base
                    for i, p in enumerate(self.primes):
                        while left % p == 0:
                            left //= p
                            mask ^= 1 << i
                    if left != 1:
                        return None  # radical outside field
                    c *= self._radval[rad_mask & mask]
                    rad_mask ^= mask
                else:
                    return None
            coeffs[rad_mask] += c
        try:
            return tuple(F(int(sp.Rational(c).p), int(sp.Rational(c).q)) for c in coeffs)
        except (TypeError, ValueError):
            return None

    def norm2(self, p, q):
        dx = self.sub(p[0], q[0])
        dy = self.sub(p[1], q[1])
        return self.add(self.mul(dx, dx), self.mul(dy, dy))

    def field_sqrt(self, x):
        """Return y in field with y*y == x (y >= 0), else None."""
        e = self.to_sympy(x)
        if e == 0:
            return self.ZERO
        s = sqrtdenest(sp.sqrt(sp.nsimplify(e)))
        y = self.parse_sympy(sp.expand(s))
        if y is None:
            return None
        return y if self.mul(y, y) == x else None


# ---- parsing Mathematica .vtx coordinates into a *given* field ----
def parse_expr(field, expr_str):
    e = sp.sympify(_pm(expr_str))
    e = sp.expand(sqrtdenest(sp.radsimp(e)))
    out = field.parse_sympy(e)
    if out is None:
        raise ValueError(f"expr outside field {field.primes}: {expr_str}")
    diff = sp.expand(field.to_sympy(out) - e)
    assert diff == 0 or sp.simplify(diff) == 0, expr_str
    return out


def load_vtx(field, path):
    pts = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        assert line.startswith('{') and line.endswith('}'), line
        inner = line[1:-1]
        depth = 0
        for i, ch in enumerate(inner):
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            elif ch == ',' and depth == 0:
                xs, ys = inner[:i], inner[i + 1:]
                break
        pts.append((parse_expr(field, xs), parse_expr(field, ys)))
    return pts
