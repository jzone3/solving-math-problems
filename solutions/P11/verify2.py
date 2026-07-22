#!/usr/bin/env python3
"""Second, independently-written verifier for CW(n,k) witnesses (numpy-based).

Checks, for witness JSON {"n":n,"k":k,"P":[...],"N":[...],"proper":bool}:
  * P, N disjoint subsets of Z_n, |P|+|N| = k
  * the full n x n circulant matrix W (W[i][j] = a[(j-i) mod n]) satisfies
    W @ W.T == k * I  (explicit matrix product, no autocorrelation shortcut)
  * properness (if claimed): for every prime p | n, the support hits at least
    two residue classes mod p (equivalent to: no shift maps the support into a
    proper subgroup of Z_n).

Usage: python3 verify2.py witness.json  -> prints PASS on success.
"""
import json
import sys

import numpy as np


def main(path):
    w = json.load(open(path))
    n, k, P, N = w["n"], w["k"], list(w["P"]), list(w["N"])
    assert set(P).isdisjoint(N) and len(P) + len(N) == k
    a = np.zeros(n, dtype=np.int64)
    a[P] = 1
    a[N] = -1
    assert int((a != 0).sum()) == k
    W = np.empty((n, n), dtype=np.int64)
    for i in range(n):
        W[i] = np.roll(a, i)
    ok = np.array_equal(W @ W.T, k * np.eye(n, dtype=np.int64))
    assert ok, "W W^T != kI"
    if w.get("proper", True):
        supp = np.array(P + N)
        for p in range(2, n + 1):
            if n % p or any(p % q == 0 for q in range(2, int(p ** 0.5) + 1)):
                continue  # need prime divisors of n only
            assert len(set(supp % p)) > 1, f"support in one class mod {p}: improper"
        print("PASS")
    else:
        print("PASS (valid CWM, improper by declaration)")


if __name__ == "__main__":
    main(sys.argv[1])
