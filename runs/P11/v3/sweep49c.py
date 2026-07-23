#!/usr/bin/env python3
"""Thm-2.4 + fold sweep using the C exhaust (cw_fold). See sweep49.py."""
import sys
import json
import re
import subprocess

TMO = 600


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
print(f"{len(cells)} open cells, k in {ks}", flush=True)
for n, k in cells:
    p = prime_power_root(k)
    if p is None or n % p == 0:
        print(f"CW({n},{k}): mult thm n/a", flush=True)
        continue
    info, settled = [], False
    for m in sorted((x for x in range(2, n) if n % x == 0), reverse=True):
        d = n // m
        if d > 8 or m > 1000:
            continue
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
