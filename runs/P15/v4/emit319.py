#!/usr/bin/env python3
"""
P15 V4 phase 39: residue-level emission of Owens sec 3.19
(primes 71 and 73).

Hole: the remaining single 9^-input in the last 3-input (0 mod 3) of
the second 5-input (2 mod 5) on the 2 mod 4 branch -- reconstructed
as the 9-cell (3,9) (the printed figure does not fix which 9-child;
documented choice).  Split mod 8: 71^ on (2 mod 8), 73^ on (6 mod 8)
with two entries supplied by depth-shifted 71^ towers (the doubling
trick).

Seventy sets per half: 1,2,4,8,16^; a five-input 7^; with 3 and
single-input 9^ copies (only one 9-input needed here) -> eighteen;
17^, 19^, two 11^, two 13^ at eleven inputs -> twenty-four; 5* and
six 25^ -> fifty-four; then 53^, 47^, 43^, 41^, 59^, 37^, two 31^,
61^, three 23^ at twenty-one, three 29^ at twenty-two, 67^.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E7 = 2
E9 = 3
E1 = 1
EBIGP = 2

ONE = "ONE"
B5 = (2, 5)
H9 = (3, 9)
C27 = ext(H9, 3, 1, 1)


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


def nine_single(inp):
    """9^ copy needing only one input on this branch.

    Started at level 2 (Nielsen's artificial depth increase): at level
    1 its modulus 27*m would repeat the 3-conjunction 3*set of the
    same set.  The level-1 slice is left to the recursion tail.
    """
    return tower(3, E9, [inp, None], base=H9, start=2)


def t25(contents):
    congs, tails = [], []
    for k in range(1, E5 + 1):
        for t, inp in enumerate(contents, start=1):
            cell = ext(B5, 5, t * 5 ** (k - 1), k)
            congs += [crt(c, m, r, n) for (r, n) in inp
                      for (c, m) in [cell]]
    tails.append(ext(B5, 5, 0, E5))
    return congs, tails


def build70(b8):
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    e16 = [ext(b8, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    e16t = [ext(b8, 2, 0, D2)]
    A1, A2, A4, A8 = [(0, 1)], [(0, 2)], [(b8[0] % 4, 4)], [b8]

    add("1", A1)
    add("2", A2)
    add("4", A4)
    add("8", A8)
    add("16^", e16, e16t)
    sets = [s[1] for s in out]
    add("7^(5 inputs,x)", *tower(7, E7, sets[:5] + [None]))
    six = [(s[1], s[2]) for s in out[:6]]
    for i, (cc, tt) in enumerate(six, start=1):
        add(f"3*{i}", x2(cc, *C27), x2(tt, *C27))
    for i, (cc, tt) in enumerate(six, start=1):
        add(f"9^({i},x)", *nine_single(cc))
    sets = [s[1] for s in out]
    add("17^", *tower(17, E1, sets[:16]))
    sets = [s[1] for s in out]
    add("19^", *tower(19, E1, sets[:18]))
    sets = [s[1] for s in out]
    add("11^a", *tower(11, E1, sets[:10]))
    add("11^b", *tower(11, E1, sets[10:20]))
    sets = [s[1] for s in out]
    add("13^a (11 inputs)", *tower(13, E1, sets[:11] + [None]))
    add("13^b (11 inputs)", *tower(13, E1, sets[11:22] + [None]))
    twentyfour = [(s[1], s[2]) for s in out[:24]]
    for i, (cc, tt) in enumerate(twentyfour, start=1):
        add(f"5*{i}", x2(cc, *B5), x2(tt, *B5))
    sets = [s[1] for s in out]
    for i in range(6):
        add(f"25^#{i+1}", *t25(sets[4 * i:4 * i + 4]))
    sets = [s[1] for s in out]
    add("53^", *tower(53, E1, sets[:52]))
    add("47^", *tower(47, E1, sets[:46]))
    add("43^", *tower(43, E1, sets[:42]))
    add("41^", *tower(41, E1, sets[:40]))
    sets = [s[1] for s in out]
    add("59^", *tower(59, E1, sets[:58]))
    sets = [s[1] for s in out]
    add("37^", *tower(37, E1, sets[:36]))
    add("31^a", *tower(31, E1, sets[:30]))
    add("31^b", *tower(31, E1, sets[30:60]))
    sets = [s[1] for s in out]
    add("61^", *tower(61, E1, sets[:60]))
    sets = [s[1] for s in out]
    add("23^a (21)", *tower(23, E1, sets[:21] + [None]))
    add("23^b (21)", *tower(23, E1, sets[21:42] + [None]))
    add("23^c (21)", *tower(23, E1, sets[42:63] + [None]))
    sets = [s[1] for s in out]
    add("29^a (22)", *tower(29, E1, sets[:22] + [None] * 6))
    add("29^b (22)", *tower(29, E1, sets[22:44] + [None] * 6))
    add("29^c (22)", *tower(29, E1, sets[44:66] + [None] * 6))
    sets = [s[1] for s in out]
    add("67^", *tower(67, E1, sets[:66]))
    assert len(out) == 70
    return out


def emit319():
    congs, tails = [], []
    setsA = build70((2, 8))
    for k in range(1, EBIGP + 1):
        for t in range(1, 71):
            cell = (t * 71 ** (k - 1) % 71 ** k, 71 ** k)
            name, cc, tt = setsA[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 71 ** EBIGP))
    setsB = build70((6, 8))
    sB = [s[1] for s in setsB]
    e71a = tower(71, 2, sB[:70], start=3)
    e71b = tower(71, 2, sB[:70], start=5)
    allB = setsB + [("71^ lv3-4", e71a[0], e71a[1]),
                    ("71^ lv5-6", e71b[0], e71b[1])]
    for k in range(1, EBIGP + 1):
        for t in range(1, 73):
            cell = (t * 73 ** (k - 1) % 73 ** k, 73 ** k)
            name, cc, tt = allB[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 73 ** EBIGP))
    return congs, tails


def main():
    congs, tails = emit319()
    mods = [n for _, n in congs]
    print(f"sec3.19: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.19: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    import emit315, emit316, emit317, emit318
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
             ("sec3.18", emit318.emit318()[0])]
    ov = 0
    for lab, cs in prevs:
        ov += len(set(mods) & set(n for _, n in cs))
    print(f"overlap w/ all previous sections: {ov}")
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 71
    print("census window (71-half):", N)
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
    B = (idx % 8 == 2) & (idx % 5 == 2) & (idx % 9 == 3)
    unc = idx[B & ~cov]
    print(f"71-half uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")


if __name__ == "__main__":
    main()
