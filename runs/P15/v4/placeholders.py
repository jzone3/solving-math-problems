#!/usr/bin/env python3
"""
P15 V4 phase 43: classify the placeholder cells of the full
duplicate-free emission.

Each placeholder is a residue cell (r, n) whose interior is not
covered by its own set's congruences.  For each, we test exactly
(arithmetic-progression intersection, no sampling) whether the first
K points of the cell are covered by the OTHER emitted congruences of
modulus <= MODCAP (larger moduli cannot help systematically: they
cover density <= 1/MODCAP of the cell).

  COVERED -- cell's tested stretch fully covered by other emitted
             congruences: the cross-section x-slot bookkeeping works
             (or the tail is absorbed), no new assignment needed.
  OPEN    -- residual points remain: a genuine coverage gap needing
             a new assignment (deeper tower levels, unfilled x).
"""
import numpy as np
from math import gcd
from globalcheck import all_sections

MODCAP = 2 * 10 ** 6
K = 4096


def main():
    secs = all_sections()
    allc = []
    for name, cc, tt in secs:
        allc += cc
    R = np.array([r for r, n in allc if n <= MODCAP], dtype=np.int64)
    N = np.array([n for r, n in allc if n <= MODCAP], dtype=np.int64)
    print(f"congruences: {len(allc)}, with modulus<= {MODCAP}: {len(N)}")
    tot_cov = tot_open = 0
    fracs = []
    for name, cc, tt in secs:
        n_cov = n_open = 0
        worst = None
        for r, n in tt:
            G = np.gcd(N, n)
            ok = (r - R) % G == 0
            idx = np.nonzero(ok)[0]
            cov = np.zeros(K, dtype=bool)
            for j in idx:
                n2, r2, g = int(N[j]), int(R[j]), int(G[j])
                n2g = n2 // g
                if n2g == 1:
                    cov[:] = True
                    break
                inv = pow((n // g) % n2g, -1, n2g)
                i0 = ((r2 - r) // g * inv) % n2g
                if i0 < K:
                    cov[i0::n2g] = True
            unc = int((~cov).sum())
            fracs.append(unc / K)
            if unc == 0:
                n_cov += 1
            else:
                n_open += 1
                if worst is None or unc > worst[0]:
                    worst = (unc, r, n)
        tot_cov += n_cov
        tot_open += n_open
        w = f" worst={worst}" if worst else ""
        print(f"{name}: placeholders={len(tt)} covered={n_cov} "
              f"open={n_open}{w}")
    print(f"\nTOTAL: covered={tot_cov} open={tot_open}")
    f = np.array(fracs)
    print("residual-fraction histogram over placeholders:")
    for lo, hi in [(0, 0.0001), (0.0001, 0.01), (0.01, 0.05),
                   (0.05, 0.1), (0.1, 0.25), (0.25, 1.01)]:
        cnt = int(((f >= lo) & (f < hi)).sum())
        print(f"  [{lo:.4f},{hi:.2f}): {cnt}")
    print(f"  mean={f.mean():.4f} median={np.median(f):.4f} "
          f"max={f.max():.4f}")


if __name__ == "__main__":
    main()
