# P06 / V1 — star-like closed forms (Graffiti WoW 129: dev(Laplacian) ≤ Randić)

Session: devin-2b85f822733548aeb2190d08b5b7bb7f (V1 of 5 parallel runs).

## 0. Statement re-verification (against reference source)

Checked `github.com/RoucairolMilo/refutationGBR` (the reference invariant code cited by the
problem file), `src/models/conjectures/GenerateGraph.rs` + `invariants.rs`:

- **Conj 129** (`CONJECTURE == 129`): `std_dev(eigenvalues of L)` ≤ `randic_index`,
  where `std_dev` is the **population** deviation (divides by n, not n−1) and
  `L = D − A` (standard Laplacian), `randic = Σ_{uv∈E} (d_u d_v)^{−1/2}`. Refutation
  requires `dev − R > 1e-4` in their code, i.e. a **strict** violation.
- **Conj 698 as coded**: LHS = sqrt of the sum of squares of the **negative** Laplacian
  eigenvalues. Since L ⪰ 0, this is numerically ~0 and the coded conjecture is **trivially
  true** — the encoding in refutationGBR appears buggy / not the real WoW 698 (definitional
  issue; flagged for V5). V1 therefore attacks 129 only.
- Openness: web check found no refutation of WoW 129 (Brewster–Dinneen–Faber 1995 exhausted
  n ≤ 10; Roucairol–Cazenave 2025 list it open, MCTS to n = 50).

## 1. Key structural identity (machine-verified, `harness.py` selftest)

For L = D − A: Σλ = 2m and Σλ² = tr L² = Σ_i d_i² + 2m, hence

    dev(L)² = Var(deg) + avg(deg)   — the LHS depends ONLY on the degree sequence.

Verified numerically against `numpy.linalg.eigvalsh` on 200 random graphs (error < 1e−9).
Consequence: a counterexample needs a degree sequence with large Var(d)+d̄ whose min-Randić
realization is still small; assortative (threshold) realizations minimize R heuristically.

## 2. Closed-form family sweeps (`scan_families.py`, all formulas x-checked vs harness)

Families: star, double star, spider, star+pendant paths, complete split CS(n,k),
pineapple, kite, double broom; parameters swept to n = 10⁶–10⁸ (closed forms, O(1) eval).

Result: **all strictly negative**. Best scores approach 0 from below:
- star K_{1,n−1}: exact dev² = R² − 2(n−1)(n−2)/n², so score ≈ −1/√(n−1) → 0⁻;
- CS(n,k) with small k similar (score → 0⁻ as n → ∞, k fixed);
- complete bipartite K_{a,b}: exact dev²−R² = 2ab(a+b−2ab)/(a+b)² ≤ 0, equality iff K₂.

## 3. NEW exact equality family (beyond the K₂ trivial case)

Annealing over threshold graphs (`anneal_threshold.py`, dev+R computed exactly from the
creation sequence, x-checked vs harness) converged at every n ∈ {10,20,40,80,160} to

    G_q = K_q ∪ (q−2)·K₁   (N = 2(q−1) vertices)  ⇒  dev(G_q) = R(G_q) = q/2  EXACTLY.

Sympy-exact proof check (`perturb_equality.py::exact_equality_check`, q up to 1000):
degrees (q−1)^q 0^(q−2) give dev² = q²(q−1)/N − (q(q−1)/N)² = q²/4 and R = C(q,2)/(q−1) = q/2.
Moreover t = q−2 isolated vertices is exactly the maximizer of dev over t.
NOT mentioned in the problem file (only the star O(1) near-miss was known). Note this
family needs **isolated vertices** — searches restricted to connected graphs can't see it.
The equality manifold makes 129 tight infinitely often: any strict local improvement
anywhere near it would refute. This is the natural attack surface.

## 4. Perturbation scan around the equality manifold (`perturb_equality.py`)

Parametrized perturbation families (mpmath 50-digit scoring; any positive would be
sympy-re-verified): clique+pendant-j, clique−matching, K_q∪cK₂∪tK₁, K_q∪K_{1,s}∪tK₁,
q ≤ 59, t ≤ 3q; plus steepest-ascent single-edge-toggle local search over ALL simple graphs
on N ∈ {8,10,12,14} vertices seeded at G_q and random 1–4-edge perturbations of it.

Result: (see run log below)

## STATUS

(pending final runs)
