#!/usr/bin/env python3
"""Systematic Thm-2.4 + fold sweep over DB-open cells CW(n, k=p^2r), p prime,
gcd(n,k)=1.

For each such open cell and each divisor m|n (1 < m < n), the fold of the
multiplier-fixed translate mod m is a <p>-fixed integer vector on Z_m with
entries |b| <= n/m, norm k, flat autocorrelation. If for SOME m that set is
EMPTY, no CW(n,k) exists. Node-capped DFS keeps each check cheap; caps make
"nonzero/cap" results inconclusive but zeros are exact.
"""
import sys
import json
import re
from math import gcd

sys.path.insert(0, ".")
from icw_enum import orbits_of


def fixed_count(m, d, k, t, cap=3 * 10 ** 7):
    orbs = orbits_of(t, m)
    sizes = [len(o) for o in orbs]
    no = len(orbs)
    suffix = [0] * (no + 1)
    for i in range(no - 1, -1, -1):
        suffix[i] = suffix[i + 1] + d * d * sizes[i]
    cs = [0] * no
    nodes = [0]
    hits = [0]

    def flat(w):
        return all(sum(w[i] * w[(i + s) % m] for i in range(m)) == 0
                   for s in range(1, m))

    def dfs(pos, norm):
        nodes[0] += 1
        if nodes[0] > cap:
            raise TimeoutError
        if norm > k or norm + suffix[pos] < k:
            return
        if pos == no:
            if norm == k:
                w = [0] * m
                for c, o in zip(cs, orbs):
                    for x in o:
                        w[x] = c
                if flat(w):
                    hits[0] += 1
                    raise StopIteration  # only need existence
            return
        for c in range(-d, d + 1):
            cs[pos] = c
            dfs(pos + 1, norm + c * c * sizes[pos])
        cs[pos] = 0

    try:
        dfs(0, 0)
    except StopIteration:
        return ">0", nodes[0]
    except TimeoutError:
        return "CAP", nodes[0]
    return 0, nodes[0]


def prime_power_root(k):
    for p in (2, 3, 5, 7, 11, 13):
        e = 0
        kk = k
        while kk % p == 0:
            kk //= p
            e += 1
        if kk == 1 and e % 2 == 0:
            return p
    return None


if __name__ == "__main__":
    ks = [int(x) for x in sys.argv[1:]] or [49, 121, 169]
    s = open("cwm.json").read()
    s = re.sub(r",\s*}", "}", s)
    db = json.loads(s)
    open_cells = []
    for key, v in db.items():
        mm = re.match(r"CW\((\d+),(\d+)\)", key)
        n_, s_ = int(mm.group(1)), int(mm.group(2))
        if v.get("status") == "Open" and s_ * s_ in ks:
            open_cells.append((n_, s_ * s_))
    open_cells.sort()
    print(f"{len(open_cells)} open cells with k in {ks}")
    for n, k in open_cells:
        p = prime_power_root(k)
        if p is None or n % p == 0:
            print(f"CW({n},{k}): multiplier thm not applicable (p|n)")
            continue
        divs = sorted((m for m in range(2, n) if n % m == 0), reverse=True)
        settled = False
        info = []
        for m in divs:
            d = n // m
            if d > 8:  # coefficient range too large -> explosion
                break
            try:
                r, nodes = fixed_count(m, d, k, p)
            except Exception as e:
                info.append(f"m={m}:ERR{e}")
                continue
            info.append(f"m={m},d={d}:{r}({nodes}n)")
            if r == 0:
                print(f"CW({n},{k}): NONEXISTENT — no <"
                      f"{p}>-fixed fold at m={m} (d={d}); {info}", flush=True)
                settled = True
                break
        if not settled:
            print(f"CW({n},{k}): inconclusive; {info}", flush=True)
