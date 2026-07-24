#!/usr/bin/env python3
"""
P15 V4 phase 19 (v2, canonical): faithful residue-level emission of
Owens sec. 3.3 (the prime 5) onto the even-branch holes 2(4), 4(8),
8(16), 16(32).  See NOTES.md secs. 34-35.

v2: all towers/splits now use CANONICAL absolute p-adic digits
(canon.ext), required for cross-section "x" bookkeeping (phase 20).
"""
from canon import crt, ext, isect

D2, D3, D5 = 9, 4, 3
N = 2 ** D2 * 3 ** D3 * 5 ** D5          # 512*81*125 = 5,184,000

HOLES = {"4": (2, 4), "8": (4, 8), "16": (8, 16), "32": (16, 32)}


def hole_cells(names):
    return [HOLES[s] for s in names]


def two_tower(branch, start_k):
    """q=2 tower inside 2-adic branch (c,m): classes c+2^(k-1) (mod 2^k)."""
    c, m = branch
    return [((c + 2 ** (k - 1)) % 2 ** k, 2 ** k)
            for k in range(start_k, D2 + 1)]


def up4():
    """4^ : covers all of 2 (mod 2): classes 2^(k-1) (mod 2^k), k>=2."""
    return [(2 ** (k - 1), 2 ** k) for k in range(2, D2 + 1)]


def three_up(a, b, ctx, depth=None):
    """3^(a,b) in context ctx: level k puts a on digit 1, b on digit 2
    of the next 3-adic position; canonical absolute digits."""
    out = []
    for k in range(1, (depth or D3) + 1):
        for t, inp in ((1, a), (2, b)):
            cell = ext(ctx, 3, t * 3 ** (k - 1), k)
            if inp is None:
                continue
            if inp == "ONE":
                out.append(cell)
            else:
                out += isect(cell, inp)
    return out


def emit():
    congs = []
    # ---- input 1 (j=0 mod 5): 16+32
    congs += isect((0, 5), hole_cells(["16", "32"]))

    # ---- input 2 (j=1): 3( , , 3^(4+8, ) + 3^(16, 32^|16br) ) + 64^|32br
    ctx = ext((1, 5), 3, 2, 1)      # third class of the 3-split
    congs += three_up(hole_cells(["4", "8"]), None, ctx)
    congs += three_up(hole_cells(["16"]), two_tower(HOLES["16"], 5), ctx)
    congs += isect((1, 5), two_tower(HOLES["32"], 6))

    # ---- input 3 (j=2): 3(64^|32br, 4+8+16+32, 3^(1,2))
    congs += isect(ext((2, 5), 3, 0, 1), two_tower(HOLES["32"], 6))
    congs += isect(ext((2, 5), 3, 1, 1), hole_cells(["4", "8", "16", "32"]))
    congs += three_up("ONE", [(0, 2)], ext((2, 5), 3, 2, 1))

    # ---- input 4 (j=3): blank, then the 125^ patch on the 8 hole:
    # 125^(3^(4,x), 3^(8,x), 3^(16^|8br,x), 3^( ,x))  [x -> sec 3.4]
    # (5^3)^ level k: 5-adic digits (0,0,t) appended, t = 1..4; labels
    # 4/8/16^ are RELATIVE 2-adic sets inside the 8 hole (s: x = 4+8s).
    hr, hn = HOLES["8"]
    rel4 = [(2, 4)]
    rel8 = [(4, 8)]
    rel16up = [(2 ** (k - 1), 2 ** k) for k in range(4, D2 - 2)]
    for k in range(1, D5 + 1):
        for t, rinp in ((1, rel4), (2, rel8), (3, rel16up), (4, None)):
            cell = ext((3, 5), 5, t * 5 ** (k + 1), k + 2)
            if rinp is None:
                continue
            for kk in range(1, D3 + 1):
                c2 = ext(cell, 3, 3 ** (kk - 1), kk)
                for rr, rn in rinp:
                    congs.append(crt((hr + hn * rr) % (hn * rn), hn * rn,
                                     c2[0], c2[1]))

    # ---- input 5 (j=4): 5(2, 4+8+16+32, 3^(1,2),
    #                       3^(32^|16br, 4+8+16) + 64^|32br, 5^(1,2,3^(1,2),4^))
    def in5(i):                      # inner 5-split: second 5-adic digit
        return ext((4, 5), 5, i, 1)
    congs += isect(in5(0), [(0, 2)])                          # "2"
    congs += isect(in5(1), hole_cells(["4", "8", "16", "32"]))
    congs += three_up("ONE", [(0, 2)], in5(2))
    congs += three_up(two_tower(HOLES["16"], 5),
                      hole_cells(["4", "8", "16"]), in5(3))
    congs += isect(in5(3), two_tower(HOLES["32"], 6))
    # 5^(1,2,3^(1,2),4^) on inner class 4: canonical 5-digits
    for k in range(1, D5 + 1):
        for t, inp in ((1, "ONE"), (2, [(0, 2)]), (3, "3UP12"), (4, up4())):
            cell = ext(in5(4), 5, t * 5 ** (k - 1), k)
            if inp == "ONE":
                congs.append(cell)
            elif inp == "3UP12":
                congs += three_up("ONE", [(0, 2)], cell)
            else:
                congs += isect(cell, inp)
    return congs


def main():
    import emitcore
    skel = emitcore.emit()
    congs = emit()
    mods = [n for _, n in congs]
    print(f"sec3.3 emission: {len(congs)} congruences")
    print(f"min modulus: {min(mods)}  (require >= 42)")
    dup = len(mods) - len(set(mods))
    print(f"duplicate moduli within section: {dup}")
    overlap = set(mods) & set(n for _, n in skel)
    print(f"modulus overlap with 2/3 skeleton: {len(overlap)}")

    # coverage census on the four holes (drop moduli outside window)
    cov = bytearray(N)
    dropped = 0.0
    for r, n in congs:
        if N % n:
            dropped += 1 / n
            continue
        cov[r % n::n] = b"\x01" * len(range(r % n, N, n))
    print(f"dropped (beyond-window) measure: {dropped:.2e}")
    for name, (hr, hn) in HOLES.items():
        tot = rem = 0
        rem_by_j = [0] * 5
        for x in range(hr, N, hn):
            tot += 1
            if not cov[x]:
                rem += 1
                rem_by_j[x % 5] += 1
        print(f"hole {name:>2} ({hr} mod {hn}): {rem}/{tot} uncovered; "
              f"by class mod 5: {rem_by_j}")


if __name__ == "__main__":
    main()
