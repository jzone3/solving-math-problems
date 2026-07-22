#!/usr/bin/env python3
"""Reciprocal-sum feasibility for a config: sum_{d | N, d >= T} 1/d must
exceed 1 (necessary; each distinct modulus d covers density exactly 1/d).
Also prints per-prime marginal contributions."""
import sys
from fractions import Fraction


def parse(levels):
    out = []
    for tok in levels.split(","):
        if "^" in tok:
            p, e = tok.split("^")
            out.append((int(p), int(e)))
        else:
            out.append((int(tok), 1))
    return out


def slack(levels, T):
    divs = [1]
    for p, e in levels:
        divs = [d * p**k for d in divs for k in range(e + 1)]
    s = sum(Fraction(1, d) for d in divs if d >= T)
    return float(s), len([d for d in divs if d >= T])


if __name__ == "__main__":
    T = int(sys.argv[1])
    lv = parse(sys.argv[2])
    s, n = slack(lv, T)
    print(f"T={T} usable divisors={n} reciprocal sum={s:.4f} (need > 1)")
