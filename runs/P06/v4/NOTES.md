# P06 V4 — exhaustive small-n attack on Graffiti 129 / 698

Session: V4 of 5 parallel runs. Variant mandate: geng-exhaust n = 11–13 (both
conjectures), then trees only to n ≈ 24.

## 0. Statement re-verification (against reference source)

Original WoW PDF (wow-july2004.pdf) is CID-encoded and un-extractable; the cited
reference invariant code github.com/RoucairolMilo/refutationGBR (Rust) was used as the
definitional source (`src/models/conjectures/GenerateGraph.rs`, `invariants.rs`):

- **Conj 129** (`CONJECTURE == 129`): population standard deviation (÷n, not n−1) of the
  eigenvalues of the standard Laplacian L = D − A is ≤ Randić index
  R(G) = Σ_{uv∈E} (d_u d_v)^{−1/2}. Unambiguous; this is what we attack.
- **Conj 698** (`CONJECTURE == 698`): as coded, it is the L²-norm of the **negative**
  eigenvalues of the **Laplacian** ≤ R(G). The Laplacian is PSD ⇒ LHS ≡ 0 ⇒ the coded
  check is **vacuous** (trivially true). This is a definitional bug/ambiguity in the
  reference harness (probably adjacency vs Laplacian mix-up: for the adjacency matrix,
  stars give L²-norm of negative eigenvalues = √(n−1) = R exactly, which would make a
  sensible tight conjecture).
- We also tested the alternative reading "L²-norm of centered Laplacian eigenvalues
  √(Σ(λ−λ̄)²) = dev·√n ≤ R": it is **massively false already at n = 5** (33/34 graphs
  violate, e.g. every star), hence cannot be the intended open conjecture either.
  ⇒ 698 cannot be attacked meaningfully without the original definition (V5's job);
  everything below is about 129 (we still logged the 698-alt counts).

Open-status check (July 2026): Roucairol–Cazenave, "Refutation of Spectral Graph Theory
Conjectures with Search Algorithms" (ECAI 2025 workshop paper), Table 1 lists both
129 and 698 as **O**(pen), attacked with 7 MCTS/beam algorithms, 15 min each, graphs up
to size 50, no counterexample. No other dedicated literature found (Exa searches).

## 1. Key structural reduction (makes exhaustion cheap)

trace(L) = 2m and trace(L²) = Σd_i² + 2m give

    dev(L)² = (Σd_i² + 2m)/n − (2m/n)²   — depends ONLY on the degree sequence.

So conj 129 ⇔ for every graph, sqrt((Σd²+2m)/n − (2m/n)²) ≤ R(G). No eigensolve needed;
each graph costs O(m). Verified against direct eigendecomposition (crosscheck.py: all
1251 graphs with n ≤ 7 + 2000 random G(n,p), agreement < 1e−9).

## 2. Exact equality family (the conjecture is TIGHT)

    G_k = K_k ∪ (k−2)·K_1   (K_k plus k−2 isolated vertices, n = 2k−2)

has dev = R = k/2 **exactly** (verified in exact arithmetic, sympy, k = 3..40; equality
condition 4(k−1)(n−k+1) = n² ⇔ n = 2k−2). Every equality/tie case found anywhere in the
searches below is of this form. Infinitely many equality cases ⇒ no slack in 129.

Padding analysis: for fixed H with m edges and S = Σd², padding with isolated vertices
gives var(N) = (S+2m)/N − (2m/N)², maximized at N* = 8m²/(S+2m) with max dev =
(S+2m)/(4m). K_k is exactly extremal for this padded bound ((S+2m)/(4m) = k/2 = R,
N* = 2k−2 integral). Stars satisfy dev² − R² = −2k(k−1)/(k+1)² < 0 exactly (k = n−1),
so the star "near-miss" family never crosses.

## 3. Exhaustive searches (all NEGATIVE — no violation of 129)

Hardware: 8 cores. Checker: `check.c` (graph6 → degrees/edges → both sides; also checks
optimal isolated-vertex padding of every graph, i.e. floor/ceil of N* clamped to > n).

| Search space | count | 129 violations | best gap (dev−R) | witness |
|---|---|---|---|---|
| all graphs n ≤ 10 (geng, incl. disconnected) | 12,293,449 | 0 | 0 (ties only: K_4∪2K_1 n=6, K_6∪4K_1 n=10) | — |
| **all graphs n = 11** | **1,018,997,864** (matches known count) | 0 | −0.01449 (K_7∪4K_1) | — |
| n ≤ 11 + optimal isolated-vertex padding (any total N) | same | 0 | 0 (ties = K_k family only) | — |
| all graphs n = 12 | 165,091,172,592 | RUNNING (64 chunks × ./run12.sh, ~17 h est.) | | |
| trees n = 13..25 (gentreeg) | 164,650,262 | 0 | −0.1837 (star K_{1,24}) | — |
| trees n = 26..28 | RUNNING | | | |

Best strict near-miss at n = 11: K_7 ∪ 4K_1, gap −0.014492815876 (it wants N = 12 =
2·7−2, where it ties exactly — confirmed by the PAD check).

698-alt (dev·√n ≤ R) violation counts at n = 11: 1,018,996,485 / 1,018,997,864 graphs
violate — reading definitively wrong.

n = 13 (5.01e13 graphs) is infeasible on this hardware (~200 core-days at our
throughput); documented as out of reach; padding check partially compensates by
covering all ≤12-core + any-padding graphs.

## 4. Degree-sequence optimization beyond exhaustive range

Since dev depends only on D, a violation needs dev(D) > min_{G realizing D} R(G).
`search_degseq.py`: hill-climb over graphical degree sequences (n ≤ 40), with
Rmin(D) estimated by assortative Havel–Hakimi + 2-swap local search minimizing R.
Multi-start from perturbed K_k∪tK_1 and random sequences. Result: converges to the
K_k ∪ (k−2)K_1 equality family at every scale, best gap = 0.000000, never positive.

Also, R ≥ (Σ_v √d_v)/(2√Δ) (per-vertex bound with neighbor degrees ≤ Δ) is tight on
K_k∪tK_1; if dev(D) ≤ (Σ√d_v)/(2√Δ) held for all degree sequences it would prove 129 —
left as a note for V5/proof-oriented follow-up.

## 4b. LP certification of ALL graphs on n = 13 (and beyond enumeration)

Since dev depends only on D, 129 holds for every graph on n vertices iff for every
graphical degree sequence D, dev(D) ≤ Rmin(D). `lp_certify.py` lower-bounds Rmin(D) by
a transportation-style LP over degree-class edge counts x_ab (min Σ x_ab/√(ab) s.t.
degree balance Σ_b x_ab + 2x_aa = a·n_a, capacity x_ab ≤ n_a n_b, x_aa ≤ C(n_a,2));
every realization is feasible, so LP-opt ≤ Rmin(D). A cheap pre-filter
R ≥ (Σ√d)/(2√Δ) handles most sequences.

Results (all graphical degree sequences enumerated via Erdős–Gallai):
- n = 11: 59,347 sequences, worst LP/cheap margin +3.6e-4 → CERTIFIED (agrees with the
  1.02e9-graph enumeration).
- n = 12: 222,116 sequences; single tight case = [6^7,0^5] = K_7∪5K_1 (exact equality,
  proven in exact arithmetic) → CERTIFIED apart from the known equality family.
- **n = 13: 836,314 sequences, worst margin +9.5e-7 (cheap bound; its LP margin is
  +1.375) → conjecture 129 CERTIFIED for ALL ≈50 trillion graphs on 13 vertices** —
  the V4 mandate n = 11–13 is thus fully covered without enumerating n = 13.
- n = 14+ running.

Caveat: float LP; any |margin| < 1e-6 case is re-examined exactly (only the K_k family
ever appears, and it is proven equal exactly).

## 5. Compute spent (so far)

- n=11 full exhaust: ~8 core × 7 min.
- trees to 25: ~2 min. n=12: ~8 core × 17 h (in progress).
- degree-sequence search: 5 min.

## 6. Dead ends / gotchas

- WoW original PDF text is not machine-extractable (CID glyphs) — definition had to be
  taken from refutationGBR Rust code.
- 698 as coded is vacuous; both natural re-readings are trivially true or trivially
  false. Do not burn compute on 698 until V5 pins the definition.
- Background jobs launched from one-shot shells get killed; use setsid + persistent tty.

## STATUS (checkpoint, n=12 still running): negative

No counterexample to 129 in: all graphs n ≤ 11 (new exhaustive frontier, previous
published frontier n ≤ 10), those graphs with arbitrary isolated-vertex padding, all
trees n ≤ 25 (mandate was 24), and degree-sequence optimization to n = 40. The
conjecture is exactly tight on the infinite family K_k ∪ (k−2)K_1 — strong structural
evidence that 129 is TRUE, and any counterexample must beat an exact-equality family.
