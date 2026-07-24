#!/usr/bin/env python3
"""
P15 V4 phase 23: residue-level emission of Owens sec. 3.6 (the prime
13) = Nielsen 4.6, with Owens's permutation (class modulo 13*5 moved
to 2 (mod 5)).

Branch: same 6/18 holes as sec 3.5 but the OTHER class modulo 4:
  B' = [3 (mod 4) n 1 (mod 3)] u [3 (mod 4) n 3 (mod 9)]   (reduced).

Structure (Nielsen 4.6): the first ten of the twelve 13^ inputs reuse
the ten sets of 4.5, with every 4 / 8^ now referring to 3 (mod 4).
The last two inputs are modified 11^ copies:
  input 11: 11^ with the 4.5 sets (4/8^ -> 3 (mod 4)), x-ing every
            entry with no 4/8^ factor (those congruences from sec 3.5
            are 2-adically unrestricted or only odd-restricted, so
            they already cover this branch);
  input 12: same skeleton with 4 -> 1 and 8^ -> 2 (fresh classes,
            allowed here since the moduli carry 11*13 >= 143).

Contents are built from tagged atoms so the branch, the 5-adic
permutation, and the keep/x filter are all parameters.
"""
import numpy as np
from canon import crt, ext

D2, D3, E5, E7, E11, E13 = 6, 4, 2, 2, 1, 2

ONE = "ONE"


def x2(cells, r, n):
    return [crt(c, m, r, n) for (c, m) in cells]


def cross(cells, others):
    return [crt(c, m, r, n) for (c, m) in cells for (r, n) in others]


class Atoms:
    """Tagged content atoms for one 2-adic branch.  Tags: '1', '2',
    '4', '8' say which 2-adic symbol the atom depends on ('-' = none).
    Each atom is (tag, congs, tails)."""

    def __init__(self, base4):
        self.base4 = base4
        b = base4
        self.E8 = [ext(b, 2, 2 ** (j - 1), j) for j in range(1, D2 + 1)]
        self.E8T = [ext(b, 2, 0, D2)]
        self.CH = [ext((3, 9), 3, 2 * 3 ** (j - 1), j)
                   for j in range(1, D3 + 1)]
        self.CHT = [ext((3, 9), 3, 0, D3)]
        self.A4 = [b]
        self.A2 = [(1, 2)]

    def atom(self, name):
        """name -> (tag, congs, tails)"""
        b = self.b = self.base4
        E8, E8T, CH, CHT = self.E8, self.E8T, self.CH, self.CHT
        table = {
            "1": ("1", ONE, []),
            "2": ("2", self.A2, []),
            "4": ("4", self.A4, []),
            "8^": ("8", E8, E8T),
            "3*1": ("-", [(1, 3)], []),
            "3*2": ("-", [(1, 6)], []),
            "3*4": ("4", x2([(1, 3)], *b), []),
            "3*8^": ("8", x2(E8, 1, 3), []),
            "9*2": ("-", [crt(3, 9, 1, 2)], []),
            "9*4": ("4", [crt(3, 9, *b)], []),
            "9*8^": ("8", x2(E8, 3, 9), []),
            "27*1": ("-", [(12, 27)], []),
            "27*4": ("4", [crt(12, 27, *b)], []),
            "9*1": ("-", [(3, 9)], []),
            "27^*1": ("-", list(CH), CHT),
            "27^*2": ("-", x2(CH, 1, 2), CHT),
            "27^*4": ("4", x2(CH, *b), CHT),
            "27^*8^": ("8", cross(CH, E8), CHT + E8T),
        }
        return table[name]

    def group(self, names, keep=None):
        """Union of atoms; keep = predicate on tags (None = all).
        Returns (congs, tails) with ONE atoms expanded to whole-cell."""
        congs, tails = [], []
        for nm in names:
            tag, cc, tt = self.atom(nm)
            if keep is not None and not keep(tag):
                continue
            if cc == ONE:
                congs.append((0, 1))
            else:
                congs += cc
            tails += tt
        return congs, tails


def tower(p, depth, sig, contents):
    """contents: list of (congs, tails) or None (blank/x)."""
    congs, tails = [], []
    for m in range(1, depth + 1):
        for t, inp in enumerate(contents, start=1):
            val = sig(t) if m == 1 else t * p ** (m - 1)
            cell = ext((0, 1), p, val, m)
            if inp is None:
                tails.append(cell)
                continue
            cc, tt = inp
            congs += [crt(c, mm, r, n) for (r, n) in cc
                      for (c, mm) in [cell]]
            tails += [crt(c, mm, r, n) for (r, n) in tt
                      for (c, mm) in [cell]]
    tails.append(ext((0, 1), p, 0, depth))
    return congs, tails


def eightyone_14(A, keep=None, sub4=None):
    """81^(1,4) rooted at 12 (mod 27)."""
    congs, tails = [], []
    for j in range(1, D3 + 1):
        if keep is None or keep("-"):
            congs.append(ext((12, 27), 3, 3 ** (j - 1), j))
        if keep is None or keep("4"):
            cell = ext((12, 27), 3, 2 * 3 ** (j - 1), j)
            congs += [cell] if sub4 else x2([cell], *A.base4)
    tails.append(ext((12, 27), 3, 0, D3))
    return congs, tails


def a33_124(A, keep=None, sub4=None):
    """3*3(1,2,4): slots (1,2,3) -> digits (1,2,0) inside 1 (mod 3)."""
    congs = []
    if keep is None or keep("-"):
        congs.append(ext((1, 3), 3, 1, 1))
        congs += x2([ext((1, 3), 3, 2, 1)], 1, 2)
    if keep is None or keep("4"):
        cell = ext((1, 3), 3, 0, 1)
        congs += [cell] if sub4 else x2([cell], *A.base4)
    return congs, []


def a33_xx1(A):
    return [ext((1, 3), 3, 0, 1)], []


def a33_xx8(A):
    return cross([ext((1, 3), 3, 0, 1)], A.E8), A.E8T


def a3314(A, keep=None, sub4=None):
    """3(3(1,4, )): digit0=1, inner digits 1 (ONE) and 2 (*4)."""
    congs = []
    if keep is None or keep("-"):
        congs.append(ext((1, 3), 3, 1, 1))
    if keep is None or keep("4"):
        cell = ext((1, 3), 3, 2, 1)
        congs += [cell] if sub4 else x2([cell], *A.base4)
    return congs, []


def ten_sets(A, sig5, keep=None, sub4=None, sub8=None):
    """The ten Nielsen-4.5 content sets over branch atoms A with the
    5-adic first-level permutation sig5.  keep filters atoms by tag
    (for the modified 11^ copies); sub4/sub8 substitute the 2-adic
    symbols (input 12: 4 -> 1, 8^ -> 2)."""
    SUB = {"4": "1", "8^": "2", "3*4": "3*1", "3*8^": "3*2",
           "9*4": "9*1", "9*8^": "9*2", "27*4": "27*1",
           "27^*4": "27^*1", "27^*8^": "27^*2"}

    def G(names):
        """Filter by ORIGINAL atom tag, then apply the 4->1 / 8^->2
        substitution (input 12)."""
        kept = [nm for nm in names
                if keep is None or keep(A.atom(nm)[0])]
        if sub4:
            kept = [SUB.get(nm, nm) for nm in kept]
        return A.group(kept)

    fv = lambda contents: tower(5, E5, sig5, contents)
    out = []
    out.append(("S1", G(["4"])))
    out.append(("S2", G(["8^"])))
    out.append(("S3", G(["3*2", "27*1", "27^*2"])))
    out.append(("S4", G(["3*4", "27*4", "27^*8^"])))
    out.append(("S5", G(["3*8^", "9*8^"])))
    out.append(("S6", fv([G(["1"]), G(["2"]), G(["3*1"]), G(["4"])])))
    out.append(("S7", fv([G(["8^"]), G(["3*2", "9*2"]), G(["3*4"]),
                          G(["3*8^", "9*8^"])])))
    c8a, t8a = a33_124(A, keep, sub4)
    c8b, t8b = eightyone_14(A, keep, sub4)
    c8c, t8c = fv([G(["27^*1"]), G(["27^*2"]), G(["27^*4"]),
                   G(["27^*8^"])])
    out.append(("S8", (c8a + c8b + c8c, t8a + t8b + t8c)))
    # S9: 7^(1,2,3*1,5^(1,2,x,4),4,8^)
    inner, innert = fv([G(["1"]), G(["2"]), None, G(["4"])])
    c9, t9 = tower(7, E7, lambda t: t,
                   [G(["1"]), G(["2"]), G(["3*1"]), (inner, innert),
                    G(["4"]), G(["8^"])])
    out.append(("S9", (c9, t9)))
    # S10 = 5^(3(3(1,4, )), , , ) + 7^(six sets)
    f10, f10t = fv([a3314(A, keep, sub4), None, None, None])
    x1 = a33_xx1(A) if keep is None else ([], [])
    s4c, s4t = fv([join(x1, G(["9*2"])), G(["8^"]), None,
                   G(["3*1", "9*4"])])
    x8 = (a33_xx8(A) if keep is None or keep("8") else ([], []))
    if sub4 and x8[0]:
        x8 = (x2([ext((1, 3), 3, 0, 1)], 1, 2), [])   # 8^ -> 2
    s6c, s6t = fv([x8,
                   G(["3*2"]), G(["3*4"]), G(["3*8^", "9*8^"])])
    c5a, t5a = a33_124(A, keep, sub4)
    c5b, t5b = eightyone_14(A, keep, sub4)
    c5c, t5c = fv([G(["27^*1"]), G(["27^*2"]), G(["27^*4"]),
                   G(["27^*8^"])])
    slot5 = (c5a + c5b + c5c, t5a + t5b + t5c)
    c10, t10 = tower(7, E7, lambda t: t,
                     [G(["3*2", "27*1", "27^*2"]),
                      G(["3*4", "27*4", "27^*8^"]),
                      G(["3*8^"]),
                      (s4c, s4t), slot5, (s6c, s6t)])
    out.append(("S10", (list(f10) + c10, list(f10t) + t10)))
    return out


def join(a, b):
    return (list(a[0]) + list(b[0]), list(a[1]) + list(b[1]))


def sig13(t):
    return {1: 2, 2: 1}.get(t, t)


def emit36():
    A = Atoms((3, 4))
    sets10 = ten_sets(A, sig13)
    # inputs 11/12: modified 11^ copies; keep only 4/8^-dependent atoms
    keep48 = lambda tag: tag in ("4", "8")
    s11 = ten_sets(A, sig13, keep=keep48)
    s12 = ten_sets(A, sig13, keep=keep48, sub4=True, sub8=True)

    def eleven(sets):
        contents = [(cc, tt) for _, (cc, tt) in sets]
        return tower(11, E11, lambda t: t, contents)

    e11c, e11t = eleven(s11)
    e12c, e12t = eleven(s12)

    congs, tails = [], []
    for k in range(1, E13 + 1):
        for t in range(1, 13):
            cell = (t * 13 ** (k - 1) % 13 ** k, 13 ** k)
            if t <= 10:
                cc, tt = sets10[t - 1][1]
            elif t == 11:
                cc, tt = e11c, e11t
            else:
                cc, tt = e12c, e12t
            congs += [crt(r, n, *cell) for (r, n) in cc]
            tails += [crt(r, n, *cell) for (r, n) in tt]
    tails.append((0, 13 ** E13))
    return congs, tails


def main():
    import emitcore
    import emit33
    import emit34
    import emit35
    congs, tails = emit36()
    mods = [n for _, n in congs]
    print(f"sec3.6: {len(congs)} congruences, {len(tails)} placeholders")
    print(f"min modulus: {min(mods)} (require >= 42)")
    from collections import Counter
    dup = [m for m, c in Counter(mods).items() if c > 1]
    print(f"dups within sec3.6: {len(dup)}", dup[:12] if dup else "")
    prev = emitcore.emit()
    c33 = emit33.emit()
    c34 = emit34.emit34()[0]
    c35, t35 = emit35.emit()
    for nm, other in (("skeleton", prev), ("sec3.3", c33),
                      ("sec3.4", c34), ("sec3.5", c35)):
        print(f"overlap w/ {nm}:",
              len(set(mods) & set(n for _, n in other)))

    # two-window census on branch B', with secs 3.1-3.5 in base:
    # (a) first-ten 13^ inputs (13-factor, no 11 needed);
    # (b) inputs 11/12 (11*13-factor, reduced 2/3/7 exponents).
    for label, N, digits in (
            ("first-ten", 2 ** 6 * 3 ** 6 * 5 ** 2 * 7 ** 2 * 13,
             range(1, 11)),
            ("inputs 11/12", 2 ** 5 * 3 ** 5 * 5 ** 2 * 7 * 11 * 13,
             (11, 12))):
        base = np.zeros(N, dtype=bool)
        for r, n in prev + c33 + list(c34) + c35 + t35:
            if N % n == 0:
                base[r % n::n] = True
        idx = np.arange(N)
        Bmask = ((idx % 12 == 7) | ((idx % 4 == 3) & (idx % 9 == 3)))
        dmask = np.isin(idx % 13, list(digits))
        cov = base.copy()
        dropped = 0.0
        for r, n in congs + tails:
            if N % n == 0:
                cov[r % n::n] = True
            else:
                dropped += 1.0 / n
        m = Bmask & dmask
        unc = idx[m & ~cov]
        print(f"census {label} (window {N}): uncovered {unc.size} / "
              f"{int(m.sum())} (dropped measure {dropped:.2e})")
        if unc.size:
            print("   by (13digit, mod45):",
                  sorted(Counter(zip(unc % 13, unc % 45)).items())[:12])


if __name__ == "__main__":
    main()
