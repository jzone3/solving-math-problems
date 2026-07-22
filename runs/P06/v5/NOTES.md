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

## 4. Conjecture 129: reduction program (sharp lemmas isolated; proof gap remains)

With R ≥ m/λ1 (steps 1–2 of the 698 proof) and R ≥ m²/S (Cauchy–Schwarz),
129 follows from ANY of:

- **G\*: λ1 · dev_L ≤ m** (λ1 adjacency spectral radius);
- **I\*: s⁺ · dev_L ≤ m** (stronger: s⁺ ≥ λ1);
- **M\*: S · dev_L ≤ m²**, S = Σ_{uv∈E} √(d_u d_v) — eigenvalue-free!

All three verified with NO violation: exhaustive n ≤ 9 (G\*, I\*), n ≤ 8/9
(M\*), annealing to n = 120 (G\*, I\*) / n = 60 (M\*) always saturating at
exactly 0, tight precisely at K_k ∪ (k−2)K_1 and asymptotically at stars.
Since √(xy) is supermodular, S is maximized among realizations of a degree
sequence by switch-stable (threshold-like) graphs, and dev_L is degree-only,
so threshold graphs are the natural extremal candidates for M\*: exhaustive
over ALL 2^(n−1) threshold creation sequences for n ≤ 21 (`threshold_scan.py`)
— max exactly 0 at the same family. Proving M\* for threshold graphs (a
2-parameter-per-block analysis) is the isolated remaining gap for 129.

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

## 5. Searches (all negative = conjectures supported)

- Exhaustive (nauty-geng, incl. disconnected): all graphs n ≤ 9 for 129 (std
  and MAD readings) and 698A; n = 10 COMPLETE (all 12,005,168 graphs): max
  score 0 for both, attained only by the equality families
  (129: K_6 ∪ 4K_1; 698A: complete bipartite + isolated).
- Exhaustive over all threshold graphs n ≤ 21 (2^20 creation sequences) for
  the M\* reduction: max exactly 0 at K_k ∪ (k−2)K_1.
- Parameterized families: stars, stars+matchings/cliques, double stars,
  complete split, K_{a,b} ± edges/matchings, complete multipartite, up to
  n = 400. All ≤ 0; K_{a,b} exactly 0 for 698A.
- Simulated annealing (edge flips, 5 seed types incl. equality-family seeds,
  scores dev_L − R and s⁻ − R): n ∈ {10,…,28,32,40,48,60,80}. Every run
  saturates at exactly 0 by rediscovering the equality families; never > 0.

## 6. Compute spent

~10 min exhaustive n ≤ 9 (both conjectures, three readings) ×2, n = 10 full
scan (12.0M graphs, ~25 min), threshold scan n ≤ 21 (~2 min, vectorized),
annealing ~3 core-h total (conjectures + 6 reduction scores, n up to 120),
degree-sequence annealing for H\*, family scans ~2 min. Single VM, numpy.

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
- `../../solutions/P06/PROOF-698.md` — full proof writeup for 698.
- `../../solutions/P06/verify.py` — independent verifier (exact arithmetic)
  for the claimed results: the 698A proof-chain inequalities, the equality
  families, and the refutationGBR-698 vacuity claim. Prints PASS.

## STATUS

**STATUS: frontier-pushed / partially SOLVED — WoW conjecture 698 (correct
adjacency reading) PROVED TRUE (elementary proof via λ1R ≥ m ⇒ λ1²+R² ≥ 2m ⇒
s⁻ ≤ R; equality iff complete bipartite + isolated; machine-checked, verify.py
PASS, exhaustive to n = 10); its refutationGBR encoding shown vacuous
(definitional bug: Laplacian has no negative eigenvalues). Conjecture 129 NOT
refuted: exhaustive n ≤ 10 (12M graphs), threshold graphs n ≤ 21, annealing to
n = 120, families to n = 400 all negative; 129 reduced to the sharp
eigenvalue-free inequality M\*: S·dev_L ≤ m² (tight at K_k ∪ (k−2)K_1 and
stars), with Hong/M2/neighbor-sum composites machine-refuted as dead ends.**
