#!/usr/bin/env python3
"""Diversify g127.wcnf for NuWLS-c (its -rnd-seed flag does not change the
local-search trajectory): apply a random variable renaming + polarity flip +
clause shuffle per copy. All are satisfiability/cost-preserving bijections."""
import random

lines = open("g127.wcnf").read().strip().split("\n")
hdr = lines[0]
cls = lines[1:]
hard = [c for c in cls if c.startswith("100000 ")]
soft = [c for c in cls if not c.startswith("100000 ")]
for i in range(1, 7):
    random.seed(i * 104729)
    perm = list(range(1, 2668))
    random.shuffle(perm)
    pol = [random.random() < 0.5 for _ in range(2668)]
    def remap(tok):
        v = int(tok)
        s = -1 if v < 0 else 1
        av = abs(v)
        nv = perm[av - 1]
        if pol[av]:
            s = -s
        return s * nv
    out = []
    for c in soft + hard:
        parts = c.split()
        w = parts[0]
        lits = [remap(t) for t in parts[1:-1]]
        out.append(w + " " + " ".join(map(str, lits)) + " 0")
    random.shuffle(out)
    with open(f"g127_shuf{i}.wcnf", "w") as f:
        f.write(hdr + "\n")
        f.write("\n".join(out) + "\n")
    # save inverse maps so a good assignment can be pulled back
    with open(f"g127_shuf{i}.map", "w") as f:
        for av in range(1, 2668):
            f.write(f"{av} {perm[av-1]} {1 if pol[av] else 0}\n")
print("done")
