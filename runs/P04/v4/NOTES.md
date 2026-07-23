# P04 — Hajós cycle-decomposition conjecture — Variant V4 (extremal families / perturbation)

Session: https://app.devin.ai/sessions/2b4567ec32f343ed852ee39ad5cdecb9
Branch: `runs/P04-v4`

## 0. Statement re-verification & openness check

- Statement checked against Heinrich–Natale–Streicher, arXiv:1705.08724 ("Hajós' cycle
  conjecture for small graphs"): *every simple Eulerian graph on n vertices decomposes into
  at most ⌊(n−1)/2⌋ edge-disjoint cycles*. Matches the problem file. This is the
  Lovász-1968-attributed Hajós conjecture, NOT the topological-K5 one.
- Openness (Exa/arXiv search, July 2026): only partial results found — Girão–Granet–Kühn–
  Osthus (dense asymptotic), Fuchs–Gellert–Heinrich (min-counterexample structure),
  exhaustive verification to n = 12 (HNS 2017), plus 2025 Erdős–Gallai-adjacent preprints
  (Bucić–Montgomery 2211.07689; 2509.01901) that do not resolve Hajós. Treated as open.
- Consequence of prior work: any counterexample has n ≥ 13, 3-connected, δ ≥ 6 for a
  *minimal* one (perturbed candidates need not be minimal, so we did not prune on this).

## 1. Toolchain (all in this directory)

- `mincyc.py` — exact oracle. CP-SAT model: k color classes; each class forced to be one
  (possibly empty) cycle via `AddCircuit` with self-loop literals; every undirected edge
  gets exactly one (class, direction); first-use inter-class symmetry breaking.
  `decomposable_within(n,E,k)` decides "∃ decomposition into ≤ k cycles";
  `min_cycles` searches upward from the ⌈Δ/2⌉ lower bound. Runtime 0.1–0.3 s per instance
  for n ≤ 20 dense.
- `search.py` — perturbation hill-climb keeping a pool of *tight* instances
  (mincyc = K = ⌊(n−1)/2⌋). Moves: (a) vertex split of a degree-≥6 vertex, moving an even
  number of its edges to a new vertex (odd n → n+1 keeps K constant — the key V4 lever);
  (b) toggling a closed pair-set (flip pairs along a random vertex cycle, length 3–8;
  preserves all degree parities); (c) double toggles. Density-biased pool selection.
- `structural_tight.py` — random Eulerian sampler with a max-degree cap Δ ≤ 2K−2, hunting
  instances tight for non-degree reasons.
- `climb.py` — direct hill-climb on mincyc(G) (accept non-decreasing moves, kick on
  stagnation), seeds: random capped-degree or splits of K_{n−1}.
- `analyze_structural.py` — includes `independent_mincyc_lb`: a pure-Python
  branch-and-bound cycle-removal decision procedure used as a second, independently
  written verifier for cross-checking CP-SAT verdicts.

## 2. Tight (equality) families confirmed by machine

All verified feasible at K and infeasible at K−1 by CP-SAT:
- K_{2k+1}, 2k+1 ∈ {5,…,15}.
- K_{2k} − perfect matching, n ∈ {14, 16}: m = K·n exactly (the unique edge-maximal
  Eulerian graphs — degree sum forces 12-regular at n=14, 14-regular at n=16); the
  decomposition must be all-Hamilton and exists (Walecki), so counting arguments alone can
  never beat the bound; Erdős–Gallai circumference extremal graphs are clique trees, which
  motivated the clique-tree seeds below.
- Clique bouquets (cliques sharing one vertex): (7,7), (5,5,5), (9,5), (7,5,3) at n=13;
  (9,7), (7,7,3), (5,5,5,3), (11,5), (13,3) at n=15; (9,9) at n=17. All tight.
- Clique trees (path-glued cliques): (5,5,5) n=13, (7,7,3) n=15, (5,5,5,5) n=17,
  (5,5,5,5,3) n=19. All tight, and *structurally* tight: Δ = 8–12 < 2K, so the ⌈Δ/2⌉
  degree bound does NOT explain tightness — tightness is additive over blocks.
- Vertex splits of K_{2k+1} (all non-isomorphic single splits of K13 → n=14 and
  K15 → n=16, exhaustive over the move parameter a ∈ {2,4,…}): all still decompose at
  the same K. No witness.

## 3. Search campaign (all negative — no witness, no timeout)

| run | seed family | n range | instances | TIGHT | witness |
|---|---|---|---|---|---|
| log_k14mpm | K14−PM | 14 | 3000 | 2772 | 0 |
| log_k13split | split(K13) | 14 | 2999 | 2714 | 0 |
| log_k16mpm | K16−PM | 16 | 2000 | 1901 | 0 |
| log_k15split (+_b) | split(K15) | 16 | 5999 | 5017 | 0 |
| log_k13 | K13 | 13–14 | 3999 | 3081 | 0 |
| log_bq77 | bouquet(7,7) | 13–14 | 4000 | 2400 | 0 |
| log_bq5553 | bouquet(5,5,5,3) | 15–16 | 4000 | 2485 | 0 |
| log_bq99 | bouquet(9,9) | 17–18 | 4000 | 2576 | 0 |
| log_ct773 (+_b) | cliquetree(7,7,3) | 15–16 | 8000 | 4810 | 0 |
| log_ct555 | cliquetree(5,5,5) | 13–14 | 4997 | 2687 | 0 |
| log_ct5555 | cliquetree(5,5,5,5) | 17–18 | 3999 | 1881 | 0 |
| log_ct55553 | cliquetree(5,5,5,5,3) | 19–20 | 3990 | 124 | 0 |

Totals: ~51,000 distinct perturbed Eulerian instances, 32,448 of them exactly tight
(mincyc = K); every single one decomposes within the Hajós bound.

Plus:
- `structural_n14_d10.txt`: 3000 random Eulerian n=14, Δ ≤ 10 — max mincyc seen = 5
  (never even reaches K=6 without a Δ=2K vertex, at this density regime).
- `structural_n16_d12.txt`: 2000 random Eulerian n=16, Δ ≤ 12 — max mincyc = 6 < K=7.
- `climb_*`: direct mincyc hill-climbs at n ∈ {14,16,18,20} (seeds: random capped and
  splits of K13/K15/K17/K19), ~30k oracle calls — every trajectory plateaus exactly at
  K and never reaches K+1.

## 4. Cross-validation of the oracle

On a structurally tight instance found by search (n=13, m=27, Δ=8, a perturbed
cliquetree(5,5,5); edge list in `structural_analysis` section of log_ct555.txt and in
§4 test), the independent pure-Python brancher agrees with CP-SAT:
not decomposable into ≤5 cycles, decomposable into 6. Both directions match.

## 5. Near-misses / observations (the interesting part)

1. **The bound is sharp *everywhere* near the extremal families.** Tightness is extremely
   common (60–80% of random parity-preserving perturbations of tight instances stay tight)
   but was never once exceeded. The tight "plateau" is huge and connected under our moves,
   which is why hill-climbing wanders it freely yet never finds a step up.
2. **Structural tightness exists and is cheap to make** (clique trees/bouquets: tightness
   adds over blocks while the degree bound does not), but block-additivity also caps it at
   exactly K: blocks of size s_i contribute ⌊s_i/2⌋ each and Σ⌊s_i/2⌋ ≤ ⌊(n−1)/2⌋ with
   equality iff all blocks odd — the Erdős–Gallai clique-tree mechanism reproduces but
   never exceeds the bound.
3. **Counting can never refute Hajós at the top end**: the edge-maximal Eulerian graphs
   K_{2k}−PM satisfy m = K·n exactly and are Hamilton-decomposable; every other Eulerian
   graph has m ≤ K·n − 2. So a counterexample must be an *obstruction* to packing, not a
   volume argument — consistent with why our volume-flavored perturbations all fail.
4. Vertex splitting (n odd → n+1 at constant K) never raised mincyc in ~9000 attempts,
   including all single splits of K13/K15 exhaustively. Splitting distributes a forced
   vertex's cycles but the decomposition always re-routes.

## 6. Dead ends

- Independent-set / bipartite-style counting bounds (cycle visits to an independent set)
  provably cannot exceed K for simple graphs — checked algebraically, max Σ_I deg is far
  below the needed 2K·⌊n/2⌋.
- Theta-like families (many degree-2 vertices on shared hub pairs) are exactly tight,
  never over: t common-neighborhood degree-2 vertices pair up into ⌈t/2⌉ 4-cycles.

## 7. Wave 2 — structured algebraic families & new gradients (after restart)

New scripts: `circulants.py`, `blowups.py`, `regular_sample.py`, `count_anneal.py`.

1. **Exhaustive circulant sweep (frontier result).** ALL connected Eulerian circulants
   C_n(S), 13 ≤ n ≤ 26 — 16,049 graphs (7,925 for n ≤ 24 + 8,124 for n = 25–26; every
   connection set S ⊆ {1..⌊n/2⌋} with even degree and gcd connectivity) — decompose within
   K = ⌊(n−1)/2⌋. Includes Paley(13), Paley(17), Paley(25), cycle powers, complements of
   cycles, and K_n/cocktail graphs as special cases. Logs: `circulants_n24.txt`,
   `circulants_n26.txt`. Zero infeasible, zero timeouts (0.1–9 s each). To our knowledge
   no exhaustive Hajós verification for any family at n up to 26 was previously reported
   (general exhaustion stops at n = 12).
2. **Blow-ups / products / named graphs** (`blowups.txt`): C_k[empty_t] and C_k[K_t]
   blow-ups (13 ≤ n ≤ 26), triangular graphs T(6), T(7) = L(K_6), L(K_7) (n = 15, 21),
   complete multipartite graphs with even degrees up to n = 26 (incl. K_{7,7,7},
   K_{5,5,5,5}, 8 parts of 2). All decompose.
3. **Minimal-counterexample-zone mass sampling** (`regular_s701/702.txt`): 40,000 random
   d-regular Eulerian graphs, d ∈ {6,8,10}, n = 13–20 (double-edge-swap randomization of
   circulant seeds; ≈1,100 graphs per (n,d) cell per seed × 2 seeds). Any minimal
   counterexample must have δ ≥ 6; every sample decomposes within K.
4. **Decomposition-count annealing** (`count_anneal.py`, new gradient): score = capped
   CP-SAT enumeration of (assignment, orientation) solutions at K; anneal toggles to
   minimize the count toward 0 (0 = counterexample, verified by a separate feasibility
   call). Runs at n = 13 (600 iters) and n = 14 (500 iters), cap 100: the count never
   dropped below the cap on any accepted state — tight instances near the extremal
   families have *many* decompositions, another sign of slack robustness.

Totals across both waves: ≈115,000 Eulerian instances exactly decided, n = 13–26,
zero violations of the Hajós bound.

## 8. Wave 3 — LP/ILP duality gap + nonabelian Cayley frontier

1. **LP/ILP duality-gap attack** (`lp_gap.py`, METHODOLOGY-V4 framing proper): fractional
   cycle-decomposition LP solved by column generation (master over a cycle pool seeded with
   all ≤5-cycles; pricing = exact max-dual-weight cycle DFS; CBC master). Sanity: K7 → 3,
   K9 → 4 (LP = ILP). Annealed toggles maximizing gap = mincyc − LP at n = 13 (500 iters,
   done) and n = 17 (partial): **the observed gap is 0.000 everywhere** — on every sampled
   Eulerian graph in these neighborhoods the fractional and integer cycle-decomposition
   numbers coincide, and for the extremal clique trees even the LP equals K exactly. There
   is no local LP/ILP gap to exploit; an LP-value certificate > K (which would imply a
   counterexample) never came close. Logs: `lp_gap_n13_s901.txt`, `lp_gap_n17_s902.txt`.
2. **Dihedral Cayley sweep** (`dihedral.py`, first nonabelian family): all Eulerian Cayley
   graphs of D_m — exhaustive over inverse-closed connection sets for m = 7, 8, 9
   (n = 14, 16, 18; 6,482 connected Eulerian graphs) and 1,729 random connection sets for
   m = 10–13 (n = 20–26). All decompose within K. Log: `dihedral.txt`. Combined with the
   circulant sweep, Hajós now machine-verified for 24k+ vertex-transitive Eulerian graphs
   on 13–26 vertices.

## STATUS

STATUS: negative / frontier-pushed — no counterexample found; ~51k perturbed instances
around all known extremal families (n = 13–20), plus exhaustive verification for ALL
16,049 connected Eulerian circulants with 13 ≤ n ≤ 26, all blow-up/multipartite/line-graph
families tried (n ≤ 26), and 40k random δ≥6 regular graphs (n = 13–20): every instance
decomposes within ⌊(n−1)/2⌋. Oracle cross-validated by an independent brancher. The
equality plateau is large, connected under parity-preserving moves, and never exceeded.

Wave 3 additions: zero LP/ILP duality gap observed anywhere (fractional = integer
cycle-decomposition number on every instance sampled; LP = K on extremal clique trees),
and 8,211 dihedral Cayley graphs (exhaustive n = 14–18, sampled to 26) all satisfy Hajós.
Most informative negative findings for future attacks: (i) any counterexample must beat
the LP relaxation too, so LP-based pruning is sound and cheap; (ii) tightness is
plentiful but always exactly K — the conjecture behaves like a sharp isoperimetric-type
inequality with a fat equality manifold rather than a fragile bound.
