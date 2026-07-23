# P16 childJ — Conjecture H: reduction to a pairwise 2-ball statement, and the death of every "c = φ(R)" shortcut

**Status: PROOF INCOMPLETE.** No counterexample to Conjecture H (the failure
set is still empty after all searches here). This file contains only rigorous
statements plus clearly-labelled verified-but-unproved conjectures. Every
identity and every inequality step of the proved lemmas is machine-verified
(`verify_sympy.py` symbolic; `exp5_identities.py` numeric exhaustive n ≤ 7).

Context: childH (`../childH/PROOF44.md`) proved Lemmas H1, H1′, H2,
Corollary H3 and reduced Bound 44 to **Conjecture H**: for every connected
graph with R := max_e arg44_e ≥ 0 there is c > −min_e s_e with
(A_L²(s+c))_e ≤ R(s_e+c) for all e ∈ E. Notation as there: e = ij,
s_e = dᵢ+dⱼ, M_e = dᵢ(dᵢ+mᵢ)+dⱼ(dⱼ+mⱼ), A_L = adjacency of L(G),
arg44_e = 2((dᵢ−1)²+(dⱼ−1)²+mᵢmⱼ−dᵢdⱼ). Shorthand throughout:

  z1_g := (A_L² 1)_g,   zs_g := (A_L² s)_g,   σ_g = z1_g − R,   κ_g = zs_g − R s_g.

## 1. New identities (proved; sympy-verified)

Let T_e := dᵢmᵢ + dⱼmⱼ − 2dᵢdⱼ. Then, for every edge e = ij:

  (I0)  M_e = s_e² + T_e                       (expand; trivial)
  (I1)  z1_e = (s_e−2)² + T_e                  (by childH Lemma H2, z1 = M−4s+4)
  (I2)  arg44_e = (s_e−2)² + (dᵢ−dⱼ)² + 2(mᵢmⱼ − dᵢdⱼ)
  (I3)  σ_e = (s_e−2)² + T_e − R
  (I5)  T_e = Σ_{k∼i,k≠j}(d_k−dⱼ) + Σ_{l∼j,l≠i}(d_l−dᵢ)

(I5) shows T_e measures how much the *second* neighborhood out-weighs the
opposite endpoints; T_e ≤ 0 for edges whose surroundings are lighter than the
edge itself, T_e > 0 for light edges attached to a dense core.

**ψ-form of the criterion.** Let w_g := zs_g − s_g·z1_g
= Σ_{2-walks g→f→h in L(G)} (s_h − s_g) (the total 2-walk "s-excess"), and for
ρ ≠ z1_g define

  ψ_g(ρ) := −s_g + w_g / (ρ − z1_g).

Then the per-edge test at level ρ, namely zs_g + c·z1_g ≤ ρ(s_g + c), reads:

  c ≤ ψ_g(ρ) if z1_g > ρ;   c ≥ ψ_g(ρ) if z1_g < ρ;   zs_g ≤ ρ s_g if z1_g = ρ.

(Elementary algebra: ρs_g − zs_g = (ρ − z1_g)s_g − w_g; sympy-verified I4.)
So the upper bounds U_e and lower bounds L_f of Corollary H3 are the *same
function* ψ evaluated on the two sides of the pole ρ = z1: Conjecture H says
the edges with z1 above R give ψ-values ≥ every ψ-value from edges below R.

## 2. Conjecture J (pairwise, 2-ball) — the sharpened target

For an edge g let B₂(g) = set of edges at line-graph distance ≤ 2 from g
(including g), and ρ₀(g) := max_{g′∈B₂(g)} arg44_{g′}. Note z1_g, zs_g, s_g
are determined by the isomorphism type of B₂(g) (with its degree data).

**Conjecture J.** Let G be connected, n ≥ 3. For every ordered pair of edges
(e, f) (f = e allowed) and every real ρ ≥ max(ρ₀(e), ρ₀(f)):

  (a) if z1_f ≤ ρ ≤ z1_e then
      q_{e,f}(ρ) := (ρs_f − zs_f)(z1_e − ρ) − (ρs_e − zs_e)(z1_f − ρ) ≥ 0;
  (b) if ρ ≤ z1_e then ρs_e − zs_e + s_f(z1_e − ρ) ≥ 0,
      with strict inequality whenever ρ < z1_e.

**Theorem J ⇒ H.** Conjecture J implies Conjecture H (hence Bound 44).

*Proof.* Fix connected G with R = max_e arg44_e ≥ 0. Then R ≥ ρ₀(g) for every
edge g, so ρ = R is admissible for every pair. Write the ord2-sum test as
c(z1_g − R) ≤ Rs_g − zs_g (g ∈ E), c > −min s.
(i) Edges with z1_g = R: clause (b) with e = g, ρ = R = z1_e gives
Rs_g − zs_g ≥ 0: constraint holds for every c.
(ii) If no edge has z1_g > R, only lower bounds L_f = (Rs_f − zs_f)/(z1_f − R)
occur; any c ≥ max(max_f L_f, 1 − min s) is feasible.
(iii) Otherwise let U = min over {e : z1_e > R} of U_e = (Rs_e−zs_e)/(z1_e−R),
attained at e*. For every f with z1_f < R, clause (a) applied to (e*, f) at
ρ = R ∈ [max(ρ₀), z1_{e*}] with z1_f ≤ R gives q ≥ 0, i.e. L_f ≤ U_{e*} = U
(divide by (z1_{e*}−R)(R−z1_f) > 0). For the positivity constraint take f = a
minimum-s edge: clause (b) strict at ρ = R < z1_{e*} gives U > −min s.
Hence c = U satisfies every constraint and c > −min s. ∎

**Verification record for Conjecture J (clauses (a),(b) incl. strictness):**

| class | count | result |
|---|---|---|
| connected 3 ≤ n ≤ 8 | 12,111 | 0 violations (`exp16_clauses.py`) |
| connected n = 9 (8 shards) | 261,080 | 0 violations (`cl_n9_*.log`) |
| trees n ≤ 16 | 32,966 (13–16) + all smaller via n≤8/exp7b | 0 violations |
| childE hard sets (190 n=10 + 8 n≤9) | 198 | 0 violations |
| random (ER/BA/trees/core+pendants, n ≤ 60) | 400 | 0 violations (`cl_rand*.log`) |

Note the quantifier: ρ ranges over the whole admissible ray, not just the
graph's own R — Conjecture J is strictly stronger than what Theorem J ⇒ H
uses, and it still has an empty failure set.

## 3. The decoupling is FALSE: no rule c = φ(R) can ever work

One might hope Conjecture J decouples: a universal threshold φ(ρ) with
ψ_f(ρ) ≤ φ(ρ) ≤ ψ_e(ρ) for all valid single-edge configurations (then
c = φ(R) certifies every graph, and the proof splits into two single-edge
inequalities). **This is false.** The two trees (both with R = 14, both
ord2-sum feasible):

- **T₁ = `HkE?K?@`** (n = 9): spider, center degree 4, four legs of length 2.
  Exact feasible interval **[−21/10, +∞)**. Binding lower edge: pendant edge
  (d = (2,1), m = (5/2, 2), s = 3, z1 = 4, zs = 21), L(14) = −21/10.
- **T₂ = `Li_GS?@?S??@?A`** (n = 13): center of degree 4 joined to four
  degree-3 vertices, each carrying two leaves (degrees 4·3⁴·1⁸). Exact
  feasible interval **[−16/7, −11/5]**. Binding upper edge: center edge
  (d = (4,3), m = (3,2), s = 7, z1 = 19, zs = 109), U(14) = −11/5.

Since −21/10 > −11/5, **the two intervals are disjoint although R is the same
number 14 for both trees.** Consequences:

1. No function of R alone (hence no constant, and no function of τ = √R,
   RHS44, …) can pick a working c for all graphs. This subsumes and explains
   all of childH §5's negative results.
2. Any proof of Conjecture H/J must use *joint* information about the two
   binding edges beyond their separate 2-ball data plus R: it must exploit
   that both configurations cannot occur in the same graph with R = 14.
   (Direct gluing experiments, `exp15_glue.py`: every way of joining T₁ and
   T₂ by a path either raises R to ≥ 16 or perturbs the binding 2-balls —
   the m-values pinned by the 2-ball data of the binding edges reach ~3 steps
   into the graph, and every attachment point breaks either the config or
   R = 14. This exclusion mechanism is exactly what a proof must formalize.)
3. The 1-ball version of Conjecture J (ρ₀ over B₁ only) is **false**: trees
   `HhOK?E?` (n=9), `IhH?K?@_?`, `IhOK?C@_?` (n=10), … violate clause (a)
   (`exp7_pairlocal.py`). The 2-ball radius in Conjecture J is minimal.

## 4. Verified structural facts (unproved, exhaustively tested)

With R replaced by the *1-ball* local ρ ≥ max_{g∈B₁(e)} arg44_g (stronger
than the global statements; tested n ≤ 8 all graphs, trees ≤ 13–14, both
childE hard sets, `exp4_signs.py`, `exp6_local.py`):

- **(V1)** z1_e ≤ ρ ⇒ zs_e ≤ ρ s_e (κ ≤ 0 whenever σ ≤ 0: lower bounds
  L_f are never positive; the σ = 0 clause of H3 is never violated).
- **(V2)** (s_e−2)² ≤ ρ ⇒ z1_e ≤ ρ (by I3: (s_e−2)² ≤ ρ forces
  (s_e−2)² + T_e ≤ ρ). Contrapositive: σ_e > 0 forces s_e > τ+2 — upper-bound
  edges are exactly first-order-heavy edges.
- **(V3)** In every graph the minimum U_e is attained at a maximum-s edge.

## 5. Lemma P (a proved sample case of V1)

**Lemma P.** Let e = ij be a pendant edge with d_j = 1, d_i = 2, and let k be
the other neighbor of i, D := d_k, f = ik. If ρ ≥ arg44_e and ρ ≥ arg44_f,
then zs_e ≤ ρ s_e = 3ρ (so edge e never contributes a positive lower bound).

*Proof.* Here m_i = (1+D)/2, m_j = 2, so arg44_e = 2D (P0). e has the single
line-graph neighbor f, so z1_e = s_f − 2 = D and, by childH Lemma H2,
zs_e = M_f − 2s_f = D² − D + 1 + D·m_k =: F (P1). Also
arg44_f = D² + (D−2)² + (1+D)m_k − 4D =: C (P2), and
3C − F = 5D² − 23D + 11 + (3+2D)m_k (P3).
- If D ≥ 4: since m_k ≥ 1, 3C − F ≥ 5D² − 21D + 14 > 0 (positive at D = 4
  and increasing), so F ≤ 3C ≤ 3ρ.
- If D = 3: 3C − F = 9m_k − 13. If m_k ≥ 13/9, F ≤ 3C ≤ 3ρ. Otherwise
  F = 7 + 3m_k < 7 + 13/3 < 18 = 3·(2D) ≤ 3ρ.
- If D = 2: 3C − F = 7m_k − 15. If m_k ≥ 15/7, F ≤ 3ρ; otherwise
  F = 3 + 2m_k < 51/7 < 12 = 3·(2D) ≤ 3ρ.
- If D = 1: G = P₃, F = 3 ≤ 3ρ (ρ ≥ arg44_e = 2). ∎

(All steps sympy-verified. The mechanism — play the neighbor constraint
arg44_f ≤ ρ against the fallback ρ ≥ arg44_e — is the template for proving
V1/V2 in general; the case split on m_k is what a full proof must organize.)

## 6. Negative result: vertex-space certificates do NOT work

The natural n-dimensional analog — for δ ≥ 2, N = Q − 2I ≥ 0 has ρ(N) = λ,
and the family x = d + t gives the linear-in-t test (N²(d+t))_v ≤ R(d_v+t) —
**fails**: 26 graphs with δ ≥ 2, n ≤ 8 admit no feasible t (first failure
`FEhf?`), 63 with δ ≥ 1 under the β = 1 shift (`exp2_vertex.py`). The
line-graph (edge-space) formulation of Conjecture H is essential.

## 7. Files

- `exp1_structure.py` — exact (Fraction) interval + binding-edge reporter.
- `exp2_vertex.py` — vertex-space certificate test (negative result §6).
- `exp3_trees_fixedc.py`, `exp12_treesfixed.py` — fixed-c scans on trees:
  c = −3/2 fails only T₂ = `Li_GS?@?S??@?A` among all trees n ≤ 17;
  c = −2 fails `FkE?G` (n=7) and T₂; c = −1 fails T₂ plus a growing family
  of subdivided-star shapes (degrees 3,3,3,2,2,2, R = 94/9) from n = 15 on.
  No fixed c works for all trees.
- `exp4_signs.py`, `exp6_local.py` — structural facts V1–V3, local versions.
- `exp5_identities.py`, `verify_sympy.py` — identity verification.
- `exp7_pairlocal.py` / `exp7b_pair2ball.py` — 1-ball pairwise (false) vs
  2-ball pairwise (holds).
- `exp8_envelope.py`, `exp9_extremal.py`, `exp10_bigpool.py`,
  `exp11_random.py`, `combine_env.py` — pooled cross-graph envelopes; found
  the ρ = 14 cross-graph conflict of §3 (`env_*.npz`).
- `exp13_witness.py` — extracted the T₁/T₂ witnesses.
- `exp14_pairbig.py`, `exp16_clauses.py` — Conjecture J at scale
  (`pair_*.log`, `cl_*.log`).
- `exp15_glue.py` — gluing attempts (no counterexample; exclusion mechanism).

## 8. Honest status and route map

- **Rigorous:** identities I0–I5, ψ-form, Theorem J ⇒ H, Lemma P, §3's
  refutation (exact rational intervals for T₁, T₂), §6's negative result.
- **Verified, unproved:** Conjecture J (≈273k graphs n ≤ 9 pairwise-complete,
  trees ≤ 16, both hard sets, 400 random n ≤ 60), structural facts V1–V3.
- **What a proof of J needs:** (1) prove V1/V2 by the Lemma P mechanism
  (bounded case analysis over the 1-ball configuration; unbounded degrees
  enter only through m-averages — the D ≥ 4 branch shows how they truncate);
  (2) for clause (a), formalize the exclusion mechanism of §3: the 2-ball
  data of a binding lower edge f with L_f(ρ) close to −2 pins m-values three
  steps out, which forces every heavy edge e in the same graph either to have
  ρ₀(e) > ρ or U_e(ρ) ≥ L_f(ρ). The T₁/T₂ pair at ρ = 14 with gap
  −21/10 vs −11/5 (only 1/10 apart) shows how little room there is: the case
  analysis must be exact, not asymptotic.
- ord4 fallback (childH route map #4) remains untouched as a plan B.

**PROOF NOT COMPLETE. Conjecture H stands; Conjecture J is the sharpened,
strictly-local-plus-exclusion form that a successor should attack.**
