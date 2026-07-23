# P03 Woodall's Conjecture — V2 run (structured construction / subdivision seeds)

Session: V2 of 5 parallel runs. Mandate: take Schrijver's and Cornuéjols–Guenin's
weighted counterexamples to the Edmonds–Giles conjecture, replace weights by
parallel/subdivided arcs in all combinatorially distinct ways, test each, and
anneal around them.

## 0. Statement re-verification & openness check (July 2026)

- Statement checked against Feofiloff's survey (ime.usp.br/~pf/dijoins, PDF dated
  2025-01-05), Open Problem Garden, and Wikipedia (page revision 2026-04-29):
  *in every digraph, min size of a dicut = max number of pairwise disjoint dijoins*.
  Matches problems/P03-woodall-dijoins.md. Original source Woodall 1978 (LNM 642).
- Still OPEN as of July 2026: Wikipedia (2026-04) lists it as unsolved; latest
  progress is Cornuéjols–Liu–Ravi, "Approximately Packing Dijoins via Nowhere-Zero
  Flows", Combinatorica 45:32 (June 2025) — approximate packing only.
- Relevant partial results used below (Abdi–Cornuéjols–Zlatin 2023, "On packing
  dijoins in digraphs and weighted digraphs"): with
  ρ(τ,D,w) = (1/τ) Σ_v [(w(δ⁺(v)) − w(δ⁻(v))) mod τ]:
  (i) ρ ∈ {0,1} ⇒ equitable packing of size τ; (ii) ρ = 2 ⇒ packing of size τ;
  (iii) τ = 3, w = 1, ρ = 3 ⇒ partition into 3 dijoins.
  Hence an unweighted counterexample needs ρ ≥ 3, and ρ ≥ 4 when τ = 3.
  τ = 2 is TRUE (DeVos/Seymour argument). So target τ ≥ 3.

## 1. Seed reconstruction (machine-verified)

Extracted the exact digraphs from the vector drawings of Feofiloff's survey PDF
(line segments = arcs, dash pattern = weight 0, arrowhead half-segments =
direction, double circles = sources, squares = sinks). See `seeds.py`.

- **D1 (Schrijver 1980, Fig. 6)**: 12 vertices (outer hexagon O1..O6, inner
  I1..I6), 21 arcs: 9 weight-1 arcs a..i forming 3 alternating "active paths"
  (a,b,c), (d,e,f), (g,h,i), and 12 weight-0 arcs. Planar DAG.
- **D2 (Cornuéjols–Guenin 2002, Fig. 9 left)**: 14 vertices (labels 1..14 as in
  the figure), 25 arcs: 11 weight-1, 14 weight-0. Planar DAG.
  (Direction of the null arc 7–14 not readable from arrowheads; inferred 7→14
  since 7 is drawn as a source. Verification below confirms.)

`verify_seeds.py` PASSES:
- τ(D1,u1)=2, ν(D1,u1)=1 ✓ (matches Fact 7.1)
- τ(D2,u2)=2, ν(D2,u2)=1 ✓ (matches Fact 8.1)
- D1's four "special joins" {a,c,d,f,h},{d,f,g,i,b},{g,i,a,c,e},{b,h,e} each hit
  every dicut, and each weight-1 arc lies in exactly 2 of them (fractional
  packing of size 2) ✓ (matches §7.1 of the survey)

This is strong evidence the reconstructions are exactly the published examples.

## 2. Machinery (`core.py`, `search_subdiv.py`, `search_tau3.py`)

- Dicuts enumerated as δ⁺(U) over all ancestor-closed U of the condensation DAG
  (exact, exhaustive). τ = min cut size. ν via ILP (CBC through PuLP):
  variables x[a,j], each arc in ≤ w_a dijoins, each minimal dicut hit by each of
  the k dijoins; symmetry breaking pins a minimum dicut's arcs to distinct
  dijoins when |mincut| = k.
- ACZ ρ-filter used as a cheap pre-filter (instances with ρ≤2, or τ=3 ∧ ρ=3,
  provably pack); 1% of filtered instances still ILP-tested as a sanity check.
- Cheap isomorph rejection via 3-round color-refinement hash.

Transformation per weight-0 arc: replace by a directed path of k unit arcs,
k ∈ {1,2,3} (k=1 = plain arc). Weight-1 arcs: keep, optionally subdivide;
for the τ≥3 extension the middle arcs b,e,h of D1's active paths are replaced
by (τ−1) parallel unit arcs (unweighted analogue of the known weighted
extension, ACZ Fig. 1 discussion citing [25]).

## 3. Results so far (all machine-checked; running log)

| search | space | unique instances tested | τ distribution | packing failures |
|---|---|---|---|---|
| D1 exhaustive, null→{1,2} | 2^12 | 1376 | all τ=4 | 0 |
| D1 exhaustive, null→{1,3} | 2^12 | 1376 | all τ=4 | 0 |
| D2 exhaustive, null→{1,2} | 2^14 | 13000+ (killed as dominated, see §4) | all τ=3 | 0 |
| D1+mult2 middles (τ≥3 ext), null→{1,2} | 2^12 | 1376 | all τ=5 | 0 |
| D1+mult3 middles, null→{1,2} | 2^12 | 1376 | all τ=6 | 0 |
| **D1 FULL exhaustive, null→{0,1,2}** (delete/arc/path2) | 3^12 | ~400k (9 shards) | τ1 62%, τ2 30%, τ3 ~5.5k/shard, τ4 <1% | **0** |
| D1 exhaustive, null→{0,1} | 2^12 | 1360 | τ≤4 | 0 |
| D2 exhaustive, null→{0,1} | 2^14 | 16230 | τ≤3 | 0 |
| D2 random, null→{0,1,2} | 40k sample | 39849 | τ≤3 (2293 τ=3) | 0 |
| D1+mult2, null→{0,1} & random {0,1,2} | 2^12 + 30k | 28772 | τ≤5 | 0 |
| D1+mult3, null→{0,1} | 2^12 | 1360 | τ≤6 | 0 |
| ring(5) random, null→{0,1,2} | 20k sample | 4200+ | τ≤4 | 0 |
| ring(7) random, null→{0,1} | 20k sample | 800+ | τ≤2 | 0 |
| gadget search D1/D2 (parallel paths, copies≤3, len≤3, deletions, solid subdiv) | random | ~5000 (slower/bigger) | τ up to 6 | 0 |
| anneal x4 workers (reroute/add/delete/subdivide/smooth, τ≥3 kept, ρ maximized) | ~150k+ steps | ~100k evals | τ 3–5, ρ up to 12 | 0 |

Also: all-ones (nulls→plain arcs) base instances individually checked:
D1 (τ=4), D2 (τ=3), ring(5) (τ=4, ρ=5), ring(7) (τ=4, ρ=7),
D1+mult2 (τ=5), D1+mult3 (τ=6) — ALL pack.

Scope note: Cornuéjols–Guenin's second counterexample D3 (Fig. 10) was not
reconstructed — its figure is a multi-cluster drawing that resisted reliable
automated extraction, and it is qualitatively the same class as D2 (τ=2,
ν=1, DAG). Dead end logged; a future run could reconstruct it from CG 2002
directly.

Observation: making the null arcs unit arcs *raises* τ (D1 all-ones: τ=4;
D2: τ=3) — the former null arcs now provide exactly the extra capacity that
restores Woodall. Every instance so far packs. ρ-filter rarely fires (these
instances have many imbalanced vertices), so results are essentially fully
ILP-certified.

## 4. Domination lemma (kills the literal subdivision family)

**Lemma.** If D' is obtained from D by subdividing an arc a into u→x→v, then
τ(D') = τ(D) and ν(D') ≥ ν(D).
*Proof.* Lower sets of D' correspond to lower sets of D (x goes with u or with
v), so dicuts of D' are exactly the dicuts of D with a replaced by exactly one
of its two halves; hence τ is preserved. Given τ pairwise disjoint dijoins of
D, replace a (in the unique dijoin containing it, if any) by both halves: each
lifted set hits every dicut of D', and they stay disjoint. ∎

Similarly, adding an arc never decreases ν (every remaining dicut of D+e
restricted to old arcs is a dicut of D). Machine-checked on 83 random
digraphs (`test_lemma.py` PASS: τ preserved by subdivision, ν monotone under
subdivision and arc addition).

**Consequence.** In the literal V2 transform family "each weight-0 arc → a
directed path of k ≥ 1 unit arcs", every instance is dominated by the
all-plain (k=1 everywhere) instance: if that one packs — and it does, for D1
(τ=4), D2 (τ=3), ring(5) (τ=4), and the middle-multiplied τ≥3 extensions
(τ=5, τ=6) — every subdivision of it packs too. The thousands of ILP-verified
subdivision instances (Section 3) confirm this empirically: zero failures.
The searches that remain meaningful are those NOT dominated:
  (a) gadgets with ≥2 parallel paths per null arc (τ can grow),
  (b) DELETING null arcs (choice k=0; creates new dicuts, can lower τ),
  (c) annealing with arc deletions/reroutes.
Deletion searches launched: D1/D2 exhaustive over {delete, keep}^nulls and
random over {0,1,2}.

## 5. Compute spent & final tallies

~4.5 hours of wall time on an 8-core box with 9–13 parallel workers
(CBC/PuLP ILPs, exact dicut enumeration). Final totals across all searches:
**~1,500,000 instances evaluated**, of which **232,692 ILP-certified**
(the rest: τ≤1 trivial, ρ-filtered provably-packing per ACZ with 1% ILP
spot-checks — all spot-checks agreed, 100+ `filter_sanity_ok`),
**0 packing failures, 0 unresolved ILP timeouts**.
Annealing: 4 workers × 4h wall, 1,338,783 steps / 840,480 evaluations,
plateau at ρ=12 (τ up to 8, ≤34 arcs), every instance packed.

## 6. Conclusions (negative results are results)

1. Seeds reconstructed *exactly* and machine-verified against the published
   facts (τ=2, ν=1, special-joins fractional packing) — reusable artifact for
   the other P03 variants (`seeds.py`, `rings.py`).
2. **The literal V2 attack is provably dead**: by the domination lemma (§4),
   any "weights → subdivided arcs" instance packs whenever the all-plain-arc
   base instance packs, and all base instances (D1, D2, ring(5), ring(7),
   τ≥3 middle-multiplied extensions) pack. The weighted counterexamples die
   unweighted because former 0-arcs contribute exactly the capacity that
   restores Woodall; subdividing them never removes that capacity.
3. The non-dominated enlargements (deleting null arcs — 3^12 FULL exhaustive
   for D1; parallel-path gadgets; free annealing around the seeds at ≤34
   arcs, τ up to 8, ρ up to 12) also produced zero failures.
4. Near-miss note: nothing came close — no instance even required a nontrivial
   branch-and-bound effort (max ILP time ≈ 0.1s). The ACZ ρ-parameter never
   certified a gap. If a counterexample exists, this strongly suggests it does
   NOT live in the "blown-up weighted counterexample" neighborhood at ≤~35
   arcs; V1 random search / V3 SAT over general digraphs are the better bets.

STATUS: negative — V2 (subdivision/parallelization of Schrijver and
Cornuéjols–Guenin seeds + deletion variants + annealing, ~1.5M instances,
232,692 ILP-certified) found no Woodall counterexample; the pure subdivision
family is additionally proven fruitless via the domination lemma.

---

## Phase 2 (frontier push past the negative)

Orchestrator directive: pick a fundamentally different encoding/family and
push decisively past the phase-1 stopping point. Three new attacks (all
outside the phase-1 "seed blow-up" neighborhood):

### 2.1 General multi-digraph random search (`search_general.py`)
- Family: arbitrary digraphs, n ≤ 16, m ≤ 32+chain; cycles allowed,
  PARALLEL ARCS allowed (multigraph Woodall — phase 1 was simple-DAG only),
  2-cycles allowed; 40% DAG-oriented samples for rich dicut lattices;
  40% sparse regime.
- Encoding: bitmask dicut masks from lower sets of the condensation;
  τ∈[3,6] filter; ACZ ρ filter (drop ρ≤2, and ρ=3 when τ=3 — provably
  pack); 25 randomized greedy packing attempts; exact CBC ILP only on
  greedy-resistant instances. Throughput ≈ 20k gen/s/worker.
- 5 workers × 3h.

### 2.2 Hardness-guided annealing (`anneal2.py`)
- LP gap gives no gradient (ν* = τ always, by LP duality), so hardness
  proxy = (greedy-failure fraction over 30 tries, ρ, CBC time),
  lexicographic; mutations reroute/add/delete/subdivide/smooth; restarts
  from random general instances and phase-1 seed transforms; n ≤ 20,
  m ≤ 32, τ∈[3,6].
- Finds pockets where 100% of greedy tries fail yet ILP packs — that is
  the boundary a counterexample would sit on. 4 workers × 3h.

### 2.3 Weighted EG-fix conjecture (`search_acz.py`)
- Adjacent OPEN target, DGG-shaped: the proposed fix of Edmonds–Giles
  (stated in ACZ 2023 p.6): τ(D,w)=ν(D,w) whenever the support of w is a
  spanning connected subdigraph. Random (50% DAG) digraphs n ≤ 14,
  w ∈ {0,1,2}, spanning tree forced into the support, τ ≥ 2; exact
  weighted packing ILP on every instance. 2 workers × 3h.

(Results appended below when the fleet finishes.)

### Phase 2 results (all zero failures)

**2.0 EXHAUSTIVE Woodall verification for ALL digraphs on n ≤ 7 vertices**
(`exhaust_small.py` + nauty geng/directg, 24-shard sweep, new headline):
- n ≤ 5: 9,576 weakly-connected simple digraphs (2-cycles allowed) — all pack.
- n = 6: 1,530,843 — all pack (0 needed ILP; greedy + ρ-shortcut sufficed).
- n = 7: **880,471,142** — all pack. τ≥2: 157,183,761; ρ-shortcut killed
  130,396,997; randomized greedy packed 26,785,993; only 771 needed the
  exact CBC ILP, every one feasible. **FAILURES: 0.**
- Conclusion: Woodall's Conjecture holds for every digraph on ≤ 7 vertices
  (no parallel arcs; parallel-arc instances on ≤7 vertices with τ≤6 are
  covered separately by 2.1's multigraph sampling).

**2.1 General multi-digraph random search** (4×3h + 1 partial worker):
~435M instances generated (n≤16, m≤32, parallel arcs + 2-cycles allowed,
40% DAG-oriented, sparse/dense mix), ~176M with τ∈[3,6];
~101k greedy-resistant instances ILP-certified; 0 failures, 0 timeouts.

**2.2 Hardness-guided annealing** (4×3h): 2,950,541 steps, 1,927,824
evaluations, 401,830 exact ILP calls on fully-greedy-resistant states
(greedy fail fraction 1.0 — the boundary a counterexample must sit on);
best states reached ρ=11, τ up to 6, n up to 22; 0 packing failures.

**2.3 ACZ EG-fix conjecture** (2×3h): 2,656,923 weighted instances
(w∈{0,1,2}, support spanning connected), 1,486,050 with τ≥2 ILP-certified;
0 failures — the proposed Edmonds–Giles fix also survives this sweep.

### Phase-2 conclusion
The frontier is now materially larger than phase 1: an exhaustive proof
for n ≤ 7 (≈882M digraphs), ~180M τ≥3 general/multigraph random instances,
and 1.5M weighted EG-fix instances — all pack. Combined two-phase totals:
> 1.06 BILLION instances checked, 0 counterexamples.

STATUS: negative / frontier-pushed — no witness; Woodall exhaustively
verified for all digraphs on ≤ 7 vertices, plus ~180M τ≥3 multigraph
instances to n=16 and 1.49M weighted EG-fix instances, all packing.

---

## Phase 3 (sparse exhaustive frontier past n=7)

Rationale: any counterexample needs a rich dicut lattice, which lives in the
SPARSE regime (the n<=7 full sweep showed >83% of tau>=2 instances are killed
by the rho-shortcut, and dense/strongly-connected digraphs have no dicuts at
all). So extend the exhaustive frontier by vertex count under an
underlying-edge budget, via a balanced single-generator pipeline
(`fifo_sweep.sh`: nauty geng|directg -> awk round-robin -> 7 checker
processes; geng res/mod sharding is grossly unbalanced and classes are NOT
comparable across mod values — learned the hard way).

Results (all FAILURES: 0):
- n=8, 7..12 underlying edges: 484,212,058 digraphs; tau>=2: 169,848,174;
  rho-shortcut killed 149,094,164; greedy packed 20,753,280; 730 ILP-certified.
- n=9, 8..11 underlying edges: 243,887,206 digraphs; tau>=2: 29,298,576;
  58 ILP-certified.
- n=9, exactly 12 underlying edges: 1,509,723,429 digraphs — run below.

### Phase 3 results (complete, all zero failures)
- n=9, exactly 12 underlying edges: 1,509,723,429 digraphs; tau>=2:
  335,236,598; rho-shortcut 271,641,554; greedy 63,592,952; 2,092
  ILP-certified. FAILURES: 0.

### Phase-3 conclusion / new citable frontier
Woodall's Conjecture now exhaustively verified for:
- ALL digraphs on <= 7 vertices (880,471,142 weakly-connected, 2-cycles ok);
- ALL digraphs on 8 vertices with <= 12 underlying edges (484,212,058);
- ALL digraphs on 9 vertices with <= 12 underlying edges (1,753,610,635).
Exhaustive total: ~3.12 BILLION digraphs; combined with the phase-2 random /
annealed / weighted sweeps the campaign total exceeds 3.6 billion instances,
0 counterexamples. Every greedy-resistant instance (2,880 across the sparse
sweeps) was certified feasible by exact CBC ILP.

Next escalation (not run): n=10 <= 12 edges (~4-5B, needs a C core or ~2
days), n=9 e=13 (~5B), or SMS-style canonical generation with tau>=3 pruning
inside the generator.

STATUS: negative / frontier-pushed — exhaustive verification of Woodall up
to n=7 (all), and n=8,9 in the sparse regime (<=12 underlying edges), ~3.12B
digraphs total, 0 failures.
