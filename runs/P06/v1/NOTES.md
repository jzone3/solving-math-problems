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

Result: **all strictly negative except the equality family itself** (score 0). Local
search from G_q and its random 1–4-edge perturbations always terminates back at score 0
(the equality graph) or below; no positive direction exists among single edge toggles on
N ∈ {8,10,12,14}.

## 5. Exhaustive check n ≤ 10, ALL graphs including disconnected (`exhaust_small.py`)

nauty-geng over all 12,293,434 graphs with 2 ≤ n ≤ 10. Only graphs with score ≥ −1e−9:
empty graphs (0 = 0) and exactly the equality family members K_q ∪ (q−2)K₁ for
q = 2,3,4,5,6 — each re-verified to be EXACTLY zero in sympy. No violation. This extends
Brewster–Dinneen–Faber's connected-only n ≤ 10 exhaust to all graphs.

## 6. Reduction to degree sequences + new exhaustive frontier (`degseq_search.py`, `frontier.py`)

Since dev depends only on d, define the realization-independent lower bound
    R_lb(d) = ½ Σ_u w_u · (sum of the d_u smallest weights among the others), w=d^{−1/2}.
Then dev(d) ≤ R_lb(d) for all graphical d of length n ⟹ conj 129 holds for all graphs on
n vertices. Exhausting ALL graphical degree sequences (Erdős–Gallai) with float scoring +
60-digit mpmath re-check of near-zeros + sympy-exact settlement of ties:

- n ≤ 23: max of dev − R_lb is EXACTLY 0, attained only by the all-zero sequence and
  (for n = 2(q−1)) the equality sequence (q−1)^q 0^(q−2).  ⟹ **conjecture 129 holds for
  every graph on ≤ 23 vertices** (new exhaustive frontier; previous exhaustive was n ≤ 10).
  Enumeration: Python (`frontier.py`) to n = 15, then C (`frontier.c`, ~200×, outputs
  cross-checked to match Python's graphical-sequence counts and near-zero lists exactly
  for n ≤ 15) single-threaded to n = 21, then sharded on (d₀,d₁) over 8 cores
  (`tasks22.txt`/`tasks23.txt`, per-shard results in `shards2*_summary.txt`; shard-sum
  cross-checked = single-run count at n = 14): 149,990,133,774 graphical sequences at
  n = 22 and 581,393,603,996 at n = 23 (~783e9 total over all n ≤ 23). Every sequence
  with float score > −1e−6 was re-verified exactly (sympy): all are the equality family
  ((q−1)^q 0^(q−2) for even n, last hit 11¹²0¹⁰ at n=22) or all-zero, diff exactly 0;
  best non-tight float score at n=23 was −0.00567.
- randomized hillclimb over graphical sequences at n = 16…400: max 0, always the equality
  sequence.
- block-structured annealing (`block_anneal.py`, ≤5 degree blocks, closed-form O(B²)
  scoring cross-checked vs expanded sequences, block-boundary Erdős–Gallai) at
  n = 10³, 10⁴, 10⁵, 10⁶: max = 0, always the equality family (e.g. (n/2)^(n/2+1) 0^(n/2−1))
  or the empty graph — nothing crosses at any scale up to a MILLION vertices.
- 114k random graphical sequences scored (blocks, power-law, uniform, equality-
  perturbations; n up to 700, `random_degseq.py`): max = 0, again exactly the equality
  sequence (350² 0³⁴⁹ at n = 700); everything else strictly negative.

## 7. Compute spent

~16 h total: family closed-form sweeps (seconds), threshold anneal (~15 min),
mpmath perturbation sweep + local search (~45 min), geng exhaust n≤10 (~8 min),
degree-sequence exhaust (Python ~30 min to n=15; C single-core ~3.5 h to n=21;
8-core sharded ~2.5 h for n=22 and ~8 h for n=23), block anneal to n=10⁶ (~20 min),
random degseq search (~10 min).

## Dead ends / lessons

- All connected star-like families approach the bound from below (score → 0⁻) but never
  cross; complete bipartite has exact closed form dev²−R² = 2ab(a+b−2ab)/(a+b)² ≤ 0.
- Isolated vertices are essential to reach equality (connected-only searches like the 2025
  MCTS runs cannot even see the tight family).
- The coded conjecture 698 in refutationGBR is trivially true as written (negative
  Laplacian eigenvalues of a PSD matrix); its true WoW statement needs V5's source work.

## STATUS

**negative / frontier-pushed.** No counterexample to WoW 129. New results:
(1) exact equality family G_q = K_q ∪ (q−2)K₁ with dev = R = q/2 (verified exactly;
`solutions/P06/verify.py` prints PASS with two independent checks);
(2) conj 129 reduced to a pure degree-sequence inequality dev(d) ≤ R_lb(d);
(3) that inequality — hence conj 129 — verified exhaustively for ALL graphs with n ≤ 23
(up from the previous exhaustive frontier n ≤ 10). Everything points to 129 being TRUE
and tight exactly on {∅, K₂, K_q ∪ (q−2)K₁}; recommend V5 attempt a proof via the
degree-sequence reduction.
