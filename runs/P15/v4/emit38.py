#!/usr/bin/env python3
"""
P15 V4 phase 28: residue-level emission of Owens sec 3.8 (the prime 19).

Branch: 2 (mod 4); target = the first input in the 5 on the 4 hole,
i.e. the cell (2 mod 4) n (1 mod 5) = 6 (mod 20).  Owens builds twenty
sets and fills the eighteen 19^-inputs with them after dropping the
bare sets 1 and 2 (moduli 19, 38 < 42):

  1..4 : 1, 2, 4, 8^          (2-adic cells containing the branch)
  5..9 : 5*1, 5*2, 5*4, 5*8^, 25^(1,2,4,8^)
  10   : 11^ copy with slot 6 = x (covered on this branch already)
  11-15: five 3^ copies over the ten sets in sequence
  16   : 13^ over the first twelve sets
  17   : 17^ over the first sixteen sets
  18-20: three 7^ copies (third entry needs only one 3-input on this
         branch); one of them is 7^(1,2,3(x,1,x),4,8^,3^(2,4)).

The slot layouts of the other two 7^ copies are not fully written out
by Owens ("we can fill three copies of 7^"); the reconstruction below
uses the remaining sets in sequence and marks the choice explicitly --
the dup-checker and census validate it, nothing is silently assumed.
"""
import numpy as np
from canon import crt, ext

D2 = 6
E5 = 2
E3 = 3
E7 = 2
E11 = 1
E13 = 1
E17 = 1
E19 = 2

ONE = "ONE"
BR2 = (2, 4)          # the 4 hole
BR5 = (1, 5)          # first input in the 5


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def e8up():
    """8^ inside 2 (mod 4): canonical digit chain above 4."""
    cells = [ext(BR2, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
    return cells, [ext(BR2, 2, 0, D2)]


E8, E8T = e8up()

A1 = [(0, 1)]
A2 = [(0, 2)]          # the mod-2 cell containing 2 (mod 4)
A4 = [BR2]

# 5-scaled contents: on the branch 5-cell 1 (mod 5)
F1 = [BR5]
F2 = x2(A2, *BR5)
F4 = x2(A4, *BR5)
F8 = x2(E8, *BR5)


def t25():
    """25^(1,2,4,8^) anchored at 1 (mod 5)."""
    congs, tails = [], []
    for k in range(1, E5 + 1):
        for t, inp in enumerate((A1, A2, A4, E8), start=1):
            cell = ext(BR5, 5, t * 5 ** (k - 1), k)
            congs += [crt(c, m, r, n) for (r, n) in inp
                      for (c, m) in [cell]]
    tails.append(ext(BR5, 5, 0, E5))
    return congs, tails


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
                          for (c, m2) in [cell] for mm in [m2]]
    tails.append(ext(base, p, 0, depth))
    return congs, tails


def sets20():
    out = []

    def add(name, congs, tails=()):
        out.append((name, list(congs), list(tails)))

    add("U1: 1", A1)
    add("U2: 2", A2)
    add("U3: 4", A4)
    add("U4: 8^", E8, E8T)
    add("U5: 5*1", F1)
    add("U6: 5*2", F2)
    add("U7: 5*4", F4)
    add("U8: 5*8^", F8, x2(E8T, *BR5))
    c25, t25c = t25()
    add("U9: 25^(1,2,4,8^)", c25, t25c)
    ten = [s[1] for s in out]
    # U10: 11^ with slot 6 = x
    e11 = tower(11, E11, ten[:5] + [None] + ten[5:9])
    add("U10: 11^(1,2,4,8^,5*1,x,5*2,5*4,5*8^,25^)", *e11)
    ten.append(e11[0])
    # U11-U15: five 3^ copies over the ten sets in sequence
    for i in range(5):
        c3 = tower(3, E3, [ten[2 * i], ten[2 * i + 1]])
        add(f"U{11 + i}: 3^(set{2 * i + 1},set{2 * i + 2})", *c3)
    twelve = ten + [out[10][1], out[11][1]]
    # U16: 13^ over the first twelve sets
    add("U16: 13^(first twelve)", *tower(13, E13, twelve))
    sixteen = twelve + [out[12][1], out[13][1], out[14][1], out[15][1]]
    # U17: 17^ over the first sixteen sets
    add("U17: 17^(first sixteen)", *tower(17, E17, sixteen))
    # U18: the prescribed 7^(1,2,3(x,1,x),4,8^,3^(2,4))
    slot3a = [ext((0, 1), 3, 2, 1)]        # 3(x,1,x): ONE on 3-digit 2
    t3_24 = tower(3, E3, [A2, A4])
    e7a = tower(7, E7, [A1, A2, slot3a, A4, E8, t3_24[0]])
    add("U18: 7^(1,2,3(x,1,x),4,8^,3^(2,4))", e7a[0], e7a[1] + t3_24[1])
    # U19/U20: remaining two 7^ copies -- reconstruction: use the
    # 5-scaled sets and the 25^/11^ sets in sequence, third slot again
    # a single 3-input (digit-2 cell within the 5-branch).
    slot3b = [crt(*ext((0, 1), 3, 5, 2), *BR5)]     # 45-cell in 5br
    e7b = tower(7, E7, [F1, F2, slot3b, F4, F8, c25])
    add("U19: 7^(5*1,5*2,3(x,1,x)|5br,5*4,5*8^,25^)",
        e7b[0], e7b[1])
    # third slot: a single 9-cell input (fresh modulus 9*7*19^k,
    # distinct from U18's 3*7*19^k and U19's 15*7*19^k)
    slot3c = [ext((0, 1), 3, 3 + 2, 2)]              # 9-cell
    t3_5_24 = tower(3, E3, [F2, F4])                 # 3^(5*2,5*4)
    t3_5_8_25 = tower(3, E3, [F8, c25])              # 3^(5*8^,25^)
    e7c = tower(7, E7, [e11[0], out[15][1], slot3c, t3_5_24[0],
                        out[16][1], t3_5_8_25[0]])
    add("U20: 7^(11^,13^,9-input,3^(5*2,5*4),17^,3^(5*8^,25^))",
        e7c[0], e7c[1] + t3_5_24[1] + t3_5_8_25[1])
    return out


def emit38():
    """Sec 3.8: 19^ filled with sets U3..U20 (drop U1, U2)."""
    congs, tails = [], []
    sets = sets20()[2:]
    assert len(sets) == 18
    for k in range(1, E19 + 1):
        for t in range(1, 19):
            cell = (t * 19 ** (k - 1) % 19 ** k, 19 ** k)
            name, cc, tt = sets[t - 1]
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 19 ** E19))
    return congs, tails


def main():
    import emitcore, emit33, emit34, emit35, emit36, emit37
    congs, tails = emit38()
    mods = [n for _, n in congs]
    print(f"sec3.8: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)}")
    dup = len(mods) - len(set(mods))
    print(f"dups within sec3.8: {dup}")
    if dup:
        from collections import Counter
        print("  dup moduli:", sorted(m for m, c in Counter(mods).items()
                                      if c > 1)[:20])
    prevs = [("skeleton", emitcore.emit()), ("sec3.3", emit33.emit()),
             ("sec3.4", emit34.emit34()[0]), ("sec3.5", emit35.emit()[0]),
             ("sec3.6", emit36.emit36()[0]), ("sec3.7", emit37.emit37()[0])]
    for lab, cs in prevs:
        print(f"overlap w/ {lab}:", len(set(mods) & set(n for _, n in cs)))
    # census on the target cell 6 (mod 20)
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 7 * 19
    print("census window:", N)
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
    B = idx % 20 == 6
    unc = idx[B & ~cov]
    print(f"target cell uncovered: {unc.size}/{B.sum()} "
          f"(dropped measure {dropped:.2e})")
    if unc.size:
        from collections import Counter
        print("  by mod 19:", sorted(Counter(unc % 19).items()))


if __name__ == "__main__":
    main()
