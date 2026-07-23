# P15 V4 — greedy + local repair at scale — run notes

Session: https://app.devin.ai/sessions/da7ba5bd517c40518a9c80f1714c0433
Variant: V4 (randomized greedy over huge modulus pools + alignment/repair).

## 0. Statement re-verification (2026-07-22)

- Original sources checked: Owens, "A Covering System with Minimum Modulus 42",
  BYU MSc thesis 2014 (scholarsarchive.byu.edu/etd/4329); Nielsen, JNT 129 (2009)
  640–666 ("A covering system whose smallest modulus is 40"); Hough, Annals 181
  (2015) (min modulus ≤ 10^16); BBMST 2022 (≤ 616,000).
- Wikipedia "Covering system" (rev. 2026-05-28) still lists 42 (Owens) as the
  constructive record; targeted Exa searches for 2024–2026 improvements found
  none. Problem confirmed open as stated: construct distinct-moduli cover with
  min modulus ≥ 43.
- KEY STRUCTURAL FACT recovered from the sources: Nielsen's min-mod-40 system
  has > 10^50 congruences and Owens's 42 system > 10^86 — these are *implicit*
  (recursive recipe) constructions, not explicit lists. Any ≥43 witness will
  almost certainly need a compressed/recursive witness format, not a literal
  congruence list.

## 1. Encoding

CRT-layered level framework (`cover.py`):
- Process prime powers p^e ("levels") in increasing order; state = holes
  (uncovered residues mod M, M = product of processed levels).
- At level p^e each hole splits into q = p^e cells; usable moduli are d·p^j
  (d | M, j = 0..e, d·p^j ≥ T, each numeric modulus used at most once =
  distinct-moduli constraint). Congruence (a mod d, b mod p^j) covers cells
  t ≡ b (mod p^j) in every hole r ≡ a (mod d).
- Lazy submodular greedy over (d, j) candidates (gains only decrease → lazy
  heap is exact), randomized tie-breaks, numpy bincount scoring.
- Verifier `solutions/P15/verify.py`: independent, stdlib-only, recursive CRT
  split, never materializes lcm; checks distinct moduli + full cover.

## 2. What was tried, in order

1. **Plain gain-greedy** (max newly covered cells per congruence):
   solves T=2,3 on small configs; stalls at T=4+ (e.g. T=10 config with
   reciprocal slack 2.21 left 296k uncovered cells). Diagnosis: hole
   fragmentation — scattered holes make each congruence's density land mostly
   on already-covered ground (>55% waste).
2. **Efficiency-greedy** (max gain·m/(Mq), i.e. least wasted density):
   worse in practice — fragments even faster (T=3 left 4 holes where
   gain-greedy left 1).
3. **Forced-alignment slot builder** (`cover2.py`, Nielsen-style fixed
   survivor cell 0 per level, per-slot set covers): solves T=3 only; too
   rigid (no j=0 whole-hole kills, whole subtrees kept on slot failure).
4. **Two-phase survivor-aligned greedy** (`cover.py --survivor`): phase 1
   covers only cells outside a random survivor class s0 (mod p), phase 2
   mops up survivor columns. Keeps holes CRT-aligned so residue classes
   stay dense. THIS is the winning V4 ingredient:
   - T=10 SOLVED first try: 1002 congruences, lcm = 2^7·3^4·5^2·7^2·11·13,
     verified PASS. (Plain greedy on same config: 296k leftover cells.)

## 3. Verified explicit covers produced so far (all PASS verify.py)

| T | levels | #congs | witness |
|---|---|---|---|
| 2 | 2^2,3 | 5 | (smoke test) |
| 3 | 2^3,3^2,5 | 17 | (smoke test) |
| 4 | 2^5,3^3,5,7 | 38 | /tmp (gain-greedy) |
| 6 | 2^5,3^3,5^2,7 | 93 | /tmp (gain-greedy) |
| 8 | 2^6,3^4,5^2,7,11,13 | 625 | /tmp (gain-greedy) |
| 10 | 2^7,3^4,5^2,7^2,11,13 | 1002 | witness_T10.json (survivor) |
| 12 | 2^7,3^4,5^3,7^2,11,13,17 | 2064 | witness_T12.json (survivor) |

## 4. Scaling analysis (why explicit lists cap out)

Hole growth per level is intrinsic: at the first level 2^e only moduli
2^j ≥ T are usable, total density 2^{floor(log2 T)-e+1}-ish << 1, so almost
all 2^e cells survive as holes; the construction only wins because hole
*density* shrinks while hole *count* multiplies. Observed (T=14 run,
levels 2^8,3^5,5^3,7^2,11,...): holes 225 → 36k → 1.8M → 22M. This is the
same explosion that makes Nielsen's T=40 system >10^50 congruences and
Owens's T=42 >10^86. An explicit machine-verifiable congruence list is
therefore fundamentally limited to T ≈ mid-teens on a 32 GB machine;
T=43 REQUIRES a compressed recursive witness format + a verifier that
checks the recipe (hole-class counting), not a list. That compressed-
witness pipeline is the real frontier for machine work on this problem.

Engineering notes:
- OOM bug fixed: np.bincount(minlength=d) allocated O(d) for divisors up to
  ~7·10^8; replaced with np.unique grouping (bounded by #holes).
- Perf: cache active-cell matrix per phase instead of recomputing per score;
  LRU-bounded residue caches (10 GB); relaxed lazy greedy (accept within 20%
  of stale upper bound) to avoid 20M-element re-sorts per heap ping-pong.
- Bottleneck at 20M+ holes: np.unique sort per divisor (~650 divisors/level).

## 5. Escalation runs (compute log)

- T=13, levels 2^7,3^4,5^3,7^2,11,13,17,19 (slack 2.55): KILLED at 8 h
  timeout mid-17-level. Hole trajectory: 4.2M (11) → 13.6M (13, used 960
  moduli) → 36.2M holes entering the 17-level (~5 h there without
  finishing). Same wall as T=14: compute-bound, not density-bound.
- T=14, levels 2^8,3^5,5^3,7^2,11,13,17,19 (slack 2.75): KILLED at 8 h
  wall-clock timeout mid-13-level. Hole trajectory: 225 → 36k → 1.8M →
  22.2M (11-level, ~2 h) → 69.5M holes entering the 13-level; the 13-level
  alone needed >5 h (69.5M-element np.unique per divisor, ~1300 divisors).
  NEGATIVE: T=14 explicit is beyond this machine/day budget with the
  current per-level greedy — compute-bound, not density-bound (slack 2.75).

## 6. Ideas not exhausted (for follow-up runs)

- Parallelize per-divisor scoring across cores (np.unique is the bottleneck;
  embarrassingly parallel over ~10^3 divisors) — likely unlocks T=14–16.
- Hole-CLASS compression: group holes by coverage-isomorphism and track
  counts, not individuals (this is exactly how Nielsen/Owens scale to
  10^50/10^86 congruences). Witness becomes a recursive recipe; verifier
  checks per-class branch accounting + modulus-usage counting instead of an
  explicit list. This is the only credible route to T≥43 and meshes V4 with V5.
- Simulated-annealing reassignment of (a, b) choices at the last two levels
  (planned repair phase) was never needed below the compute wall — greedy +
  survivor alignment already fully covered whenever the level completed.

## 7. Final summary

STATUS: negative (frontier-pushed on the tooling side; no new record).

- Re-verified problem statement + openness (record still 42, July 2026).
- Built a fully automated pipeline (build + independent verify) for
  distinct-moduli covering systems with min modulus ≥ T; key algorithmic
  finding: survivor-class alignment beats both plain max-gain greedy and
  max-efficiency greedy by a wide margin (T=10 config: 296k uncovered cells
  for plain greedy vs 0 with alignment).
- Verified explicit covers produced for T = 2,3,4,6,8,10,12 (largest:
  2064 congruences, lcm 2^7·3^4·5^3·7^2·11·13·17). T=13/14 attempts hit an
  8 h compute wall at 36–70M holes, density slack unused (2.5–2.75).
- Distance to record remains enormous: T=42 needs >10^86 congruences —
  explicit-list search cannot reach it on any hardware; compressed
  recursive witnesses (hole-class counting) are the mandatory next step.
