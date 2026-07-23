#!/usr/bin/env python3
"""Thm-2.4 + fold sweep using the C exhaust (cw_fold). See sweep49.py."""
import sys
import json
import re
import subprocess

TMO = 240


def norbits(t, m):
    seen, c = set(), 0
    for x in range(m):
        if x in seen:
            continue
        y = x
        while y not in seen:
            seen.add(y)
            y = y * t % m
        c += 1
    return c


def prime_power_root(k):
    for p in (2, 3, 5, 7, 11, 13):
        e, kk = 0, k
        while kk % p == 0:
            kk //= p
            e += 1
        if kk == 1 and e % 2 == 0:
            return p
    return None


ks = [int(x) for x in sys.argv[1:]] or [49, 121, 169]
s = re.sub(r",\s*}", "}", open("cwm.json").read())
db = json.loads(s)
cells = sorted((int(mm.group(1)), int(mm.group(2)) ** 2)
               for key, v in db.items()
               if (mm := re.match(r"CW\((\d+),(\d+)\)", key))
               and v.get("status") == "Open" and int(mm.group(2)) ** 2 in ks)
import os
done = set()
resume = os.environ.get("RESUME")
if resume and os.path.exists(resume):
    for line in open(resume):
        mm = re.match(r"CW\((\d+),(\d+)\):", line)
        if mm:
            done.add((int(mm.group(1)), int(mm.group(2))))
print(f"{len(cells)} open cells, k in {ks}; resuming past {len(done)}",
      flush=True)
for n, k in cells:
    if (n, k) in done:
        continue
    p = prime_power_root(k)
    if p is None or n % p == 0:
        print(f"CW({n},{k}): mult thm n/a", flush=True)
        continue
    import math
    folds = [(x, n // x) for x in range(2, n)
             if n % x == 0 and n // x <= 8]
    folds.sort(key=lambda md: norbits(p, md[0]) * math.log(2 * md[1] + 1))
    info, settled = [], False
    for m, d in folds:
        r = subprocess.run(["./cw_fold", str(m), str(d), str(k), str(p),
                            str(TMO)], capture_output=True, text=True)
        out = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "ERR"
        info.append(f"m={m},d={d}:{out}")
        if out == "COUNT 0":
            print(f"CW({n},{k}): NONEXISTENT (fold m={m}, d={d}); {info}",
                  flush=True)
            settled = True
            break
    if not settled:
        print(f"CW({n},{k}): inconclusive; {info}", flush=True)
