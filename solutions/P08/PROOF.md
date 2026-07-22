# Graffiti conjectures 39 and 40 are TRUE (proof)

**Statement (WoW 39/40, per the Roucairol–Cazenave 2025 encoding).** For every
connected graph G on n vertices, let dev(D) be the population standard deviation of
the n² entries of the distance matrix D, and let n⁺(G), n⁻(G) be the numbers of
positive and negative adjacency eigenvalues. Then

- (39) dev(D) ≤ n⁺(G), and
- (40) dev(D) ≤ n⁻(G).

**Proof.** Let d = diam(G).

*Step 1 (Popoviciu's inequality).* Every entry of D lies in [0, d]. For any finite
multiset of reals contained in an interval [a, b], the population variance is at most
(b − a)²/4 (Popoviciu, 1935). Hence Var(D) ≤ d²/4, i.e.

  dev(D) ≤ d/2.

(The same bound holds if the deviation is taken over the off-diagonal entries only,
or over the n(n−1)/2 unordered pairs, so the proof is robust to the exact reading of
"deviation of the distance matrix".)

*Step 2 (induced geodesic path).* Let u, v realize the diameter and let
P: u = x₀, x₁, …, x_d = v be a shortest u–v path. P is an *induced* path: any edge
x_i x_j with |i − j| ≥ 2 would create a shorter u–v walk, contradicting minimality.
So G contains P_{d+1} (the path on d + 1 vertices) as an induced subgraph.

*Step 3 (inertia of a path).* The adjacency eigenvalues of P_k are
2cos(jπ/(k+1)), j = 1, …, k. They are positive exactly for j < (k+1)/2 and negative
exactly for j > (k+1)/2, so

  n⁺(P_k) = n⁻(P_k) = ⌊k/2⌋.

*Step 4 (Cauchy interlacing).* If H is an induced subgraph of G, the adjacency
matrix of H is a principal submatrix of that of G, and Cauchy interlacing gives
n⁺(G) ≥ n⁺(H) and n⁻(G) ≥ n⁻(H). With H = P_{d+1}:

  n⁺(G) ≥ ⌊(d+1)/2⌋ ≥ d/2  and  n⁻(G) ≥ ⌊(d+1)/2⌋ ≥ d/2.

*Conclusion.* dev(D) ≤ d/2 ≤ min(n⁺(G), n⁻(G)). (Degenerate case n = 1: dev = 0 =
n⁺ = n⁻, and the inequalities hold with equality; for d = 0 there is no path step
but dev(D) = 0. For n ≥ 2, d ≥ 1 and Step 2–4 apply.) ∎

**Remarks.**
- The proof shows the much stronger dev(D) ≤ diam(G)/2 ≤ min(n⁺, n⁻); the
  conjectured inequalities are far from tight (exhaustive search over all 273 192
  connected graphs with n ≤ 9 gives max dev − min(n⁺, n⁻) = −0.2194, attained by
  the star K₁,₃ with dev(D) = 0.7806 and n⁺ = n⁻ = 1).
- Machine verification: `solutions/P08/verify.py` independently re-checks every step
  numerically (Popoviciu on the actual distance matrices, inducedness of geodesic
  paths, path inertia up to k = 2000, interlacing consequence, and the end-to-end
  inequality on an exhaustive sweep of all connected graphs with n ≤ 7 plus
  thousands of larger random/structured graphs) and prints PASS.
- The neighboring WoW 38 (Var(D) ≤ −λ_min) is a different statement and is NOT
  settled by this argument.
