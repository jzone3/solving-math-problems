#!/usr/bin/env python3
"""
Canonical p-adic cell arithmetic for the Nielsen/Owens diagrams.

Key point (phase 20 finding): tower/split slot labels in the thesis are
ABSOLUTE p-adic digit positions on the p-adic tree of Z, shared across
sections.  Emitting towers by naive relative placement (c + m*cls mod
m*p^k) permutes the digits depending on the context modulus unit, so
coverage bookkeeping ("x" = already covered elsewhere) breaks across
sections.  All emitters must use these canonical helpers.
"""
from math import gcd


def crt(r1, n1, r2, n2):
    g = gcd(n1, n2)
    assert (r1 - r2) % g == 0
    l = n1 // g * n2
    m2 = n2 // g
    if m2 == 1:
        return (r1 % l, l)
    inv = pow((n1 // g) % m2, -1, m2)
    t = ((r2 - r1) // g * inv) % m2
    return ((r1 + n1 * t) % l, l)


def pval(m, p):
    d = 0
    while m % p == 0:
        m //= p
        d += 1
    return d, m


def ext(cell, p, val, depth_add):
    """Refine cell by setting its next depth_add p-adic digits to the
    base-p digits of val (0 <= val < p^depth_add), keeping all other
    prime constraints."""
    c, m = cell
    d, mo = pval(m, p)
    pd = p ** d
    newp = (c % pd) + val * pd
    return crt(c % mo, mo, newp, pd * p ** depth_add)


def isect(cell, alist):
    """Intersect absolute congruences with a compatible cell."""
    return [crt(r, n, cell[0], cell[1]) for (r, n) in alist]
