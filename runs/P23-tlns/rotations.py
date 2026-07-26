"""Exact rotation families over the smallest field containing each omega_t."""
from fractions import Fraction as Fr
import math

import mfield


def squarefree_split(n):
    e, s = n, 1
    f = 2
    while f * f <= e:
        while e % (f * f) == 0:
            e //= f * f
            s *= f
        f += 1
    return e, s


def omega_for_t(t):
    """Return (field, (real, imaginary)) for omega_t exactly."""
    t = Fr(t)
    e, s = squarefree_split(int(4 * t - 1))
    embedded = 0
    for p in (3, 11):
        if e % p == 0:
            e //= p
            embedded ^= 1 << ([3, 11].index(p))
    primes = [3, 11]
    if e > 1 and e not in primes:
        primes.append(e)
    primes.sort()
    field = mfield.MField(primes)
    masks = {p: 1 << i for i, p in enumerate(primes)}
    def elt(pairs):
        out = [Fr(0)] * field.N
        for mask, value in pairs.items():
            out[mask] = Fr(value)
        return tuple(out)
    real = elt({0: (2 * t - 1) / (2 * t)})
    imag = elt({(masks[e] if e > 1 else 0) ^
                embedded:
                Fr(s, 1) / (2 * t)})
    return field, (real, imag)


def omega_for_r(r):
    return omega_for_t(Fr(r + 1, 4))


def in_field_rotations():
    """Return exact rotations from findrot plus t=16 and t=28 families."""
    out = {}
    for r in (3, 5, 11, 15, 33, 55, 165):
        field, w = omega_for_r(r)
        label = f"w[{r}]"
        out[label] = (field, w)
        out[label + "~"] = (field, (w[0], tuple(-x for x in w[1])))
        out[label + "^2"] = (field, (field.sub(field.mul(w[0], w[0]),
                                                   field.mul(w[1], w[1])),
                                     field.scal(2, field.mul(w[0], w[1]))))
    for t in (16, 28):
        field, w = omega_for_t(t)
        label = f"t{t}"
        out[label] = (field, w)
        out[label + "~"] = (field, (w[0], tuple(-x for x in w[1])))
        out[label + "^2"] = (field, (field.sub(field.mul(w[0], w[0]),
                                                   field.mul(w[1], w[1])),
                                     field.scal(2, field.mul(w[0], w[1]))))
    return out
