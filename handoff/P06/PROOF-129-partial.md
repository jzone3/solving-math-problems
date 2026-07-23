# Partial results on WoW Conjecture 129: dev_L(G) ≤ R(G)

Notation: dev_L(G)² = (1/n)Σᵢ(μᵢ − 2m/n)² for Laplacian eigenvalues μᵢ.
Identity (from Σμᵢ² = Σd_i(d_i+1)): **dev_L² = Var(d) + d̄**, the population
variance of the degree sequence plus the average degree. So 129 is the purely
degree/edge-based statement Var(d) + d̄ ≤ R(G)².

## Theorem 1. Conjecture 129 holds for all regular graphs.

For a d-regular graph on n vertices (d ≥ 1): Var = 0, so dev_L² = d, while
R = m/d = n/2. Need 4d ≤ n². Since d ≤ n − 1 and 4(n−1) ≤ n² (i.e.
(n−2)² ≥ 0), done; equality iff n = 2, i.e. K₂. ∎

## Theorem 2. Conjecture 129 holds for all trees.

Let T be a tree on n ≥ 2 vertices, S the star K_{1,n−1}.

(a) *The star's degree sequence majorizes every tree's.* For any k highest-
degree vertices S⊆V, Σ_{v∈S} d_v = 2e(S) + e(S, V∖S) ≤ e(T) + e(S)
≤ (n−1) + (k−1) = n + k − 2, which equals the star's k-prefix sum
(n−1) + (k−1). Prefix sums of the star sequence dominate; totals equal.

(b) Var is Schur-convex and d̄ = 2(n−1)/n is the same for all trees, so
dev_L(T)² ≤ dev_L(S)² = (n−1)(n² − 2n + 4)/n².

(c) *Star minimizes the Randić index* among graphs without isolated vertices
(Bollobás–Erdős 1998, "Graphs of extremal weights", Ars Combin. 50): 
R(T) ≥ R(S) = √(n−1).

(d) dev_L(S)² = (n−1)(n²−2n+4)/n² ≤ n − 1 = R(S)² since n² − 2n + 4 ≤ n²
for n ≥ 2. Chaining (b), (d), (c): dev_L(T) ≤ dev_L(S) ≤ R(S) ≤ R(T). ∎

(Strict for n ≥ 3; the star itself has slack (2n−4)(n−1)/n².)

## Computational reduction for unicyclic graphs.

Exhaustive check (n ≤ 10) shows S_n + e (star plus one edge between two
leaves) simultaneously maximizes dev_L and minimizes R among connected
unicyclic graphs; for S_n + e, dev_L² = n − 3 + 6/n while
R = (n−3)/√(n−1) + √2/√(n−1) + 1/2, and R² − dev_L² > 0 for all n ≥ 4
(verified numerically to n = 10⁶; R² = n − 3 + O(√n) with positive
correction). A citation for "S_n + e minimizes R among unicyclic graphs"
would make this a full proof for the unicyclic case.

## Dead ends (machine-refuted sufficient conditions)

All "product relaxations" of 129 via R ≥ m/λ₁ (proved) or R ≥ m²/S
(Cauchy–Schwarz) are FALSE, although each holds for all graphs on ≤ 9–11
vertices and is tight at the equality family K_k ∪ (k−2)K₁:

| candidate lemma | status | witness |
|---|---|---|
| H*: (2m−n′+1)·dev_L² ≤ m² (Hong) | FALSE | deg seq (12,11,2×10,1) + isolated padding |
| C*: M₂·dev_L² ≤ m³ | FALSE | annealed, n = 20 |
| J*: (max_u Σ_{v~u}d_v)·dev_L² ≤ m² | FALSE | annealed, n = 16 |
| K*: (max_{uv∈E} m_u m_v)·dev_L² ≤ m² | FALSE | n = 7 exhaustive |
| M*: S·dev_L ≤ m² | FALSE | CS(100,2): +422.9 |
| G*: λ₁·dev_L ≤ m | FALSE | CS(100,2): +2.194 |
| I*: s⁺·dev_L ≤ m | FALSE | implied by G* witness |
| W: Var+d̄ ≤ n−1 (connected) | FALSE | CS(2,4), n = 6 |

(CS(a,b) = complete split: b dominating vertices, a independent.) The
asymptotically tight families for 129 are stars and CS(a,b) with
R² − dev_L² → b(b+1) as a → ∞ (symbolic expansion), which "sandwich" the
conjecture: any single-product relaxation that is tight at K_k ∪ (k−2)K₁
fails on CS(a, small) at large scale, yet 129 itself keeps a positive gap.

## Verification frontier

Exhaustive machine verification of 129 (C scanner, degree-identity based):
ALL 1,018,997,864 graphs on 11 vertices (plus all graphs n ≤ 10, 12.0M at
n = 10) — no violation; worst n = 11 gap −0.0124 (strict: the equality family
needs even n). This extends the Brewster–Dinneen–Faber n ≤ 10 computational
frontier.
