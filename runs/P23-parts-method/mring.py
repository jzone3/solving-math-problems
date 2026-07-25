"""Exact coordinate ring used by Parts' base graphs.

The four coordinates ``(a, b, c, d)`` denote

    (a + b*sqrt(33) + i*(c*sqrt(3) + d*sqrt(11))) / den

with ``den = 4*3**h``.  The h=1 lattice is the one used by the
orbit-filling tables.  Arithmetic keeps an explicit integer denominator and
uses only integer/rational arithmetic.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, lcm, sqrt
from functools import reduce
from itertools import product

F = Fraction


@dataclass(frozen=True)
class R:
    v: tuple
    den: int = 12

    def __post_init__(self):
        if len(self.v) != 4 or self.den <= 0:
            raise ValueError("an R element needs four coefficients and positive denominator")
        vals = tuple(F(x) for x in self.v)
        den = self.den
        if any(x.denominator != 1 for x in vals):
            scale = 1
            for x in vals:
                scale = lcm(scale, x.denominator)
            vals = tuple(x * scale for x in vals)
            den *= scale
        ints = tuple(int(x) for x in vals)
        g = reduce(gcd, (abs(x) for x in ints), 0)
        g = gcd(g, den)
        if g > 1:
            ints = tuple(x // g for x in ints)
            den //= g
        object.__setattr__(self, "v", ints)
        object.__setattr__(self, "den", den)

    def __add__(self, other):
        other = as_r(other)
        d = lcm(self.den, other.den)
        return R(tuple(a * (d // self.den) + b * (d // other.den)
                       for a, b in zip(self.v, other.v)), d)

    def __neg__(self):
        return R(tuple(-x for x in self.v), self.den)

    def __sub__(self, other):
        return self + (-as_r(other))

    def scale(self, q):
        q = F(q)
        return R(tuple(q * x for x in self.v), self.den)

    def __mul__(self, other):
        other = as_r(other)
        a, b, c, d = self.v
        A, B, C, D = other.v
        # (a+b√33+i(c√3+d√11)) times (A+B√33+i(C√3+D√11)).
        out = (
            a * A + 33 * b * B - 3 * c * C - 11 * d * D,
            a * B + b * A - c * D - d * C,
            a * C + 11 * b * D + c * A + 11 * d * B,
            a * D + 3 * b * C + 3 * c * B + d * A,
        )
        return R(out, self.den * other.den)

    def conjugate(self):
        return R((self.v[0], self.v[1], -self.v[2], -self.v[3]), self.den)

    def as_h1(self):
        """Return the integer (a,b,c,d) tuple if this is in the h=1 lattice."""
        if 12 % self.den:
            return None
        q = tuple(x * (12 // self.den) for x in self.v)
        if any(not isinstance(x, int) for x in q):
            return None
        q = tuple(int(x) for x in q)
        return q if (q[0] - q[1] + q[2] + q[3]) % 4 == 0 else None

    def to_float(self):
        a, b, c, d = self.v
        return ((a + b * sqrt(33)) / self.den,
                (c * sqrt(3) + d * sqrt(11)) / self.den)


def as_r(x):
    return x if isinstance(x, R) else R(x)


ZERO = R((0, 0, 0, 0))
ONE = R((1, 0, 0, 0), 1)
ETA = R((0, 2, 2, 0))                 # (sqrt(33)+i sqrt(3))/6
ETA2 = ETA * ETA


def unit_difference(delta):
    """Exact h=1 unit-distance test for an integer difference tuple."""
    a, b, c, d = delta
    return (a * a + 33 * b * b + 3 * c * c + 11 * d * d == 144
            and a * b + c * d == 0)


def unit_distance(p, q):
    p, q = as_r(p), as_r(q)
    d = p - q
    if d.den != 12:
        return False
    return unit_difference(d.v)


def to_mfield(p, field):
    """Convert an R complex number to a compatible MField complex pair."""
    x, y = p if isinstance(p, tuple) else (p, ZERO)
    if not isinstance(x, R):
        raise TypeError("to_mfield expects (real, imaginary) R elements")
    outx = [F(0)] * field.N
    outy = [F(0)] * field.N
    outx[0], outx[5] = F(x.v[0], x.den), F(x.v[1], x.den)
    outy[1], outy[4] = F(y.v[2], y.den), F(y.v[3], y.den)
    return tuple(outx), tuple(outy)


def tuple_to_mfield(v, field, den=12):
    """Convert an integer coordinate tuple directly to an MField point."""
    a, b, c, d = v
    return to_mfield((R((a, b, 0, 0), den), R((0, 0, c, d), den)), field)


def from_mfield(p, field):
    """Convert a field point when it lies in this ring's subfield."""
    x, y = p
    if any(x[i] for i in range(field.N) if i not in (0, 5)):
        return None
    if any(y[i] for i in range(field.N) if i not in (1, 4)):
        return None
    den = 1
    for q in (x[0], x[5], y[1], y[4]):
        den = lcm(den, q.denominator)
    return (R((int(x[0] * den), int(x[5] * den), 0, 0), den),
            R((0, 0, int(y[1] * den), int(y[4] * den)), den))


def lattice_point(p, field):
    q = from_mfield(p, field)
    if q is None:
        return None
    vals = (q[0].v[0] * (12 // q[0].den) if 12 % q[0].den == 0 else None,
            q[0].v[1] * (12 // q[0].den) if 12 % q[0].den == 0 else None,
            q[1].v[2] * (12 // q[1].den) if 12 % q[1].den == 0 else None,
            q[1].v[3] * (12 // q[1].den) if 12 % q[1].den == 0 else None)
    if any(v is None for v in vals):
        return None
    vals = tuple(int(v) for v in vals)
    return vals if (vals[0] - vals[1] + vals[2] + vals[3]) % 4 == 0 else None


# tau matrices from definitions.tex.  A matrix is represented row-major.
TAUS = (
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    ((F(-1, 2), 0, F(-3, 2), 0), (0, F(-1, 2), 0, F(-1, 2)),
     (F(1, 2), 0, F(-1, 2), 0), (0, F(3, 2), 0, F(-1, 2))),
    ((F(-1, 2), 0, F(3, 2), 0), (0, F(-1, 2), 0, F(1, 2)),
     (F(-1, 2), 0, F(-1, 2), 0), (0, F(-3, 2), 0, F(-1, 2))),
    ((-1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, -1)),
    ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, -1)),
)


def tau(v, matrix):
    return tuple(sum(F(a) * b for a, b in zip(row, v)) for row in matrix)


def orbit(v):
    """The order-24 base orbit generated by the six optional transforms."""
    out = {tuple(v)}
    changed = True
    while changed:
        changed = False
        for x in tuple(out):
            for matrix in TAUS[1:]:
                y = tuple(int(z) if F(z).denominator == 1 else z
                          for z in tau(x, matrix))
                if y not in out:
                    out.add(y)
                    changed = True
    return frozenset(out)


def orbit_key(v):
    return (sum(x != 0 for x in v), sum(x < 0 for x in v), tuple(v))


def orbit_representative(v):
    return min(orbit(v), key=orbit_key)


def H():
    return frozenset({(0, 0, 0, 0), (12, 0, 0, 0), (-12, 0, 0, 0),
                      (6, 0, 6, 0), (6, 0, -6, 0),
                      (-6, 0, 6, 0), (-6, 0, -6, 0)})


def r_tuple(v):
    return R(v)


def eta_power(k):
    out = ONE
    base = ETA if k >= 0 else R((0, 2, -2, 0))
    for _ in range(abs(k)):
        out = out * base
    return out


def rotated_h(m):
    out = set()
    for k in range(-m, m + 1):
        e = eta_power(k)
        for v in H():
            z = e * R(v)
            q = z.as_h1()
            if q is None:
                raise ValueError("rotated H vertex left h=1 lattice")
            out.add(q)
    return frozenset(out)


def minkowski_sum(left, right):
    return frozenset(tuple(a + b for a, b in zip(x, y))
                     for x, y in product(left, right))


def base_graph(n, m):
    result = frozenset({(0, 0, 0, 0)})
    hm = rotated_h(m)
    for _ in range(n):
        result = minkowski_sum(result, hm)
    return result
