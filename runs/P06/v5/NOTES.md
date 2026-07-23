# P06 — V5 run (definitional audit + literature-first reasoning)

Session: devin-9deb68e98d174f6da7a5147877859d94 (V5 of 5 parallel runs).
Branch: `runs/P06-v5`.

## 1. Definitional audit (V5 mandate)

Re-derived the precise statements from the ORIGINAL source: Fajtlowicz,
*Written on the Wall* (wow-july2004.ps, fetched via web.archive.org from
math.uh.edu/~clarson/, converted with ghostscript). Exact text:

- **129**: "deviation of eigenvalues of Laplacian ≤ the Randić index."
- **698**: "length of negative eigenvalues ≤ the Randić Index."

Supporting glossary (Brewster–Dinneen–Faber 1995, Discrete Math 147, glossary
pp. 52–54, fetched from cs.auckland.ac.nz/~mjd/graffiti/graffiti1.pdf):

- "Length (of a vector). The square root of the sum of the squares of the components."
- "Eigenvalue(s). Unless otherwise specified, the eigenvalue(s) of the
  **adjacency** matrix of the graph."  (WoW itself says the same near conj. 698.)

**Reading of "deviation":** population standard deviation. Pinned by a
consistency check: WoW 244 "deviation of eigenvalues of Laplacian ≤ n/2" is
marked PROVED (FMS 12.88); under the unnormalized sqrt-of-sum-of-squares
reading K_n trivially refutes it, so deviation must be the (population) std
dev. We nevertheless also tested the mean-absolute-deviation reading (below).

### Definitional BUG found in refutationGBR (Roucairol–Cazenave 2025)

`src/models/conjectures/GenerateGraph.rs`, CONJECTURE == 698 computes the L2
norm of the **negative eigenvalues of the LAPLACIAN** — but the Laplacian is
PSD, so that quantity is identically 0 and the tested statement `0 ≤ R(G)` is
**vacuously true**. The 2025 MCTS search reported for 698 (open row, Table 1
of the ECAI-2025 paper) was therefore searching a theorem-by-bug; the original
WoW 698 is about the **adjacency** spectrum. Their conj 129 code matches the
std-dev reading (population std dev of Laplacian eigenvalues).

So the correct statements attacked here:
- **129**: sqrt( (1/n) Σ (μ_i − 2m/n)² ) ≤ R(G), μ_i Laplacian eigenvalues.
- **698A** (faithful): s⁻(G) := sqrt( Σ_{λ_i<0} λ_i² ) ≤ R(G), λ_i adjacency
  eigenvalues.

Both confirmed open as of the ECAI-2025 paper (rows "129 O", "698 O" in its
Table 1); no dedicated literature found linking dev_L or s⁻ to R.

## 2. Key identities / near-miss structure

- **dev_L is degree-based**: Σμ_i² = Σ d_i(d_i+1), so
  dev_L² = Var(d) + d̄  (population variance of the degree sequence plus
  average degree). Conjecture 129 is a *degree-sequence + Randić* statement;
  no eigensolve needed.
- **Equality families found (exact):**
  - 129: G = K_k ∪ (k−2)K_1 gives dev_L = k/2 = R exactly (x=(k−1)/n with
    n=2(k−1) maximizes x−x² = 1/4). Stars only approach equality (ratio → 1).
  - 698A: every complete bipartite K_{a,b} (± isolated vertices) gives
    s⁻ = √(ab) = R exactly.
  These infinite tight families explain why MCTS "near-misses" clustered at
  star-like graphs and why no counterexample was found.

## 3. MAIN RESULT: proof of 698A (so WoW 698 is TRUE, a theorem)

Let G have m ≥ 1 edges, adjacency spectrum λ_1 ≥ … ≥ λ_n,
s⁺² = Σ_{λ>0} λ², s⁻² = Σ_{λ<0} λ², S = Σ_{uv∈E} √(d_u d_v),
R = Σ_{uv∈E} 1/√(d_u d_v).

1. **λ1 ≥ S/m.** Rayleigh quotient with x_u = √(d_u):
   xᵀAx = 2S, xᵀx = 2m.
2. **S·R ≥ m².** Cauchy–Schwarz on the m edge weights w_e = √(d_u d_v):
   (Σ_e 1)² ≤ (Σ_e w_e)(Σ_e 1/w_e).
3. Hence **λ1·R ≥ m**, so **λ1² + R² ≥ 2λ1R ≥ 2m** (AM–GM).
4. Since Σλ_i² = 2m and s⁺² ≥ λ1²:
   **s⁻² = 2m − s⁺² ≤ 2m − λ1² ≤ R².** ∎

Every step is elementary; the sharp intermediate inequality λ1² + R² ≥ 2m
appears to be new (equality iff complete bipartite plus isolated vertices:
needs CS equality (d_u d_v constant on edges), √d a λ1-eigenvector, and
s⁺ = λ1, i.e. one positive eigenvalue ⇒ complete multipartite ⇒ complete
bipartite). Machine checks: exhaustive all graphs n ≤ 9 (E* = λ1²+R²−2m ≥ 0,
min 0 at complete bipartite) and the final inequality on n ≤ 10 / annealing to
n = 80 — no violation, equality exactly as characterized.

## 4. Conjecture 129: partial theorems + all product reductions refuted

**Proved (see solutions/P06/PROOF-129-partial.md):**
- 129 holds for all REGULAR graphs (trivial from dev_L² = d, R = n/2).
- 129 holds for all TREES: the star's degree sequence majorizes every tree's
  (forest prefix-sum bound Σ_S d ≤ (n−1)+(k−1)), Var is Schur-convex, and
  Bollobás–Erdős 1998 gives R(T) ≥ R(star) = √(n−1) ≥ dev_L(star).
- Unicyclic case reduced computationally to S_n+e (max dev_L AND min R among
  unicyclic, verified n ≤ 10), where the gap is >1 and growing (~√n).

**Reduction program (all refuted — 129 defeats every product relaxation):**
With R ≥ m/λ1 (steps 1–2 of the 698 proof) and R ≥ m²/S (Cauchy–Schwarz),
129 would follow from any of G\*: λ1·dev_L ≤ m, I\*: s⁺·dev_L ≤ m,
M\*: S·dev_L ≤ m². Each holds exhaustively for n ≤ 9–11 and saturates at 0
in annealing to n = 120, tight at K_k ∪ (k−2)K_1 — yet ALL are FALSE at
scale: symbolic analysis of the complete-split family CS(a,b) (b dominating,
a independent vertices; `mstar_symbolic.py`) shows M\* fails for a ≫ b
(CS(100,2): +422.9), and numerically G\* fails there too (CS(100,2): +2.19),
hence I\* as well. The sandwich structure: along CS(a,b), a → ∞,
R² − dev_L² → b(b+1) > 0 (2nd-order expansion), so CS(a, small b) are
asymptotically near-tight for 129 while violating every product surrogate.
This is strong structural evidence 129 is *sharp in two independent regimes*
(K_k ∪ (k−2)K_1 exactly; stars/CS(a,b) asymptotically) and needs a proof
that tracks both.

Refuted intermediate routes (dead ends, all machine-refuted):
- **H\*** (Hong composite): (2m − n′ + 1)·dev_L² ≤ m² is FALSE as a pure
  degree-sequence statement — annealing over graphical sequences
  (`hstar_search.py`) finds e.g. d = (12,11,2×10,1) with adversarial isolated
  padding, gap +10.96. Hong's bound is too lossy for hub-plus-many-low-degree
  sequences (their λ1 is far below √(2m−n′+1)).
- **C\***: M2 · dev_L² ≤ m³ (M2 = Σ_E d_u d_v): holds n ≤ 9 but FALSE at
  n = 20/30 (annealed violations, `reduction_anneal.py`).
- **J\***: (max_u Σ_{v~u} d_v) · dev_L² ≤ m²: FALSE (n = 16 annealed).
- **K\***: (max_{uv∈E} m_u m_v) · dev_L² ≤ m² (m_u = avg neighbor degree):
  FALSE already at n = 7 exhaustive.
- **D\*** (AM–GM via M1): FALSE at stars.
- **G\*, I\*, M\*** (see above): FALSE at CS(a,2), a ≳ 40–100.
- **W** (route via Bollobás–Erdős for all connected graphs):
  Var(d)+d̄ ≤ n−1 is FALSE for connected graphs (CS(2,4), n = 6, +0.22);
  works only for trees where majorization saves it.

## 5. Searches (all negative = conjectures supported)

- Exhaustive (nauty-geng, incl. disconnected): all graphs n ≤ 9 for 129 (std
  and MAD readings) and 698A; n = 10 COMPLETE (all 12,005,168 graphs): max
  score 0 for both, attained only by the equality families
  (129: K_6 ∪ 4K_1; 698A: complete bipartite + isolated).
- **n = 11 COMPLETE for 129: all 1,018,997,864 graphs** (C scanner
  `scan129.c`, degree-identity dev_L + exact R accumulation, 8-way geng
  res/mod split, ~30 min wall). NO violation; worst gap −0.01243 at
  J?ACKMF`{N_ (K_6 ∪ 5K_1). This extends the Brewster–Dinneen–Faber n ≤ 10
  computational frontier for 129. (M\* also ≤ 0 for all n ≤ 11.)
- Exhaustive over all threshold graphs n ≤ 21 (2^20 creation sequences) for
  the M\* reduction: max exactly 0 at K_k ∪ (k−2)K_1 (M\* fails only later,
  n ≳ 40).
- Block-threshold scan of 129 itself (`threshold_blocks.py`): all 1- and
  2-block-pair threshold graphs with block sizes on a log grid up to 12000
  (n up to 24002, 195k graphs, exact O(1) formulas): max score 0 (K_2),
  near-misses only at huge stars (−0.009 at n = 12001).
- All trees n ≤ 14 and all connected unicyclic graphs n ≤ 10 (networkx/geng):
  extremal-structure checks for the partial theorems.
- Parameterized families: stars, stars+matchings/cliques, double stars,
  complete split, K_{a,b} ± edges/matchings, complete multipartite, up to
  n = 400. All ≤ 0; K_{a,b} exactly 0 for 698A.
- Simulated annealing (edge flips, 5 seed types incl. equality-family seeds,
  scores dev_L − R and s⁻ − R): n ∈ {10,…,28,32,40,48,60,80}. Every run
  saturates at exactly 0 by rediscovering the equality families; never > 0.

## 6. Compute spent

~10 min exhaustive n ≤ 9 (both conjectures, three readings) ×2, n = 10 full
scan (12.0M graphs, ~25 min), **n = 11 full scan (1.019B graphs, 8 cores ×
~30 min, C)**, threshold scan n ≤ 21 (~2 min, vectorized), block-threshold
scans to n = 24002, annealing ~4 core-h total (conjectures + 7 reduction
scores, n up to 120), degree-sequence annealing for H\*, sympy symbolic
analysis of CS(a,b), family scans. Single 8-core VM.

## 7. Files

- `invariants.py` — invariant definitions under all readings.
- `exhaustive.py`, `exhaustive_mad.py` — geng-based exhaustive scans.
- `family_scan.py` — closed-form family scans.
- `local_search.py` — annealed edge-flip search.
- `test_reduction.py`, `test_reduction2.py`, `test_reduction698.py`,
  `test_reduction129.py`, `test_reduction129b.py` — machine checks of the
  reduction chains (E*/F*/G*/H*/I*/J*, C*/D*).
- `hstar_search.py` — degree-sequence annealing refuting H\*.
- `reduction_anneal.py` — graph annealing refuting C\*, supporting G\*/I\*.
- `mstar_anneal.py`, `threshold_scan.py` — the eigenvalue-free M\* reduction.
- `mstar_symbolic.py` — symbolic refutation of M\* on CS(a,b,c) + ray
  asymptotics (also yields the R²−dev² → b(b+1) near-tightness result).
- `scan129.c` — fast exhaustive C scanner (used for the full n = 11 run;
  logs in `logs/n11_*.log`).
- `threshold_blocks.py` — block-threshold closed-form scan to n ≈ 24000.
- `../../solutions/P06/PROOF-698.md` — full proof writeup for 698.
- `../../solutions/P06/PROOF-129-partial.md` — 129 proved for trees and
  regular graphs; unicyclic reduction; dead-end table.
- `../../solutions/P06/verify.py` — independent verifier (exact arithmetic)
  for the claimed results: the 698A proof-chain inequalities, the equality
  families, and the refutationGBR-698 vacuity claim. Prints PASS.

## STATUS

**STATUS: frontier-pushed / partially SOLVED — WoW conjecture 698 (correct
adjacency reading) PROVED TRUE (elementary proof via λ1R ≥ m ⇒ λ1²+R² ≥ 2m ⇒
s⁻ ≤ R; equality iff complete bipartite + isolated; machine-checked, verify.py
PASS, exhaustive to n = 10); its refutationGBR encoding shown vacuous
(definitional bug: Laplacian has no negative eigenvalues). Conjecture 129 NOT
refuted but frontier pushed hard: PROVED for trees and regular graphs;
exhaustively verified for ALL graphs n ≤ 11 (1.019B graphs, beyond the n ≤ 10
literature frontier); block-threshold graphs to n = 24002; annealing to
n = 120; two independent asymptotically-tight families identified
(K_k ∪ (k−2)K_1 exact, CS(a,b) with R²−dev² → b(b+1)); ALL eight product
relaxations (Hong/M2/S/λ1/s⁺/neighbor-sum composites) machine-refuted,
explaining why the conjecture resists simple spectral proofs.**

## Round 4: new encoding — degree-sequence transportation bound N*, and n = 12

**N\* (new reduction, realization-free).** For degree sequence d (all ≥ 1)
let e be the 2m endpoint multiset (vertex of degree k contributes k copies of
k). Since 1/√(xy) is symmetric supermodular, every perfect matching of e
(in particular the edge set of ANY realization) has weight ≥ the antitone
pairing:  LB(d) = Σ_{i=1..m} (e_(i) e_(2m+1−i))^{−1/2} ≤ R(G).
LB is EXACT for stars, cliques, complete split CS(a,b), complete bipartite.
N\*: dev_max(d) ≤ LB(d), where dev_max maximizes dev_L over isolated-vertex
padding (optimal n = clamp(8m²/(M1+2m), ≥ n′)). N\* ⟹ 129 for every graph
with non-isolated degree sequence d, ANY padding, ANY realization.

Machine results (`nstar_check.py`, `nstar_blocks.py`):
- ALL graphical degree sequences with n′ ≤ 12 (all ~163k sequences at
  n′ = 12): N\* holds; max = 0 exactly at regular K_k sequences.
  NOTE: this is stronger than graph-by-graph search — it certifies 129 for
  all graphs with support ≤ 12 REGARDLESS of realization and padding.
- All 2-class degree sequences (a^p b^q) with values/counts on a log grid to
  3000 (n′ ≤ 6000, 57.8k graphical class-tuples): max −0.018 (stars).
- 3-class sequences on a log grid to 800: running (see logs/nstar_mode3.log).
- Sequence annealing (n′ ≤ 250): all negative.
- LB tightness at every near-tight family means there is NO LP-integrality
  gap to exploit at the known extremal structures.

**n = 12 exhaustive sweep of 129** (all ~165.6 billion graphs, 1000-way geng
split × 8 cores, C scanner): running, logs/n12/chunk_*.log.

### Round 4 results (final)
- **n = 12 COMPLETE for 129: all 165,091,172,592 graphs** (1000-way geng
  split, C scanner, ~3.5h on 8 cores; chunk count cross-checked against the
  exact number of n=12 graphs). NO violation: max score exactly 0, attained
  ONLY by the equality graph K_7 ∪ 5K_1 (degrees 6^7 0^5). M* likewise ≤ 0
  at n = 12. Summary: logs/n12_summary.txt (chunks: logs/n12_chunks.tar.gz).
  Computational frontier for 129 now n ≤ 12 (literature: n ≤ 10).
- 3-class N* scan complete: 5,079,684 graphical class-tuples (values/counts
  log grid to 800, n′ up to ~2400): N* holds, worst −0.178 (quasi-complete
  sequences), no LP-integrality gap found anywhere near tightness.
- Combined with N* for all sequences with n′ ≤ 12: conjecture 129 is now
  verified realization-free for every graph whose non-isolated part has at
  most 12 vertices, with ANY number of isolated vertices (any total n).
