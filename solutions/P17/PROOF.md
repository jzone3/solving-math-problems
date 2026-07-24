# P17 — Self-contained proof that WoW 20 & 21 are true

This is an independent, from-scratch write-up (with every step re-derived and
checked by hand, and spot-checked numerically in
`runs/P17/v1/check_kumar_pragada.py`) of the argument of Kumar–Pragada,
arXiv:2607.19817 (22 Jul 2026), plus the short deduction of WoW 20 & 21.
Notation: G simple graph on n vertices, m edges, adjacency matrix A = A(G)
with eigenvalues λ₁ ≥ … ≥ λₙ, energy E(G) = Σ|λᵢ|, independence number α(G),
inertia counts n⁺(G), n⁻(G). Since tr A = 0, Σ_{λ>0} λ = E(G)/2.

## Target statements

- **WoW 20**: n⁺(G) ≤ Σ_{λ>0} λ = E(G)/2.
- **WoW 21**: n⁻(G) ≤ Σ_{λ>0} λ = E(G)/2.

## Step 0 — SDP formulation of energy (Abiad–Coutinho–Juliano–Reijnders)

**Lemma 0.** E(G) = 2·min{ tr M : M ⪰ 0, M − A ⪰ 0 }.

*Proof.* Write the spectral decomposition A = P − Q with P, Q ⪰ 0, PQ = 0
(P = positive part, Q = negative part). Then tr P = Σ_{λ>0} λ = E/2, P ⪰ 0,
and P − A = Q ⪰ 0, so P is feasible: min ≤ E/2. Conversely, if M ⪰ 0 and
M − A ⪰ 0, then for the spectral projector Π onto the nonnegative eigenspaces
of A: tr M ≥ tr(ΠMΠ) ≥ tr(ΠAΠ) = Σ_{λ≥0} λ = E/2 (first inequality since
M ⪰ 0 makes tr M ≥ tr of any compression; second since M ⪰ A). ∎

## Step 1 — Neighbourhood deletion inequality

**Lemma 1.** For any graph G: 4m + Σ_{v∈V} E(G − N[v]) ≤ n·E(G).

*Proof.* Both sides are additive over connected components (a short check:
if G = G₁ ⊔ G₂ and the inequality holds for each Gᵢ, summing and using
E(G) = E(G₁) + E(G₂) gives it for G). So assume G connected, n ≥ 2.

Let A = P − Q as above and B := P + Q, so B² = A², B ⪰ 0, and since
diag A = 0: P_vv = Q_vv = B_vv/2, and Σ_v P_vv = tr P = E(G)/2. Also
B_vv > 0 for all v (if B_vv = 0 then B ⪰ 0 forces row v of B to vanish,
so deg(v) = (B²)_vv = 0, contradicting connectivity).

For v ∈ V let S(v) := V \ N[v], let x_v := column v of P restricted to
S(v) (note P_uv = Q_uv for u ∈ S(v), since A_uv = 0 there), and define the
Schur complement
  P_v := P[S(v)] − x_v x_vᵀ / P_vv .

**Claim A: E(G − N[v]) ≤ 2 tr(P_v).**
P_v is the Schur complement of the positive entry P_vv in the PSD matrix
P[S(v) ∪ {v}], hence P_v ⪰ 0. Similarly Q_v := Q[S(v)] − x_v x_vᵀ/Q_vv ⪰ 0.
Since P_vv = Q_vv and A[S(v)] = P[S(v)] − Q[S(v)]:
  P_v − A(G − N[v]) = Q_v ⪰ 0,
so P_v is feasible in Lemma 0 for G − N[v]; the claim follows.

**Claim B: for every edge uv, with x=B_uu, y=B_vv, z=B_uv:**
  ((x−1)² − z²)/x + ((y−1)² − z²)/y ≥ 0.
From 2P = B + A and 2Q = B − A, the 2×2 principal minors of 2P and 2Q at
{u,v} give xy ≥ (z+1)² and xy ≥ (z−1)², hence √(xy) ≥ 1 + |z| and
(√(xy) − 1)² − z² ≥ 0. Then
  ((x−1)²−z²)/x + ((y−1)²−z²)/y = ((x+y)/xy)(xy + 1 − z²) − 4
    ≥ (2/√(xy))(xy + 1 − z²) − 4        (AM–GM on x+y)
    = (2/√(xy))((√(xy) − 1)² − z²) ≥ 0. ∎(B)

**Claim C: 2 Σ_v tr(P_v) ≤ n·E(G) − 4m.**
tr(P_v) = Σ_{u∈S(v)} P_uu − (1/P_vv) Σ_{u∈S(v)} P_uv². Each u lies in S(v)
for exactly n − 1 − deg(u) vertices v, and 2P_uv = B_uv for u ∈ S(v), so
  2 Σ_v tr(P_v) = n·E(G) − Σ_v (deg(v)+1) B_vv − Σ_v (1/B_vv) Σ_{u∈S(v)} B_uv².
Using deg(v) = (B²)_vv = B_vv² + Σ_{u∼v} B_uv² + Σ_{u∈S(v)} B_uv², the
required inequality
  Σ_v (deg(v)+1) B_vv + Σ_v (1/B_vv) Σ_{u∈S(v)} B_uv² ≥ 4m
rearranges edge-by-edge to exactly the sum over edges of the quantity in
Claim B, hence holds. ∎(C)

Claims A + C give Lemma 1. ∎

## Step 2 — Theorem: E(G) ≥ 2(n − α(G))

Induction on n; trivial for n ≤ 1. For n ≥ 2: for each v,
α(G − N[v]) ≤ α(G) − 1 (add v back to any independent set of G − N[v]).
G − N[v] has n − 1 − deg(v) vertices, so by induction
  E(G − N[v]) ≥ 2(n − 1 − deg(v) − (α(G) − 1)) = 2(n − deg(v) − α(G)).
Summing over v and applying Lemma 1:
  n·E(G) ≥ 4m + Σ_v 2(n − deg(v) − α) = 4m + 2n² − 4m − 2nα = 2n(n − α),
so E(G) ≥ 2(n − α(G)). ∎

## Step 3 — Cvetković inertia bound and conclusion

**Inertia bound.** α(G) ≤ min{n − n⁺(G), n − n⁻(G)}.
*Proof.* An independent set S gives a |S|-dimensional coordinate subspace on
which xᵀAx = 0. If |S| > n − n⁺, this subspace meets the n⁺-dimensional
positive eigenspace nontrivially, giving x ≠ 0 with xᵀAx > 0 — contradiction.
Symmetrically for n⁻. ∎

Combining: E(G)/2 ≥ n − α(G) ≥ max{n⁺(G), n⁻(G)}, i.e.

  **n⁺(G) ≤ Σ_{λ>0} λ  (WoW 20)  and  n⁻(G) ≤ Σ_{λ>0} λ  (WoW 21).** ∎

## Verification performed in this repo

- Every step above re-derived by hand from the paper
  (`runs/P17/v1/kumar-pragada-2607.19817.pdf`).
- Lemma 1, the Theorem, and the corollary spot-checked numerically on 400
  random graphs with exact α: `runs/P17/v1/check_kumar_pragada.py`, 0 failures.
- The corollary certified with exact arithmetic (no floats on the accept
  path) on all 1024 graphs on 5 vertices plus equality/near-equality
  families: `solutions/P17/verify_corollary.py` → PASS.
- Consistent with the exhaustive counterexample search (none exists):
  `runs/P17/v1/NOTES.md`.
