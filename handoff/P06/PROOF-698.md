# WoW Conjecture 698 is TRUE (adjacency reading): s⁻(G) ≤ R(G)

**Statement (Fajtlowicz, Written on the Wall, #698).** "length of negative
eigenvalues ≤ the Randić Index." Per the WoW / Brewster–Dinneen–Faber
glossary: *length* = Euclidean norm, *eigenvalues* = adjacency eigenvalues.
So with λ₁ ≥ … ≥ λ_n the adjacency eigenvalues of a graph G with m ≥ 1 edges,

  s⁻(G) := √( Σ_{λᵢ<0} λᵢ² )  ≤  R(G) := Σ_{uv∈E} (d_u d_v)^{−1/2}.

**Theorem.** s⁻(G) ≤ R(G) for every graph G, with equality iff the non-trivial
component structure is a single complete bipartite graph (plus isolated
vertices).

**Proof.** Assume m ≥ 1 (if m = 0 both sides are 0). Let
S = Σ_{uv∈E} √(d_u d_v).

1. *(Rayleigh)* With x = (√d_u)_u ≠ 0:
   λ₁ ≥ (xᵀAx)/(xᵀx) = 2S / 2m = S/m.

2. *(Cauchy–Schwarz over the m edges, weights w_e = √(d_u d_v) > 0)*
   m² = (Σ_e 1)² ≤ (Σ_e w_e)(Σ_e w_e^{−1}) = S·R.

3. Combining, λ₁ R ≥ (S/m) R ≥ m, hence by AM–GM
   λ₁² + R² ≥ 2 λ₁ R ≥ 2m.

4. Since Σᵢ λᵢ² = trace(A²) = 2m and s⁺² := Σ_{λᵢ>0} λᵢ² ≥ λ₁²,
   s⁻² = 2m − s⁺² ≤ 2m − λ₁² ≤ R².  ∎

**Equality analysis.** s⁻ = R forces equality throughout:
(a) s⁺ = λ₁, i.e. λ₁ is the only positive eigenvalue; restricting to the
non-trivial components, a connected graph with exactly one positive eigenvalue
is complete multipartite (Smith's theorem), and one positive eigenvalue in
total forces a single non-trivial component;
(b) equality in Cauchy–Schwarz: d_u d_v constant over edges;
(c) λ₁ = R and λ₁R = m give λ₁² = m.
For a complete multipartite graph K_{n₁,…,n_k} with k ≥ 3, s⁺ = λ₁ holds but
(b)+(c) cannot both hold: every pair of parts is adjacent, so d_u d_v constant
over edges (b) forces all parts equal, K_{k×a}; then λ₁ = (k−1)a and
λ₁² = (k−1)²a² > k(k−1)a²/2 = m exactly when k > 2, contradicting (c)
(e.g. K₃: λ₁² = 4 > 3 = m). The two-part case K_{a,b} has
spectrum {±√(ab), 0^{n−2}}, so s⁻ = √(ab) = ab/√(ab) = R: equality holds.
Isolated vertices change neither side. (For m = 0 both sides vanish, so equality
also holds trivially for empty graphs.) ∎

**Sharp intermediate inequality (assembly of known results).** λ₁(G)² + R(G)² ≥ 2m,
equality iff complete bipartite plus isolated vertices. Its two ingredients are
1993-vintage theorems of Favaron, Mahéo and Saclé ("Some eigenvalue properties in
graphs (conjectures of Graffiti — II)", Discrete Math. 111 (1993)): λ₁ ≥ S/m and
λ₁·R ≥ m (see Li–Shi, "A survey on the Randić index", Thm 2.16, and
Elphick–Wocjan arXiv:1508.07950, which generalizes λ₁ ≥ S/m). The closest
published relative of the main theorem is Arizmendi–Arizmendi, "Energy of a graph
and Randić index", LAA 609 (2020): E(G) ≥ 2R(G) — an L1-norm lower bound; neither
result implies the other (698 upper-bounds the L2 norm s⁻ by R).

**Consequence for the literature.** The open row "698" in Roucairol–Cazenave
(ECAI 2025, refutationGBR) is settled: no counterexample exists. Moreover
their Rust encoding of 698 used the *Laplacian* spectrum, whose negative part
is empty (L ⪰ 0), so their search target was vacuously true regardless.

**Machine verification.** `verify.py` (this directory) checks the equality
families in exact arithmetic and every inequality of the chain on all 2^15
labeled graphs with 6 vertices plus 4000 random graphs; exhaustive nauty-geng
scans (n ≤ 10) and simulated annealing (n ≤ 80) found max(s⁻ − R) = 0,
attained only at complete bipartite (+ isolated) graphs.
