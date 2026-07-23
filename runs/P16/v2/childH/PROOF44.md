# P16 childH — Bound 44 via the second-order Collatz–Wielandt method

**Status: PROOF INCOMPLETE.** No counterexample. This file contains only
rigorous statements. Every algebraic identity is machine-verified
(`verify_identities.py`, numeric, exhaustive n ≤ 7 + 300 random graphs n ≤ 30;
`verify_sympy.py`, symbolic). The remaining gap is Conjecture H (Section 5),
now verified exhaustively for **all connected graphs n ≤ 10** and all trees
n ≤ 18 — a single, purely finite-dimensional linear-feasibility statement that
implies Bound 44 in full.

Target (DHS arXiv:2606.14550 Table 2):

  **Bound 44**: μ(G) ≤ max_{ij∈E} t44(i,j), t44 = 2 + √(arg44),
  arg44 = 2((dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ), negative argument ⇒ edge excluded.

Notation (as childE): G simple connected, n ≥ 3; d = degrees, m = average
neighbor degrees, E edges; for e = ij: s_e = dᵢ + dⱼ,
M_e = dᵢ(dᵢ+mᵢ) + dⱼ(dⱼ+mⱼ). Q = D + A, A_L = adjacency of the line graph
L(G), λ = λ_max(A_L) ≥ 0. By childB Lemma B1, μ(G) ≤ ρ(Q) = 2 + λ.
R := max_{e∈E} arg44_e, τ := √R (so RHS44 = 2 + τ; compare CW values of A_L
against τ and of A_L² against R = τ², never against RHS44 — childE pitfall).
Everything below proves the strengthened form ρ(Q) ≤ 2 + τ, i.e. λ² ≤ R.

New vertex quantities (second-neighborhood sums):
P_i = Σ_{k∼i} d_k²  and  W_i = Σ_{k∼i} d_k m_k = (A²d)_i.

## 1. Lemma H1 (second-order Collatz–Wielandt)

For every positive vector y indexed by E,

  λ² ≤ max_{e∈E} (A_L² y)_e / y_e.

In particular, Bound 44 holds for G whenever some y > 0 satisfies
(A_L² y)_e ≤ R·y_e for all e.

*Proof.* Let B = A_L² (entrywise nonnegative) and D = diag(y). Then
D⁻¹BD has the same spectrum as B, and its spectral radius is at most its
maximum row sum (any matrix norm dominates the spectral radius), which is
max_e (By)_e / y_e. Since A_L is symmetric, the eigenvalues of B are the
squares of those of A_L, and by Perron–Frobenius λ = ρ(A_L) ≥ |θ| for every
eigenvalue θ of A_L; hence ρ(B) = λ². Thus
λ² = ρ(B) ≤ max_e (A_L² y)_e / y_e. For the second claim: λ² ≤ R gives
λ ≤ τ, so μ(G) ≤ ρ(Q) = 2 + λ ≤ 2 + τ = RHS44. ∎

### Lemma H1′ (first-order ⇒ second-order, same weight)
If y > 0 and A_L y ≤ τ y entrywise (τ ≥ 0), then A_L² y ≤ τ² y entrywise.
*Proof.* A_L is entrywise nonnegative, so it preserves the entrywise order:
A_L(A_L y) ≤ A_L(τ y) = τ A_L y ≤ τ² y. ∎
(Consequence: the second-order test with a weight family is at least as strong
as the first-order test with the same family — childE's Lemma E1 certificates
are all inherited.)

## 2. Lemma H2 (exact expansion of A_L² on shifted-sum weights)

Let y_e = s_e + c with c > −min_e s_e (so y > 0). Then for every e = ij ∈ E,
EXACTLY (no Jensen step, machine-verified):

  (A_L 1)_e = s_e − 2                       (line-graph degree)
  (A_L s)_e = M_e − 2 s_e
  (A_L y)_e = M_e + (c−2)s_e − 2c           (childE Lemma E1 kernel)
  (A_L M)_e = (dᵢ−2)dᵢ(dᵢ+mᵢ) + (dⱼ−2)dⱼ(dⱼ+mⱼ) + P_i + P_j + W_i + W_j
  (A_L² y)_e = (A_L M)_e + (c−2)(M_e − 2s_e) − 2c(s_e − 2).

*Proof.* For e = ij, (A_L x)_e = Σ_{k∼i,k≠j} x_{ik} + Σ_{l∼j,l≠i} x_{jl}.
With x = 1 this is (dᵢ−1)+(dⱼ−1). With x = s: Σ_{k∼i,k≠j}(dᵢ+d_k) =
(dᵢ−1)dᵢ + (dᵢmᵢ − dⱼ) using Σ_{k∼i} d_k = dᵢmᵢ; adding the symmetric term
gives dᵢ² + dⱼ² + dᵢmᵢ + dⱼmⱼ − 2s_e = M_e − 2s_e. Linearity gives the third
line. With x = M: Σ_{k∼i,k≠j} M_{ik} = Σ_{k∼i,k≠j} [dᵢ(dᵢ+mᵢ) + d_k(d_k+m_k)]
= (dᵢ−1)dᵢ(dᵢ+mᵢ) + (P_i + W_i) − dⱼ(dⱼ+mⱼ); adding the symmetric term gives
the fourth line. The fifth line is A_L applied to the third, using lines 1–2
and linearity. ∎

## 3. Corollary H3 (exact linear-in-c feasibility criterion)

Fix G and R = max arg44 (note R ≥ λ² ≥ 0 is forced whenever any certificate
below exists; empirically R ≥ 0 on every graph scanned). Define per edge

  σ_e := M_e − 4s_e + 4 − R      (= (A_L² 1)_e − R, the slope)
  κ_e := (A_L M)_e − 2M_e + 4s_e − R·s_e     (the intercept).

Then (A_L²(s + c))_e ≤ R(s_e + c) for all e  ⇔  σ_e·c ≤ −κ_e for all e
(machine-verified in `verify_sympy.py`). Hence the ord2-sum test succeeds iff

  max( −min_e s_e , max_{σ_e<0} (−κ_e/σ_e) ) ≤ min_{σ_e>0} (−κ_e/σ_e)

and κ_e ≤ 0 for every edge with σ_e = 0 — an exact interval intersection
(`exp1_ord2sum.py`), no numerical optimization.

### Remark (endpoints)
- If σ_e ≤ 0 for all e, i.e. max_e (M_e − 4s_e + 4) ≤ R, then y = 1 (the
  c → ∞ limit, "second-order Anderson–Morley") is itself a valid certificate.
  This alone covers 6,478 of the 12,111 connected graphs n ≤ 8.
- Regular graphs (degree d): s = 2d, M = 4d², arg44 = 4(d−1)² = R, and
  (A_L² 1)_e = (2d−2)² = R: equality, the test is tight for every c.
- If max_e s_e ≤ τ + 2, the first-order y = 1 certificate (Anderson–Morley,
  (A_L 1)_e = s_e − 2 ≤ τ) already suffices, hence so does ord2 (Lemma H1′).

## 4. Verification record (exhaustive; float64, tol 1e−9)

Conjecture H (below) tested by the exact interval criterion of Corollary H3:

| class | count | outcome |
|---|---|---|
| connected, 3 ≤ n ≤ 8 | 12,111 | ord2-sum feasible: **all** (`exp1_ord2sum.py`) |
| connected, n = 9 | 261,080 | **all** (8 shards, `n9_*.log`, 0 fails) |
| connected, n = 10 | 11,716,571 | **all**: first-order sum (exact, childE exp15 criterion) covers 11,716,324; the remaining **247** all pass ord2-sum (16 shards, `n10_*.log`; by Lemma H1′ the fast path is sound) |
| childE residue `n10_fails.txt` | 190 | **all** pass ord2-sum directly; rechecked in EXACT Fraction arithmetic (`exp6_exact_recheck.py`, no floats) |
| childE n ≤ 9 sum-failures (8 graphs, δ=1) | 8 | **all** pass ord2-sum (exact arithmetic too) |
| trees, 3 ≤ n ≤ 18 | 204,994 | **all** (`trees_ord2.log`, `trees17_18.log`) — incl. the 6 childE spider trees |

This re-proves ρ(Q) ≤ RHS44 for every connected graph n ≤ 10 purely by
certificates, and extends the certificate coverage of trees from 14 to 18.

## 5. Conjecture H and the reduction

**Conjecture H.** For every connected graph G with max_e arg44 ≥ 0 there is a
c > −min_e s_e with (A_L²(s+c))_e ≤ R(s_e+c) for all e ∈ E; equivalently, the
interval of Corollary H3 is nonempty.

**Theorem (reduction).** Conjecture H implies Bound 44 for all connected
graphs (by Lemma H1 + Corollary H3 + childB Lemma B1). ∎

By Lemma H2, Conjecture H only involves the local data
(dᵢ, dⱼ, mᵢ, mⱼ, P_i, P_j, W_i, W_j) per edge — one neighborhood layer deeper
than Bound 44 itself, but still a finite family of LINEAR inequalities in c.

### What a proof must overcome (binding-structure data, `exp5_binding.log`)
On every one of the 198 hard graphs (190 + 8), the binding upper bound U is at
the **maximum-degree-sum edge** (s_e = max s > τ + 2, forcing c small), and
the binding lower bound L is at a **low-degree edge** (profiles (3,2), (3,5),
(2,2), (3,1)… — a low-degree vertex adjacent to the dense core, forcing c
large). So the pairwise inequality to prove is L_f ≤ U_e with f = min-degree-
type edge, e = max-s edge, exactly the one-order-up analog of childE §5(a);
the global counting identity Σᵢ dᵢmᵢ = Σ_e s_e (equivalently Σᵢ P_i = Σᵢ dᵢmᵢ·
… second-moment versions Σᵢ W_i = Σᵢ dᵢ·(A²d)ᵢ/dᵢ, Σᵢ P_i = Σ_k d_k³-type
sums) is the natural tool to bound (A_L M) at the max-s edge while every
arg44_e stays ≤ R.

### No shortcut through a fixed or closed-form c (negative results)
- No universal constant c: c = −1 fails on 48 graphs n ≤ 8 (`exp4_fixedc.py`);
  the feasible intervals of GCdbF? ([−3,−2]) and H?`@f@h ([−2,−1]) intersect
  only at c = −2, and other graphs exclude −2.
- Simple invariant rules fail at n ≤ 8: c = −δ (64 fails), c = −min s/2 (269),
  c = −min s + 1 (9,705), c = δ − Δ (3,992). The content of Conjecture H is
  genuinely the *nonemptiness of the interval*, not any explicit c.

## 6. Honest status

- **Rigorous and complete:** Lemmas H1, H1′, H2, Corollary H3, the reduction
  theorem, and the endpoint remarks. All machine-verified.
- **Verified but not proved:** Conjecture H (n ≤ 10 exhaustive: 11,989,762
  connected graphs; trees n ≤ 18). No known graph — of ANY size — where the
  shifted-sum second-order test fails; unlike every first-order family tried
  by childB/childE, this one currently has an empty failure set.
- **Missing:** an analytic proof of the pairwise inequality L ≤ U (Section 5).
  This requires controlling P_i + W_i at the extremal edges via the counting
  identities; none of that case analysis is carried out here.

**PROOF NOT COMPLETE.** Sharpest known target: prove Conjecture H via the
binding-pair analysis of Section 5.
