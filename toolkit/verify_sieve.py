#!/usr/bin/env python3
"""Exact segmented residue-sieve verifier for covering systems.

When every modulus divides N, the congruences cover Z if and only if they
cover every residue in [0, N).  This verifier checks that condition directly
with bounded-size NumPy boolean chunks, without constructing a full Z_N array.
"""

import json
import sys
from math import gcd
from multiprocessing import Pool

import numpy as np


CHUNK_SIZE = 500_000_000
WORKERS = 4


def fail(message):
    print(f"FAIL: {message}")
    return 1


_NORMALIZED = ()


def _init_worker(normalized):
    global _NORMALIZED
    _NORMALIZED = normalized


def _sieve_chunk(bounds):
    lo, hi = bounds
    covered = np.zeros(hi - lo, dtype=np.bool_)
    remaining = hi - lo
    for residue, modulus in _NORMALIZED:
        start = lo + ((residue - lo) % modulus)
        if start < hi:
            sl = covered[start - lo::modulus]
            if sl.all():
                continue
            missing = ~sl
            remaining -= int(missing.sum())
            sl[missing] = True
            if remaining == 0:
                return None
    if remaining:
        uncovered = np.flatnonzero(~covered)
        return lo + int(uncovered[0])
    return None


def main(path):
    try:
        witness = json.load(open(path))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"cannot read witness: {exc}")

    try:
        minmod = int(witness["minmod"])
        congruences = [
            (int(residue), int(modulus))
            for residue, modulus in witness["congruences"]
        ]
    except (KeyError, TypeError, ValueError) as exc:
        return fail(f"invalid witness format: {exc}")

    moduli = [modulus for _, modulus in congruences]
    if any(modulus <= 1 for modulus in moduli):
        return fail("modulus <= 1")
    if len(set(moduli)) != len(moduli):
        return fail("duplicate moduli")
    if not moduli:
        return fail("empty congruence list")
    if min(moduli) < minmod:
        return fail(f"modulus below minmod {minmod}")

    N = 1
    for modulus in moduli:
        N = N // gcd(N, modulus) * modulus

    for modulus in moduli:
        if N % modulus:
            return fail(f"modulus {modulus} does not divide N={N}")

    normalized = [(residue % modulus, modulus)
                  for residue, modulus in congruences]
    normalized.sort(key=lambda item: item[1])
    bounds = [(lo, min(lo + CHUNK_SIZE, N))
              for lo in range(0, N, CHUNK_SIZE)]
    with Pool(processes=WORKERS,
              initializer=_init_worker,
              initargs=(normalized,)) as pool:
        for uncovered in pool.imap_unordered(_sieve_chunk, bounds):
            if uncovered is not None:
                pool.terminate()
                return fail(f"uncovered residue {uncovered}")

    print(f"PASS: sieve cover, {len(congruences)} congruences, "
          f"min modulus {minmod}, N={N}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
