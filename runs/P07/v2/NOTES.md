# P07 (Graffiti 154) — V2 structured-families run — NOTES

Session: devin-59dd7504264e49519cec37751851f8fc (2026-07-22). Variant V2: broad structured
families with symbolic/exact optimization of 2mμ²/n³.

## Statement re-verification (against the cited operational source)

- Cloned https://github.com/RoucairolMilo/refutationGBR and read
  `src/models/conjectures/GenerateGraph.rs`, `CONJECTURE == 154` block, plus
  `invariants.rs` (`std_dev`, `mean`, `dist_matrix`). Their exact test:
  `stdev(adjacency eigenvalues) - n / mean_dist > 1e-5` refutes, where
  - `stdev` = **population** std-dev of all n adjacency eigenvalues (= √(2m/n), since
    trace A = 0, trace A² = 2m), and
  - `mean_dist` = mean of **all n² entries** of the distance matrix (diagonal zeros
    included), i.e. μ_RC = S/n² with S = Σ over ordered pairs of dist(u,v).
  So the R–C encoding is exactly equivalent to the integer inequality **2·m·S² ≤ n⁷**.
  Note μ_RC = μ_std·(n−1)/n where μ_std = S/(n(n−1)) is the common convention; the R–C
  convention is the *harder* one to violate, so a witness for it also kills the μ_std form
  (2·m·S² ≤ n³(n(n−1))²).
- Confirmed in the ECAI-2025 PDF (Table 1) that 154 is marked **O** (open), searched with
  "any" graphs to size 50, no counterexample found. Also confirmed 143 marked O at n=100.
- Caveat: could not retrieve Fajtlowicz's original "Written on the Wall" text of conj. 154
  online (WoW file not hosted; A–H survey and FMS 1993 paywalled; Brewster–Dinneen–Faber
  1995 PDF text doesn't quote it). The problem file cites the R–C 2025 encoding/Table 1 as
  the source of the open status, and that encoding was matched line-by-line. Orchestrator
  should double-check WoW's original phrasing (esp. its average-distance convention) before
  announcing; the witness violates *both* plausible conventions, so only a materially
  different WoW invariant would change the verdict. (A sample-stdev variant with n−1
  divisor is *larger* than the population stdev, which only strengthens the violation.)

## Result — SOLVED (counterexample found)

**Witness: lollipop L(50, 70)** — K₅₀ with a pendant path of 70 vertices attached at one
clique vertex; n = 120, m = 1295, S = 372120 (ordered-pair distance sum).

- 2·m·S² = 358 645 832 496 000 > n⁷ = 358 318 080 000 000  (R–C convention; excess 3.28e11)
- 2·m·S² > n³(n(n−1))² = 352 370 995 200 000  (standard μ convention; excess 6.27e12)
- Float mirror of the R–C test: stdev = √(2m/n) = 4.645787 > n/μ_RC = 4.643663
  (margin 2.1e−3 ≫ their 1e−5 threshold).

Verifier: `solutions/P07/verify.py` — stdlib-only, builds the lollipop, BFS all-pairs,
pure-integer comparison under both conventions, prints PASS. Independent cross-check with a
*differently written* evaluator (`runs/P07/v2/crosscheck_eig.py`: numpy `eigvalsh` +
Floyd–Warshall, literal stdev vs n/μ, no reformulation): PASS.

This is the **minimal violating parameter choice within the lollipop family under the R–C
convention** (exhaustive exact scan over all (a, ℓ), a+ℓ = n, for n ≤ 220: first violation
at n = 120, a = 50). Under the standard μ convention the first lollipop violation is
already at n = 118 (a = 50). Whether smaller (n < 118) counterexamples exist outside these
families is left open — R–C searched all graphs to n = 50 without success, and the family
ratio at n = 50 is only 0.479, so the true minimum plausibly sits in 50 < n < 118.

## What was searched (encodings, sizes, compute)

All scoring exact (Python `fractions`); score R = 2·m·S²/n⁷ (violation ⇔ R > 1).

1. **Lollipop L(a, ℓ)** (`families.py`, `optimize.py`): closed-form
   S = a² + aℓ² + 3aℓ − a + (ℓ³ − 7ℓ)/3, machine-verified against BFS on random parameters.
   Exhaustive over all a for n ∈ [20, 220] and spot checks to n = 300. Ratio grows linearly:
   R ≈ n·g(a/n); best a/n → c* = (1+√33)/16 ≈ 0.4215, g(c*) ≈ 0.007510 (sympy), so
   R ~ n/133 asymptotically — the conjecture fails for **all** large n, not marginally.
   Values: R(n=50) = 0.479, R(100) = 0.851, **R(120) = 1.000915 (first > 1)**, R(150) = 1.226,
   R(200) = 1.601, R(300) = 2.351.
2. **Dumbbell D(a, ℓ, b)** (`symbolic.py`, `optimize.py`): closed-form S derived with sympy,
   BFS-verified. Exhaustive over all (a, b) for n ∈ [20, 220]: always dominated by the
   lollipop (b = 0 collapse is optimal); no dumbbell beats L at any n scanned.
3. **Theta graphs θ(l₁,l₂,l₃)** (`other_families.py`): exhaustive at n = 120 over all
   partitions: max R = 0.124 (degenerate near-cycle). Sparse ⇒ hopeless (cycles give R ~ 1/8).
4. **Brooms** K_a + p pendant paths (`other_families.py`): at n = 120, p = 2 equal paths max
   R = 0.473 (a = 43); R decreases monotonically in p. Splitting the path only hurts.
5. **Join K_a ∨ P_ℓ**: diameter ≤ 2 ⇒ R ≈ 0.009. Dead end, as expected.

Dead ends: an early brute-force BFS dumbbell scan over all (a,b,ℓ) at n ≥ 100 with rational
arithmetic was killed for slowness (~10 min, no output) and replaced by the closed forms.

Compute: ~25 min total CPU. No SAT/annealing needed — the closed-form family optimization
(exactly the regime the edge-by-edge MCTS at n ≤ 50 could not reach) decided the problem.

## Why R–C missed it

max R at n = 50 is 0.479 — no graph on ≤ 50 vertices in this family violates, and the
violation threshold for the best family is n ≈ 118–120, far above their search size. The
1995 exhaustive n ≤ 10 frontier is irrelevant at this scale.

## Sibling conj. 143 (Var(positive eigenvalues) ≤ m/μ)

Not attacked here (assigned to V5); note that the same lollipop family is the natural
candidate but 143 needs an eigensolve; μ convention caveat applies there too.

STATUS: SOLVED — Graffiti 154 refuted by lollipop L(50,70) (n=120), verified by
solutions/P07/verify.py (integer arithmetic, both μ conventions) + independent
numpy cross-check; family analysis shows failure for all n ≳ 120.
