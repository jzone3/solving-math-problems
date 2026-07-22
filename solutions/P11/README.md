# P11 solutions — circulant weighing matrices

## CW(96,36) — witness found (cell listed "Open" in the La Jolla dataset, 2026-04-24)

Witness (first row, `cw96_36.txt`):

```
00-0+0+0+00000+0+0+0-0+0-00000-0+0+0+0+0+0-000-000+0-0+0+00000-0+0+0+0-0-00000-0+0-0-0-0+0-000+0
```

Verify: `python3 verify.py 36 "$(cat cw96_36.txt)"` → PASS
(checks weight 36 and all 95 nontrivial periodic autocorrelations = 0).

Found by multiplier-symmetric RRR/difference-map search (`runs/P11/v4/rrr_sym.py`,
multiplier t=41), i.e. genuinely produced by the V4 pipeline, not copied.

**Important caveat (honesty note).** The witness is supported entirely on the even
residues, and its 2-decimation is a valid CW(48,36). The dataset lists CW(48,6)
as "Yes" (Arasu–Gordon–Zhang era result) while still listing CW(96,6) as "Open".
By the classical padding implication — if CW(n,k) exists then CW(mn,k) exists
(interleave zeros) — CW(96,36) existence is an immediate consequence of
CW(48,36). So this closes the repository cell, but it is a bookkeeping
propagation rather than a mathematically new existence result. Recommended
action: report the witness (or the implication) to the maintainer of
github.com/dmgordo/circulant-weighing-matrices.

The remaining five target cells (105, 112, 117, 120, 132) have **no** such
divisor shortcut (CW(39,6), CW(56,6), CW(60,7) are "No"; k > n rules out the
rest), so they remain the genuinely hard targets.
