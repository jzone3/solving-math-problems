#!/usr/bin/env python3
"""
P15 V4 phase 41: consolidated GLOBAL check over the full sec 3.1-3.20
residue replica: (a) global modulus distinctness across all ~12.3M
congruences at once (not just pairwise section checks), (b) global
minimum modulus, (c) a joint census over a large exact window with
dropped-measure accounting.
"""
import numpy as np
from collections import Counter


def all_sections():
    import emitcore, emit33, emit34, emit35, emit36, emit37, emit38
    import emit39, emit310, emit311, emit312, emit313, emit314
    import emit315, emit316, emit317, emit318, emit319, emit320
    secs = [("skeleton", emitcore.emit(), []),
            ("sec3.3", emit33.emit(), [])]
    for name, mod in [("sec3.4", emit34.emit34), ("sec3.5", emit35.emit),
                      ("sec3.6", emit36.emit36), ("sec3.7", emit37.emit37),
                      ("sec3.8", emit38.emit38), ("sec3.9", emit39.emit39),
                      ("sec3.10", emit310.emit310),
                      ("sec3.11", emit311.emit311),
                      ("sec3.12", emit312.emit312),
                      ("sec3.13", emit313.emit313),
                      ("sec3.14", emit314.emit314),
                      ("sec3.15", emit315.emit315),
                      ("sec3.16", emit316.emit316),
                      ("sec3.17", emit317.emit317),
                      ("sec3.18", emit318.emit318),
                      ("sec3.19", emit319.emit319),
                      ("sec3.20", emit320.emit320)]:
        cc, tt = mod()
        secs.append((name, cc, tt))
    return secs


def main():
    secs = all_sections()
    allc, allt = [], []
    for name, cc, tt in secs:
        print(f"{name}: {len(cc)} congruences, {len(tt)} placeholders")
        allc += cc
        allt += tt
    mods = [n for _, n in allc]
    print(f"\nTOTAL: {len(allc)} congruences, {len(allt)} placeholders")
    print(f"global min modulus: {min(mods)}")
    cnt = Counter(mods)
    dups = {m: c for m, c in cnt.items() if c > 1}
    print(f"GLOBAL duplicate moduli values: {len(dups)}")
    if dups:
        worst = sorted(dups.items(), key=lambda kv: -kv[1])[:20]
        print("  worst:", worst)
    small = sorted(mods)[:10]
    print(f"10 smallest moduli: {small}")
    # joint census
    N = 2 ** 7 * 3 ** 4 * 5 ** 2 * 7 ** 2
    print(f"\njoint census window: {N}")
    cov = np.zeros(N, dtype=bool)
    dropped = 0.0
    for r, n in allc + allt:
        if N % n == 0:
            cov[r % n::n] = True
        else:
            dropped += 1.0 / n
    unc = int((~cov).sum())
    print(f"uncovered in window: {unc}/{N} "
          f"({unc/N:.4f}; dropped measure {dropped:.3e})")


if __name__ == "__main__":
    main()
