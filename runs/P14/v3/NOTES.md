# P14 / V3 — Prescribed automorphisms (Kramer–Mesner orbit-matrix ILP)

Session: https://app.devin.ai/sessions/742f2b6ef2bf49f0a1703cb0a32c4870
Variant: **V3** — Kramer–Mesner reduction under small prescribed groups; orbit-matrix ILP via OR-Tools CP-SAT.

## Problem statement re-verification

- Statement checked against Kaski–Östergård "Enumeration of Balanced Ternary Designs"
  (Discrete Appl. Math. 138 (2004) 133–141) companion page
  https://users.ics.aalto.fi/pkaski/btd.html which reproduces the Billington–Robinson
  (Ars Combin. 16 (1983)) / Kunkle–Sarvate (CRC Handbook) tables of admissible BTD
  parameter lists with R ≤ 15.
- All four target instances appear there **with no enumeration data (open cells)**:
  - class [1]=43 / [2]=15: (14,18; 7,1,9; 7,4)
  - class [1]=76 / [2]=31: (12,15; 6,2,10; 8,6)
  - class [1]=79 / [2]=33: (12,20; 4,3,10; 6,4)
  - class [1]=234 / [2]=121: (14,28; 8,3,14; 7,6)
- Definition used (standard, matches Kunkle–Sarvate): V×B multiplicity matrix M over {0,1,2};
  every column sums to K; every row has exactly r1 ones and r2 twos (row sum R = r1+2r2);
  for every unordered pair i<j: Σ_b M[i][b]·M[j][b] = Λ.
- Admissibility double-checked by machine: VR = BK and Λ(V−1) = RK − r1 − 4r2 hold for all four.
- Still open as of July 2026 as far as searchable literature shows (Exa searches for the exact
  parameter strings return only the census page / definition papers; no existence claims).

## Encoding

`km_solve.py`:
- Enumerate ALL candidate blocks = functions m: V→{0,1,2} with Σm = K
  (45474 blocks for V=14,K=7; 28314 for V=12,K=8; 8074 for V=12,K=6).
- Prescribe a group G ≤ Sym(V); the design's block multiset is assumed G-invariant, so it is a
  union of full block orbits with integer multiplicities x_O ≥ 0.
- Constraints (all exact, integer-linear):
  - Σ_O |O|·x_O = B
  - per element-orbit representative e: Σ_O #{b∈O : m_b(e)=1}·x_O = r1 and (=2 count) = r2
  - per pair-orbit representative (i,j): Σ_O (Σ_{b∈O} m_b(i)m_b(j))·x_O = Λ
- Solved as CP-SAT feasibility (8 workers).

## Validation of the pipeline

- Trivial group (G=1) on three known-EXISTING census entries reproduces designs instantly:
  (5,5;1,2,5;5,4), (8,8;4,1,6;6,4), (6,12;4,2,8;4,4) → SAT, and each witness passes the
  independent checker `solutions/P14/verify.py` (PASS).
- Trivial group on a known-NONEXISTENT entry (10,10;3,1,5;5,2) (census Nd=0) → INFEASIBLE (0.4 s),
  i.e. the encoding is exact, not just sufficient.

## Group sweep (results filled in as runs complete)

See `sweep1.log` etc. STATUS line at bottom.
