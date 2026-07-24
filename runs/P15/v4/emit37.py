#!/usr/bin/env python3
"""
P15 V4 phase 27: residue-level emission of Owens sec 3.7 (the prime 17)
= a 17^ on the 12-hole, filled with sixteen of the seventeen sets
Nielsen constructs for his prime-19 section (4.8), dropping the one
set that is itself a 17^ (Owens: "as only one of these sets involved
the prime 17, we may use the other sixteen sets").

The 12-hole: T=42 removes the modulus-12 congruence of the 3-tower's
level-1 input on the odd branch, reopening the single coset
    13 (mod 24)   [= 1 (mod 12), relative 2-adic cell 2 (mod 4)].
Note 13 (mod 24) is inside 1 (mod 12), the first branch of sec 3.5,
so the x-slots in Nielsen's 11^-based sets (partial covers from the
prime 11) are checkable against the actually-emitted sec 3.5.

Sets (Nielsen 4.8, transcribed with canonical digit semantics):
  1..10: 4, 8^, 3*1, 3*2, 3*4, 3*8^, 9^(1,2), 9^(4,8^),
         5^(1,2,4,8^), 5^(3*1,3*2,3*4,3*8^)
  11/12: two 7^'s splitting the twelve sets {1,2,S1..S10}
  13/14: 11^(x,x,1,2,3*1,5^(x,x,1,x),5^(x,2,3*1,3*2),3*2,
             7^(x,x,1,2,x,x),9^(1,2))  and its (1->4, 2->8^) copy
  15:    13^ over twelve sets avoiding 5^/11^ starters
  16:    the composite four-part set (5^ + 7^ + 11^ + big 13^);
         transcribed with blank/tail placeholders where Nielsen's
         "save room" notation under-determines slots -- all counted
         and census-checked, never silently assumed.

Owens's 11*5 / 13*5 permutations only move x-positions inside cited
5^ towers here (no filled slot content sits on 5-digit 1 or 4), so
they affect the census expectations, not the emitted congruences.
"""
import numpy as np
from canon import crt, ext

D2 = 6     # 8^-style 2-chain depth
E5 = 2
E7 = 2
E9 = 3     # 9^ tower depth (3-adic levels beyond digit)
E11 = 1
E13 = 1
E17 = 2

HOLE = (13, 24)
ONE = "ONE"


def e8up(base=(1, 4)):
    cells = [ext(base, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(base, 2, 0, D2)]


E8, E8T = e8up()


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


A1 = [(0, 1)]
A2 = [(1, 2)]
A4 = [(1, 4)]
A3_1 = [(1, 3)]
A3_2 = [(1, 6)]
A3_4 = [(1, 12)]
A3_8 = x2(E8, 1, 3)


def nineup(c1, c2):
    """9^(a,b): 3-adic tower anchored at the hole's mod-9 cell (4 mod 9,
    since 13 = 1 + 1*3 + 1*9): level m puts input t on the canonical
    digit cell above 9.  Contents are absolute cells CONTAINING the
    branch (covering more than needed is fine, phase 22)."""
    congs, tails = [], []
    for m in range(1, E9 + 1):
        for t, inp in enumerate((c1, c2), start=1):
            cell = ext((4, 9), 3, t * 3 ** (m - 1), m)
            if inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext((4, 9), 3, 0, E9))
    return congs, tails


N9_12, N9_12T = nineup(ONE, A2)          # 9^(1,2)
N9_48, N9_48T = nineup(A4, E8)           # 9^(4,8^)


def tower(p, depth, contents, base=(0, 1)):
    congs, tails = [], []
    for m in range(1, depth + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(base, p, t * p ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(base, p, 0, depth))
    return congs, tails


def five(contents):
    return tower(5, E5, contents)


def seven(contents):
    return tower(7, E7, contents)


def join(*pieces):
    congs, tails = [], []
    for c, t in pieces:
        congs += c
        tails += t
    return congs, tails


def sets16():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("T1: 4", A4)
    add("T2: 8^", E8, E8T)
    add("T3: 3*1", A3_1)
    add("T4: 3*2", A3_2)
    add("T5: 3*4", A3_4)
    add("T6: 3*8^", A3_8, E8T)
    add("T7: 9^(1,2)", N9_12, N9_12T)
    add("T8: 9^(4,8^)", N9_48, N9_48T)
    f9 = five([ONE, A2, A4, E8])
    add("T9: 5^(1,2,4,8^)", *f9)
    f10 = five([A3_1, A3_2, A3_4, A3_8])
    add("T10: 5^(3*1,3*2,3*4,3*8^)", *f10)
    # T11/T12: two 7^'s over the twelve sets {1,2,T1..T10}
    s7a = seven([A1, A2, A4, E8, A3_1, A3_2])
    add("T11: 7^(1,2,4,8^,3*1,3*2)", *s7a)
    s7b = seven([A3_4, A3_8, N9_12, N9_48, f9[0], f10[0]])
    add("T12: 7^(3*4,3*8^,9^(1,2),9^(4,8^),5^a,5^b)",
        s7b[0], s7b[1] + f9[1] + f10[1])
    # T13/T14: the 11^ partial-cover sets
    def eleven_set(one, two, four, eight):
        i6 = five([None, None, one, None])
        i7 = five([None, two, x2(one, 1, 3), x2(two, 1, 3)])
        i9 = seven([None, None, one, two, None, None])
        return tower(11, E11, [None, None, one, two, x2(one, 1, 3),
                               i6[0], i7[0], x2(two, 1, 3),
                               i9[0], nineup_c(one, two)[0]]), \
               i6[1] + i7[1] + i9[1] + nineup_c(one, two)[1]

    def nineup_c(c1, c2):
        return nineup(ONE if c1 == A1 else c1, c2)

    e13a, extr_a = eleven_set(A1, A2, A4, E8)
    add("T13: 11^(x,x,1,2,3*1,5^(x,x,1,x),5^(x,2,3*1,3*2),3*2,"
        "7^(x,x,1,2,x,x),9^(1,2))", e13a[0], e13a[1] + extr_a)
    e14a, extr_b = eleven_set(A4, E8, A4, E8)
    add("T14: same with 1->4, 2->8^", e14a[0], e14a[1] + extr_b)
    # T15: 13^ over twelve sets avoiding 5^/11^ starters
    t13 = tower(13, E13, [A1, A2, A4, E8, A3_1, A3_2, A3_4, A3_8,
                          N9_12, N9_48, s7a[0], s7b[0]])
    add("T15: 13^(1,2,4,8^,3*1,3*2,3*4,3*8^,9^(1,2),9^(4,8^),7^a,7^b)",
        t13[0], t13[1] + N9_12T + N9_48T)
    # T16: composite four-part set
    p1 = five([None, N9_12, N9_48, None])
    inner5 = five([N9_12, None, None, N9_48])
    p2 = seven([None, None, None, inner5[0], None, None])
    i11_3 = inner5
    i11_4 = seven([A3_1, A3_2, A3_4, None, A3_8, N9_12])
    f_1x2 = five([A1, None, None, A2])
    f_4x8 = five([A4, None, None, E8])
    f_31x32 = five([A3_1, None, None, A3_2])
    f_34x38 = five([A3_4, None, None, A3_8])
    p3b = seven([N9_48, f_1x2[0], f_4x8[0], None,
                 f_31x32[0], f_34x38[0]])
    inner7b = seven([None, None, inner5[0], None, None, None])
    # 5^*c: content c on the 5^ chain cells 5^(k-1) (mod 5^k)
    FUP = [ext((0, 1), 5, 5 ** (k - 1), k) for k in range(1, E5 + 1)]
    FUPT = [ext((0, 1), 5, 0, E5)]

    def fup_c(content):
        if content == ONE:
            return list(FUP)
        return [crt(c, m, r, n) for (c, m) in FUP for (r, n) in content]

    def eleven3(s1, s2, s3):
        """Nielsen's space-saving 11^ written with three inputs."""
        return tower(11, E11, [s1, s2, s3] + [None] * 7)

    e11_51 = eleven3(fup_c(ONE), A1, A2)
    e11_52 = eleven3(fup_c(A2), A4, E8)
    e11_54 = eleven3(fup_c(A4), A3_1, A3_2)
    e11_58 = eleven3(fup_c(E8), A3_4, A3_8)
    e11_531 = eleven3(fup_c(A3_1), N9_12, N9_48)
    e11_532 = eleven3(fup_c(A3_2) + f_34x38[0],
                      seven([A1, A2, A4, None, E8, A3_1])[0], None)
    e11_9 = eleven3(fup_c(N9_12),
                    seven([A3_2, A3_4, A3_8, None, N9_12, N9_48])[0],
                    None)
    p4 = tower(13, E13, [f_1x2[0], f_4x8[0], f_31x32[0], f_34x38[0],
                         inner5[0], e11_51[0], e11_52[0], e11_54[0],
                         e11_58[0], e11_531[0], e11_532[0],
                         e11_9[0]])
    p3 = tower(11, E11, [None, None, i11_3[0], i11_4[0], p3b[0],
                         None, None, None, inner7b[0], None])
    congs16, tails16 = join(p1, p2, p3, p4)
    tails16 += (inner5[1] + i11_4[1] + p3b[1] + inner7b[1] + f_1x2[1]
                + f_4x8[1] + f_31x32[1] + f_34x38[1] + FUPT
                + e11_51[1] + e11_52[1] + e11_54[1] + e11_58[1]
                + e11_531[1] + e11_532[1] + e11_9[1])
    add("T16: composite (reserve 5^ + 7^ + 11^ + big 13^)",
        congs16, tails16)
    return out


def emit37():
    """Sec 3.7: 17^ filling the 12-hole 13 (mod 24).  As in emit35, the
    17-cells are pure (t*17^(k-1) mod 17^k) and contents are absolute
    cells containing the branch -- congruences cover more than the
    hole, which is allowed and keeps moduli 24-free (Nielsen's moduli
    for this section are content * 17^k)."""
    congs, tails = [], []
    sets = sets16()
    assert len(sets) == 16, len(sets)
    for k in range(1, E17 + 1):
        for t in range(1, 17):
            cell = (t * 17 ** (k - 1) % 17 ** k, 17 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 17 ** E17))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36
    congs, tails = emit37()
    mods = [n for _, n in congs]
    print(f"sec3.7: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.7: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prev = emitcore.emit()
    c33 = emit33.emit()
    c34 = emit34.emit34()[0]
    c35 = emit35.emit()[0]
    c36 = emit36.emit36()[0]
    for lab, cs in (("skeleton", prev), ("sec3.3", c33), ("sec3.4", c34),
                    ("sec3.5", c35), ("sec3.6", c36)):
        print(f"overlap w/ {lab}:",
              len(set(mods) & set(n for _, n in cs)))
    # census on the 12-hole, windowed without 11/13 factors first
    N = 2 ** 7 * 3 ** 5 * 5 ** 2 * 7 ** 2 * 17
    print("census window:", N)
    base = np.zeros(N, dtype=bool)
    for r, n in prev + c33 + list(c34) + list(c35) + list(c36):
        if N % n == 0:
            base[r % n::n] = True
    cov = base.copy()
    dropped = 0.0
    for r, n in congs + tails:
        if N % n == 0:
            cov[r % n::n] = True
        else:
            dropped += 1.0 / n
    idx = np.arange(N)
    Bmask = idx % 24 == 13
    unc = idx[Bmask & ~cov]
    print(f"12-hole uncovered: {unc.size} of {Bmask.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 17:", sorted(Counter(unc % 17).items()))


if __name__ == "__main__":
    main()
