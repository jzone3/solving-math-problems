# Proof of Graffiti conjectures 39 and 40

**Statement (WoW 39/40, per "Written on the Wall" July 2004, conjectures 39–40; same
formulation as implemented by Roucairol–Cazenave).** Let G be a connected graph on n
vertices, D its distance matrix, and dev(D) the standard deviation of the n² entries of D.
Let n⁺(G), n⁻(G) be the numbers of positive and negative eigenvalues of the adjacency
matrix A(G). Then

- (39) dev(D) ≤ n⁺(G), and
- (40) dev(D) ≤ n⁻(G).

**Theorem.** For every connected graph G with diameter d,

  dev(D) ≤ d/2 ≤ ⌈d/2⌉ ≤ min(n⁺(G), n⁻(G))   for n ≥ 2,

and for n = 1 trivially dev(D) = 0 = n⁺ = n⁻; hence both (39) and (40) hold.

## Lemma 1 (Popoviciu). dev(D) ≤ d/2.

All n² entries of D lie in [0, d] (diagonal entries are 0, and d = max entry by definition
of diameter). For any finite list of reals contained in an interval [m, M], the variance is
at most (M − m)²/4 (Popoviciu's inequality on variances: Var(X) ≤ (M−m)²/4 for any random
variable supported in [m, M]; apply it to the uniform distribution over the multiset of
entries). Hence Var ≤ d²/4 and dev ≤ d/2. ∎

(This is robust to the exact convention for "dev": the standard deviation over the n(n−1)
off-diagonal entries, over unordered pairs, or the *mean absolute deviation* are all ≤ the
half-range d/2 as well.)

## Lemma 2 (interlacing). n⁺(G) ≥ ⌈d/2⌉ and n⁻(G) ≥ ⌈d/2⌉ (n ≥ 2).

Let u, v realize the diameter and take a shortest u–v path P. A shortest path is an
induced path (a chord would shortcut it), so G contains an induced subgraph isomorphic to
P_{d+1}, the path on d+1 vertices. The adjacency matrix of an induced subgraph is a
principal submatrix of A(G), so by Cauchy eigenvalue interlacing the inertia is monotone:
n⁺(G) ≥ n⁺(P_{d+1}) and n⁻(G) ≥ n⁻(P_{d+1}).

The eigenvalues of P_m are 2cos(kπ/(m+1)), k = 1,…,m; exactly ⌊m/2⌋ of them are positive
and ⌊m/2⌋ negative (with one zero eigenvalue iff m is odd). With m = d+1:
n⁺(P_{d+1}) = n⁻(P_{d+1}) = ⌊(d+1)/2⌋ = ⌈d/2⌉. ∎

## Conclusion

For n ≥ 2 (so d ≥ 1): dev(D) ≤ d/2 ≤ ⌈d/2⌉ ≤ min(n⁺, n⁻). For n = 1, dev(D) = 0 = n⁺ = n⁻.
Both conjectures hold for every connected graph. ∎

## Remarks

- The same argument shows dev(D) can never beat any invariant that is ≥ ⌈d/2⌉; the entire
  search program (exhaustive n ≤ 10 in 1995, MCTS n ≤ 50 in 2025, and the "unsearched
  n > 50 tree regime") could never have found a counterexample.
- Conjecture 38 (variance of D ≤ −λ_min) does *not* survive this argument — variance grows
  like d², and indeed P₁₀ already refutes it (var = 5.61 > 1.92 = −λ_min), consistent with
  38 being marked refuted while 39/40 stayed open.
- Verification: `verify.py` in this directory machine-checks (a) Lemma 1 exactly in
  rational arithmetic, (b) Lemma 2 and the full conjectures numerically with a safe
  tolerance direction, on all connected graphs with n ≤ 8 (via nauty geng if available,
  otherwise a built-in exhaustive enumeration for n ≤ 7), thousands of random connected
  graphs up to n = 120, and structured high-deviation families up to n = 1000.
