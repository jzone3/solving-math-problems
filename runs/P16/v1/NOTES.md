# P16 v1 — BHS bounds 44 & 46: direct counterexample search (quotient graphs + annealing)

Session: https://app.devin.ai/sessions/14967f8607f4457da2a394f0eb1fa53d
Branch: `runs/P16-v1`. Variant: V1 (direct counterexample search over equitable-partition
quotient graphs + simulated annealing on the violation margin; exact certificate path via
rational char poly + Sturm in `verify_p16.py`).

## Outcome (TL;DR)

**Negative result — no counterexample found.** Both bounds survived:
- exhaustive search over ALL connected graphs on 2–10 vertices (~11.9M graphs at n=10);
- exhaustive enumeration of realizable equitable-partition quotient structures with k=2
  (cell sizes ≤ 30, entries ≤ 30) and k=3 (cell sizes ≤ 14);
- simulated annealing over quotient structures, k ≤ 6, cell sizes up to 400, entries up
  to 200 (36+ seeds × 200k–400k iters per bound);
- simulated annealing directly on graphs (edge flips), n ∈ {10, 14, 18, 24, 30, 40}.

The maximum violation margin ever observed is **exactly 0**, attained precisely on
(a,b)-semiregular bipartite structures with a = b (regular bipartite: μ = 2a = RHS for both
bounds). All perturbations away from these tight configurations are strictly negative.
This is soft evidence the two bounds are **true**, with equality exactly on regular
bipartite graphs — consistent with them surviving three prior refutation campaigns.

## Statement fidelity (mandatory check — found an error in the catalog file)

- Primary source used: Damnjanović–Ha–Stevanović, arXiv:2606.14550 (v1, 2026-06-12),
  LaTeX source (arXiv e-print), Table 2 lines 176–177:
  - Bound 44: `2+\sqrt{2((d_i-1)^2+(d_j-1)^2+m_i m_j-d_i d_j)}` over edges ij ∈ E
  - Bound 46: `2+\sqrt{2(d_i^2+d_j^2)-16d_i d_j/(m_i+m_j)+4}` over edges ij ∈ E
- **The catalog file `problems/P16-bhs-44-46.md` had the whole expression under the
  radical — WRONG.** The leading "2 +" is OUTSIDE the sqrt. Corrected in this branch.
  (PDF text extraction loses radical extent; the LaTeX source is unambiguous.)
- Conventions: G connected, ≥ 2 vertices, no isolated vertices; d_i = degree; m_i =
  (1/d_i) Σ_{j∈N(i)} d_j; μ(G) = largest eigenvalue of L = D − A; max over edges of G.
- Residual risk: the numbering 44/46 comes from Ghebleh–Al-Yakoob–Kanso–Stevanović,
  DAM 380 (2026) (paywalled, not independently re-checked), and the original BHS 2006
  LAA 414 paper is paywalled. DHS 2026 (co-authored by Stevanović, who co-authored both)
  restates the formulas explicitly, so this risk is low.

## Priority check (2026-07-23) — bounds 44/46 still open

- arXiv:2606.14550 (2026-06-12) Theorem 1.1: of the 36 remaining bounds, 22 confirmed,
  12 refuted, **44 and 46 explicitly left open**. This is the openness certificate.
- GitHub artifact repos checked (the P07-scoop lesson):
  - `Ivan-Damnjanovic/bhs-bounds` (DHS supplementary; last push 2026-06-28: README only;
    scripts `bound_confirmation.py` / `bound_refutation.py` — no 44/46 resolution).
  - `txh2120/bhs-counterexamples` (Taewoo Ha, v1.2.0, 2026-04-05): refutes bounds
    11, 13, 40, 45, 48 only — predates DHS and is subsumed by it; 44/46 untouched.
  - GitHub repo/code search: "bhs-bounds", "laplacian spectral radius bound
    counterexample", "Brankov", "2606.14550" — nothing further.
- Zenodo API (`laplacian spectral radius bound`): nothing on 44/46.
- OpenReview search: nothing relevant.
- Exa web search ("Bound 44"/"Bound 46" Laplacian, BHS 2026): only the DHS paper, its
  supplementary repo, the Ha repo, and the earlier campaigns (GKAS DAM 2026;
  Taieb–Roucairol–Cazenave–Harutyunyan LION 2025; Roucairol–Cazenave arXiv:2409.18626).
- arXiv API listing was flaky from this box (empty responses); covered via Exa +
  Semantic Scholar instead. Semantic Scholar: zero citations of 2606.14550 so far.

## Encoding

Search space: pairs (n, B) — cell sizes n_1..n_k and k×k nonnegative-integer quotient
matrix B, realizable per DHS Lemma 2.3 (b_ii ≤ n_i − 1; b_ii or n_i even; b_ij ≤ n_j;
n_i·b_ij = n_j·b_ji), cell graph connected. Then a connected G with this equitable
partition exists; μ(G) ≥ ρ(L_B), L_B = diag(s) − B, s_i = Σ_j b_ij; and both d_i = s_i and
m_i = (Σ_j b_ij s_j)/s_i are constant per cell, so RHS(bound) is computed *exactly* from B.
Violation margin = ρ(L_B) − max_{cell-edges} f(d_i,m_i,d_j,m_j). ρ(L_B) computed on the
symmetrized similarity M_ij = −e_ij/√(n_i n_j) (e_ij = n_i b_ij) via `eigvalsh` (search
path only).

Note: L_B is independent of the diagonal entries b_ii (internal edges cancel:
L_B[i][i] = s_i − b_ii = Σ_{j≠i} b_ij). Internal edges only shape d_i/m_i, i.e., the RHS —
so in this family they can only *raise* effective degrees; the μ lower bound never sees
them. A finer partition is needed to capture internal structure (the direct graph
annealing screen covers this from the other side).

## Scripts

- `search_quotient.py` — annealing over (n, B); moves: off-diagonal ±(n_j/g) steps keeping
  n_i b_ij = n_j b_ji, diagonal ±, resize cells, duplicate/drop cells; random restarts;
  geometric cooling.
- `enum_small.py` — exhaustive k=2 (n ≤ 30, b ≤ 30) and k=3 (n ≤ 14, diagonals ≤ 6 values)
  enumeration.
- `exhaustive_geng.py` / `geng10_chunk.py` — nauty-geng exhaustive over all connected
  graphs n ≤ 10 (n=10 split 20 ways via `res/mod`).
- `anneal_graphs.py` — direct edge-flip annealing on graphs, n up to 40.
- `verify_p16.py` — **exact independent verifier** (accept path has no floats):
  realizability check; char poly of L_B by Faddeev–LeVerrier over `Fraction`; Sturm-chain
  root counting to certify a rational λ with ρ(L_B) > λ; RHS comparison by exact squaring
  (λ > 2 and (λ−2)² > inner, inner ∈ ℚ per cell-edge). Prints PASS iff refutation certified.
  Sanity-checked: correctly *rejects* the tight K_{a,a} states (margin 0).

## Compute log / frontiers

| Search | Scope | Result (best margin) |
|---|---|---|
| exhaustive geng | all connected graphs n = 2..9 (273k at n=9) | 0 at regular bipartite (n even); < 0 otherwise; no violation |
| exhaustive geng | all connected graphs n = 10 (~11.7M), 20 chunks | no violation (see geng10_*.log) |
| enum k=2 | n_i ≤ 30, b ≤ 30, full diagonals | 0 (semireg. bipartite a=b); never > 0 |
| enum k=3 | n_i ≤ 14 | 0; never > 0 |
| anneal quotient | k ≤ 6, n_i ≤ 400, b ≤ 200; 2×(12+24+40) seeds, 200k–400k iters | 0; never > 0 |
| anneal graphs | n ∈ {10,14,18,24,30,40}, 3 seeds each, 60k flips | best ≈ −0.075 (44), ≈ −0.19 (46); tight states are bipartite-regular-like |

Hardware: 8-core VM, pure Python/NumPy; total ≈ 2–3 CPU-hours.

## Observations / negative results

1. Equality analysis: for any (a,b)-semiregular bipartite graph, μ = a + b, and
   f44 = 2 + √(2((a−1)² + (b−1)²)) ≥ 2 + (a−1) + (b−1) = a + b with equality iff a = b;
   same for f46 (inner = (2a−2)² when a = b). So both bounds are tight exactly on regular
   bipartite graphs — matching every 0-margin state the searches found.
2. Per-edge, f44 ≥ d_i + d_j (Anderson–Morley RHS) whenever m_i m_j ≥ d_i d_j
   (2(x²+y²) − (x+y)² = (x−y)² with x = d_i−1, y = d_j−1). A violation would need
   m_i m_j < d_i d_j on the near-maximizing edges, i.e., adjacent degree-dominant hubs —
   double-star-like shapes; these were explored heavily by the graph annealer, always < 0.
3. Bound 46's expression is **not real on all connected graphs**: e.g. on P₄ the middle
   edge has inner = 2(4+4) − 16·4/3 + 4 = −4/3; also one graph each at n = 6, 7, 8, two at
   n = 9. On all such graphs the max over the remaining (real) edges still exceeds μ, so
   no "vacuous" violation either. Worth flagging to DHS as a well-definedness footnote.
4. No near-misses with margin in (−0.01, 0) other than exact-0 tight states drifting via
   float noise; the landscape around the tight manifold slopes strictly downward.
5. The wide annealing runs' final "best" states with float margin ≈ +1.4e-14 (e.g.
   n = (52,13,13,13,13) with B giving a 40-regular bipartite structure, and
   n = (10,10,5,5,5,5) giving a 20-regular bipartite structure) were fed to the exact
   verifier and correctly REJECTED (`FAIL: could not certify rho(L_B) > RHS`) —
   they are equality cases, not violations. Final run totals: 80 annealing seeds
   (2×40 wide @ 400k iters) over quotients, graph annealer up to n = 40, exhaustive
   n ≤ 10 complete (11,716,571 connected graphs at n = 10, matching the known count).

## Suggested next steps (other variants)

- V5/proof direction looks promising: try Collatz–Wielandt on L or the signless
  Laplacian Q with test vector v_i = d_i + m_i − 2 or similar, aiming to prove
  μ ≤ 2 + √(2((d_i−1)² + (d_j−1)² + m_i m_j − d_i d_j)) via μ ≤ max edge of ρ(Q)-style
  2×2 block comparisons (the 22 DHS confirmations follow this pattern).
- If search is retried: weighted-graph relaxation of the margin (continuous d/m profiles)
  to find where the constrained optimum sits; only then round to integer quotients.
