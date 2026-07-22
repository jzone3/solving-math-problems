#!/usr/bin/env python3
"""Independent (second implementation) exhaust of small ICW_d(m,k) orbit
spaces, to re-verify the zero-solution results from exhaust_cw.c:

  ICW3(44,81) fixed by 3  (core of AGZ Prop 4.2, kills CW(132,81))
  ICW2(91,64) fixed by 2  (core of AGZ Prop 5.1, kills CW(182,64))

Different code path: itertools product over orbit coefficient vectors in
lexicographic order with numpy full-vector autocorrelation via FFT check
at candidate leaves; no shared code with the C engine beyond the problem
definition.
"""
import sys
import numpy as np
from itertools import product


def orbits(m, t):
    seen, out = set(), []
    for x in range(m):
        if x in seen:
            continue
        orb, y = [], x
        while y not in seen:
            seen.add(y)
            orb.append(y)
            y = y * t % m
        out.append(orb)
    return out


def exhaust(m, s, d, t):
    k = s * s
    orbs = orbits(m, t)
    sizes = [len(o) for o in orbs]
    u = len(orbs)
    d = min(d, s)
    count = 0
    # depth-first via explicit product with early moment filtering done
    # by suffix bounds
    suffix = [0] * (u + 1)
    for i in range(u - 1, -1, -1):
        suffix[i] = suffix[i + 1] + d * sizes[i]

    sols = []

    def rec(i, vec, rsum, rsq):
        nonlocal count
        if rsq > k or abs(s - rsum) > suffix[i]:
            return
        if i == u:
            if rsum == s and rsq == k:
                a = np.zeros(m, dtype=np.int64)
                for c, orb in zip(vec, orbs):
                    for x in orb:
                        a[x] += c
                fa = np.fft.rfft(a)
                power = np.abs(fa) ** 2
                if np.allclose(power, k, atol=1e-6):
                    sols.append(list(a))
            return
        for c in range(-d, d + 1):
            vec.append(c)
            rec(i + 1, vec, rsum + c * sizes[i], rsq + c * c * sizes[i])
            vec.pop()

    rec(0, [], 0, 0)
    return sols


def main():
    for (m, s, d, t) in [(44, 9, 3, 3), (91, 8, 2, 2)]:
        sols = exhaust(m, s, d, t)
        print(f"ICW{d}({m},{s*s}) fixed by {t}: {len(sols)} solutions")
    print("done")


if __name__ == "__main__":
    main()
