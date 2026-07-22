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

## Next (in progress)
Grand unified ILP: L1+L2+L3 together + spectral second-moment identities
(trace((N^T N)^2) = (V-1)theta^2 + tau^2, Frobenius identities for S,D,A
matrices coupling W-, P-, Y-variables) + forbidden configurations from L<8
(n22<=1 always; m12,m21<=1 when L=4).
