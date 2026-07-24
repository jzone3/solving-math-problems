#!/usr/bin/env python3
"""
P15 V4 phase 45: fresh-modulus patch assignment for every open
placeholder cell.

A placeholder cell (r, n) is the arithmetic progression r mod n.  A
patch is a finite set of congruences with moduli n*d (d > 1) covering
the cell completely: choosing residues a_j mod d_j that cover Z gives
congruences r + a_j*n (mod d_j*n).  Overlap with existing congruences
is harmless (covering systems may overlap); the ONLY constraint is
global modulus freshness -- each n*d_j must be distinct from all
12.33M emitted moduli and from every other patch modulus.

For each cell we greedily build a distinct-modulus cover of Z/L
(L = 10080 = 2^5*3^2*5*7) from the divisors d of L with n*d free,
choosing at each step the residue class covering the most uncovered
points.  Cells are processed in decreasing n (rarer collisions last).
"""
from globalcheck import all_sections

L = 10080


def cover_scales(free_ds):
    """Greedy distinct-modulus cover of Z/L using progressions a mod d,
    d from free_ds.  Returns list of (a, d) or None."""
    unc = set(range(L))
    out = []
    ds = sorted(free_ds)
    for d in ds:
        if not unc:
            break
        # best residue class mod d
        cnt = {}
        for x in unc:
            a = x % d
            cnt[a] = cnt.get(a, 0) + 1
        a, c = max(cnt.items(), key=lambda kv: kv[1])
        out.append((a, d))
        unc -= set(range(a, L, d))
    return out if not unc else None


def main():
    secs = all_sections()
    used = set()
    for name, cc, tt in secs:
        for r, n in cc:
            used.add(n)
    tails = []
    for name, cc, tt in secs:
        for r, n in tt:
            tails.append((name, r, n))
    divs = sorted(d for d in range(2, L + 1) if L % d == 0)
    print(f"used moduli: {len(used)}, cells: {len(tails)}, "
          f"candidate scales: {len(divs)}")

    tails.sort(key=lambda t: -t[2])
    patches = []
    fail = 0
    for name, r, n in tails:
        free = [d for d in divs if n * d not in used]
        sol = cover_scales(free)
        if sol is None:
            fail += 1
            continue
        for a, d in sol:
            m = n * d
            used.add(m)
            patches.append(((r + a * n) % m, m))
    print(f"cells patched: {len(tails) - fail}/{len(tails)}, "
          f"failed: {fail}")
    print(f"patch congruences: {len(patches)}")
    mods = [m for _, m in patches]
    assert len(set(mods)) == len(mods)
    print(f"patch moduli distinct: OK; min patch modulus: {min(mods)}")
    import json
    with open("patches45.json", "w") as f:
        json.dump(patches, f)
    print("wrote patches45.json")


if __name__ == "__main__":
    main()
