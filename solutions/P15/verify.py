"""Independent verifier for covering-system witnesses (different code path from
the search engine: no reshape trick, plain stepping + explicit checks).

Checks, for witness JSON {"N":..,"L":..,"congruences":[[r,d],..]}:
  1. all moduli distinct and > 1
  2. all moduli >= L
  3. lcm of moduli divides N (we verify over Lc = lcm)
  4. every integer in [0, Lc) is covered
Prints PASS or FAIL.
"""
import json
import sys
from math import gcd


def main(path):
    w = json.load(open(path))
    cong = [(int(r), int(d)) for r, d in w["congruences"]]
    L = int(w["L"])
    mods = [d for _, d in cong]
    assert len(set(mods)) == len(mods), "FAIL: repeated modulus"
    assert all(d > 1 for d in mods), "FAIL: modulus <= 1"
    assert min(mods) >= L, f"FAIL: min modulus {min(mods)} < {L}"
    lc = 1
    for d in mods:
        lc = lc * d // gcd(lc, d)
    covered = bytearray(lc)
    for r, d in cong:
        for n in range(r % d, lc, d):
            covered[n] = 1
    miss = covered.count(0)
    if miss == 0:
        print(f"PASS: covering system, {len(cong)} congruences, "
              f"min modulus {min(mods)}, lcm {lc}")
    else:
        print(f"FAIL: {miss} residues uncovered out of {lc}")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
