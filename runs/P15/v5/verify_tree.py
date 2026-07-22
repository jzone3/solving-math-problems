"""CRT-structured covering verifier (no lcm materialization).

Witness JSON: {"L":.., "congruences":[[r,d],..]}.
Checks: distinct moduli, all >= L, and that the classes cover Z, by DFS on cells:
a cell (a, M) is covered iff some congruence (r,d) with d | M has a = r (mod d),
else split the cell by a prime factor p of some modulus with more p-adic depth
than M and recurse into all p children.  Terminates because moduli are finite.
Prints PASS or FAIL.
"""
import json
import sys
from collections import defaultdict


def factorize(n):
    f = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def main(path):
    w = json.load(open(path))
    cong = [(int(r) % int(d), int(d)) for r, d in w["congruences"]]
    L = int(w["L"])
    mods = [d for _, d in cong]
    if len(set(mods)) != len(mods):
        print("FAIL: repeated modulus"); sys.exit(1)
    if min(mods) < L or min(mods) <= 1:
        print(f"FAIL: min modulus {min(mods)} < L={L}"); sys.exit(1)

    facs = {d: factorize(d) for d in mods}
    maxexp = defaultdict(int)
    for d in mods:
        for p, e in facs[d].items():
            maxexp[p] = max(maxexp[p], e)
    primes = sorted(maxexp)

    import sys as _s
    _s.setrecursionlimit(100000)
    stack = [(0, 1, {p: 0 for p in primes})]
    checked = 0
    while stack:
        a, M, exp = stack.pop()
        # is cell covered by a single congruence?
        hit = False
        for r, d in cong:
            if M % d == 0 and a % d == r:
                hit = True
                break
        if hit:
            checked += 1
            continue
        # find a prime to split on: some modulus d that is "compatible" with the
        # cell (d's projection to current depths matches a) and needs more depth
        split_p = None
        for r, d in cong:
            g = 1
            ok = True
            need = None
            for p, e in facs[d].items():
                ce = exp[p]
                if e > ce:
                    need = p
                else:
                    g *= p ** e
            if need is None:
                continue
            if a % g == r % g:
                split_p = need
                break
        if split_p is None:
            print(f"FAIL: uncovered cell {a} mod {M}")
            sys.exit(1)
        p = split_p
        for i in range(p):
            e2 = dict(exp)
            e2[p] += 1
            stack.append((a + i * M, M * p, e2))
    print(f"PASS: covering system, {len(cong)} congruences, min modulus "
          f"{min(mods)}, cells checked {checked}")


if __name__ == "__main__":
    main(sys.argv[1])
