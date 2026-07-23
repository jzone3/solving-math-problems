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

## Group sweep results

Groups prescribed (per V, as cycle types of a generator, plus a few non-cyclic):
- V=14: C14, C13, C11(11-cycle), D14, D7, F21, C7×C2, C7(7,7), C7f(7), C6(6,6), C5(5,5), C5(5),
  C4(4,4,4), C3(3^4), C3(3^3), C3(3^2), C3(3), C2(2^7), C2(2^6), C2(2^5), C2(2^4), C2(2^3), C2(2^2), C2(2)
- V=12: C12, C11, D12, D6, G12(|G|=12), C7(7), C6(6,6), C6(6+6 interleaved), C6(6), C5(5,5), C5(5),
  C4(4,4,4), C4(4,4), C3(3^4), C3(3^3), C3(3^2), C3(3), C2(2^6), C2(2^5), C2(2^4), C2(2^3), C2(2^2), C2(2)

### *** SOLVED: instance 4, BTD(14,28; 8,3,14; 7,6) EXISTS ***

- Found by CP-SAT on the Kramer–Mesner orbit ILP with prescribed **C3 = ⟨(0 1 2)(3 4 5)(6 7 8)(9 10 11)⟩**
  (two fixed points), 1786 s; a second witness under C3(3^3) (5 fixed points), 927 s.
- Witnesses: `witness_inst4_C3a.json`, `witness_inst4_C3b.json`; copied to
  `solutions/P14/witness_BTD_14_28_8_3_14_7_6{,_alt}.json`.
- Verified PASS by `solutions/P14/verify.py` AND by a second, differently-written numpy
  Gram-matrix check (M·Mᵀ has all off-diagonal entries 6, diagonal 20; column sums 7;
  rows have exactly 8 ones and 3 twos).
- This is the Handbook-open cell that CPro1 apparently never attempted.

### Negative results (INFEASIBLE = no design admits that automorphism)

- inst1 (14,18;7,1,9;7,4): INFEASIBLE for ALL groups tried with element order ≥ 3 —
  C14, C13, C11, D14, D7, F21, C7×C2, both C7 actions, C6, both C5 actions, C4, all four C3
  cycle types (3^4, 3^3, 3^2, 3). Hence **any BTD(14,18;7,1,9;7,4) has automorphism group a 2-group**
  (every element of odd prime order 3,5,7,11,13 and every 4-element/6-element pattern tried is excluded;
  note C4/C6 exclusions used one cycle type only, so precisely: no automorphism of order 3,5,7,11,13).
  C2 cycle types all UNKNOWN at 600 s (sweep 3 escalates to 7200 s).
- inst2 (12,15;6,2,10;8,6): INFEASIBLE for C12, C11, D12, D6, G12, C7, both C6 actions,
  C6(6), both C5 actions, C4(4,4), C4(4,4,4) (723 s), C3(3^3), C3(3^2) (543 s), C3(3) (256 s);
  UNKNOWN: C3(3^4) even @3600 s, and all C2 types @600 s.
  So no automorphism of order 4, 5, 6, 7, 11, 12; order 3 excluded except the fixed-point-free
  cycle type 3^4 (still open; being retried in sweep 3).
- inst3 (12,20;4,3,10;6,4): INFEASIBLE for everything of order ≥ 3 tried, including all C3 and C4,
  C5, C6, C7, C11, C12 types. Only C2 types outstanding.
- inst4 additionally INFEASIBLE for C14, C13, C11, C7 (7,7 — took 3491 s), C7f, C7×C2, D7, D14, F21,
  C6, C5 both, C4 — so the found designs' full automorphism groups are (multiples of) C3 but no
  larger odd-order/7-type symmetry exists.

### Compute log

- sweep1: all groups × 4 instances @ 600 s each (`sweep1.log`), ~4 h wall.
- sweep2: long reruns + extra prime cycle types @ 3600 s (`sweep2.log`), ~8 h wall;
  produced the instance-4 witnesses.
- sweep3: C2 cycle-type ladder @ 7200 s, two 4-worker lanes (`sweep3_lane{0,1}.log`):
  inst1 C2(2^7), C2(2^6) and inst2 C2(2^6), C2(2^5) all **UNKNOWN even at 7200 s**;
  ladder aborted in favour of targeted full-width runs.
- sweep4 (`sweep4.log`): 8 workers, 14400 s each — inst2 C3(3^4) fixed-point-free: UNKNOWN;
  inst1 C2(2^7) fixed-point-free: UNKNOWN. The order-2 (and inst2's fixed-point-free order-3)
  Kramer–Mesner subproblems halve the variable count but remain out of CP-SAT reach at ~4 h —
  they are nearly as hard as the unrestricted problems.

## Dead ends / near-misses

- No near-miss witnesses for instances 1–3: every decided prescribed group is INFEASIBLE
  (exact, not timeout), so within V3's method the only remaining room is order-2 prescriptions
  (undecided) or trivial group (V1/V2/V4 territory).
- Suggested follow-ups for other variants: instance 1's search should exploit ρ2=1
  (each element doubled in exactly one block); the C2 KM subproblems would suit a SAT encoding
  with cardinality networks (V2) better than CP-SAT integers.

STATUS: SOLVED (existence, instance 4 BTD(14,28;8,3,14;7,6) — verified witnesses in solutions/P14/);
frontier-pushed on instances 1–3 (all prescribed automorphisms of order ≥3 excluded; order-2 cases
undecided after ~30 h total compute); no nonexistence proofs obtained.
