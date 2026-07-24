# P16 childL — Conjecture J: clause (b) reduced to one single-edge inequality; clause (a) settled over the pool universe by an exclusion lemma

**Status: PROOF INCOMPLETE** (no counterexample; the failure set of Conjecture
J is still empty after targeted adversarial search). This file contains only
rigorous statements plus clearly-labelled verified-but-unproved conjectures.
Every identity is machine-verified (`verify_sympy.py` symbolic;
`exp5_symbolic.py` exhaustive-exact n ≤ 7).

Context: childH proved Bound 44 ⇐ Conjecture H; childJ proved H ⇐ Conjecture J
(`../childJ/PROOF_H.md` §2). Notation as there: e = ij, s_e = dᵢ+dⱼ,
z1 = A_L²1, zs = A_L²s, w = zs − s·z1, arg44, B₂(e), ρ₀(e) = max_{B₂(e)} arg44,
T_e = dᵢmᵢ+dⱼmⱼ−2dᵢdⱼ, z1_e = (s_e−2)²+T_e.

**Conjecture J** (childJ). Connected G, n ≥ 3; for every ordered edge pair
(e,f) and every ρ ≥ max(ρ₀(e), ρ₀(f)):
(a) if z1_f ≤ ρ ≤ z1_e then q_{e,f}(ρ) := (ρs_f−zs_f)(z1_e−ρ) − (ρs_e−zs_e)(z1_f−ρ) ≥ 0;
(b) if ρ ≤ z1_e then ρs_e − zs_e + s_f(z1_e−ρ) ≥ 0, strict when ρ < z1_e.

Call an edge g **heavy at ρ** if z1_g > ρ, **light** if z1_g < ρ.

## 1. Warning: the "s_f = 2" shortcut for clause (b) is FALSE

s_f appears in (b) with coefficient z1_e − ρ ≥ 0, so the worst case is
minimal s_f — but the correct floor is **s_f ≥ 3**, not 2: in a connected
graph with n ≥ 3 no edge has two degree-1 endpoints. The s_f = 2 relaxation
is genuinely false: for the T₂-center configuration (s_e,z1_e,zs_e) =
(7,19,109), ρ = ρ₀ = 14 (`Li_GS?@?S??@?A` of childJ §3):
ρs_e − zs_e + 2(z1_e−ρ) = 98 − 109 + 10 = **−1 < 0**, while with s_f = 3 the
value is +4. Successors: do not "simplify" to s_f = 2.

## 2. Theorem L1: clause (b) ⇔ two single-edge statements

Define, for a single edge e:

  **(B)**  if z1_e > ρ₀(e) then D_e := ρ₀(e)(s_e−3) + 3z1_e − zs_e > 0;
  **(W=)** if z1_e = ρ₀(e) then w_e = zs_e − s_e z1_e ≤ 0.

**Theorem L1.** (B) ∧ (W=) (for every edge of every connected graph, n ≥ 3)
implies clause (b) of Conjecture J. Conversely clause (b) implies both
(take f = a minimum-s edge resp. ρ = z1_e; (B) also needs f with s_f = 3,
so strictly the forward direction is what matters).

*Proof.* Fix (e,f) and ρ with max(ρ₀(e),ρ₀(f)) ≤ ρ ≤ z1_e. Let
g(ρ, s_f) := ρs_e − zs_e + s_f(z1_e−ρ). It is affine in s_f with coefficient
z1_e − ρ ≥ 0 and s_f ≥ 3, so g(ρ,s_f) ≥ g(ρ,3) =: g₃(ρ), with equality only
if s_f = 3 or ρ = z1_e. g₃(ρ) = ρ(s_e−3) + 3z1_e − zs_e is affine
nondecreasing in ρ (s_e ≥ 3), so for ρ ≥ ρ₀(e): g₃(ρ) ≥ g₃(ρ₀(e)) = D_e.
Case z1_e > ρ₀(e): (B) gives D_e > 0, hence g(ρ,s_f) ≥ g₃(ρ) > 0 for every
admissible ρ ≤ z1_e — this is (b) including strictness (indeed strict even
at ρ = z1_e). Case z1_e = ρ₀(e): the only admissible ρ with ρ ≤ z1_e is
ρ = z1_e, where g(z1_e,s_f) = z1_e s_e − zs_e = −w_e ≥ 0 by (W=); strictness
is not required at ρ = z1_e. ∎  (Algebra machine-verified, V-2 of
`verify_sympy.py`.)

So clause (b) — a two-edge, ray-quantified statement — is EQUIVALENT to a
single-edge, single-point statement about heavy edges.

## 3. Structural identities for (B)  (proved; sympy + exhaustive n ≤ 7)

Since s = A_L1 + 2·1, we get zs = A_L³1 + 2·A_L²1, i.e.

  **(I6)** Σ_{f ∼_L e} z1_f = (A_L z1)_e = zs_e − 2 z1_e.

Since e has s_e − 2 line-graph neighbors, for any ρ:

  **(I7)** (z1_e − ρ) − Σ_{f∼e}(z1_f − ρ) = 3z1_e − zs_e + (s_e−3)ρ.

Hence with D_e(ρ) := ρ(s_e−3) + 3z1_e − zs_e:

- **Excess-contraction form.** (B) ⇔ for heavy e at ρ ≥ ρ₀(e):
  Σ_{f∼e} (z1_f − ρ) < z1_e − ρ — the line-graph neighbors of a heavy edge
  carry, in total, strictly less z1-excess over the level than the edge
  itself. (The z1-excess z1_g − ρ is the natural "heaviness"; note many
  neighbors are light and contribute negatively.)
- **c = −3 form.** With v := s − 3·1 ≥ 0 (entrywise, n ≥ 3):
  (B) ⇔ (A_L²v)_e < ρ v_e for heavy e, i.e. U_e(ρ) > −3: **the shifted-sum
  weight with c = −3 satisfies every heavy (upper-bound) constraint.** Only
  the light side of c = −3 fails (childJ's T₁); this is the exact split of
  the failed fixed-c certificate into its true half.
- **Vertex closed form** (via childH H2; `exp5_symbolic.py`):
  D_e(ρ) = ρ(x+y−3) + 12 − Φᵢ − Φⱼ, where x = dᵢ, y = dⱼ and
  Φᵢ = Pᵢ + Wᵢ + mᵢx(x−7) + x³ − 7x² + 16x = Σ_{k∼i}[z1_{ik} − 3s_{ik} + 12].

## 4. Verification record for (B)/(W=)  (exact rational arithmetic throughout)

| class | count | result | min D_e over heavy edges |
|---|---|---|---|
| connected 3 ≤ n ≤ 9 | 273,191 | 0 violations (`exp1_clauseb.py`, `cl_b_n9.log`) | **1** |
| trees 3 ≤ n ≤ 16 | 32,506 | 0 violations (`cl_b_trees.log`) | 2 |
| childE hard sets (190 n=10 + 8 n≤9) | 198 | 0 violations | 11/2 |
| random (trees/ER/core+pendant/BA, n ≤ 60) | 400 | 0 violations (`exp9.log`) | 29/3 |

The identity (I6) was asserted on every edge of every graph in the n ≤ 9 run.

**Tight cases** (`exp3_tightB.py`, `exp4_tightdump.py`): min margin D_e = 1,
attained only at near-3-regular graphs (`GCpb`o`, `GCXecW`, `G?ovF?`, n = 8):
heavy e has s_e = 6, z1_e = 15, ρ₀ = 14, arg44 ≡ 14 on the whole 2-ball,
three heavy neighbors (z1 = 15, excess +1) and one light neighbor
(z1 = 11, excess −3). At exact regularity z1 = arg44 = (s−2)² and the
premise z1 > ρ₀ fails; (B) is the statement that the first near-regular
perturbation already contracts. Any proof must be exact here — no room for
a lossy step (compare d-regular: everything collapses to equality).

## 5. Failed proof routes for (B)  (documented so successors skip them)

1. **1-ball version is FALSE**: with ρ₁(e) = max_{B₁(e)} arg44 in place of
   ρ₀(e), (B) fails at `G?`acK` (n = 8), margin −2/3 (`exp2_b1ball.py`).
   The 2-ball radius is necessary already for clause (b), not just (a).
2. **Per-neighbor bounds fail**: z1_f − ρ ≤ X_f := z1_f − arg44_f summed
   over f ∼ e (i.e. Σ_f X_f < z1_e − ρ) fails 3,478 times at n ≤ 8
   (min −524/25); the positive-part variant fails 13,550 times
   (`exp3_tightB.py`). The light neighbors' negative excesses are essential.
3. **Uniform first-shell multiplier certificate fails**: subtracting each
   first-shell slack (ρ − arg44_f) once plus the premise slack (z1_e − ρ)
   once makes ρ cancel exactly, leaving a ρ-free residual R in
   (x,y,mᵢ,mⱼ,Pᵢ,Pⱼ,Wᵢ,Wⱼ,Nᵢ,Nⱼ) (`exp6_residual.py`) — but R ≥ 0 is false
   (min −184/7 on heavy edges n ≤ 8, `exp6b_scan.py`).
4. **LP over natural slack features** (premise, own, first shell, d-weighted
   first shell, 2-walk-weighted second shell): no nonnegative combination
   improves on the trivial bound on the sample set (`exp8_lp.py`) — the
   optimum puts zero weight on every slack. The mechanism that makes (B)
   true is not a linear combination of these slacks; it is the forced
   coexistence of light neighbors next to heavy ones (§4's tight pattern).

## 6. Clause (a): the ψ/q-identity and the conflict search

**(I8)** With E := z1_e − ρ ≥ 0, F := ρ − z1_f ≥ 0 (the clause-(a) window):
q_{e,f}(ρ) = EF(s_f − s_e) − w_f E − w_e F, so for E,F > 0:
q ≥ 0 ⇔ ψ_f(ρ) ≤ ψ_e(ρ) in childJ's uniform ψ-form (V-1, sympy).
By (I8) and (B), if w_f ≤ (s_f−3)F (i.e. ψ_f(ρ) ≤ −3) then q > 0
outright; so **only light edges with ψ_f(ρ) > −3 (in particular w_f > 0)
can ever conflict with a heavy edge**.

**Adversarial cross-graph conflict search** (`exp7b_fast.py`): pool = all
connected graphs n ≤ 8, all trees n ≤ 17, the 198 childE/childH hard graphs
(93,444 graphs; 42,952 distinct light tuples (s,z1,zs,ρ₀) with w > 0 and
4,774 distinct heavy tuples). For every cross pair, minimize q exactly over
the admissible window [max(ρ₀ᵉ,ρ₀ᶠ,z1_f), z1_e] (endpoints + interior
stationary point, Fraction arithmetic). Result:

> **Exactly ONE conflicting pair** in ~205 million: light (3,4,21,ρ₀=14) vs
> heavy (7,19,109,ρ₀=14), min q = −5 — precisely childJ's T₁-pendant /
> T₂-center obstruction, recovered from scratch.

## 7. Lemma X: the unique conflict is unrealizable (PROVED)

**Lemma X.** Let G be connected and contain an edge f with
(s_f, z1_f, zs_f) = (3, 4, 21) and ρ₀(f) ≤ 14. Then G ≅ T₁ = `HkE?K?@`
(spider: center degree 4, four legs of length 2).

*Proof.* s_f = 3 forces d = (2,1) up to order: f = ij, dᵢ = 2, dⱼ = 1
(dᵢ = dⱼ = 1 would give G = K₂). Let k be the other neighbor of i, g = ik.
The only line-graph neighbor of f is g, so z1_f = s_g − 2 = dᵢ + d_k − 2 =
d_k, hence **d_k = 4**; and mᵢ = (dⱼ+d_k)/2 = 5/2. Next
zs_f = M_g − 2s_g with M_g = dᵢ(dᵢ+mᵢ) + d_k(d_k+m_k) = 9 + 16 + 4m_k, so
zs_f = 21 forces **m_k = 2**, i.e. Σ_{x∼k} d_x = 8: besides i (degree 2),
k has three more neighbors with degree sum 6. Every edge kx (x ∼ k, x ≠ i)
is at line-distance 2 from f, so ρ₀(f) ≤ 14 gives
arg44_{kx} = 2(9 + (d_x−1)² + 2m_x − 4d_x) ≤ 14.
If d_x = 1 then m_x = d_k = 4 and arg44 = 26 > 14 — impossible; so each of
the three satisfies d_x ≥ 2, and their degree sum is 6, forcing
**d_x = 2 for all three** (and for x = i). Then the constraint reads
1 + 2m_x ≤ 6, i.e. m_x ≤ 5/2; but m_x = (d_k + d_w)/2 = (4+d_w)/2 ≥ 5/2
where w is x's other neighbor, so m_x = 5/2 and **d_w = 1**: every neighbor
of k is a degree-2 vertex whose other neighbor is a leaf. All degrees of
all reached vertices are now saturated, so this component is exactly T₁,
and G connected ⇒ G = T₁. ∎ (Arithmetic sympy-verified, V-4; scan
confirmation: in all 354,326 pool graphs the tuple occurs 8 times, all in
graphs canonically equal to T₁, `exp10_lemmaX.py` + nauty-labelg.)

**Corollary X1.** T₁ has no heavy edge at any admissible level: its edges
have z1 ∈ {4, 13} and ρ₀ ≡ 14, so z1 < ρ₀ everywhere (verified exactly).
Hence no connected graph contains both the light tuple (3,4,21,ρ₀≤14) and
ANY heavy edge usable at ρ ≥ 14 together with it — in particular the unique
conflicting pair of §6 can never occur inside one graph.

**Theorem L2 (pool-complete clause (a)).** For every connected graph G and
every edge pair (e,f) of G whose tuples (s,z1,zs,ρ₀) both occur in the §6
pool tuple-sets, clause (a) of Conjecture J holds for all admissible ρ.
*Proof.* q_{e,f}(ρ) < 0 at an admissible ρ requires the (light,heavy) tuple
pair to be a §6 conflict, and the only one is excluded by Lemma X /
Corollary X1. ∎

This turns childJ's "exclusion mechanism" intuition into an actual proof
for the entire tuple universe seen so far: the binding light configuration
pins its whole component, and that component contains no heavy partner.

## 8. Honest status and route map

- **Rigorous:** Theorem L1 (clause (b) ⇔ (B) ∧ (W=)), identities I6–I8 and
  the closed form of D_e, Lemma X + Corollary X1 + Theorem L2, and the
  negative results of §1/§5.
- **Verified, unproved:** (B) and (W=) themselves (273k graphs n ≤ 9, trees
  ≤ 16, hard sets, 400 random n ≤ 60; min margin 1 at near-3-regular
  graphs); clause (a) beyond the pool tuple universe.
- **What remains for a full proof of J:**
  1. Prove (B): Σ_{f∼e}(z1_f−ρ) < z1_e−ρ for heavy e. All linear-slack
     routes fail (§5); the truth lives in the constraint that arg44 ≤ ρ on
     the whole 2-ball while z1_e > ρ, which forces enough light neighbors.
     Suggested angle: classify the neighbor excess vector directly — in
     every tight case the 2-ball is arg44-constant; try an exchange
     argument perturbing towards regularity, where (B) degenerates to the
     (true, strict) statement 3z1 > zs + o(1) off-regularity. A margin
     conjecture D_e ≥ 1 (integer-valued in all extremal cases) may be the
     right induction target.
  2. Prove (W=): w_e ≤ 0 when z1_e = ρ₀(e) (childJ's V1 at one point).
  3. Clause (a) beyond the pool: enumerate ABSTRACT realizable 2-ball
     tuples (s,z1,zs,ρ₀) parametrically (degrees ≤ 2+√(2ρ+4)+2 via
     arg44_g ≥ (s_g−2)²/2 − 2(s_g−2), which holds since m ≥ 1) and show
     every conflicting pair is unrealizable by the Lemma-X pinning
     mechanism. The scan says conflicts are extraordinarily rare (1 in
     2·10⁸); the proof should show a conflict forces ψ_f(ρ) > −3 > ...
     pinned components with no heavy partner, exactly as in Lemma X.
- Files: `common.py` (exact 2-ball environment; sparse6 support),
  `exp1_clauseb.py` (B/W= scans), `exp2_b1ball.py`, `exp3_tightB.py`,
  `exp4_tightdump.py`, `exp5_symbolic.py` (D_e closed form),
  `exp6_residual.py`/`exp6b_scan.py`, `exp7b_fast.py` (conflict search;
  `exp7_crosspool.py` slow exact version), `exp8_lp.py`, `exp9_random.py`,
  `exp10_lemmaX.py`, `verify_sympy.py`; logs `cl_b_n9.log`,
  `cl_b_trees.log`, `exp6b.log`, `exp7b.log`, `exp9.log`, `exp10.log`.

**PROOF NOT COMPLETE.** Conjecture J stands. Clause (b) is now a single
inequality (B) about one heavy edge; clause (a) is proved over the entire
observed tuple universe via Lemma X, and the remaining gap is the
parametric version of that exclusion plus (B)/(W=).
