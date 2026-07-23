#!/usr/bin/env python3
"""Standalone verifier for the P03/V4 run's checkable claims.

No third-party dependencies (pure Python 3, brute force only).

Claim A (validation artifact): Schrijver's 1980 weighted digraph, transcribed
in runs/P03/v4/schrijver_instance.py, has min-weight dicut tau_w = 2 and
does NOT admit 2 disjoint dijoins inside its weight-1 arcs (nu_w = 1). This
reproduces Schrijver's refutation of the Edmonds-Giles conjecture and
certifies our transcription + machinery.

Claim B (spot-check of the exhaustive scans' machinery): a handful of small
unweighted digraphs have tau = nu as reported (gap 0), computed here by
brute force independent of the ILP code used in the run.

Prints PASS iff all checks succeed.

NOTE: this run found NO counterexample to Woodall's conjecture; there is no
witness to verify. STATUS is negative/frontier-pushed (see runs/P03/v4/).
"""

import itertools
import sys

# --- Schrijver instance (independent re-statement, kept in sync with
# runs/P03/v4/schrijver_instance.py) ---
TL, TR, R, BR, BL, L, uL, uR, mR, lR, lL, mL = range(12)
W1 = [(TR, R), (TR, uL), (mL, uL),
      (L, TL), (L, lL), (lR, lL),
      (BR, BL), (BR, mR), (uR, mR)]
W0 = [(TR, TL), (L, BL), (BR, R),
      (uR, uL), (mL, lL), (lR, mR),
      (TL, uL), (TR, uR), (R, mR), (L, mL), (BL, lL), (BR, lR)]
N = 12
ARCS = W1 + W0
WEIGHT = [1] * len(W1) + [0] * len(W0)


def dicuts(n, arcs):
    """All nonempty dicuts, brute force over all vertex subsets."""
    out = []
    for r in range(1, n):
        for U in itertools.combinations(range(n), r):
            Uset = set(U)
            if any(v in Uset and u not in Uset for (u, v) in arcs):
                continue  # an arc enters U
            cut = frozenset(i for i, (u, v) in enumerate(arcs)
                            if u in Uset and v not in Uset)
            if cut:
                out.append(cut)
    return out


def check_schrijver():
    cuts = dicuts(N, ARCS)
    tau_w = min(sum(WEIGHT[i] for i in c) for c in cuts)
    if tau_w != 2:
        return False, f"tau_w = {tau_w}, expected 2"
    ones = [i for i, w in enumerate(WEIGHT) if w == 1]
    # 2 disjoint dijoins would have to use only weight-1 arcs; try all
    # 2-colorings of the nine weight-1 arcs (each class must hit every dicut)
    for split in range(1 << len(ones)):
        J1 = {ones[i] for i in range(len(ones)) if (split >> i) & 1}
        J2 = set(ones) - J1
        if all(c & J1 for c in cuts) and all(c & J2 for c in cuts):
            return False, "found 2 disjoint dijoins -- transcription wrong"
    # nu_w >= 1: the full weight-1 set must itself be a dijoin
    if not all(c & set(ones) for c in cuts):
        return False, "weight-1 arcs are not even one dijoin"
    return True, "tau_w=2, nu_w=1 reproduced"


def max_packing_bruteforce(n, arcs):
    """Exact max number of disjoint dijoins by brute force (tiny cases)."""
    cuts = dicuts(n, arcs)
    tau = min(len(c) for c in cuts)
    m = len(arcs)

    def can_pack(k):
        # assign each arc a label in 0..k (k = unused); DFS with pruning
        labels = [-1] * m

        def ok_partial():
            return True

        def rec(i):
            if i == m:
                return all(
                    all(any(labels[a] == j for a in c) for c in cuts)
                    for j in range(k))
            for lab in range(k + 1):
                labels[i] = lab
                # prune: a dicut fully labeled and missing some class j fails
                good = True
                for c in cuts:
                    if max(c) <= i:
                        present = {labels[a] for a in c}
                        if any(j not in present for j in range(k)):
                            good = False
                            break
                if good and rec(i + 1):
                    return True
            labels[i] = -1
            return False

        return rec(0)

    k = tau
    while k >= 1:
        if can_pack(k):
            return tau, k
        k -= 1
    return tau, 0


def check_small_cases():
    cases = [
        # (n, arcs, expected tau, expected nu)
        (2, [(0, 1), (0, 1), (0, 1)], 3, 3),
        (4, [(0, 2), (0, 3), (1, 2), (1, 3)], 2, 2),
        (3, [(0, 1), (0, 1), (0, 2), (1, 2), (1, 2)], 3, 3),
    ]
    for (n, arcs, et, en) in cases:
        tau, nu = max_packing_bruteforce(n, arcs)
        if (tau, nu) != (et, en):
            return False, f"case {arcs}: got ({tau},{nu}), want ({et},{en})"
    return True, "small unweighted cases agree"


def main():
    ok1, msg1 = check_schrijver()
    print(("ok" if ok1 else "FAIL"), "-", msg1)
    ok2, msg2 = check_small_cases()
    print(("ok" if ok2 else "FAIL"), "-", msg2)
    if ok1 and ok2:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
