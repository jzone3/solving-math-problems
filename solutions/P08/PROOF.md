# P08 — Graffiti conjectures 39 & 40 are TRUE (proof)

**Statement (WoW 39/40, verbatim from Fajtlowicz's "Written on the Wall", wow-july2004):**
"39. The deviation of the distance matrix is not more than the number of positive
eigenvalues." / "40. … the number of negative eigenvalues." (Eigenvalues = adjacency
eigenvalues; conjectures implicitly restricted to connected graphs.)

Operational encoding used by Roucairol–Cazenave 2025 (whose Table 1 lists both as open):
dev(D) = **population standard deviation of all n² entries** of the distance matrix
(diagonal zeros included); n⁺/n⁻ = number of adjacency eigenvalues > 0 / < 0.

**Theorem.** For every connected graph G on n ≥ 1 vertices with diameter d,

  dev(D) ≤ d/2 ≤ ⌈d/2⌉ ≤ min( n⁺(G), n⁻(G) )   (n ≥ 2; trivial for n = 1),

and the first inequality is strict for n ≥ 3 (for K_2, dev = 1/2 = d/2 < 1 = ⌈d/2⌉).
Hence Graffiti 39 and 40 both hold, strictly for all n ≥ 2.

## Proof

**Lemma 1 (Popoviciu).** Any finite population of reals contained in [a, b] has
variance ≤ (b−a)²/4, hence standard deviation ≤ (b−a)/2.
*Proof.* Var(X) ≤ E[(X − (a+b)/2)²] ≤ ((b−a)/2)². ∎

All n² entries of D lie in [0, d], so **dev(D) ≤ d/2**. Strictness for n ≥ 3: equality
in Popoviciu forces every entry to be 0 or d with mean d/2; D contains entries equal
to 1 (adjacent pairs), so equality forces d = 1, i.e. G = K_n, where
dev(D) = √(n−1)/n, and √(n−1)/n = 1/2 only for n = 2. So dev(D) < d/2 for n ≥ 3,
and dev(D) = d/2 = 1/2 < 1 = ⌈d/2⌉ for K_2.

**Lemma 2 (geodesic gives an induced path).** If d(u,v) = d, the vertices of a
shortest u–v path induce P_{d+1}: an edge between path vertices at path-distance ≥ 2
would shorten the geodesic. ∎

**Lemma 3 (inertia of a path).** P_m has eigenvalues 2cos(kπ/(m+1)), k = 1…m, so
n⁺(P_m) = n⁻(P_m) = ⌊m/2⌋ (spectrum symmetric; 0 is an eigenvalue iff m is odd). ∎

**Lemma 4 (Cauchy interlacing ⇒ inertia monotone under induced subgraphs).** If H is
an induced subgraph of G on m of n vertices, with eigenvalues sorted decreasingly,
λ_k(G) ≥ λ_k(H) ≥ λ_{k+n−m}(G). Taking k = n⁺(H): λ_{n⁺(H)}(H) > 0 ⇒ λ_{n⁺(H)}(G) > 0,
so n⁺(G) ≥ n⁺(H); symmetrically (bottom end) n⁻(G) ≥ n⁻(H). ∎

Combining Lemmas 2–4 with m = d+1:

  n⁺(G) ≥ n⁺(P_{d+1}) = ⌊(d+1)/2⌋ = ⌈d/2⌉, and likewise n⁻(G) ≥ ⌈d/2⌉.

With Lemma 1: dev(D) < d/2 ≤ ⌈d/2⌉ ≤ min(n⁺, n⁻) for n ≥ 2. For n = 1,
dev = 0 = n⁺ = n⁻. ∎

## Remarks

- The proof is definition-robust: it works whether "deviation" means population or
  sample standard deviation, or mean absolute deviation (MAD ≤ SD), and whether the
  diagonal is included or the deviation is taken over the n(n−1) off-diagonal entries
  (then values lie in [1, d] and the bound (d−1)/2 is even smaller). It also covers
  Roucairol–Cazenave's numerically-thresholded counts (eigenvalues > 1e-4): the ⌈d/2⌉
  positive eigenvalues guaranteed by interlacing are ≥ the corresponding P_{d+1}
  eigenvalues, the smallest of which is 2sin(π/(d+2)) ≈ 2π/d > 1e-4 for all d < ~60000,
  far beyond any searchable size. The exact-count conjecture is proved for all n.
- Tightness: balanced double brooms (path of h vertices with b ≫ h pendant leaves on
  each end) give dev/min(n⁺,n⁻) → 1 (empirically 0.965 at h=800, b=8000, n=16800),
  so the inequality is asymptotically sharp — explaining why counterexample searches
  (exhaustive n ≤ 10, MCTS n ≤ 50) found nothing yet the conjecture "felt" attackable.
- This also immediately re-proves the n ≤ 10 exhaustive findings and shows no search
  at any n can succeed.

`verify.py` in this directory machine-checks every step that admits finite
verification: Lemma 3 for m ≤ 600, Lemma 4 on random induced subgraphs, the full
inequality chain (with the dev ≤ d/2 comparison done in exact integer arithmetic) on
(i) ALL connected graphs with n ≤ 7, (ii) large structured families including the
near-extremal double brooms, and (iii) seeded random connected graphs up to n = 300.
