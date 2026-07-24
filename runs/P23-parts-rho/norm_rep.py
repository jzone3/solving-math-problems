"""Which t admit lattice points at radius sqrt(t) AT ALL (not just in the
radius-2 pool)?  A lattice point u has |u|^2 = t (rational!) iff
    N(u) = a^2 + 33 b^2 + 3 c^2 + 11 d^2 = 144 t   and   M(u) = ab + cd = 0,
with a - b + c + d = 0 (mod 4).  Reference cross edges (u, omega_t u) exist
iff such points exist.  Exhaustive search over |a|<=12*sqrt(t), etc.
"""
import math


def reps(t, only_first=False):
    T = 144 * t
    out = []
    amax = int(math.isqrt(T))
    bmax = int(math.isqrt(T // 33))
    cmax = int(math.isqrt(T // 3))
    dmax = int(math.isqrt(T // 11))
    for b in range(-bmax, bmax + 1):
        rb = T - 33 * b * b
        for d in range(-dmax, dmax + 1):
            rd = rb - 11 * d * d
            if rd < 0:
                continue
            for c in range(-cmax, cmax + 1):
                rc = rd - 3 * c * c
                if rc < 0:
                    continue
                a2 = rc
                a = math.isqrt(a2)
                if a * a != a2:
                    continue
                for aa in ({a, -a} if a else {0}):
                    if aa * b + c * d == 0 and (aa - b + c + d) % 4 == 0:
                        out.append((aa, b, c, d))
                        if only_first:
                            return out
    return out


if __name__ == "__main__":
    for t in range(1, 33):
        r = reps(t)
        print(f"t={t:2d}: {len(r):5d} lattice points with |u|^2 = t"
              f"   e.g. {r[0] if r else '-'}")
