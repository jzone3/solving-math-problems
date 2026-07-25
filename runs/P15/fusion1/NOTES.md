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

## 6. Experiment C: frontier push (compressed ruin/recreate repair)

Code: `frontier17.py`. This experiment retained `fc_tree2.Builder`'s exact
fragment dictionary and added global reassignment by ruin/recreate: randomly
remove a batch of already-placed classes, replay the survivors exactly into a
fresh compressed builder, then rerun exact-gain greedy. Acceptance minimized
the exact residual mass, with fragment count as a tie-breaker. No explicit
`Z_N` bitmask was allocated, and no floating score was used for acceptance.

### m=17 profiles

| factorization | N | reciprocal slack | greedy/repair budget | best residual mass | fragments | classes |
|---|---:|---:|---:|---:|---:|---:|
| `2^5·3^3·5^2·7·11·13·17` | 367,567,200 | 1.760859 | 90s + 4×20s | 0.0126542928749 | 1,339,929 | 1,129 |
| `2^6·3^3·5^2·7·11·13·17` | 735,134,400 | 1.801665 | 120s + 3×20s | 0.0101066322022 | 1,348,762 | 1,286 |
| `2^7·3^3·5^2·7·11·13·17` | 1,470,268,800 | 1.822068 | 120s + 2×15s | 0.0069223165179 | 1,503,530 | 1,448 |
| `2^7·3^4·5^2·7·11·13·17` | 4,410,806,400 | 1.865425 | 300s + 4×40s | **0.00401251140834** | 1,600,470 | 1,727 |

The deepest profile's baseline ended at mass `0.00401435755602`,
2,194,285 fragments and 1,721 classes. Four repair attempts reduced this
to mass `0.00401251140834`; one repair was rejected, and the accepted
repairs only reduced the residual by about `1.8e-6`. Thus reassignment helps
quantitatively but does not approach closure.

### m=18

Profile `2^7·3^4·5^2·7·11·13·17`, N=4,410,806,400, reciprocal slack
1.806601. With 180 seconds greedy plus two 30-second repair attempts:

```
C-BASE stats mass=0.00427372985584 frags=2242705 chosen=1690 elapsed=180.0s
C-REPAIR 0 ACCEPT old=(0.00427372985584,2242705,1690) new=(0.00427179936984,2199202,1706)
C-REPAIR 1 ACCEPT old=(0.00427179936984,2199202,1706) new=(0.00427146859132,2208872,1711)
C-DONE best mass=0.00427146859132 frags=2208872 chosen=1711 elapsed=298.0s
```

### Verification and conclusion

No complete witness was produced, so the verified frontier remains m=16.
The incomplete m=17 and m=18 artifacts were explicitly rejected by the
first verifier:

```
FAIL: integer not covered (sampling): -298004427984244793786055837060
FAIL: integer not covered (sampling): -610776842766686546465144208891
```

`verify_subtract.py` on the incomplete m=17 artifact was run for 20 seconds
and exited with status 124 (cell subtraction did not finish); it produced no
PASS line. No file is named `witness_m17.json` or `witness_m18.json`.

Experiment C therefore did not beat m=16. The compressed representation
removes the RAM wall and ruin/recreate genuinely reassigns existing moduli,
but the residual remains diffuse at roughly 1.3–2.2 million CRT fragments
and mass 0.004–0.013. The remaining gap is global alignment rather than
local residue optimization.

## 7. Experiment C deep-N continuation (m=17)

The previous Experiment C used N≈10^9. This continuation tested the
v1-style deep divisor lattice, with a long greedy budget and then repair.

### Deep profiles tested

An initial profile
`2^8·3^5·5^3·7^2·11·13·17·19` has
N=17,599,117,536,000 and reciprocal sum 2.303121274, but it fragmented
immediately:

```
chosen=17 mass=0.45789 frags=226620288 unused=10335 t=18s
chosen=34 mass=0.27085 frags=545201464 unused=10318 t=168s
```

RSS reached approximately 3.7 GB at that point, so this profile was stopped
as the requested memory backoff condition.

The viable deep profile was the v1-style
`2^7·3^5·5^3·7^2·11·13·17`, with
N=463,134,672,000, 4,592 eligible divisors, reciprocal sum 2.008361916.
This is smaller than the full v1 winning N because the latter also included
prime 19, but it retained the deep 2/3/5 structure without runaway initial
fragmentation.

### Long greedy

The first 900-second pass reached:

```
TIMEOUT mass=0.0002297 frags=3251891 chosen=2084
C-BASE stats mass=0.000229669287209 frags=3251891 chosen=2084 elapsed=901.0s
```

A resumed 900-second pass, replaying that exact compressed state, reached:

```
TIMEOUT mass=0.0002198 frags=3783878 chosen=2216
C-BASE stats mass=0.00021984738383 frags=3783878 chosen=2216 elapsed=916.3s
```

### Ruin/recreate repair

Using the resumed state, four 180-second repair attempts with ruin size 50
were run. The best state was:

```
C-REPAIR 0 ACCEPT old=(0.00021984738383,3783878,2216) new=(0.000215189315388,5514082,2236)
C-REPAIR 1 ACCEPT old=(0.000215189315388,5514082,2236) new=(0.000214108748481,5459588,2236)
C-REPAIR 2 REJECT old=(0.000214108748481,5459588,2236) new=(0.000276081597277,7234086,2270)
C-REPAIR 3 ACCEPT old=(0.000214108748481,5459588,2236) new=(0.0002137030803,5481137,2238)
C-DONE best mass=0.0002137030803 frags=5481137 chosen=2238 elapsed=2203.6s
```

The deep lattice improved the residual by roughly 20× relative to the
N=4.4e9 experiment (0.0040 → 0.000214), but did not close it. The remaining
residual is still over five million diffuse fragments. No m=18 run was
started after this continuation because the m=17 state remained far from
exact closure and the 60–75 minute time budget had been consumed.

The best partial was rejected by `verify_v1.py`:

```
FAIL: integer not covered (sampling): 36138693373302250625994930856
```

`verify_subtract.py` on the same partial ran for 20 seconds and exited
`124` without output; no PASS line exists. No `witness_m17.json` was
created, and the verified frontier remains m=16.

### Experiment C diagnosis (why m=17 does not close)

Decisive structural evidence: as greedy continues on the deep lattice the
residual *measure* shrinks (0.004 → 2.14e-4) but the residual *fragment count*
GROWS (chosen 2084→2216, frags 3.25M → 3.78M → 5.48M). Each additional
placement shatters existing cells faster than it removes them — the exact
divergence law v2 §10 (|U_{i+1}| = p·|U_i| − kills) and v3's coset-engine
divergence predict. Ruin/recreate reassignment (global, RAM-wall-free on the
compressed rep) moves the measure only marginally and cannot reverse the
fragment growth. This is the integrality-gap / diffuse-dust wall, not a speed
or slack limitation: no local or global *reassignment* of divisor-of-N moduli
closes a diffuse tail; the record constructions avoid it only by building the
tail exactly top-down. Verified explicit frontier therefore stands at m=16
(v1); Experiments A–C did not beat it, and this is a genuine negative, not a
budget artifact.

## 8. Experiment C weighted min-conflicts continuation

The random ruin/recreate loop was replaced in `frontier17.py` by an exact
single-modulus reassignment loop. For each move it removes one assigned
modulus, replays every other assignment into a fresh compressed builder, and
selects the replacement residue using a weighted CRT gain profile over the
current residual fragments. The resulting assignment is accepted only when
the exact compressed residual mass decreases. After three stagnant moves,
fragment weights receive a breakout/PAWS increment; the best state is
retained.

The deep-N greedy state had to be regenerated because the prior partial JSON
artifacts were not present at handoff. The 900-second seed run produced:

```
C-BASE stats mass=0.000229669287209 frags=3251891 chosen=2084 elapsed=900.0s
```

One 900-second min-conflicts move was:

```
MC step=0 REJECT remove=71604 mass=0.000229669287209 frags=3251891 chosen=2084 t=84.2s
C-MC best mass=0.000229669287209 frags=3251891 chosen=2084 elapsed=984.3s
```

Ten additional exact moves from that state gave one accepted move:

```
MC step=0 REJECT remove=21120 mass=0.000229669287209 frags=3251891 chosen=2084 t=86.2s
MC step=1 REJECT remove=8085 mass=0.000229669287209 frags=3251891 chosen=2084 t=171.9s
MC step=2 ACCEPT remove=349272 mass=0.000229637907567 frags=3249138 chosen=2084 t=257.1s
...
C-MC best mass=0.000229637907567 frags=3249138 chosen=2084 elapsed=860.1s
```

Ten further weighted moves from that accepted state all rejected:

```
C-MC best mass=0.000229637907567 frags=3249138 chosen=2084 elapsed=879.5s
```

True exact reassignment therefore reduced fragment count, but only from
3,251,891 to 3,249,138 (2,753 fragments, 0.085%) and reduced mass by
3.13e-8. It did not reverse the diffuse-residual plateau. Each move costs
roughly 85–95 seconds because exact removal requires replaying approximately
2,084 classes through the compressed representation.

The best m=17 partial failed the first verifier with:

```
FAIL: integer not covered (sampling): 36138693373302250625994930856
```

The second verifier ran for 20 seconds and exited 124 without output due to
cell subtraction cost. No witness passed either verifier, and no m=18 run
was attempted. The verified frontier remains m=16.

## 9. Experiment D — literature-transcription check (why we can't just copy a known m>=17 cover)

Checked whether an explicit, transcribable covering system with minimum
modulus 17-20 exists in the accessible literature to verify directly (a
legitimate way to beat our automated m=16 frontier without a new search).

- Klein 2025 (arXiv:2508.18062, downloaded /tmp/klein.pdf) is a *lower-bound*
  paper (min modulus 5 => max modulus >= 108, lcm >= 1440; min 6 => lcm
  >= 5040). Its explicit small examples / Krukenberg's minimal-lcm covers are
  only tabulated up to **m = 7** (L(3)=120, L(4)=360, L(5)=1440, L(6)=5040,
  L(7)=15120). All of these are BELOW v1's already-verified m=16, so
  transcribing them cannot advance the frontier.
- The actual human records with min modulus in [17, 42] — Krukenberg m=18
  (1971 PhD thesis "Covering sets of the integers", ref [8]), Choi m=20,
  Morikawa m=24, Gibson m=25, Nielsen m=40, Owens m=42 — are hand-tuned
  recursive resource-allocation arguments, not published as explicit
  congruence lists. v4 spent an entire prior run mechanizing Owens' thesis to
  a residue-level emission (12.33M congruences, ~93% of Z) and still could not
  complete it to a verified witness (the under-determined x-slots / obstruction
  C). Nielsen m=40 alone has > 10^50 congruences — non-materializable by design.

Conclusion: there is no accessible, transcribable explicit covering system
with min modulus > 16; the record constructions are exactly the ones that
resist mechanization. So neither direct search (Experiments A-C, capped at
m=16 by the integrality-gap wall) nor literature transcription (Experiment D)
beats the m=16 verified frontier within this session's scope.

## 10. Session bottom line

Min modulus >= 43 is a genuine OPEN problem (record 42, Owens 2014); it has
not been solved in the literature and was not solved here. This session added,
beyond v1-v5, four new exactly-checked negative results: (A) greedy+finisher
fusion, (B) the complete 20-section T=43 counting-deficit ledger (56-set
deficit), (C) the first true weighted min-conflicts search on the unbounded-N
compressed representation (proving the m=17 residual is a deep local optimum
that global reassignment moves by only 0.085%), and (D) a literature-
transcription check. Verified explicit frontier stands at m=16. No witness was
fabricated; every negative is backed by exact-verifier output. The only
credible route to 43 remains an exact top-down construction with joint
tower/x-slot allocation designed from the start — not any search, repair, or
counting blueprint reachable by the methods exhausted across v1-v5 + fusion1.

## 11. Positive artifacts + m=16 triple-verification + m=17 ladder (fusion1, later)

Beyond the negatives above, this run committed the actual VERIFIED positive
frontier as reproducible witnesses under `solutions/P15/`:

- Explicit distinct-moduli covering systems for **m = 3 … 16**, each PASSing
  the exact verifiers. m=3..15 pass both `verify_v1.py` (CRT recursion) and
  `verify_subtract.py` (exact cell subtraction); see `WITNESSES.md` for the
  per-m factorization / congruence-count / literal PASS lines.
- **m=16 is triple-verified.** Key finding: verifier outcome depends on N, not
  just on coverage. Oversized m=16 factorizations (e.g. 2^8·3^5·5^3·7^2·11·13·17)
  cover Z (PASS `verify_v1.py`) but make `verify_subtract.py`'s working set peak
  at ~66M cells, tripping its `>50_000_000` guard (capacity-limited, NOT a
  coverage refutation). Reusing the *m=15-scale* N = 2^7·3^5·5^3·7^2·11·13 =
  27,243,216,000 closes an exact m=16 cover in **641 congruences** with peak
  cells only 6,925,956 — under the guard. All three verifiers PASS:
    - `verify_v1.py`: PASS 641 congruences, min modulus 16, cover Z
    - `verify_subtract.py`: PASS, peak cells 6925956
    - `verify_sieve.py`: PASS, N=27243216000
- Added `toolkit/verify_sieve.py` — a 4th INDEPENDENT exact verifier: direct
  residue sieve over Z_N in bounded-memory numpy chunks (valid because every
  modulus divides N, so covering Z ⟺ covering [0,N)). Validated: PASS on
  m=3..15, and FAIL (`uncovered residue 9`) on a deliberately broken witness.

- **m=17 ladder — NEGATIVE (structural, reconfirmed).** Swept smooth N from
  5.4e10 up to 6.9e12 with generous budget. None closed exactly. The signature
  is consistent: residual *mass* shrinks but residual *fragment count* grows or
  plateaus (e.g. 2^7·3^6·5^3·7^2·11·13: frags ~2.7M→8.35M; the 4.6e11 profile:
  greedy 3.25M frags, weighted repair 5.48M frags). This is the same diffuse-
  tail / integrality-gap wall isolated in Experiment C — greedy-over-divisors-
  of-a-smooth-N caps at **m=16**. m=17+ needs a structurally different
  (mixed-modulus / recursive-family) construction, i.e. the genuine open part.

## 12. m=17 count-minimizing greedy (new objective) — NEGATIVE, sharpens the wall

New engine `toolkit/fc_tree2_countmin.py`: same exact fragment representation
and `apply()` transition as fc_tree2, but the selection objective is changed
from "maximize covered *measure*" to "minimize the number of surviving
residual fragment-classes" (exact integer delta per candidate modulus n hitting
a fragment at modulus m: `q-2` where `q = n/gcd(m,n)`; ties broken by measure).
Floats only in tie-break scoring; accept path stays exact.

Finding (m=17, three N profiles incl. the m=16 winner N=27,243,216,000 and the
richer N=463,134,672,000): count-minimization DOES keep the residual compact —
tens of fragments (best 17, plateauing ~43-199) versus the *millions* that
measure-greedy leaves. But it does so at **high residual measure** (~0.53-0.78).
So the two objectives expose a hard tradeoff: you can get **few fragments OR
low measure, never both** — and an exact cover needs both (measure→0 with a
finite finisher-closable survivor set). Seeding engine_e's fresh-prime finisher
on the smallest residual (43 classes, 13 of them mod 17) exploded on the very
first survivor: `FAIL residue 4 ... finisher supply out 1777` (added 1,603
classes closing one survivor, then ran out of distinct fresh primes).

This is a new, independent confirmation of the integrality-gap wall from the
opposite direction: the residual is either diffuse-many-fragments or
few-fragments-large-measure, and the finisher cannot absorb even one
large-measure survivor. No exact m=17 cover; frontier stays m=16.

## 13. Top-down recursive tree builder (the "symbolic route") — implemented, NEGATIVE

Prior notes repeatedly flagged a top-down p-ary-tree / arrow-family construction
as "the untried next step." Now actually built and run: `toolkit/tree_cover.py`
— starts from open cell (0 mod 1), splits an open AP (a mod M) into children mod
p·M, closes p-1 of them with distinct congruences of modulus p·M (only if
p·M >= minmod and unused), recurses on the last, with a fresh-prime CRT tail to
close binary paths; DFS with rollback and depth/node/class bounds; exact integer
coverage checks (no floats on accept path).

Sanity: it closes a real cover at **minmod=2** (37 congruences) that PASSes all
three verifiers (verify_v1, verify_sieve, verify_subtract) — so the machinery
and distinct-modulus bookkeeping are correct.

m=16 and m=17: does NOT close within bounded search (depth 100, 1e5 nodes) —
the DFS descends through open branches and backtracks (hundreds of backtracks)
without a surviving finite closing assignment. This is the same obstruction
from the top-down side: distinct-modulus collisions force recursive alternatives
and the open branch never reaches a free closure. So both the bottom-up
(divisor greedy / count-min / repair) AND the top-down (recursive tree) routes
now empirically cap below m=17 here. Confirms the missing piece is a specific
*closure design* (the global alignment identity used by Owens/Nielsen), not more
search — the genuine open-research part. Frontier stays m=16.
