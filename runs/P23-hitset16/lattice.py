"""Exact integer arithmetic for Parts' base lattice (arXiv:2010.12665).

A lattice point is an integer 4-tuple (a,b,c,d) representing the complex number

    z = (a + b*sqrt(33) + i*(c*sqrt(3) + d*sqrt(11))) / 12

(denominator 4*3^h with h=1).  Valid base-graph points satisfy
a - b + c + d = 0 (mod 4).

Squared modulus: |z|^2 = (N + M*sqrt(33)) / 144 with
    N = a^2 + 33 b^2 + 3 c^2 + 11 d^2,   M = 2 (a b + c d).

Two lattice points are at unit distance iff their difference (a,b,c,d)
satisfies  N = 144 and M = 0  -- pure integer arithmetic.

Rotations:
    eta      = sqrt(omega_3) = (sqrt(33) + i sqrt(3)) / 6   (apex angle of the
               sqrt3,sqrt3,1 triangle, half-angle)
    omega_t  = (2t-1 + i*sqrt(4t-1)) / (2t)                 (Polymath16 wiki)
Parts' rho = omega_4 = (7 + i sqrt(15))/8.

omega_t maps a pair of lattice points at radius sqrt(t) to a unit-distance
pair: |1 - omega_t|^2 = 1/t.

Multiplication by eta and (for 'native' t) by omega_t keeps points inside the
lattice; both are implemented as exact integer maps with divisibility checks.

Cross-edge condition (fully integer).  For u=(a1,b1,c1,d1), v=(a2,b2,c2,d2):
    w = u * conj(v):  w_r = (P + Q sqrt33)/144, w_i = (R sqrt3 + S sqrt11)/144
        P = a1 a2 + 33 b1 b2 + 3 c1 c2 + 11 d1 d2
        Q = a1 b2 + a2 b1 + c1 d2 + c2 d1
        R = c1 a2 + 11 d1 b2 - a1 c2 - 11 b1 d2
        S = d1 a2 + 3 c1 b2 - a1 d2 - 3 b1 c2
    |u - omega_t v|^2 = |u|^2 + |v|^2 - ((2t-1) w_r + sqrt(4t-1) w_i)/t
Writing 4t-1 = e*s^2 (e squarefree), sqrt(4t-1)*w_i =
    s*(R sqrt(3e) + S sqrt(11e))/144.
  e == 3  (t = 1, 7, 19, 37, ...):  sqrt(3e)=3, sqrt(11e)=sqrt33
  e == 11 (t = 3, 25, ...):         sqrt(3e)=sqrt33, sqrt(11e)=11
  otherwise 1, sqrt33, sqrt(3e), sqrt(11e) are linearly independent over Q.
Unit cross-edge  |u - omega_t v|^2 = 1  iff (integer conditions):
  generic e: R == 0 and S == 0 and
             t*(N1+N2) - (2t-1)*P == 144*t  and  t*(M1+M2) == (2t-1)*Q
  e == 3:    t*(N1+N2) - (2t-1)*P - 3*s*R == 144*t
             and t*(M1+M2) - (2t-1)*Q - s*S == 0
  e == 11:   t*(N1+N2) - (2t-1)*P - 11*s*S == 144*t
             and t*(M1+M2) - (2t-1)*Q - s*R == 0
"""

from fractions import Fraction as F
import math

SQ33 = math.sqrt(33.0)
SQ3 = math.sqrt(3.0)
SQ11 = math.sqrt(11.0)


def norm144(p):
    """144*|z|^2 as (N, M) meaning N + M*sqrt33."""
    a, b, c, d = p
    return (a * a + 33 * b * b + 3 * c * c + 11 * d * d, 2 * (a * b + c * d))


def is_unit(p, q):
    a, b, c, d = (p[i] - q[i] for i in range(4))
    return a * a + 33 * b * b + 3 * c * c + 11 * d * d == 144 and a * b + c * d == 0


def to_complex(p):
    a, b, c, d = p
    return complex((a + b * SQ33) / 12.0, (c * SQ3 + d * SQ11) / 12.0)


def conj33(p):
    """sqrt33-conjugate (Parts' tau5)."""
    a, b, c, d = p
    return (a, -b, c, -d)


def add(p, q):
    return tuple(p[i] + q[i] for i in range(4))


def sub(p, q):
    return tuple(p[i] - q[i] for i in range(4))


def neg(p):
    return tuple(-x for x in p)


def _apply_frac(mat, den, p):
    """Apply integer matrix mat / den to p; raise if result non-integral."""
    out = []
    for row in mat:
        s = sum(m * x for m, x in zip(row, p))
        if s % den:
            raise ValueError(f"non-integral image of {p}")
        out.append(s // den)
    return tuple(out)


# z * eta, eta = (sqrt33 + i sqrt3)/6:
#   a' = 33b - 3c, b' = a - d, c' = a + 11d, d' = 3b + 3c   (all / 6)
ETA = ([(0, 33, -3, 0), (1, 0, 0, -1), (1, 0, 0, 11), (0, 3, 3, 0)], 6)
# z * eta^-1, eta^-1 = (sqrt33 - i sqrt3)/6
ETAI = ([(0, 33, 3, 0), (1, 0, 0, 1), (-1, 0, 0, 11), (0, -3, 3, 0)], 6)


def mul_eta(p, k=1):
    mat, den = ETA if k >= 0 else ETAI
    for _ in range(abs(k)):
        p = _apply_frac(mat, den, p)
    return p


def squarefree_split(n):
    """n = e * s^2 with e squarefree; return (e, s)."""
    s = 1
    e = n
    f = 2
    while f * f <= e:
        while e % (f * f) == 0:
            e //= f * f
            s *= f
        f += 1
    return e, s


def omega_native_matrix(t):
    """For native t (4t-1 in {3 s^2, 11 s^2}) return (mat, den) of z*omega_t.

    omega_t = (2t-1 + i sqrt(4t-1))/(2t).
    e=3:  i*sqrt(4t-1) = i*s*sqrt3:   z*(x + i s sqrt3)  with x=2t-1
      (a+b s33 + i(c s3 + d s11)) * i s sqrt3 = i s (a s3 + 3 b s11) - s(3c + d s33)
      a' = x a - 3 s c ; b' = x b - s d ; c' = x c + s a ; d' = x d + 3 s b  (/2t)
    e=11: i*sqrt(4t-1) = i*s*sqrt11:
      (a+b s33 + i(c s3+d s11)) * i s sqrt11 = i s (a s11 + 11 b s3) - s(3c ... )
      compute: i s sqrt11 * (c s3 + d s11) * i = -s(c s33 + 11 d)
      a' = x a - 11 s d ; b' = x b - s c ; c' = x c + 11 s b ; d' = x d + s a  (/2t)
    """
    e, s = squarefree_split(4 * t - 1)
    x = 2 * t - 1
    if e == 3:
        return ([(x, 0, -3 * s, 0), (0, x, 0, -s), (s, 0, x, 0), (0, 3 * s, 0, x)], 2 * t)
    if e == 11:
        return ([(x, 0, 0, -11 * s), (0, x, -s, 0), (0, 11 * s, x, 0), (s, 0, 0, x)], 2 * t)
    raise ValueError(f"t={t} is not native (4t-1 = {e}*{s}^2)")


def cross_prod_ints(u, v):
    """(P, Q, R, S) for w = u * conj(v) (see module docstring)."""
    a1, b1, c1, d1 = u
    a2, b2, c2, d2 = v
    P = a1 * a2 + 33 * b1 * b2 + 3 * c1 * c2 + 11 * d1 * d2
    Q = a1 * b2 + a2 * b1 + c1 * d2 + c2 * d1
    R = c1 * a2 + 11 * d1 * b2 - a1 * c2 - 11 * b1 * d2
    S = d1 * a2 + 3 * c1 * b2 - a1 * d2 - 3 * b1 * c2
    return P, Q, R, S


def cross_is_unit(u, v, t, es=None):
    """Exact test:  |u - omega_t * v| == 1."""
    e, s = es if es is not None else squarefree_split(4 * t - 1)
    N1, M1 = norm144(u)
    N2, M2 = norm144(v)
    P, Q, R, S = cross_prod_ints(u, v)
    x = 2 * t - 1
    if e == 3:
        return (t * (N1 + N2) - x * P - 3 * s * R == 144 * t
                and t * (M1 + M2) - x * Q - s * S == 0)
    if e == 11:
        return (t * (N1 + N2) - x * P - 11 * s * S == 144 * t
                and t * (M1 + M2) - x * Q - s * R == 0)
    return (R == 0 and S == 0
            and t * (N1 + N2) - x * P == 144 * t
            and t * (M1 + M2) == x * Q)


def omega_t_complex(t):
    return complex((2 * t - 1) / (2 * t), math.sqrt(4 * t - 1) / (2 * t))


# Parts' symmetry transforms tau_0..tau_5 (definitions.tex); tau1/tau2 are
# rotations by 2pi/3 (integer matrices /2), tau3/tau4 reflections, tau5 conj.
TAU1 = ([(-1, 0, -3, 0), (0, -1, 0, -1), (1, 0, -1, 0), (0, 3, 0, -1)], 2)
TAU2 = ([(-1, 0, 3, 0), (0, -1, 0, 1), (-1, 0, -1, 0), (0, -3, 0, -1)], 2)


def tau1(p):
    return _apply_frac(*TAU1, p)


def tau2(p):
    return _apply_frac(*TAU2, p)


def tau3(p):
    a, b, c, d = p
    return (-a, -b, c, d)


def tau4(p):
    a, b, c, d = p
    return (a, b, -c, -d)


def orbit24(p):
    """Orbit of p under the order-24 base symmetry group."""
    out = set()
    for q in (p, tau1(p), tau2(p)):
        for r in (q, tau3(q)):
            for w in (r, tau4(r)):
                out.add(w)
                out.add(conj33(w))
    return out


# 7-vertex hexagonal wheel H (denominator 12)
H = [(0, 0, 0, 0), (12, 0, 0, 0), (-12, 0, 0, 0),
     (6, 0, 6, 0), (6, 0, -6, 0), (-6, 0, 6, 0), (-6, 0, -6, 0)]


def Hm(m):
    """H^m = union_{alpha=-m..m} eta^alpha H."""
    out = set()
    for alpha in range(-m, m + 1):
        for p in H:
            out.add(mul_eta(p, alpha))
    return sorted(out)


def minkowski(A, B):
    return sorted({add(p, q) for p in A for q in B})


def radius2_144(p):
    """(144*|z|^2 as float, 144*|conj z|^2 as float) for filtering."""
    N, M = norm144(p)
    return (N + M * SQ33, N - M * SQ33)


def check_lattice(p):
    a, b, c, d = p
    return (a - b + c + d) % 4 == 0
