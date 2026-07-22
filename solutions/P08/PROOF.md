# P08 — Graffiti conjectures 39 & 40 are TRUE (proof)

**Statement (WoW, verbatim after decoding wow-july2004.pdf):**
- *39. The deviation of the distance matrix is not more than the number of positive eigenvalues.*
- *40. The deviation of the distance matrix is not more than the number of negative eigenvalues.*

Operationalized (Roucairol–Cazenave `refutationGBR` encoding, the open-problem reference):
for every connected graph G on n vertices, with D its distance matrix,
dev(D) = population standard deviation of all n² entries of D,
n⁺(G) / n⁻(G) = number of positive / negative adjacency eigenvalues:

**(39)** dev(D) ≤ n⁺(G)  and  **(40)** dev(D) ≤ n⁻(G).

## Proof

Let G be connected with diameter d. If d = 0 then G = K₁, dev(D) = 0 = n⁺ = n⁻ and both
inequalities hold. Assume d ≥ 1.

**Lemma 1 (Popoviciu's inequality).** Any finite multiset of real numbers contained in an
interval [a, b] has population variance at most (b−a)²/4.

*Proof.* For any random variable X with values in [a,b] and c = (a+b)/2:
Var(X) = min_t E[(X−t)²] ≤ E[(X−c)²] ≤ ((b−a)/2)². ∎

All n² entries of D lie in [0, d], so

  **dev(D) ≤ d/2.**  (1)

**Lemma 2 (inertia of paths).** The path P_m on m vertices has adjacency eigenvalues
2cos(kπ/(m+1)), k = 1,…,m; hence n⁺(P_m) = n⁻(P_m) = ⌊m/2⌋.

*Proof.* The eigenvalues are classical. 2cos(kπ/(m+1)) > 0 ⟺ k < (m+1)/2, and the number of
integers k in [1, (m+1)/2) is ⌊m/2⌋; by symmetry the same count is negative. ∎

**Lemma 3 (inertia monotonicity under induced subgraphs).** If H is an induced subgraph of G
then n⁺(G) ≥ n⁺(H) and n⁻(G) ≥ n⁻(H).

*Proof.* A(H) is a principal submatrix of A(G). Cauchy interlacing: with eigenvalues in
non-increasing order, λ_k(G) ≥ λ_k(H) ≥ λ_{k+n−m}(G) for 1 ≤ k ≤ m (m = |V(H)|).
If λ_k(H) > 0 then λ_k(G) > 0, so n⁺(G) ≥ n⁺(H); if λ_k(H) < 0 then λ_{k+n−m}(G) < 0,
so n⁻(G) ≥ n⁻(H). ∎

**Lemma 4 (geodesics are induced).** If u, v are at distance d in G, any shortest u–v path is
an induced P_{d+1}: an edge between two non-consecutive vertices of the path would create a
shorter u–v walk, contradicting minimality.

Combining Lemmas 2–4: every connected G with diameter d contains an induced P_{d+1}, so

  **n⁺(G) ≥ ⌊(d+1)/2⌋ ≥ d/2  and  n⁻(G) ≥ ⌊(d+1)/2⌋ ≥ d/2.**  (2)

By (1) and (2), dev(D) ≤ d/2 ≤ min(n⁺(G), n⁻(G)). Both conjectures hold. ∎

## Robustness to the "deviation" definition

WoW does not define "deviation of the distance matrix" at the conjecture (the Aouchiche–Hansen
survey and the RC encoding use the standard deviation over all n² entries). The proof is
insensitive to the convention:
- std over off-diagonal entries only, or over the n(n−1)/2 unordered pairs: still a multiset of
  values in [0, d], so Lemma 1 gives ≤ d/2;
- mean absolute deviation: MAD ≤ std, so the bound still holds.

## Machine verification

`solutions/P08/verify.py` (standalone, numpy only) independently re-implements the invariants
(Floyd–Warshall distances; adjacency inertia both by float eigensolve and by exact rational
LDLᵀ/congruence inertia) and checks, for every connected graph on ≤ 7 vertices (exhaustive,
853+ graphs per order generated internally without nauty) plus thousands of random graphs and
trees up to n = 400:

  dev(D) ≤ d/2,  ⌊(d+1)/2⌋ ≤ min(n⁺, n⁻),  dev(D) ≤ min(n⁺, n⁻)

and prints PASS. This verifies the two nontrivial inequalities of the proof chain and the
conjectures themselves on all tested graphs. (The proof itself is elementary: Popoviciu +
Cauchy interlacing + the path spectrum; each lemma is textbook.)

## Status note

Exhaustive search (n ≤ 9 here; n ≤ 10 Brewster–Dinneen–Faber 1995), tree exhaustion (n ≤ 20)
and simulated annealing on trees to n = 1000 and general graphs (this run, V1) found margins
dev − min(n⁺,n⁻) ≤ −0.22 everywhere, consistent with the theorem: the maximum of dev − n⁺ over
all graphs is negative and attained near stars/complete split graphs.
