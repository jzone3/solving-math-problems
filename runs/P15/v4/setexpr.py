"""Up-arrow set-expression engine for the Nielsen/Owens covering calculus.

We only need MODULUS MULTISETS (values), not residues: Owens's stated
permutations of Nielsen's inputs change residues, never moduli. Grammar
(values relative to the enclosing branch; final moduli get multiplied by
the branch scale):

  C(n)            one congruence, modulus n
  T(n)            2-tower starting at n: {n * 2^i, i >= 0}        (n^ with
                                                                  n a 2-power)
  T3(n), T5(n)..  p-tower starting at n: {n * p^i}
  Tow(p, subs)    p^(s_1..s_{p-1}): union over levels k>=1 of
                  p^k * mods(s_i); the tower itself recurses forever.
  Lev(p, subs)    p(s_1,...,s_p): one split, p * mods(s_i) for given
                  (non-blank) inputs.
  Sum(a, b, ...)  union.
  X               already covered / blank: contributes nothing.

All expansions are capped at CAP; results are SETS of modulus values.
"""

CAP_DEFAULT = 10**7


def C(n):
    return ("C", n)


def T(n, p=2):
    return ("T", n, p)


def Tow(p, *subs):
    return ("Tow", p, subs)


def Lev(p, *subs):
    return ("Lev", p, subs)


def Sum(*subs):
    return ("Sum", subs)


X = ("X",)


def mods(expr, cap=CAP_DEFAULT):
    kind = expr[0]
    out = set()
    if kind == "X":
        return out
    if kind == "C":
        if expr[1] <= cap:
            out.add(expr[1])
        return out
    if kind == "T":
        n, p = expr[1], expr[2]
        v = n
        while v <= cap:
            out.add(v)
            v *= p
        return out
    if kind == "Sum":
        for s in expr[1]:
            out |= mods(s, cap)
        return out
    if kind == "Lev":
        p, subs = expr[1], expr[2]
        for s in subs:
            for m in mods(s, cap // p):
                out.add(p * m)
        return out
    if kind == "Tow":
        p, subs = expr[1], expr[2]
        inner = set()
        for s in subs:
            inner |= mods(s, cap // p)
        pk = p
        while pk <= cap:
            for m in inner:
                if pk * m <= cap:
                    out.add(pk * m)
            pk *= p
        return out
    raise ValueError(kind)


# ---------------------------------------------------------------------------
# Nielsen (2009) section 4.5, prime 11 (== Owens 3.5 up to input permutation,
# which leaves the modulus multiset unchanged).  The ten inputs of 11^:
# ---------------------------------------------------------------------------

def nielsen_p11_inputs():
    i1 = C(4)
    i2 = T(8)
    i3 = Sum(C(6), C(27), ("T", 54, 3))            # 3*2 + 27*1 + 27^*2
    i4 = Sum(C(12), C(108), _t3mul(27, T(8)))      # 3*4 + 27*4 + 27^*8^
    i5 = Sum(_mul(3, T(8)), _mul(9, T(8)))         # 3*8^ + 9*8^
    i6 = Tow(5, C(1), C(2), C(3), C(4))
    i7 = Tow(5, T(8), Sum(C(6), C(18)), C(12),
             Sum(_mul(3, T(8)), _mul(9, T(8))))
    i8 = Sum(Lev(3, _mul(3, Sum(C(1), C(2), C(4)))),     # 3*3(1,2,4)
             Tow(3, C(27), C(108)),                       # 81^(1,4): 81*3^i*{1,4}
             Tow(5, _t3mul(27, C(1)), _t3mul(27, C(2)),
                 _t3mul(27, C(4)), _t3mul(27, T(8))))
    i9 = Tow(7, C(1), C(2), C(3),
             Tow(5, C(1), C(2), X, C(4)), C(4), T(8))
    i10 = Sum(
        Tow(5, Lev(3, Lev(3, C(1), C(4), X), X, X), X, X, X),
        Tow(7,
            Sum(C(6), C(27), ("T", 54, 3)),
            Sum(C(12), C(108), _t3mul(27, T(8))),
            _mul(3, T(8)),
            Tow(5, Sum(Lev(3, _mul(3, C(1))), C(18)), T(8), X,
                Sum(C(3), C(36))),
            Sum(Lev(3, _mul(3, Sum(C(1), C(2), C(4)))),
                Tow(3, C(27), C(108)),
                Tow(5, _t3mul(27, C(1)), _t3mul(27, C(2)),
                    _t3mul(27, C(4)), _t3mul(27, T(8)))),
            Tow(5, Lev(3, _mul(3, T(8))), C(6), C(12),
                Sum(_mul(3, T(8)), _mul(9, T(8))))))
    return [i1, i2, i3, i4, i5, i6, i7, i8, i9, i10]


def _mul(k, expr):
    """k * expr: scale every modulus by k."""
    return ("Scale", k, expr)


def _t3mul(base, expr):
    """base^(3-tower) * expr: {base*3^i} times mods(expr)."""
    return ("T3Scale", base, expr)


_orig_mods = mods


def mods(expr, cap=CAP_DEFAULT):  # noqa: F811 - extend with scale nodes
    if expr[0] == "Scale":
        k, sub = expr[1], expr[2]
        return {k * m for m in mods(sub, cap // k)}
    if expr[0] == "T3Scale":
        base, sub = expr[1], expr[2]
        out = set()
        b = base
        while b <= cap:
            for m in mods(sub, cap // b):
                out.add(b * m)
            b *= 3
        return out
    return _orig_mods(expr, cap)


def nielsen_p11_moduli(cap=CAP_DEFAULT):
    """All moduli of the prime-11 section: 11^k * input moduli, k >= 1."""
    inner = set()
    for e in nielsen_p11_inputs():
        inner |= mods(e, cap // 11)
    out = set()
    pk = 11
    while pk <= cap:
        for m in inner:
            if pk * m <= cap:
                out.add(pk * m)
        pk *= 11
    return out


def nielsen_p13_moduli(cap=CAP_DEFAULT):
    """Prime-13 section: first ten inputs of 13^ reuse the SAME sets as the
    prime-11 section; inputs 11 and 12 are modified 11^s (same moduli set,
    with entries '20/21 -> x' dropped and, for input 12, 4 -> 1, 8^ -> 2 -
    both only shrink or keep the value set; we over-approximate by the full
    11^ set plus {1,2} at the 11-levels)."""
    inner = set()
    for e in nielsen_p11_inputs():
        inner |= mods(e, cap // 13)
    # the two modified 11^ inputs
    eleven = nielsen_p11_moduli(cap // 13)
    inner |= eleven
    # input 12 replaces 4 -> 1 and 8^ -> 2 inside the 11^: adds 11^j*{1,2}
    pk = 11
    while pk <= cap // 13:
        inner.add(pk)
        if 2 * pk <= cap // 13:
            inner.add(2 * pk)
        pk *= 11
    out = set()
    pk = 13
    while pk <= cap:
        for m in inner:
            if pk * m <= cap:
                out.add(pk * m)
        pk *= 13
    return out


if __name__ == "__main__":
    cap = 10**5
    U11 = nielsen_p11_moduli(cap)
    U13 = nielsen_p13_moduli(cap)
    print(f"p=11 section: {len(U11)} moduli <= {cap}; "
          f"smallest: {sorted(U11)[:12]}")
    print(f"p=13 section: {len(U13)} moduli <= {cap}; "
          f"smallest: {sorted(U13)[:12]}")
    # clearance yield for the 42-hole patch: free 11-/13-divisible M >= 43
    from math import gcd
    from owens_smooth import used_smooth
    U = used_smooth(cap) | U11 | U13
    freed = []
    for M in range(43, 3000):
        big = M
        smooth = M
        for p in (2, 3, 5, 7):
            while smooth % p == 0:
                smooth //= p
        if smooth == 1 or smooth % 11 and smooth % 13:
            continue  # only 11/13-divisible candidates here
        rest = smooth
        for p in (11, 13):
            while rest % p == 0:
                rest //= p
        if rest != 1:
            continue  # other unknown primes involved
        g = gcd(M, 42)
        if M // g and M not in U and (M // gcd(M, 42)) * g == M:
            freed.append(M)
    print(f"FREED {2,3,5,7,11,13}-smooth moduli >= 43 (patch-usable, "
          f"M<3000): {freed[:40]}")
    print(f"total {len(freed)}; density sum = "
          f"{sum(gcd(M,42)/M for M in freed):.4f} (inner density)")
