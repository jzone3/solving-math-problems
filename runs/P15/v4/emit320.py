#!/usr/bin/env python3
"""
P15 V4 phase 40: residue-level emission of Owens sec 3.20
(primes 79 and 83) -- the FINAL section of the construction.

Hole: fourth 5-input (4 mod 5) on the 32 hole (16 mod 32), split by
the 3-digit: 79^ fills the first 3-input (1 mod 3), 83^ the second
(2 mod 3).

Seventy-eight sets per 3-input: 1,2,4,8,16,32,64^; with 3^ (single-
input copies, depth-shifted as in sec 3.19) -> fourteen; seven 7^
copies at two inputs -> twenty-one; 5* and five 25^ -> forty-seven;
then 47^, three 17^, five 11^, two 29^, 59^, 53^, 61^, two 31^,
five 13^, 67^, three 23^, four 19^, 71^, 73^ -> seventy-eight, which
fill the 79^.  The 83-side reuses its own seventy-eight sets plus a
depth-shifted 79^ tower, a 43^, and two 41^ -> eighty-two sets
filling the 83^ and finishing the construction.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E3 = 3
E1 = 1
EBIGP = 2

ONE = "ONE"
B2 = (16, 32)
B5 = (4, 5)


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def tower(p, depth, contents, base=(0, 1), start=1):
    congs, tails = [], []
    for m in range(start, start + depth):
        for t, inp in enumerate(contents, start=1):
            cell = ext(base, p, t * p ** (m - 1), m)
            if inp is None:
                tails.append(cell)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext(base, p, 0, start + depth - 1))
    return congs, tails


def t25(contents):
    congs, tails = [], []
    for k in range(1, E5 + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(B5, 5, t * 5 ** (k - 1), k)
            congs += [crt(c, m, r, n) for (r, n) in inp
                      for (c, m) in [cell]]
    tails.append(ext(B5, 5, 0, E5))
    return congs, tails


def build78(b3):
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    e64 = [ext(B2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    e64t = [ext(B2, 2, 0, D2)]
    add("1", [(0, 1)])
    add("2", [(0, 2)])
    add("4", [(0, 4)])
    add("8", [(0, 8)])
    add("16", [(16, 16)])
    add("32", [(16, 32)])
    add("64^", e64, e64t)
    seven = [(s[1], s[2]) for s in out]
    # single-input 3^ copies over the fixed mod-3 cell, depth-shifted
    # to level 2 as in sec 3.19 (level 1 would repeat modulus 3*m of
    # nothing here, but keeps the copies mutually and globally fresh)
    for i, (cc, tt) in enumerate(seven, start=1):
        add(f"3^({i})", *tower(3, E3, [cc, None], base=b3, start=2))
    sets = [s[1] for s in out]
    for i in range(7):
        add(f"7^#{i+1} (2 inputs)",
            *tower(7, E7, sets[2 * i:2 * i + 2] + [None] * 4))
    twentyone = [(s[1], s[2]) for s in out[:21]]
    for i, (cc, tt) in enumerate(twentyone, start=1):
        add(f"5*{i}", x2(cc, *B5), x2(tt, *B5))
    sets = [s[1] for s in out]
    for i in range(5):
        add(f"25^#{i+1}", *t25(sets[4 * i:4 * i + 4]))
    sets = [s[1] for s in out]
    add("47^", *tower(47, E1, sets[:46]))
    add("17^a", *tower(17, E1, sets[:16]))
    add("17^b", *tower(17, E1, sets[16:32]))
    add("17^c", *tower(17, E1, sets[32:47] + [None]))
    sets = [s[1] for s in out]
    add("11^a", *tower(11, E1, sets[:10]))
    add("11^b", *tower(11, E1, sets[10:20]))
    add("11^c", *tower(11, E1, sets[20:30]))
    add("11^d", *tower(11, E1, sets[30:40]))
    add("11^e", *tower(11, E1, sets[40:50]))
    sets = [s[1] for s in out]
    add("29^a", *tower(29, E1, sets[:28]))
    add("29^b", *tower(29, E1, sets[28:56]))
    sets = [s[1] for s in out]
    add("59^", *tower(59, E1, sets[:58]))
    sets = [s[1] for s in out]
    add("53^", *tower(53, E1, sets[:52]))
    sets = [s[1] for s in out]
    add("61^", *tower(61, E1, sets[:60]))
    sets = [s[1] for s in out]
    add("31^a", *tower(31, E1, sets[:30]))
    add("31^b", *tower(31, E1, sets[30:60]))
    sets = [s[1] for s in out]
    add("13^a", *tower(13, E1, sets[:12]))
    add("13^b", *tower(13, E1, sets[12:24]))
    add("13^c", *tower(13, E1, sets[24:36]))
    add("13^d", *tower(13, E1, sets[36:48]))
    add("13^e", *tower(13, E1, sets[48:60]))
    sets = [s[1] for s in out]
    add("67^", *tower(67, E1, sets[:66]))
    sets = [s[1] for s in out]
    add("23^a", *tower(23, E1, sets[:22]))
    add("23^b", *tower(23, E1, sets[22:44]))
    add("23^c", *tower(23, E1, sets[44:66]))
    sets = [s[1] for s in out]
    add("19^a", *tower(19, E1, sets[:18]))
    add("19^b", *tower(19, E1, sets[18:36]))
    add("19^c", *tower(19, E1, sets[36:54]))
    add("19^d", *tower(19, E1, sets[54:72]))
    sets = [s[1] for s in out]
    add("71^", *tower(71, E1, sets[:70]))
    sets = [s[1] for s in out]
    add("73^", *tower(73, E1, sets[:72]))
    assert len(out) == 78
    return out


def emit320():
    congs, tails = [], []
    setsA = build78((1, 3))
    for k in range(1, EBIGP + 1):
        for t in range(1, 79):
            cell = (t * 79 ** (k - 1) % 79 ** k, 79 ** k)
            name, cc, tt = setsA[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 79 ** EBIGP))
    setsB = build78((2, 3))
    sB = [s[1] for s in setsB]
    e79 = tower(79, 2, sB[:78], start=3)
    e43 = tower(43, E1, sB[:42], start=2)
    e41a = tower(41, E1, sB[:40], start=2)
    e41b = tower(41, E1, sB[40:78] + [None] * 2, start=3)
    allB = setsB + [("79^ lv3-4", e79[0], e79[1]),
                    ("43^ lv2", e43[0], e43[1]),
                    ("41^ lv2", e41a[0], e41a[1]),
                    ("41^ lv3", e41b[0], e41b[1])]
    for k in range(1, EBIGP + 1):
        for t in range(1, 83):
            cell = (t * 83 ** (k - 1) % 83 ** k, 83 ** k)
            name, cc, tt = allB[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 83 ** EBIGP))
    return congs, tails


def main():
    congs, tails = emit320()
    mods = [n for _, n in congs]
    print(f"sec3.20: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.20: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    import emit315, emit316, emit317, emit318, emit319
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0]),
             ("sec3.8", emit38.emit38()[0]), ("sec3.9", emit39.emit39()[0]),
             ("sec3.10", emit310.emit310()[0]),
             ("sec3.11", emit311.emit311()[0]),
             ("sec3.12", emit312.emit312()[0]),
             ("sec3.13", emit313.emit313()[0]),
             ("sec3.14", emit314.emit314()[0]),
             ("sec3.15", emit315.emit315()[0]),
             ("sec3.16", emit316.emit316()[0]),
             ("sec3.17", emit317.emit317()[0]),
             ("sec3.18", emit318.emit318()[0]),
             ("sec3.19", emit319.emit319()[0])]
    ov = 0
    for lab, cs in prevs:
        o = len(set(mods) & set(n for _, n in cs))
        if o:
            print(f"  overlap w/ {lab}: {o}")
        ov += o
    print(f"overlap w/ all previous sections: {ov}")
    N = 2 ** 8 * 3 ** 3 * 5 ** 2 * 79
    print("census window (79-half):", N)
    base = np.zeros(N, dtype=bool)
    for lab, cs in prevs:
        for r, n in cs:
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
    B = (idx % 32 == 16) & (idx % 5 == 4) & (idx % 3 == 1)
    unc = idx[B & ~cov]
    print(f"79-half uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()
