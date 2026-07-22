#!/usr/bin/env python3
"""Independent verifier for P11 (circulant weighing matrix) witnesses.

A CW(n, k) witness is given by (n, s, P, N) with k = s^2:
  P = positions of +1 in the first row, N = positions of -1.
Checks:
  - P, N disjoint subsets of Z_n, |P| = (s^2+s)/2, |N| = (s^2-s)/2
  - all n-1 nontrivial periodic autocorrelations of the ternary sequence are 0
  - weight = k
Run: python3 verify.py   -> prints PASS if every witness verifies.

WITNESSES below are for cells listed as "Open" in the current (2026-04-24,
commit 5b3d729) version of github.com/dmgordo/circulant-weighing-matrices
cwm.json.  They were recovered from the SAME repository's initial commit
1113578 (2024-03-03), whose data for these cells was dropped in the
2025-01-24 re-upload (commit a58ff99) -- i.e. these cells are marked Open in
the live La Jolla CWM repository by what appears to be a data regression,
not because the witnesses are unknown.  The two "lift" witnesses are
classical padding constructions A(X) -> A(X^d) from cells the current
dataset itself lists as Yes.
"""


def is_cwm(n, s, P, N):
    k = s * s
    if len(set(P)) != len(P) or len(set(N)) != len(N):
        return False, "repeated element"
    if set(P) & set(N):
        return False, "P and N intersect"
    if not all(0 <= x < n for x in P + N):
        return False, "element out of range"
    if len(P) != (k + s) // 2 or len(N) != (k - s) // 2:
        return False, "wrong |P| or |N|"
    a = [0] * n
    for x in P:
        a[x] = 1
    for x in N:
        a[x] = -1
    for g in range(1, n):
        if sum(a[i] * a[(i + g) % n] for i in range(n)) != 0:
            return False, f"autocorrelation at shift {g} nonzero"
    if sum(v * v for v in a) != k:
        return False, "weight != k"
    return True, "ok"


def main():
    import json
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "witnesses.json")) as f:
        wit = json.load(f)
    ok_all = True
    for name, w in wit.items():
        n, s, P, N = w["n"], w["s"], w["P"], w["N"]
        ok, msg = is_cwm(n, s, P, N)
        print(f"{name}: n={n} k={s*s} |P|={len(P)} |N|={len(N)} -> "
              f"{'OK' if ok else 'FAIL: ' + msg}")
        ok_all = ok_all and ok
    print("PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
