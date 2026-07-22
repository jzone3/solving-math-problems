#!/usr/bin/env python3
"""Extract known CWM existence table + witness sets from cwm.json (dmgordo repo).
Note: repo keys are CW(n,s) with weight k = s^2. Tolerates trailing commas."""
import json
import re


def load(path="cwm.json"):
    s = open(path).read()
    s = re.sub(r",\s*}", "}", s)
    return json.loads(s)


def table(d):
    """Return dict (n, k) -> {'status':..., 'sets':[(P,N),...]}"""
    out = {}
    for key, v in d.items():
        n, s = map(int, re.findall(r"\d+", key))
        out[(n, s * s)] = {
            "status": v.get("status"),
            "comment": v.get("comment", ""),
            "sets": [tuple(x) for x in v.get("sets", [])],
        }
    return out


if __name__ == "__main__":
    d = table(load())
    for kk in (36, 49, 81):
        yes = sorted(n for (n, k), v in d.items() if k == kk and v["status"] in ("Yes", "All"))
        opn = sorted(n for (n, k), v in d.items() if k == kk and v["status"] == "Open")
        print(f"k={kk} YES n: {yes}")
        print(f"k={kk} OPEN n (first 20): {opn[:20]}")
    # base material: all Yes/All cells with witnesses, small k
    wit = sorted(((n, k) for (n, k), v in d.items() if v["sets"]), key=lambda t: (t[1], t[0]))
    print("cells with explicit witnesses:", len(wit))
    for kk in (4, 9, 16, 25, 36, 49, 64, 81, 100):
        print(f"  k={kk}:", [n for (n, k) in wit if k == kk][:15])
