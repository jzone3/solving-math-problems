"""
Exhaustive check of Woodall's conjecture over ALL simple DAGs on 8 labeled
vertices (fixed topological order covers all isomorphism classes), using
literature-based pruning:

- tau >= 3 requires every source (indeg 0) to have outdeg >= 3 and every sink
  (outdeg 0) indeg >= 3; no isolated vertices (else tau = 0).
- For tau = 3 (unweighted): Abdi-Cornuejols-Zlatin 2023 Thm (iii) + (i)(ii)
  prove packing whenever rho(3,D) <= 3; by arc-reversal symmetry also whenever
  rho(3,reverse(D)) <= 3. So a tau=3 counterexample needs
  sum_v((outdeg-indeg) mod 3) >= 12 AND sum_v((indeg-outdeg) mod 3) >= 12.
- For tau = t >= 4: ACZ (i)(ii) prove packing whenever rho(t,D) <= 2 (and
  reverse); a counterexample needs sum_v((outdeg-indeg) mod t) >= 3t (both
  directions). Also every source needs outdeg >= t, sink indeg >= t.

Survivors of the vectorized degree/rho prune get exact tau + SAT packing check.

Run: python3 exhaustive8.py [start_chunk end_chunk]  (chunks of 2^22 masks, 64 total)
"""

import sys
import time
import numpy as np

from harness import tau, has_k_disjoint_dijoins

N = 8
PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
P = len(PAIRS)                    # 28
TOTAL = 1 << P
CHUNK = 1 << 22
POP = np.array([bin(x).count('1') for x in range(1 << 16)], dtype=np.int8)

# bitmask (over the 28 pair-bits) of pairs with tail v / head v
OUTBITS = np.zeros(N, dtype=np.uint32)
INBITS = np.zeros(N, dtype=np.uint32)
for idx, (u, v) in enumerate(PAIRS):
    OUTBITS[u] |= (1 << idx)
    INBITS[v] |= (1 << idx)


def popcount32(arr):
    return (POP[arr & 0xFFFF] + POP[(arr >> 16) & 0xFFFF]).astype(np.int8)


def prune_chunk(masks):
    """Return boolean array: True = potential counterexample, needs full check."""
    outd = np.empty((N, len(masks)), dtype=np.int8)
    ind = np.empty((N, len(masks)), dtype=np.int8)
    for v in range(N):
        outd[v] = popcount32(masks & OUTBITS[v])
        ind[v] = popcount32(masks & INBITS[v])
    deg = outd + ind
    # no isolated vertices
    alive = (deg > 0).all(axis=0)
    # tau=3 stream degree conditions
    src_ok3 = ((ind != 0) | (outd >= 3)).all(axis=0)
    snk_ok3 = ((outd != 0) | (ind >= 3)).all(axis=0)
    exc = (outd.astype(np.int16) - ind.astype(np.int16))
    rho3 = (np.mod(exc, 3)).sum(axis=0)
    rho3r = (np.mod(-exc, 3)).sum(axis=0)
    cand3 = alive & src_ok3 & snk_ok3 & (rho3 >= 12) & (rho3r >= 12)
    # tau>=4 stream (t = 4..7): source outdeg >= t etc., rho(t) >= 3t
    cand_hi = np.zeros(len(masks), dtype=bool)
    for t in range(4, 8):
        src_ok = ((ind != 0) | (outd >= t)).all(axis=0)
        snk_ok = ((outd != 0) | (ind >= t)).all(axis=0)
        rt = (np.mod(exc, t)).sum(axis=0)
        rtr = (np.mod(-exc, t)).sum(axis=0)
        cand_hi |= alive & src_ok & snk_ok & (rt >= 3 * t) & (rtr >= 3 * t)
    return cand3 | cand_hi


def full_check(mask):
    arcs = [PAIRS[i] for i in range(P) if (mask >> i) & 1]
    t = tau(N, arcs)
    if t is None or t < 3:
        return None
    if has_k_disjoint_dijoins(N, arcs, t):
        return None
    return (t, arcs)


if __name__ == "__main__":
    nchunks = TOTAL // CHUNK
    c0, c1 = 0, nchunks
    if len(sys.argv) > 2:
        c0, c1 = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    survivors = 0
    checked_full = 0
    nonpack = 0
    for c in range(c0, c1):
        base = c * CHUNK
        masks = np.arange(base, base + CHUNK, dtype=np.uint32)
        cand = prune_chunk(masks)
        idxs = np.nonzero(cand)[0]
        survivors += len(idxs)
        for i in idxs:
            r = full_check(int(masks[i]))
            checked_full += 1
            if r is not None:
                nonpack += 1
                print("NONPACKING:", r, flush=True)
        print(f"chunk {c+1}/{nchunks} survivors={survivors} "
              f"full_checked={checked_full} nonpack={nonpack} "
              f"t={time.time()-t0:.0f}s", flush=True)
    print(f"DONE chunks[{c0},{c1}) survivors={survivors} nonpacking={nonpack} "
          f"wall={time.time()-t0:.0f}s", flush=True)
