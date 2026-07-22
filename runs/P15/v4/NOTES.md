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

## 4. Status

(in progress — escalation to T=12/14/16 running)
