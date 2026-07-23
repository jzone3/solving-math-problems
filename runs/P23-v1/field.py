"""Exact arithmetic in Q(sqrt3, sqrt5, sqrt11).
Element = tuple of 8 Fractions indexed by bitmask b over primes (3,5,11):
value = sum_b coef[b] * sqrt(prod of primes in b).
Basis order: 1, r3, r5, r15, r11, r33, r55, r165 (bit0=3, bit1=5, bit2=11).
"""
from fractions import Fraction as F

PRIMES = (3, 5, 11)
N = 8
ZERO = tuple(F(0) for _ in range(N))
ONE = (F(1),) + tuple(F(0) for _ in range(N - 1))

def _radval(b):
    v = 1
    for i, p in enumerate(PRIMES):
        if b >> i & 1:
            v *= p
    return v

# precompute multiplication table: (b1,b2) -> (integer factor, resulting mask)
MUL = {}
for b1 in range(N):
    for b2 in range(N):
        common = b1 & b2
        MUL[(b1, b2)] = (_radval(common), b1 ^ b2)

def add(x, y):
    return tuple(x[i] + y[i] for i in range(N))

def sub(x, y):
    return tuple(x[i] - y[i] for i in range(N))

def mul(x, y):
    out = [F(0)] * N
    for b1 in range(N):
        c1 = x[b1]
        if not c1:
            continue
        for b2 in range(N):
            c2 = y[b2]
            if not c2:
                continue
            f, b = MUL[(b1, b2)]
            out[b] += c1 * c2 * f
    return tuple(out)

def inv(x):
    """Multiplicative inverse via 8x8 exact linear solve."""
    # matrix M with M[i][j] = coefficient of basis i in x * e_j
    M = [[F(0)] * N for _ in range(N)]
    for j in range(N):
        for b1 in range(N):
            if not x[b1]:
                continue
            f, b = MUL[(b1, j)]
            M[b][j] += x[b1] * f
    # solve M y = e0 by Gaussian elimination
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

def scal(r, x):
    return tuple(r * c for c in x)

def field_sqrt(x):
    """Return y with y*y == x and y in the field, else None."""
    e = to_sympy(x)
    if e == 0:
        return ZERO
    from sympy.simplify.sqrtdenest import sqrtdenest
    s = sqrtdenest(sp.sqrt(sp.nsimplify(e)))
    try:
        y = parse_sympy(sp.expand(s))
    except (ValueError, AssertionError):
        return None
    return y if mul(y, y) == x else None

def parse_sympy(e):
    """Convert an expanded sympy radical expression to a field element."""
    coeffs = [sp.Integer(0)] * N
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
                for i, p in enumerate(PRIMES):
                    if left % p == 0:
                        left //= p
                        mask |= 1 << i
                if left != 1:
                    raise ValueError(f"radical sqrt({base}) outside field")
                c *= _radval(rad_mask & mask)
                rad_mask ^= mask
            else:
                raise ValueError(f"unexpected factor {f}")
        coeffs[rad_mask] += c
    def toF(v):
        v = sp.Rational(v)
        return F(int(v.p), int(v.q))
    return tuple(toF(c) for c in coeffs)

def norm2(p, q):
    dx = sub(p[0], q[0])
    dy = sub(p[1], q[1])
    return add(mul(dx, dx), mul(dy, dy))

import sympy as sp
from sympy.parsing.mathematica import parse_mathematica as _pm

_rads = {b: sp.sqrt(_radval(b)) for b in range(1, N)}

def parse_expr(expr_str):
    """Parse a Mathematica scalar expression into an 8-tuple field element."""
    from sympy.simplify.sqrtdenest import sqrtdenest
    e = sp.sympify(_pm(expr_str))
    e = sp.expand(sqrtdenest(sp.radsimp(e)))
    if not e.is_Add and not e.is_Mul and not e.is_Rational and not e.is_Pow:
        e = sp.expand(e)
    coeffs = [sp.Integer(0)] * N
    terms = e.as_ordered_terms() if e.is_Add else [e]
    for t in terms:
        c, rad_mask = sp.Integer(1), 0
        for f in t.as_ordered_factors():
            if f.is_Rational:
                c *= f
            elif f.is_Pow and f.exp == sp.Rational(1, 2):
                base = int(f.base)
                # factor base over PRIMES; leftover square factor multiplies c
                mask = 0
                left = base
                for i, p in enumerate(PRIMES):
                    if left % p == 0:
                        left //= p
                        mask |= 1 << i
                assert left == 1, f"unexpected radical sqrt({base}) in {expr_str}"
                c *= _radval(rad_mask & mask)
                rad_mask ^= mask
            else:
                raise ValueError(f"unexpected factor {f} in {expr_str}")
        coeffs[rad_mask] += c
    def toF(x):
        x = sp.Rational(x)
        return F(int(x.p), int(x.q))
    out = tuple(toF(c) for c in coeffs)
    # cross-check reconstruction against original expression (exact, via sympy)
    diff = sp.expand(to_sympy(out) - e)
    assert diff == 0 or sp.simplify(diff) == 0, expr_str
    return out

def to_sympy(x):
    return sum(sp.Rational(c.numerator, c.denominator) * (_rads[b] if b else 1)
               for b, c in enumerate(x) if c)

def to_float(x):
    import math
    return sum(float(c) * math.sqrt(_radval(b)) for b, c in enumerate(x) if c)

def load_vtx(path):
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
                xs, ys = inner[:i], inner[i+1:]
                break
        pts.append((parse_expr(xs), parse_expr(ys)))
    return pts

def edges_of(pts):
    """Exact unit-distance edges, with float prefilter for speed."""
    n = len(pts)
    fl = [(to_float(p[0]), to_float(p[1])) for p in pts]
    E = []
    for i in range(n):
        xi, yi = fl[i]
        for j in range(i+1, n):
            dx = xi - fl[j][0]
            dy = yi - fl[j][1]
            d2 = dx*dx + dy*dy
            if abs(d2 - 1.0) < 1e-6:
                if norm2(pts[i], pts[j]) == ONE:
                    E.append((i, j))
    return E
