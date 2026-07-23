"""Rebuild zscan.c candidates (DBG/CAND lines) in Python and verify with core.py.

For DBG lines: cross-check C's tau3 flag exactly, and check C packed=1 implies SAT
packable (WalkSAT success is a certificate direction; packed=0 in DBG just means the
heuristic failed). For CAND lines (dumped unresolved candidates): decide exactly with
SAT; any UNSAT is a tau=3 Woodall counterexample witness.
"""
import sys

from bip import all_min_dicuts, pack3


def rebuild(f, owners, sdigits):
    k = (16 - f) // 3
    S = {}
    idx = 0
    for a in range(4):
        for b in range(k):
            S[a, b] = int(sdigits[idx]); idx += 1
    nbrs = [None] * 12
    for a in range(4):
        for i in range(3):
            nb = []
            for b in range(k):
                for o in range(3):
                    if S[a, b] >> o & 1:
                        nb.append(3 * b + (o + i) % 3)
            for j, ow in enumerate(owners):
                if ow == a:
                    nb.append(3 * k + j)
            nbrs[3 * a + i] = tuple(sorted(nb))
    return nbrs


def main():
    n = dbg_mism = dumped_unsat = 0
    for line in sys.stdin:
        parts = line.split()
        if parts and parts[0] in ("DBG", "CAND") or (len(parts) > 2 and parts[2].startswith("CAND")):
            d = dict(p.split("=") for p in parts if "=" in p)
            f = int(d["f"])
            owners = [int(c) for c in d["owners"]]
            nbrs = rebuild(f, owners, d["S"])
            assert sum(len(nb) for nb in nbrs) == 48
            tau, md = all_min_dicuts(nbrs, 16)
            t3 = 1 if tau == 3 else 0
            if parts[0] == "DBG":
                ct3, cpk = int(d["tau3"]), int(d["packed"])
                if ct3 != t3:
                    dbg_mism += 1
                    print("TAU MISMATCH:", line.strip())
                elif t3:
                    packable = pack3(nbrs, md)
                    if cpk == 1 and not packable:
                        dbg_mism += 1
                        print("PACK MISMATCH (C packed but SAT says no):", line.strip())
            else:
                if t3 and not pack3(nbrs, md):
                    dumped_unsat += 1
                    print("!!! COUNTEREXAMPLE:", line.strip())
            n += 1
    print(f"verified={n} mismatches={dbg_mism} counterexamples={dumped_unsat}")


if __name__ == "__main__":
    main()
