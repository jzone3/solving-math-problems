"""Third independent verifier: exact cell subtraction, fat classes first.

Uncovered set starts as Z = {(0 mod 1)} and each congruence class (r, m),
processed in ascending modulus order, is subtracted exactly: any intersecting
cell (a mod M) is split along lcm(M, m) and the covered child removed.
PASS iff no cells remain.  Handles witnesses whose lcm is astronomically
large (e.g. Engine E/F outputs), where the flat sweep and naive CRT-tree
verifiers are infeasible.
"""
import json
import sys
from math import gcd


def main(path):
    w = json.load(open(path))
    cong = [(int(r), int(m)) for r, m in w["congruences"]]
    mods = [m for _, m in cong]
    assert len(set(mods)) == len(mods), "duplicate moduli"
    assert all(m > 1 for m in mods), "modulus 1"
    cong.sort(key=lambda t: t[1])
    cells = {(0, 1)}
    peak = 0
    for r, m in cong:
        new = set()
        for (a, M) in cells:
            g = gcd(M, m)
            if a % g != r % g:
                new.add((a, M))
                continue
            lcm = M // g * m
            k = lcm // M
            # split cell into k children mod lcm; remove the covered one
            inv_target = None
            for i in range(k):
                c = a + i * M
                if c % m == r:
                    inv_target = c % lcm
                    break
            assert inv_target is not None
            for i in range(k):
                c = (a + i * M) % lcm
                if c != inv_target:
                    new.add((c, lcm))
        cells = new
        peak = max(peak, len(cells))
        if len(cells) > 50_000_000:
            print("FAIL: cell blowup")
            sys.exit(1)
    if cells:
        print(f"FAIL: {len(cells)} uncovered cells remain, e.g. {min(cells)}")
        sys.exit(1)
    print(f"PASS: covering system, {len(cong)} congruences, min modulus "
          f"{min(mods)}, peak cells {peak}")


if __name__ == "__main__":
    main(sys.argv[1])
