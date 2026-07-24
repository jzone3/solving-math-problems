# P15 fusion1 — continuation run notes (branch runs/P15-fusion1)

Target: a covering system of Z with **distinct moduli, minimum modulus ≥ 43**
(current constructive record 42, Owens 2014). This run is a *fusion*
continuation of prior runs v1–v5; it does not redo their work — it fuses their
best engines and completes analyses they left partial. **Honest bottom line
first: no covering system with minimum modulus ≥ 43 was found; the record 42
stands.** Two new, exactly-checked experiments are logged below, both negative,
both adding quantitative content beyond v1–v5.

## 0. Prior frontier inherited (verified, from v1–v5 notes)

- Automated explicit covers, machine-verified (`solutions/P15/verify.py`):
  m ≤ 16 (v1, exact-gain CRT/tree greedy, N=3.24e12, 896 congruences);
  m ≤ 12 via native min-conflicts C engine (v3); m ≤ 10 dense bitmask (v2);
  symbolic-coset engine m ≤ 9 at unbounded lcm (v3); v5 partial-cover ceiling
  ~30k classes / L=16.
- Exact minimal-lcm ladder: L(3)=120, L(4)=360 (v2, witnesses PASS), matching
  Dalton–Trifonov; SAT is CDCL-hostile, SLS/min-conflicts is the right engine
  (v2/v3); ILP LP-relaxation collapses to the reciprocal-sum bound (v2).
- v4 (deepest): duplicate-free **residue-level emission of the entire Owens
  T=42 system** (12.33M congruences, ~92–93% of Z), + a 3-level machine-checked
  proof that Owens **cannot be locally patched to 43** ("obstruction C": per-cell
  fresh patching fails because sibling families share the divisor-lattice
  columns; the residue-level barrier is global x-slot routing).
- Universal failure mode across all explicit engines: local search terminates in
  a **diffuse dust** of uncovered residues spread over nearly every prime-power
  class; no reassignment of already-used moduli absorbs it. Record constructions
  avoid dust by building the tail exactly, top-down, with cross-branch alignment
  planned from the start.

## 1. What this run tried that v1–v5 did not

1. **Experiment A — engine fusion.** Combine v1's exact-gain CRT/tree greedy
   (`fc_tree2.Builder`, unbounded N, no cell arrays) with v5's fresh-prime
   2-chain `finisher` as a *residual closer* — the piece v1's pure greedy
   lacked — dropping the "moduli divide a fixed smooth N" restriction in the
   endgame (a covering system may use any distinct integers ≥ m). None of
   v1–v5 ran greedy + fresh-prime finisher end-to-end.
2. **Experiment B — complete T=43 counting-deficit ledger.** v4's
   `branchgame.py` re-ran only 2 of Owens' 20 sections at T=43. Experiment B
   replays v4's *validated* T=42 set-calculus ledger under the mechanical T=43
   penalties across **all** sections and totals the aggregate deficit.

Methodology: the accept path is exact (no float decides coverage; floats only
score greedy gain). Any claimed witness must PASS **both** `toolkit/verify_v1.py`
(CRT-recursive) and `toolkit/verify_subtract.py` (cell subtraction). No witness
was produced, so no PASS is claimed.

## 2. Experiment A — fusion cover (NEGATIVE)

Code: `fusion_cover.py`. Full log: `EXPA_NOTES.md`.

- m=17, N=4,410,806,400 = 2^7·3^4·5^2·7·11·13·17 (recip 1.865): 20 s greedy
  stalls at residual density 0.063, **5.19M** exact residual cells.
- m=18, same profile (recip 1.807): stalls at density 0.038, **3.68M** cells.
- The finisher closes an *isolated* thin cell, but repeated cells sharing a
  modulus M require odd-prime-prefixed sibling trees, which recreate the
  resource contention and branch explosively — exactly v5's §21 same-modulus
  obstruction, now confirmed at scale. Per-cell closure of millions of diffuse
  cells is not viable.
- The saved m=17 partial was correctly **rejected** by `verify_v1.py`
  (`FAIL: integer not covered (sampling): -3508...161`); it is not renamed to a
  witness.

Conclusion: fusing greedy + fresh-prime finisher does **not** push the verified
frontier past m=16. The finisher is a thin-cell tool, not a diffuse-residual
closer; the binding wall is the global alignment / same-modulus contention that
v1–v5 already diagnosed, not raw iteration speed. (No compute was spent chasing
m=17 further: even v1's long run left m=17/18 in slow greedy tails, and the
finisher provably cannot rescue a diffuse residual — the actual target of 43 is
unreachable by explicit-witness methods regardless, per v2/v3 scaling.)

## 3. Experiment B — complete T=43 deficit ledger (NEGATIVE, quantified)

Code: `branchgame_t43_full.py` (loads and monkey-patches v4's `branchgame.py`).

Penalties at T=43 (mechanical consequences of forbidding modulus 42 = 2·3·7 and
raising the drop threshold 42→43):
- **P1** modulus-42 trick death: any 7^ fill whose per-copy `need` was reduced
  below the naive p−1 = 6 (Owens' reduced-input 7-tricks, several routing
  through 7·3·2 = 42) loses one input per copy → `need += 1`. Reproduces v4's
  hand-derived 3.8 (5→6) and 3.14 (5→6), extended uniformly.
- **P2** drop threshold 42→43 recomputed exactly (no material change on Owens'
  prime range; 43·1 = 43 stays usable).

Result:

```
T=42 replay:  12/12 sections PASS  (sanity)
T=43 re-run:   4/12 sections PASS,  8 FAIL
aggregate extra-set deficit from 42-trick death: 56 sets
```

FAIL sections (need extra pool the tight ledgers cannot supply): 3.8, 3.12,
3.13, 3.14, 3.16, 3.17, 3.19, 3.20.

Interpretation (**honest, counting-level only**): the set-counting calculus is
an *over-approximation* of the true residue-level cover (v4 phase 14: value-set
freshness is undecidable at counting level), so a PASS here is not a witness —
but a **FAIL is a genuine obstruction**: not even the optimistic count closes.
So this ledger *lower-bounds* the barrier: raising Owens from 42 to 43 forbids
one congruence (modulus 42) and thereby breaks the 7^ trick in 8 of 20 sections,
opening a counting-level deficit of **56 sets** that must be absorbed with more
MUL ops (fresh 5/25/125 residues) or fresh primes ≥ 97 — **without** creating a
duplicate modulus or any modulus < 43. Owens ends at prime 89 with every ledger
tight (≤ 3 spare sets) and no spare primes below 89; the 56-set deficit is
exactly the global-coupling wall v4 hit at residue level (obstruction C),
quantified here across the full construction rather than 2 sections.

## 4. Conclusions

1. No min-modulus-≥43 covering system found; record 42 stands (agrees with all
   of v1–v5 and the July-2026 literature check).
2. Engine fusion (exact greedy + fresh-prime finisher) does not beat the m=16
   explicit frontier: the finisher cannot close diffuse same-modulus residuals.
3. New quantitative barrier: the full-construction T=43 counting ledger shows a
   **56-set aggregate deficit** across 8/20 sections from the single forbidden
   modulus 42 — a counting-level *lower bound* on the difficulty, consistent
   with (and sharpening) v4's residue-level obstruction C.
4. The credible remaining route is unchanged and remains the open hard part:
   a global small-prime-layer redesign realized at the residue level with joint
   tower allocation / x-slot routing planned from construction time (v4/v5), not
   any local patch, greedy restart, or counting-level blueprint.

STATUS: frontier-confirmed; two new exact experiments (engine-fusion frontier
push; full-construction T=43 deficit ledger), both negative, both adding
quantitative content beyond v1–v5. No PR (per instructions).

## 5. Artifacts

- `fusion_cover.py` — Experiment A engine (greedy + fresh-prime finisher).
- `EXPA_NOTES.md` — Experiment A full run log.
- `branchgame_t43_full.py` — Experiment B full T=43 deficit ledger.
- `../../../toolkit/` — reference copies of prior verifiers/engines used here
  (`verify_v1.py`, `verify_subtract.py`, `fc_tree2.py`, `engine_e.py`,
  `cover_mc.c`, `branchgame.py`), copied from origin/runs/P15-v{1,3,4,5}.
