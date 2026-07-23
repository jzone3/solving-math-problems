#!/usr/bin/env python3
"""Standalone verifier for the nonexistence of CW(120, 49).

THEOREM. There is no circulant weighing matrix CW(120, 49).

PROOF (machine-checked here).
1. Suppose A is a CW(120,49), viewed as a {0,±1} vector (a_i) on Z_120 with
   all nontrivial periodic autocorrelations 0 and weight 49.
2. k = 49 = 7^2 and gcd(120, 49) = 1, so by the classical multiplier theorem
   (Arasu–Gordon–Zhang, "New nonexistence results on circulant weighing
   matrices", Cryptogr. Commun. 13 (2021), Theorem 2.4, citing [3]):
   7 is a multiplier of A and fixes some translate A'. Thus a'_{7i} = a'_i,
   i.e. A' is constant on the orbits of x -> 7x on Z_120.
3. Fold A' modulo 40 (fibers of size 3): b_j = sum_{i ≡ j (mod 40)} a'_i.
   Then |b_j| <= 3; every character of Z_40 lifts to Z_120, and |Â'|^2 = 49
   at every character (including the trivial one, since the row sum is ±7),
   hence B = (b_j) has periodic autocorrelation 49·delta_0 on Z_40.
   Moreover B is fixed by x -> 7x on Z_40 (folding commutes with the
   multiplier action).
4. This script exhaustively enumerates ALL vectors on Z_40 with entries in
   [-3,3], constant on <7>-orbits, squared norm 49, and flat autocorrelation.
   There are NONE. Contradiction — so no CW(120,49) exists.       QED

Controls (also machine-checked below):
  (a) the same code finds >0 solutions for <7>-fixed ICW_15(8,49) (m=8,d=15);
  (b) the same code finds 0 solutions for <3>-fixed ICW_3(44,81), reproducing
      the published AGZ Prop 4.2 computation (no CW(132,81)).

Run: python3 verify_no_cw120_49.py    -> prints PASS (about 2-4 minutes).
"""


def orbits(t, m):
    seen, out = set(), []
    for x in range(m):
        if x in seen:
            continue
        o, y = [], x
        while y not in o:
            o.append(y)
            y = (y * t) % m
        out.append(o)
        seen.update(o)
    return out


def count_fixed_icws(m, d, k, t):
    """number of <t>-fixed integer vectors on Z_m, entries in [-d,d],
    squared norm k, autocorrelation k*delta_0."""
    orbs = orbits(t, m)
    sizes = [len(o) for o in orbs]
    no = len(orbs)
    suffix_max = [0] * (no + 1)
    for i in range(no - 1, -1, -1):
        suffix_max[i] = suffix_max[i + 1] + d * d * sizes[i]
    cs = [0] * no
    found = [0]

    def flat(w):
        for s in range(1, m):
            if sum(w[i] * w[(i + s) % m] for i in range(m)) != 0:
                return False
        return True

    def dfs(pos, norm):
        if norm > k or norm + suffix_max[pos] < k:
            return
        if pos == no:
            if norm == k:
                w = [0] * m
                for c, o in zip(cs, orbs):
                    for x in o:
                        w[x] = c
                if flat(w):
                    found[0] += 1
            return
        for c in range(-d, d + 1):
            cs[pos] = c
            dfs(pos + 1, norm + c * c * sizes[pos])
        cs[pos] = 0

    dfs(0, 0)
    return found[0]


if __name__ == "__main__":
    # control (a): solutions exist for m=8 folding
    ca = count_fixed_icws(8, 15, 49, 7)
    assert ca > 0, f"control (a) failed: expected >0, got {ca}"
    print(f"control (a): <7>-fixed ICW_15(8,49) count = {ca} (>0)  OK")

    # control (b): reproduce AGZ Prop 4.2 (no CW(132,81))
    cb = count_fixed_icws(44, 3, 81, 3)
    assert cb == 0, f"control (b) failed: expected 0, got {cb}"
    print("control (b): <3>-fixed ICW_3(44,81) count = 0 (matches AGZ)  OK")

    # main theorem: no <7>-fixed ICW_3(40,49)
    main = count_fixed_icws(40, 3, 49, 7)
    assert main == 0, f"MAIN CHECK FAILED: found {main} fixed ICW_3(40,49)"
    print("main: <7>-fixed ICW_3(40,49) count = 0")
    print("=> no CW(120,49) exists (via AGZ Thm 2.4 multiplier argument)")
    print("PASS")
