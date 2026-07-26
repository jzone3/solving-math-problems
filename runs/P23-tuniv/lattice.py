"""Exact Parts lattice and Minkowski pool construction."""
import math
import os

P, Q, M = 3, 11, 12


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def radius2_144(v):
    a, b, c, d = v
    return (a * a + 33 * b * b + 3 * c * c + 11 * d * d,
            2 * (a * b + c * d))


def radius2_float(v):
    s, t = radius2_144(v)
    return min(s + t * math.sqrt(33), s - t * math.sqrt(33)) / 144.0


def units():
    out = []
    for a in range(-12, 13):
        for b in range(-2, 3):
            for c in range(-6, 7):
                for d in range(-4, 5):
                    if radius2_144((a, b, c, d)) == (144, 0):
                        out.append((a, b, c, d))
    return sorted(out)


UNIT = units()


H = [(0, 0, 0, 0), (12, 0, 0, 0), (-12, 0, 0, 0),
     (6, 0, 6, 0), (6, 0, -6, 0), (-6, 0, 6, 0), (-6, 0, -6, 0)]


def _apply_frac(mat, den, p):
    out = [sum(a * b for a, b in zip(row, p)) for row in mat]
    if any(x % den for x in out):
        raise ValueError("non-integral lattice transform")
    return tuple(x // den for x in out)


ETA = ([(0, 33, -3, 0), (1, 0, 0, -1),
        (1, 0, 0, 11), (0, 3, 3, 0)], 6)
ETAI = ([(0, 33, 3, 0), (1, 0, 0, 1),
         (-1, 0, 0, 11), (0, -3, 3, 0)], 6)
TAU1 = ([(-1, 0, -3, 0), (0, -1, 0, -1),
         (1, 0, -1, 0), (0, 3, 0, -1)], 2)
TAU2 = ([(-1, 0, 3, 0), (0, -1, 0, 1),
         (-1, 0, -1, 0), (0, -3, 0, -1)], 2)


def mul_eta(p, k=1):
    mat, den = ETA if k >= 0 else ETAI
    for _ in range(abs(k)):
        p = _apply_frac(mat, den, p)
    return p


def Hm(m):
    return sorted({mul_eta(p, k) for k in range(-m, m + 1) for p in H})


def tau1(p):
    return _apply_frac(*TAU1, p)


def tau2(p):
    return _apply_frac(*TAU2, p)


def orbit24(p):
    out = set()
    for q in (p, tau1(p), tau2(p)):
        for r in (q, (-q[0], -q[1], q[2], q[3])):
            for w in (r, (r[0], r[1], -r[2], -r[3])):
                out.add(w)
                out.add((w[0], -w[1], w[2], -w[3]))
    return out


_CACHE = {}


def build_base(layers=3, radius=2.0):
    """Return sums of at most ``layers`` unit vectors in the physical disk."""
    key = (layers, round(radius, 10))
    if key in _CACHE:
        return _CACHE[key]
    cur = {(0, 0, 0, 0)}
    for k in range(layers):
        nxt = set()
        for x in cur:
            for u in UNIT:
                y = add(x, u)
                if radius2_float(y) <= (radius + layers - k - 1 + 1e-9) ** 2:
                    nxt.add(y)
        cur = nxt
    out = sorted(p for p in cur if (s := radius2_144(p))[0] +
                 s[1] * math.sqrt(33) <= 144.0 * (radius + 1e-9) ** 2)
    _CACHE[key] = out
    return out


def to_complex(v):
    a, b, c, d = v
    return complex(a + b * math.sqrt(33), c * math.sqrt(3) + d * math.sqrt(11)) / 12


def is_unit(v):
    return radius2_144(v) == (144, 0)


def omega_t_complex(t):
    return complex(2 * t - 1, math.sqrt(4 * t - 1)) / (2 * t)


def squarefree_split(r):
    for q in range(1, r + 1):
        if q * q == r:
            return q, 1
    return 1, r
