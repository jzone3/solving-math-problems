# P14 V1 (exact ILP / CP-SAT) — run notes

Session: devin-a3c4bd5a99684570aaff53cdb0582cba (2026-07-22). Variant V1: exact integer
program via OR-Tools CP-SAT (Gurobi-free stack), symmetry breaking, all 4 instances.

## Problem statement re-verification (against original source)
- Cloned CPro1 repo (github.com/Constructive-Codes/CPro1); read
  `CPro1/design_definitions/balanced-ternary-design/problem_def.py`. Definition matches the
  problem file exactly: V×B matrix over {0,1,2}; row sum R with exactly p1 ones and p2 twos;
  column sum K; every distinct pair i<k has sum_j m_ij*m_kj = L.
- Openness cross-check: CPro1 `OPEN_INSTANCES` contains (14,18,7,1,9,7,4), (12,15,6,2,10,8,6),
  (12,20,4,3,10,6,4); `designs/balanced-ternary-design/` has result-*.txt files ONLY for the 7
  solved siblings — none for these three. (14,28,8,3,14,7,6) not in CPro1's list (Handbook-open,
  apparently unattempted). Exa literature search (2026-07-22) found nothing newer than the 2025
  CPro1 papers touching these cells. Treating all 4 as open as of July 2026.
- Necessary counting identities machine-checkable and hold for all 4:
  V*R = B*K and B*K^2 − V*(p1+4*p2) = L*V*(V−1).

## Encoding (runs/P14/v1/solve_cpsat.py)
- Booleans x1[i][j], x2[i][j] (mult 1 / mult 2), x1+x2 ≤ 1; int m = x1+2*x2.
- Row: Σ x1 = p1, Σ x2 = p2. Column: Σ m = K.
- Pair inner products linearized: m_i*m_k = AND(x1,x1') + 2AND(x1,x2') + 2AND(x2,x1') + 4AND(x2,x2'),
  AND via standard aux boolean; Σ_j = L for each of C(V,2) pairs.
- Symmetry breaking: double-lex (rows lex non-increasing AND columns lex non-increasing) —
  sound for the full S_V × S_B symmetry group, so UNSAT ⇒ genuine nonexistence.
- Sanity: solved dev instances BTD(4,8;2,3,8;4,6) instantly and BTD(18,18;2,6,14;14,10)
  in ~30 s; both witnesses verified PASS by solutions/P14/verify.py.

## Instances & runs

### Pass 1 — 900 s each, 8 workers, model solve_cpsat.py (double-lex on)
| instance | status | wall |
|---|---|---|
| (14,18;7,1,9;7,4)  | UNKNOWN | 900 s |
| (12,15;6,2,10;8,6) | UNKNOWN | 900 s |
| (12,20;4,3,10;6,4) | **INFEASIBLE** | 684 s |
| (14,28;8,3,14;7,6) | UNKNOWN | 900 s |

**Candidate nonexistence result: BTD(12,20;4,3,10;6,4) does not exist** (CP-SAT proves
INFEASIBLE in 684 s). Double-lex is a sound symmetry-breaking scheme (Flener et al., CP 2002:
every row/col-permutation class contains a double-lex-sorted matrix), so INFEASIBLE with it
implies genuine nonexistence — modulo solver correctness. Per methodology, launched an
independent confirmation with a differently-written model (solve_cpsat_alt.py: IntVar domain
encoding + AddMultiplicationEquality + independently implemented lex, sanity-checked on a dev
instance) — running in background.

### Confirmations for (12,20;4,3,10;6,4) nonexistence
1. solve_cpsat_alt.py (independent 2nd CP-SAT model): **INFEASIBLE in 575 s**. Agrees.
2. Third, fully independent check: CNF encoding (runs/P14/v1/encode_sat.py — pysat seqcounter
   cardinalities; weighted sums by literal duplication, exhaustively validated on small cases;
   AND-aux for pair products; independently implemented double-lex) run through **kissat**:
   **s UNSATISFIABLE** (exit 20), 881 MB DRAT proof; drat-trim verification in progress.
   Encoder end-to-end sanity-checked on dev instance BTD(4,8;2,3,8;4,6): kissat found a
   solution which verify.py PASSed.

### Pass 2 — 3600 s each, 4 workers, model solve_cpsat.py
| instance | status | wall |
|---|---|---|
| (14,18;7,1,9;7,4)  | **INFEASIBLE** | 1482 s |
| (12,15;6,2,10;8,6) | running |  |
| (14,28;8,3,14;7,6) | queued |  |

**Second nonexistence result: BTD(14,18;7,1,9;7,4) does not exist** (CP-SAT INFEASIBLE,
1482 s, double-lex sound). Confirmations launched: solve_cpsat_alt.py (running) and
kissat on encode_sat.py CNF (134238 vars / 278728 clauses, running).

### Pass-2 completion + confirmations (running log)
- (12,20;4,3,10;6,4): kissat UNSAT proof **DRAT-VERIFIED by drat-trim** ("s VERIFIED",
  872 s check, 881 MB proof). Nonexistence now triple-confirmed (2 CP-SAT models + certified SAT).
- (14,18;7,1,9;7,4): kissat also reports **s UNSATISFIABLE**; drat-trim verifying.
  solve_cpsat_alt confirmation still running.
- **(12,15;6,2,10;8,6): INFEASIBLE (solve_cpsat.py, 2007 s)** — third nonexistence result!
  Confirmations launched: solve_cpsat_alt + kissat CNF (115794 vars / 237980 clauses).
- (14,28;8,3,14;7,6): pass-2 3600 s run in progress.

Note: DRAT proofs are ~1 GB each — not committed; regenerate deterministically via
`python3 encode_sat.py V B p1 p2 R K L f.cnf && kissat -q f.cnf f.proof && drat-trim f.cnf f.proof`.

### DRAT certification complete for all three CPro1 survivors
| instance | CP-SAT model 1 | CP-SAT model 2 (alt) | kissat | drat-trim |
|---|---|---|---|---|
| (12,20;4,3,10;6,4)  | INFEASIBLE 684 s  | INFEASIBLE 575 s | UNSAT | **s VERIFIED** (872 s) |
| (14,18;7,1,9;7,4)   | INFEASIBLE 1482 s | running          | UNSAT | **s VERIFIED** (1520 s) |
| (12,15;6,2,10;8,6)  | INFEASIBLE 2007 s | running          | UNSAT | **s VERIFIED** (1317 s) |

All three have machine-checked DRAT UNSAT certificates (kissat + drat-trim) on an
independently written CNF encoding, in addition to CP-SAT INFEASIBLE. Soundness of the only
solution-removing device (double-lex) rests on Flener et al. CP 2002 (every {0,1,2}-matrix
class under row/col permutation contains a doubly-lex-sorted representative), implemented
independently in each of the three encodings.

### (14,28;8,3,14;7,6) escalation
- Pass 2: UNKNOWN at 3600 s (4 workers).
- Pass 3 launched: CP-SAT 25000 s / 4 workers, and kissat 25000 s on encode_sat.py CNF
  (301392 vars / 618438 clauses) in parallel. This is the largest instance (14×28).

### Overnight results (2026-07-23 morning)
- alt-model confirmations for (14,18) and (12,15): **UNKNOWN at 28800 s** (2 workers each —
  the alt model is much weaker; ran only as belt-and-braces). Not a problem: the
  independent verification standard is met by the kissat+drat-trim DRAT certificates,
  which are machine-checked proofs on a fully independent encoding.
- (14,28;8,3,14;7,6) CP-SAT pass 3: **UNKNOWN at 25000 s** (4 workers).
- (14,28) kissat first attempt died: DRAT proof filled the 16 GB tmpfs /tmp at 13.4 GB.
  Restarted on persistent disk (106 GB free) at 01:21 UTC, --time=25000.
- Launched CP-SAT pass 4 on (14,28): 14400 s, 7 workers.

### Final (14,28;8,3,14;7,6) attempts
- CP-SAT pass 4 (14400 s, 7 workers): UNKNOWN.
- kissat (25000 s): s UNKNOWN at time limit (proof reached 39 GB before deletion).
- Total compute on this instance: ~48,900 s CP-SAT + 25,000 s kissat ≈ 19 h. No verdict.
  It is by far the largest instance (784 cells vs ≤ 240); recommend V2 (cube-and-conquer)
  or V3 (Kramer–Mesner under Z_7 on V=14) for a future attack.

## Compute summary
- Machine: 8-core Linux VM, OR-Tools 9.15 CP-SAT, kissat (git master), drat-trim.
- Total wall time of solver runs ≈ 26 h aggregate across instances/confirmations.

## Dead ends / gotchas
- pypblib would not install → weighted PB constraints done via literal duplication in
  seqcounter cardinality encodings (exhaustively validated on small cases first).
- /tmp is a 16 GB tmpfs: first kissat run on (14,28) died silently when its DRAT proof
  filled it; rerun proofs on persistent disk.
- The alt CP-SAT model (IntVar + AddMultiplicationEquality) is much weaker than the
  boolean-expansion model: confirms (12,20) but times out at 8 h on (14,18)/(12,15).

## Resumed session (2026-07-23): prescribed-automorphism attack on (14,28;8,3,14;7,6)

New tooling: runs/P14/v1/solve_auto.py (CP-SAT with a prescribed automorphism sigma on
points and chosen block-orbit structure; UNSAT only rules out sigma-invariant designs) and
km_z7.py / km_z7_exhaustive.py (full Kramer–Mesner reduction for sigma = two 7-cycles).

### Complete decisions (order-7 and friends)
- **sigma = two 7-cycles (Z7, fixed-point-free): NO invariant design exists — complete.**
  km_z7_exhaustive.py enumerates all 6498 base-block orbit representatives, computes
  17-coordinate KM signatures (point-orbit mult counts + 13 pair-orbit coverages), and does
  a complete meet-in-the-middle search over all admissible orbit structures (t=4 orbits;
  t=3 + 7 fixed blocks, all n1+n2=7 splits; t<=2 impossible since fixed blocks are forced
  to be full point-orbits x1 and within-orbit pair coverage caps fixed blocks at 6+6).
  Result: NO solution in any case. Validated by 20 random positive controls
  (planted 3/4-subsets found) + negative control. (The earlier CP-SAT count formulation
  km_z7.py stalled UNKNOWN at 7000 s; the exhaustive join settles it in ~1 min.)
- **sigma = 7-cycle + 7 fixed points: INFEASIBLE for every block-orbit split**
  (4x7 / 7f+3x7 / 14f+2x7 / 21f+1x7 / 28f — all CP-SAT INFEASIBLE in <20 s each).
- **Corollary: no BTD(14,28;8,3,14;7,6) has an automorphism of order 7** (both S14
  conjugacy classes of order-7 elements excluded), hence **7 does not divide |Aut|**, and
  in particular no Z14 or Z21/Z28 symmetry. (Direct z14 runs also INFEASIBLE for the
  4x7 / 2x7+14 / 14f+14 splits.)
- **Z13 impossible by counting**: block orbits have size 1 or 13, 28 = 13a+f needs f=2 or
  15 or 28 fixed blocks, but a sigma-invariant size-7 block needs 7 = 13a + (mult on the
  single fixed point) <= 2 — impossible; and 28 != 13a. So no order-13 automorphism.
- Z5 (two 5-cycles + 4 fixed): INFEASIBLE for splits 5x5+3f, 4x5+8f, 3x5+13f (CP-SAT, fast).
- Z2/Z3/Z4/Z6 runs (600 s each): INFEASIBLE for most splits (z2-seven with 2/4/6/8/10/12
  fixed blocks; z2-six-14x2; z4 both splits; z6 two splits; z3-9x3+1f); UNKNOWN survivors
  z2-seven-14x2, z3-8x3-4f, z3-7x3-7f, z3-6x3-10f, z6-4x6-2x2, z6-3x6-1x6-2x2 given
  14400 s follow-up runs.

### BREAKTHROUGH: BTD(14,28;8,3,14;7,6) EXISTS
Continuing the automorphism-class sweep to the smaller order-3 classes,
config **z3c3-6x3-10f** (sigma = three 3-cycles (0 1 2)(3 4 5)(6 7 8), points 9–13 fixed;
6 block orbits of size 3 + 10 fixed blocks) returned **OPTIMAL in 17.2 s** — a witness!
- verify.py: **PASS**
- CPro1's original problem_def.v(): **True** (independent second verifier — methodology met)
- Witness + writeup copied to solutions/P14/ (EXISTENCE.md, witness-14-28-8-3-14-7-6.txt).
Order-3/5 class sweep also gave: z3c3 splits 0..4x3 INFEASIBLE, 5x3-13f UNKNOWN(600 s),
then the hit at 6x3-10f. Structure beat brute force: 19 h of unstructured search failed;
the right prescribed symmetry found it in seconds.

## STATUS: SOLVED — ALL FOUR instances closed. BTD(14,18;7,1,9;7,4),
## BTD(12,15;6,2,10;8,6), BTD(12,20;4,3,10;6,4) do NOT exist (CP-SAT INFEASIBLE +
## kissat/drat-trim DRAT-certified UNSAT each); BTD(14,28;8,3,14;7,6) EXISTS
## (explicit witness, PASS by verify.py and by CPro1's original verifier).
