# P14 — V5 (nonexistence attack) — NOTES

Session: https://app.devin.ai/sessions/edba29d88f024bee9027b77c70d9b87a
Variant: V5 = counting / divisibility / linear-algebra nonexistence proofs.

Instances (V,B; r1,r2,R; K,L):
- I1 = (14,18; 7,1,9; 7,4)   theta = r1+4r2-L = 7
- I2 = (12,15; 6,2,10; 8,6)  theta = 8
- I3 = (12,20; 4,3,10; 6,4)  theta = 12
- I4 = (14,28; 8,3,14; 7,6)  theta = 14

Model: N in {0,1,2}^{V x B}; row = r1 ones + r2 twos; column sums K;
N N^T = theta I + L J.

## 0. Statement re-verification / literature check (2026-07-22)
- Definition confirmed against Kunkle–Sarvate "Balanced (part) ternary designs"
  (CRC Handbook ch. entry, kunklet.people.charleston.edu/section.pdf) and their
  JCMCC paper 93_01.pdf. Parameters match Handbook row numbers: I1 = row 43
  ([3] numbering) / #15 in Kunkle table; I2 = #31; I3 = #33; I4 = row 234/#121.
- Kaski–Östergård, "Enumeration of balanced ternary designs", DAM 138 (2004):
  their web table (users.ics.aalto.fi/pkaski/btd.html) leaves exactly these rows
  (43, 76, 79, 234) with blank Nd/Ns — unclassified, consistent with open.
- Kunkle–Sarvate table: for I1 the only OPEN b2 value is 14 = V*r2, i.e. the
  literature has (apparently) ruled out any block containing 2+ doubled elements
  for I1; reference [7,(2.2)] and [4]. (Not re-derived here yet; noted as a
  published restriction, used only as a cross-check target for our relaxations.)
- Conclusion: statement is faithful to the source; all 4 instances still open.

## 1. Standard necessary conditions (conditions.py) — machine-verified
All four instances PASS every classical condition:
R=r1+2r2, VR=BK, L(V-1)=RK-(r1+4r2) (= r1(K-1)+2r2(K-2)),
global pair count, Fisher (Gram is PD: theta>0, so B>=V; holds).
No divisibility obstruction at this level.

## 2. Linear algebra / lattice obstructions (gram_lattice.py)
- Gram G = theta I + L J is positive definite (theta>0) with det theta^(V-1)(theta+LV).
- Rational representability of G by I_B (Hasse–Minkowski): codim B-V is
  4, 3, 8, 14 >= 3, so no rational obstruction exists (verified; Hasse
  invariants computed for the record).
- mod 2: singles matrix S=N mod 2 satisfies S S^T = theta I + L J (mod 2):
  I1: SS^T=I -> rank_2(S)=14<=18 OK (needs r1 odd: 7 ✓).
  I2,I3,I4: SS^T=0 -> rows of S form a self-orthogonal binary code (needs r1
  even ✓); dim bounds B/2 all satisfiable. I4: sum of rows = all-ones (K odd),
  1_B in code, weight 28 even ✓.
- NO linear-algebra contradiction found.

## 3. Counting-relaxation ILPs (counting_ilp.py = L1+L2, profile_ilp.py = +L3)
Exact double-counting consequences turned into integer feasibility problems
(CBC): infeasible would equal a nonexistence proof.
- L1: block-type counts n_d (d = #doubles per block) x pair-type counts P_(a,b,c)
  with a+2b+4c=L; five coupling identities. All 4 instances FEASIBLE.
- L2: ordered block-pair signatures (n11,m12,m21,n22) coupled per block type d
  (exact marginals (K-2d)(r1-1), d*r1, (K-2d)r2, d(r2-1) per block), z- and
  y-couplings to P_t. All 4 FEASIBLE.
- L3: element profiles ((u_d),(w_d)) x oriented neighbor types (a,beta,gamma,c),
  full marginal + orientation-symmetry + 2P_t couplings. All 4 FEASIBLE.
  (Feasible solutions do not respect the published I1 restriction n_{d>=2}=0,
  confirming these relaxations are strictly weaker than known case analysis.)

## 4. Grand unified ILP (grand_ilp.py) — two-point closure
L1+L2+L3 + ALL two-point trace identities: T1 trace((N^TN)^2)=(V-1)theta^2+tau^2;
T2..T4 trace((AA^T)^2),((SS^T)^2),((DD^T)^2); T5 trace(SD^T DS^T); T6
trace(SS^T DD^T); T8 trace((SD^T)^2); T10 trace(AA^T NN^T); T11 trace(SS^T NN^T);
T12 trace(DD^T NN^T); forbidden n22>=2 (two blocks sharing 2 common doubles
force a pair with coverage >= 8 > L).

IMPORTANT incident: the first version had a wrongly derived T10
(assumed trace(AA^T NN^T) decomposes as sum y*z; correct block-side entry is
(A^T N)_{bb'} = n11+m12+2(m21+n22)). The buggy model returned INFEASIBLE for
I1, I2, I4 — a false "nonexistence proof". Caught by mandatory validation:
validate_model.py recomputes every identity on explicit known BTDs
(BTD(4,9;3,3,9;4,7) and BTD(4,8;2,3,8;4,6) from Kunkle–Sarvate, plus a fresh
CP-SAT-found BTD(8,20;8,1,10;4,4) with r2=1). After the fix all three test
designs PASS all identities, and the grand ILP is FEASIBLE for ALL FOUR
instances. Also: forcing n_2+n_3>=1 for I1 stays feasible, so the two-point
relaxation cannot even re-derive the published b2=14 restriction for I1 —
counting at the 2-point level is definitively too weak to kill any cell.
CONCLUSION of the pure-counting program: negative (documented; no
Fisher/divisibility/rational-congruence/mod-p/2-point-counting obstruction
exists for any of the 4 instances).

## 5. Reduced algebraic formulation for I1 (reduced_i1.py)
r2=1 and (published, Kunkle–Sarvate table) b2=14 force: 14 blocks
{x_i,x_i} u S_i (bijection i<->x_i, |S_i|=5) + 4 pure 7-subsets. With T (14x14
0/1, zero diag, row sums 5), Q (4x14, row sums 7):
    N = [2I + T^T | Q^T],  N N^T = 7I+4J  <=>  T^T T + 2(T+T^T) + Q^T Q = 3I+4J.
Diagonal gives indeg_T(v) + colsum_Q(v) = 7. Eigenvalue corollary: on 1^perp,
2(T+T^T) = 3I - T^T T - Q^T Q <= 3I, so lambda_2(T+T^T) <= 3/2 — a directed-SRG-like
rigidity. CP-SAT decides this sector completely; the complementary sector
(some block with >= 2 doubles) is the 'force_multidouble' branch of the full model.

## 6. Complete CP-SAT decision runs (cpsat_btd.py) — V5 counting exhausted,
borrowing complete search (UNSAT = nonexistence proof)
Model: s/d indicator booleans, product ANDs for the 91/66 pair equations,
row/col lex symmetry breaking (sound: only removes isomorphic copies).
Sanity: finds known BTD(8,20;8,1,10;4,4) in 0.4 s (witness re-verified by
validate_model.py identities).
Runs (4h budget each, in progress): I1 full, I2 full, I1-reduced (b2=14 sector).

## 7. CP-SAT run results (8-core box, 4 workers each)
- I1 full  (14,18;7,1,9;7,4): UNKNOWN after 14400 s (no design found, no UNSAT).
- I2 full  (12,15;6,2,10;8,6): UNKNOWN after 14400 s.
- I1 reduced b2=14 sector (T,Q matrix equation, 252 booleans): UNKNOWN after
  14400 s — even the collapsed algebraic form resists a complete decision.
- I3, I4: launched 4 h runs (results below).
- I3 full (12,20;4,3,10;6,4): UNKNOWN after 14400 s.
- I4 full (14,28;8,3,14;7,6): UNKNOWN after 14400 s.
(~20 CPU-core-hours total across the five 4 h runs; no witness, no UNSAT.)

## Compute spent
- Counting ILPs: seconds-to-minutes each (CBC), all four instances, three levels.
- CP-SAT complete searches: 5 runs x 4 h wall (4 workers each) = ~80 core-hours.

## Dead ends / lessons
- Two-point (pair/block-pair/element-profile + all trace identities) counting
  closure is provably too weak: feasible for all 4 cells, and cannot re-derive
  even the published I1 b2=14 restriction. Any counting-based nonexistence
  proof must use >= 3-point structure or explicit case analysis.
- Rational congruence (Hasse-Minkowski) can never bite here: codim B-V >= 3.
- mod-2 self-orthogonal-code conditions are all satisfiable.
- False-infeasibility incident (buggy T10 trace identity) underscores the
  methodology rule: validate every identity against explicit known designs
  before trusting an infeasibility conclusion.

## STATUS: negative (no cell closed; frontier pushed)
No nonexistence proof and no design. Contributions: (i) machine-verified proof
that all classical counting/divisibility/linear-algebra obstructions vanish on
all four cells; (ii) a validated reusable two-point counting-ILP library;
(iii) a clean algebraic reformulation of I1's b2=14 sector as the 0/1 matrix
equation T^T T + 2(T+T^T) + Q^T Q = 3I + 4J (with lambda_2(T+T^T) <= 3/2
spectral corollary) — a compact target for future algebraic or SAT attacks;
(iv) first (to our knowledge) complete-solver attack on all four cells:
4 h CP-SAT each, all UNKNOWN — these cells are genuinely hard, not neglected-easy.
