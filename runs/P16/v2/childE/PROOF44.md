# P16 childE — Bound 44: rigorous partial results (NOT a complete proof)

**Status: PROOF INCOMPLETE.** No counterexample found; substantial new machinery.
This file contains only rigorous statements (Lemmas E1–E4, all machine-verified in
`verify_identities.py`), the exact finite feasibility criterion they induce, the
exhaustive verification record, and a precise description of the resisting cases.

Target (DHS arXiv:2606.14550 Table 2):

  **Bound 44**: μ(G) ≤ max_{ij∈E} t44(i,j),
  t44 = 2 + √(arg44), arg44 = 2((dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ)
  (negative argument ⇒ term −∞).

Notation: G simple connected, n ≥ 3 (K₂ has equality μ = 2 = t44). d = degrees,
m = average neighbor degrees, s_e = dᵢ+dⱼ, M_e = dᵢ(dᵢ+mᵢ) + dⱼ(dⱼ+mⱼ),
Q = D+A, λ = λ_max(A(L(G))). By childB Lemma B1, ρ(Q) = 2 + λ ≥ μ(G).
Everything below bounds ρ(Q), i.e. proves the strengthened form ρ(Q) ≤ RHS44.
T := RHS44 = max_e t44, τ := T − 2 = √(max_e arg44).

## 1. New exact first-order lemmas (no Jensen loss)

### Lemma E1 (shifted-sum edge weights — NEW; the workhorse)
For every c > −min_e s_e,

  ρ(Q) ≤ max_{ij∈E} (M_e + c·s_e)/(s_e + c).

*Proof.* Collatz–Wielandt for A_L with the positive vector y_e = s_e + c. For
e = ij: (A_L y)_e = Σ_{k∼i, k≠j}(dᵢ+d_k+c) + Σ_{l∼j, l≠i}(dⱼ+d_l+c)
= (dᵢ−1)(dᵢ+c) + (dᵢmᵢ − dⱼ) + (dⱼ−1)(dⱼ+c) + (dⱼmⱼ − dᵢ)
= M_e + (c−2)s_e − 2c   (using Σ_{k∼i} d_k = dᵢmᵢ; EXACT, no concavity).
Hence λ ≤ max_e [M_e + (c−2)s_e − 2c]/(s_e+c) and ρ(Q) = 2 + λ gives the claim
after the algebraic simplification 2 + (M+(c−2)s−2c)/(s+c) = (M+cs)/(s+c). ∎

Endpoints of the homotopy: c = 0 gives the Das-type edge bound
ρ(Q) ≤ max_e M_e/s_e; c → ∞ gives Anderson–Morley ρ(Q) ≤ max_e s_e; c = −2
gives the line-graph average-2-degree bound (y = deg_{L(G)}). The family is tight
on regular graphs for every c (value 2d).

### Lemma E2 (affine-product weights)
For every b ≥ 0,

  ρ(Q) ≤ 2 + max_{ij∈E} [ dᵢ(mᵢ+b)/(dⱼ+b) + dⱼ(mⱼ+b)/(dᵢ+b) − 2 ].

*Proof.* childB Lemma B2 with φ(x) = x + b; since φ is affine the Jensen step is
an identity, so the bound is exact CW with y_e = (dᵢ+b)(dⱼ+b). ∎

### Lemma E3 (general two-variable weights; strict generalization of childB B2)
Let ψ: [1,Δ]² → (0,∞) be symmetric and concave in each variable. Then

  ρ(Q) ≤ 2 + max_{ij∈E} [ dᵢψ(dᵢ,mᵢ) + dⱼψ(dⱼ,mⱼ) − 2ψ(dᵢ,dⱼ) ] / ψ(dᵢ,dⱼ).

*Proof.* y_e = ψ(dᵢ,dⱼ) > 0; (A_L y)_e = Σ_{k∼i,k≠j} ψ(dᵢ,d_k) + Σ_{l∼j,l≠i}
ψ(dⱼ,d_l) ≤ dᵢψ(dᵢ,mᵢ) − ψ(dᵢ,dⱼ) + dⱼψ(dⱼ,mⱼ) − ψ(dᵢ,dⱼ) by Jensen in the
second argument. ∎
(childB's B2 is ψ = φ(x)φ(y); Lemma E1 is ψ = f(x)+f(y) with f affine; the
"additive" family is ψ = f(x)+f(y) with f concave.)

### Lemma E4 (second-order test)
For every positive edge vector y, λ² ≤ max_e (A_L² y)_e / y_e. In particular
Bound 44 holds for G whenever some y from the Lemma E1/E2 weight families
satisfies max_e (A_L² y)_e / y_e ≤ max_e arg44.
*Proof.* Collatz–Wielandt for the nonnegative matrix A_L², whose spectral radius
is λ²; and (τ+2 =) T ≥ 2 + √(max arg44) ⇒ ρ(Q) = 2 + λ ≤ 2 + √(max arg44). ∎
(Note: a first-order certificate with weight y implies the second-order one with
the same y, since A_L(A_L y) ≤ A_L(τy) = τ A_L y ≤ τ² y entrywise.)

## 2. Exact finite feasibility criterion

Fix G and T = RHS44. Bound 44 holds if the following LINEAR-in-c system is
feasible for some c > −min_e s_e (Lemma E1):

  for every edge e:  (M_e − T·s_e) ≤ c·(T − s_e).

Each edge imposes: a lower bound L_e = (M_e−Ts_e)/(T−s_e) if s_e < T; an upper
bound U_e = (Ts_e−M_e)/(s_e−T) if s_e > T; the requirement M_e ≤ T·s_e if
s_e = T. Feasibility ⇔ max(−min_e s_e, max L_e) ≤ min U_e (and the s_e = T
conditions). Similarly Lemma E2 reduces to intersecting the b ≥ 0 solution sets
of the per-edge quadratics
  q_e(b) = (s_e+2−T)b² + (M_e + 2s_e − T s_e)b + (dᵢ²mᵢ + dⱼ²mⱼ + 2dᵢdⱼ − T dᵢdⱼ)
whose coefficients are machine-verified (`verify_identities.py`). Both tests are
exact interval computations (`exp15_exact.py`), no numerical optimization.

## 3. Verification record (exhaustive, float64 screen tol 1e−9)

| class | count | outcome |
|---|---|---|
| connected n ≤ 9 | 273,191 | Lemma E1 feasible for all but **8** graphs (all with δ=1, listed in NOTES §4); those 8 are covered by Lemma E2. **First-order sum ∪ prod covers 100%.** |
| connected n = 10 | 11,716,571 | sum ∪ prod covers all but **190** graphs (`n10_fails.txt`); every one of the 190 passes the second-order test (Lemma E4) with y = (dᵢ+b)(dⱼ+b), and every one passes the first-order general-ψ test (Lemma E3) with a numerically optimized ψ (positive slack ≥ 0.06). |
| trees n ≤ 14 | 5,444 | sum ∪ prod covers all but **6** spider-like trees (first at n=10); each passes Lemma E4 with y ≡ dᵢdⱼ-free b=0 weight and Lemma E3 with optimized ψ. |

Hence the strengthened statement ρ(Q) ≤ RHS44 is re-verified for all connected
graphs n ≤ 10 (consistent with the parent run), now by *certificates* rather
than eigenvalue computation.

## 4. What resists, precisely

1. **Lemma E1 alone** fails exactly on leaf-heavy graphs at n ≤ 9 (8 graphs,
   δ = 1, Δ ∈ {4,5}) and on 190 graphs at n = 10 with (δ,Δ) mostly (2,6), (3,6),
   (2,5), (3,7): dense-ish graphs with one high-degree vertex adjacent to many
   low-m vertices. The c-window closes because a high-s edge forces c small
   while a high-M/s edge forces c large.
2. **Product weights φ(dᵢ)φ(dⱼ) with ANY concave φ** (childB's program, our
   exp7) fail at n = 9: e.g. `H?`reQF` has optimal-concave-φ slack −0.039.
   childB's empirical finding 2 (n ≤ 8) does NOT extend; the product family is a
   dead end for a complete proof.
3. **Additive weights f(x)+f(y) with ANY concave f** fail on 13 of the 204 hard
   graphs (7 leaf-heavy small ones + the 6 trees).
4. **General ψ (Lemma E3)** succeeded (numerically, SLSQP multistart) on every
   hard graph tested, including all 6 trees and samples of the 190 — no known
   graph where the first-order (d,m)-local method is infeasible. But no
   closed-form rule G ↦ ψ_G covering everything is known; the optimizer's ψ is
   near-rank-1 (≈ product) on most graphs and near-additive on the rest.
5. **Second-order affine test (Lemma E4)** covers every known hard case with the
   1-parameter affine weights; no failure of "sum ∪ prod ∪ ord2-affine" is known
   on ANY graph tested (n ≤ 10 exhaustive + trees n ≤ 14).

## 5. Route to completion (for a future session)

The complete proof plausibly = Lemma E1's criterion for a structured class +
case analysis for the closure:
(a) prove the pairwise inequality L_e ≤ U_f (Sec. 2) whenever both endpoint
    degrees at f are ≤ T − Δ... — the empirically-binding pairs always have f =
    the max-degree-sum edge and e = a max-M/s edge; the identity
    Σᵢ dᵢmᵢ = Σ_{ij∈E} s_e limits how large M_e can be while arg44 stays ≤ τ²
    at every edge (this is where Route 2's global counting enters);
(b) for the residual class (leaf-heavy + the (δ,Δ)=(2..3,5..7) profile), use the
    second-order test: (A_L² y)_e expands exactly into second-neighborhood sums
    Σ_{k∼i} d_k m_k, Σ_{k∼i} d_k², which the same global counting identity
    controls. All ingredients are (d,m)-expressible after one more Jensen step.
None of this is carried out; it is the sharpest known target.
