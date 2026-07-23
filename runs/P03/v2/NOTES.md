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
