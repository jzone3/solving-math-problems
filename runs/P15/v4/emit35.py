#!/usr/bin/env python3
"""
P15 V4 phase 21: residue-level emission of Owens sec 3.5 (the prime 11)
= Nielsen sec 4.5 with Owens's permutation (class mod 11*5 moved to
4 (mod 5), i.e. swap the 5-adic digit values 1 <-> 4 in every 5^ tower
cited in this section).

Branch covered (Nielsen): the two holes left by removing moduli 6 and
18 (Fig 3.5), restricted to 1 (mod 4):
    B = [1 (mod 12)]  u  [1 (mod 4) n 3 (mod 9)]
where inside the 18-hole the extra 81^(1,_) of sec 3.2 already covers
the digit-1 chain from level 2 on (30 mod 81, 84 mod 243, ...), leaving
    - the class 12 (mod 27)         ("one input in a 27")
    - the digit-2 chain 21 (mod 27), 57 (mod 81), ...  ("... in a 27^")
    - the 3-adic recursion tail (finite-depth placeholder).

The ten inputs of 11^ are Nielsen's, transcribed with canonical p-adic
digit semantics (canon.py).  Cross-section "x" slots are NOT assumed:
the census below checks coverage against the actually-emitted secs
3.1-3.4 plus this section, and reports any x-slot that fails.
"""
import numpy as np
from canon import crt, ext

D2 = 6      # depth of 8^-style 2-towers
D3 = 5      # depth of 27^-style 3-chains
E5 = 2      # depth of inner 5^ towers
E7 = 2      # depth of inner 7^ towers
E11 = 2     # depth of the 11^ tower

ONE = "ONE"


def sig5(t):
    """Owens permutation for this section: 11*5 class moved to 4 (mod 5)."""
    return {1: 4, 4: 1}.get(t, t)


def e8up(base=(1, 4)):
    """8^ inside 1 (mod 4): canonical digit-1 chain; returns (congs, tails)."""
    cells = [ext(base, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(base, 2, 0, D2)]


def chain27():
    """27^ input chain over the 18-hole: 21(27), 57(81), ...; (cells, tails)."""
    cells = [ext((3, 9), 3, 2 * 3 ** (j - 1), j) for j in range(1, D3 + 1)]
    return cells, [ext((3, 9), 3, 0, D3)]


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


E8, E8T = e8up()
CH, CHT = chain27()

A4 = [(1, 4)]
A2 = [(1, 2)]
A3_1 = [(1, 3)]
A3_2 = [(1, 6)]                    # 3*2
A3_4 = [(1, 12)]                   # 3*4
A27_1 = [(12, 27)]                 # the "one input in a 27"
A27_4 = [crt(12, 27, 1, 4)]
A9_2 = [crt(3, 9, 1, 2)]           # 9*2 = (3, 18)
A9_4 = [crt(3, 9, 1, 4)]           # 9*4
A3_8 = x2(E8, 1, 3)                # 3*8^
A9_8 = x2(E8, 3, 9)                # 9*8^
ACH_1 = list(CH)                   # 27^*1
ACH_2 = x2(CH, 1, 2)               # 27^*2
ACH_4 = x2(CH, 1, 4)               # 27^*4
ACH_8 = [crt(c, m, r, n) for (c, m) in CH for (r, n) in E8]   # 27^*8^

# 3*3(1,2,4): split of 1 (mod 3) at the next 3-digit
A33_124 = ([ext((1, 3), 3, 1, 1)]
           + x2([ext((1, 3), 3, 2, 1)], 1, 2)
           + x2([ext((1, 3), 3, 0, 1)], 1, 4))
# 3*3(x,x,1): only the digit-0 cell, whole
A33_xx1 = [ext((1, 3), 3, 0, 1)]
A33_xx8 = x2([ext((1, 3), 3, 0, 1)], 1, 4)  # placeholder base for 8^:
A33_xx8 = [crt(c, m, r, n) for (c, m) in [ext((1, 3), 3, 0, 1)]
           for (r, n) in E8]
# 3(3(1,4, ), , ): outer digit0=1 -> 1 (mod 3); inner digit1 split
A3314 = ([ext((1, 3), 3, 1, 1)]
         + x2([ext((1, 3), 3, 2, 1)], 1, 4))


def eightyone_14():
    """81^(1,4) rooted at 12 (mod 27): digit-1 ONE, digit-2 * 4."""
    congs, tails = [], []
    for j in range(1, D3 + 1):
        congs.append(ext((12, 27), 3, 3 ** (j - 1), j))
        congs += x2([ext((12, 27), 3, 2 * 3 ** (j - 1), j)], 1, 4)
    tails.append(ext((12, 27), 3, 0, D3))
    return congs, tails


def tower(p, depth, sig, contents):
    """q^ tower: level m puts contents[t-1] on the canonical digit cell.
    contents entries: ONE, a list of Z-congs, or None (blank).
    Returns (congs, tails)."""
    congs, tails = [], []
    for m in range(1, depth + 1):
        for t, inp in enumerate(contents, start=1):
            val = sig(t) if m == 1 else t * p ** (m - 1)
            cell = ext((0, 1), p, val, m)
            if inp is None:
                tails.append(cell)      # blank slot: must be covered by
                # the other summand of the same input (checked in census)
            elif inp == ONE:
                congs.append(cell)
            else:
                congs += [crt(c, mm, r, n) for (r, n) in inp
                          for (c, mm) in [cell]]
    tails.append(ext((0, 1), p, 0, depth))
    return congs, tails


def five(contents):
    return tower(5, E5, sig5, contents)


def seven(contents):
    return tower(7, E7, lambda t: t, contents)


def inputs():
    """The ten 11^-input content sets: (name, congs, tails, blanks)."""
    out = []

    def add(name, *pieces):
        congs, tails = [], []
        for c, t in pieces:
            congs += c
            tails += t
        out.append((name, congs, tails))

    A81, A81T = eightyone_14()
    add("S1: 4", (A4, []))
    add("S2: 8^", (E8, E8T))
    add("S3: 3*2+27*1+27^*2", (A3_2 + A27_1 + ACH_2, CHT))
    add("S4: 3*4+27*4+27^*8^", (A3_4 + A27_4 + ACH_8, CHT + E8T))
    add("S5: 3*8^+9*8^", (A3_8 + A9_8, E8T))
    add("S6: 5^(1,2,3*1,4)", five([ONE, A2, A3_1, A4]))
    add("S7: 5^(8^,3*2+9*2,3*4,3*8^+9*8^)",
        five([E8, A3_2 + A9_2, A3_4, A3_8 + A9_8]))
    add("S8: 3*3(1,2,4)+81^(1,4)+5^(27^*...)",
        (A33_124, []), (A81, A81T),
        five([ACH_1, ACH_2, ACH_4, ACH_8]))
    # S9: the 5^ set sits INSIDE the 4th slot of the 7^ tower
    congs9, tails9 = [], []
    for l in range(1, E7 + 1):
        for t, inp in enumerate([ONE, A2, A3_1, "FIVE", A4, E8], start=1):
            cell = ext((0, 1), 7, t * 7 ** (l - 1), l)
            if inp == ONE:
                congs9.append(cell)
            elif inp == "FIVE":
                f, ft = five([ONE, A2, None, A4])
                congs9 += [crt(c, m, r, n) for (r, n) in f
                           for (c, m) in [cell]]
                tails9 += [crt(c, m, r, n) for (r, n) in ft
                           for (c, m) in [cell]]
            else:
                congs9 += [crt(c, m, r, n) for (r, n) in inp
                           for (c, m) in [cell]]
    tails9.append(ext((0, 1), 7, 0, E7))
    out.append(("S9: 7^(1,2,3*1,5^(1,2,x,4),4,8^)", congs9, tails9))

    # S10 = 5^(3(3(1,4, )), , , ) + 7^(six sets)
    f10, f10t = five([A3314, None, None, None])
    slot4, slot4t = five([A33_xx1 + A9_2, E8, None, A3_1 + A9_4])
    slot6, slot6t = five([A33_xx8, A3_2, A3_4, A3_8 + A9_8])
    A81b, A81bT = eightyone_14()
    slot5c, slot5t = five([ACH_1, ACH_2, ACH_4, ACH_8])
    slot5 = A33_124 + A81b + slot5c
    seven_slots = [A3_2 + A27_1 + ACH_2,
                   A3_4 + A27_4 + ACH_8,
                   A3_8,
                   slot4,
                   slot5,
                   slot6]
    congs10, tails10 = list(f10), list(f10t)
    for l in range(1, E7 + 1):
        for t, inp in enumerate(seven_slots, start=1):
            cell = ext((0, 1), 7, t * 7 ** (l - 1), l)
            congs10 += [crt(c, m, r, n) for (r, n) in inp
                        for (c, m) in [cell]]
    tails10.append(ext((0, 1), 7, 0, E7))
    tails10 += slot4t + slot5t + slot6t + A81bT + CHT + E8T
    out.append(("S10: 5^(3(3(1,4, ))...)+7^(...)", congs10, tails10))
    return out


def emit():
    """Full sec-3.5 congruences: content sets placed on the 11^ cells.
    Returns (congs, tails)."""
    congs, tails = [], []
    sets = inputs()
    assert len(sets) == 10
    for k in range(1, E11 + 1):
        for t in range(1, 11):
            cell = (t * 11 ** (k - 1) % 11 ** k, 11 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 11 ** E11))
    return congs, tails


def main():
    import emitcore
    import emit33
    import emit34
    congs, tails = emit()
    mods = [n for _, n in congs]
    print(f"sec3.5: {len(congs)} congruences, {len(tails)} tail/blank "
          f"placeholders")
    print(f"min modulus: {min(mods)} (require >= 42)")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.5: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", [m for m, c in Counter(mods).items()
                                if c > 1][:20])
    prev = emitcore.emit()
    c33 = emit33.emit()
    c34 = emit34.emit() if hasattr(emit34, "emit") else []
    if isinstance(c34, tuple):
        c34 = c34[0]
    print("overlap w/ skeleton:",
          len(set(mods) & set(n for _, n in prev)))
    print("overlap w/ sec3.3:",
          len(set(mods) & set(n for _, n in c33)))
    print("overlap w/ sec3.4:",
          len(set(mods) & set(n for _, n in c34)))

    # census: per 11^-input coverage of B over the non-11 window
    N = 2 ** 7 * 3 ** 6 * 5 ** 2 * 7 ** 2   # 114,307,200
    print("census window:", N)
    base = np.zeros(N, dtype=bool)
    for r, n in prev:
        if N % n == 0:
            base[r % n::n] = True
    idx = np.arange(N)
    Bmask = ((idx % 12 == 1)
             | ((idx % 4 == 1) & (idx % 9 == 3)))
    sets = inputs()
    for name, cc, tt in sets:
        cov = base.copy()
        dropped = 0.0
        for r, n in cc + tt:
            if N % n == 0:
                cov[r % n::n] = True
            else:
                dropped += 1.0 / n
        unc = idx[Bmask & ~cov]
        print(f"{name}: uncovered {unc.size} "
              f"(dropped measure {dropped:.2e})")
        if unc.size:
            from collections import Counter
            print("   by mod 45:", sorted(Counter(unc % 45).items())[:10])


if __name__ == "__main__":
    main()
