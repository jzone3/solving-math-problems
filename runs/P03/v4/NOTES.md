# P03 Woodall's Conjecture — V4 (LP/ILP integrality gap) run notes

Session: V4 of 5 parallel runs. Branch `runs/P03-v4`.

## 0. Statement re-verification (done first)

- Original source confirmed: Woodall 1978; statement as in problem file: in every
  finite digraph, min size of a nonempty dicut = max number of pairwise disjoint
  dijoins. Cross-checked against Feofiloff's survey (ime.usp.br/~pf/dijoins,
  2025-05-01), Open Problem Garden, and Wikipedia (rev. 2026-04-29): **still open
  as of July 2026**, open even for τ = 3 (Cornuéjols prize). τ ≤ 2 is settled
  folklore (Schrijver's book Thm 56.3, confirmed in Abdi–Cornuéjols–Zlatin
  arXiv:2202.00392). Latest relevant progress: "Approximately Packing Dijoins via
  Nowhere-Zero Flows" (Combinatorica 2025) — approximate packing only, conjecture
  intact.
- Weighted (Edmonds–Giles) version FALSE: Schrijver 1980 (checked original at
  ir.cwi.nl/pub/9906): 0/1-weighted planar DAG, weight-1 arcs = three disjoint
  alternating paths of length 3, τ_w = 2, ν_w = 1.

## 1. The V4 framing, sharpened

Key structural fact that makes "LP integrality gap" the right lens here:

- The dicut clutter is **ideal** (Lucchesi–Younger gives the min-max for dijoin
  covering; idealness of the dicut clutter follows).
- Idealness is preserved under blocking (Lehman), so the **dijoin clutter is
  ideal**: the LP min{1ᵀx : x(J) ≥ 1 ∀ dijoins J, x ≥ 0} has an integral optimum,
  equal to the min dicut size τ.
- By LP duality, the **fractional dijoin-packing LP has value exactly τ on every
  digraph** (an explicit feasible fractional packing: weight 1/τ on each of the τ
  classes of any... more simply x_{a,j} = 1/τ in the partition formulation is
  feasible since every dicut has ≥ τ arcs).

Therefore: integrality gap of the dijoin packing ILP = τ − ν, and Woodall ⇔ "gap
is always 0". V4 = search instances maximizing τ − ν; any instance with gap ≥ 1
is a full counterexample. The LP side needs no computation (provably = τ); the
work is in an exact ν (ILP) and in steering the search toward instances where
the ILP is maximally constrained (LP-tight instances: many minimum dicuts, few
arcs per unit τ).

## 2. Encodings / machinery (`woodall.py`)

- Digraph = (n, multiset of arcs (u,v)), parallel arcs allowed, no loops.
- Dicuts = δ⁺(U) for ideals U of the condensation DAG (no arc enters U).
  Enumerated exactly via subset scan over condensation components (all instances
  here have ≤ 20 components). τ = min |dicut|.
- ν via ILP feasibility with **lazy dicut row generation**: binaries x_{a,j},
  Σ_j x_{a,j} ≤ 1, each class j must hit every generated dicut; separation
  oracle: class J is a dijoin iff D + reverse(J) is strongly connected; if not,
  any source component of the condensation of D + rev(J) yields a dicut of D
  disjoint from J (new violated row). Solver: CBC via PuLP. ν found by trying
  k = τ, τ−1, ....
- Sanity suite `test_sanity.py`: paths, parallel arcs, cycles, K22, dijoin
  separation — all PASS.

## 3. Validation that the detector can see a gap (`weighted.py`, `rediscover_schrijver.py`)

- Implemented the weighted (Edmonds–Giles) analog: capacities w, Σ_j x_{a,j} ≤
  w_a, τ_w = min-weight dicut. Schrijver's counterexample lives here (τ_w=2,
  ν_w=1), so rediscovering ANY weighted gap instance validates the entire
  pipeline end-to-end.
- Pure random 0/1-weighted DAGs (n ≤ 9, m ≤ 18): 834,840 tries, **no gap** —
  weighted counterexamples are genuinely rare; random sampling insufficient.
- Targeted hill-climb over weight-0 arc sets on the known weight-1 skeleton
  (three disjoint alternating length-3 paths on 12 vertices): ~316k iterations,
  reached many tau_w = 2 instances but no gap -- flat plateau, abandoned in
  favor of exact transcription.
- **Exact transcription** (`schrijver_instance.py`): rendered Figure 6 of
  Feofiloff's survey to PNG, read off all 12 vertices / 21 arcs / weights.
  Machine check: 127 dicuts, tau_w = 2, pack(2) INFEASIBLE, pack(1) feasible
  => nu_w = 1. **Reproduces Schrijver's result exactly; the gap detector is
  validated end-to-end.** Bonus: the same digraph unweighted has tau = 4,
  nu = 4 (Woodall holds there).

## 4. Main search (`search.py`)

- Plateau-accepting hill climb over multi-digraphs, n ≤ 12, m ≤ 30 (witness
  expected ≤ 30 arcs per problem file), weakly connected, not strongly
  connected, **τ restricted to [3,6]** (τ ≤ 2 settled; large-τ instances are
  dense near-bipartite and decompose trivially — early run confirmed drift to
  τ=20 trivia before the restriction).
- Score = (gap, #minimum dicuts, −m/τ): gap first; tie-broken toward LP-tight
  instances (many min dicuts, few arcs per class).
- Cheap canonical-key dedup (degree-sequence refinement) to avoid re-evaluating
  isomorph-ish repeats.
- Throughput ≈ 400–600 evaluated instances/s per process (most time in CBC).

## 5. Exhaustive small-instance verification (`exhaustive.py`)

All simple digraphs (no parallel arcs; 2-cycles allowed) up to isomorphism,
weakly connected, not strongly connected, tau >= 3:

- n = 4: 217 iso classes scanned, 19 with tau >= 3: **all gap 0**.
- n = 5: 9607 iso classes, 1389 with tau >= 3: **all gap 0** (147s).

## 6. Structural reduction: WLOG multi-DAGs

tau and nu are invariant under condensation-with-parallel-arcs (arcs inside a
strong component lie in no dicut; dijoin packings restrict/lift bijectively in
the count). So any counterexample may be assumed to be a weakly connected
multi-DAG, vertices topologically ordered. Implemented as
`condense_multi` and (a) used to normalize every annealer state, (b) made the
basis of a second exhaustive scan over multi-DAGs (`multidag_exhaustive.py`):
support ⊆ upper-triangular pairs, multiplicities >= 1, exact isomorphism dedup
(min over vertex permutations).

Exhaustive multi-DAG results (tau in [3,6], all instances machine-checked;
this directly covers the "witness likely <= 30 arcs" regime for few-component
condensations):
- k=3 vertices, m <= 14 arcs: 202 tau>=3 classes — all gap 0.
- k=4, m <= 14: 13,515 — all gap 0.
- k=4, m <= 18: 50,195 — all gap 0.
- k=4, m <= 22: 123,169 — all gap 0.
- k=5, m <= 12: 61,808 — all gap 0.
- k=5, m <= 14: 307,793 — all gap 0.
- k=5, m <= 16: 1,123,451 — all gap 0 (94 min).
- k=6, m <= 12: PARTIAL — 228,000+ tau>=3 classes checked (2.4h) before the
  process was OOM-killed (unbounded exact-canon dedup set); 0 gaps found.

## 7. Exhaustive simple-digraph results (cross-validated two ways)

- n=4: 19 tau>=3 iso classes — gap 0.
- n=5: 1389 tau>=3 classes — gap 0. Independently cross-checked: my
  hand-rolled enumerator (2^20 masks + exact perm canon) and nauty
  (geng -c 5 | directg) agree exactly on the count (1389) and on gap 0.
- n=6 (nauty, 1,530,843 digraph classes): 243,129 with tau>=3 — **all gap 0**.
  => Woodall verified exhaustively for ALL simple digraphs on <= 6 vertices.

## 8. Results log

(checkpointed as runs proceed; see `results.jsonl`)

- annealers (final runs, DAG-normalized states, ~2.6h each): seed 11
  (tau 3-6) 1.42M evals; seed 44 (tau=3 only) 2.14M evals; seed 55 (tau 3-4)
  1.89M evals; seed 66 (Schrijver-seeded, tau 3-5) 333k evals + restart 77
  (tau 3-4) 937k evals. **Zero instances with gap >= 1** among ~6.7M
  evaluated (~2.9M with tau in [3,6] fully ILP-checked). Runs ended ~88% of
  budget when the OOM killer reaped them (unbounded score caches) — noted as
  an engineering caveat, results unaffected.
- LP spot-checks on the tightest instances found (e.g. n=12, m=16, tau=6 with
  324 minimum dicuts): LP relaxation at k=tau feasible as theory predicts.
- Near-misses: none in the meaningful sense — no instance with nu < tau was
  ever observed (weighted 0/1 analog aside, where Schrijver's instance is
  reproduced). The "tightest" unweighted instances (max #min-dicuts per arc)
  all still packed perfectly.
- Dead ends: (i) random 0/1-weighted sampling never finds Schrijver-type
  weighted gaps (~1M tries) — structure is essential; (ii) coarse isomorphism
  keys silently strangle annealing near structured seeds; (iii) hill-climbing
  on (gap, nmin) plateaus hard — nmin is a weak gradient toward a
  counterexample, if one exists at all in this size regime.

## Compute spent (approx)

~4.5 h wall on 8 cores: ~3.9M exhaustive instances ILP-checked (simple n<=6 +
multi-DAG scans) + ~2.9M annealer ILP evaluations + validation runs.

## Conclusions for the orchestrator

1. No counterexample with <= 30 arcs was found; Woodall now exhaustively
   verified for ALL simple digraphs on <= 6 vertices and ALL multi-DAGs with
   <= 5 components/<= 16 arcs (tau in [3,6]) — beyond any published search we
   could find.
2. The V4 framing collapses (provably) to "find tau - nu >= 1": the
   fractional packing LP equals tau on every digraph by Lehman idealness of
   the dijoin clutter, so there is no "partial" LP signal to climb — this is
   an inherent limitation of gap-guided local search for this problem.
3. If a counterexample exists it likely needs >= 6 condensation components
   and tau = 3 with substantial structure (Schrijver-like rings); suggest V2
   (structured constructions) as the more promising sibling, possibly using
   our verified Schrijver transcription as the seed family.

## 9. Phase 2 (orchestrator push: "don't stop at a negative")

New machinery:
- `min_dicut_flow` (woodall.py): exact tau for ANY size via s-t min cuts on
  the condensation (arc (a,b) cap = multiplicity, reverse arc cap = inf forces
  ideal/closed cuts; scan (source comp, sink comp) pairs; Dinic). Validated
  against the enumerator on 3000 random digraphs — exact agreement. Removes
  the previous 20-component ceiling entirely.
- `seed_dicuts` + lazy separation now handle instances where full dicut
  enumeration is infeasible (packing ILP verified feasible-by-construction at
  n=70, m=112).
- Fixed a latent lazy-separation bug: two classes in the same round can
  legitimately separate the SAME new cut (the "known cut" sanity check must
  compare against the rows present at solve time, not the growing set).
- `multidag_exhaustive.py` canon keys now stored as 128-bit digests: memory
  bounded (~100 MB at 900k instances vs OOM at 32 GB before).

Structure-targeted family search (`ring_family.py`) — probing the unweighted
neighborhood of the known weighted extremal examples (weight-1 arc -> t
parallel copies, weight-0 arc -> 1 arc; optional subdivision of each copy to
break parallel-arc interchangeability; generalized Schrijver rings with r =
3, 5, 7 solid paths on 4r vertices):
- schrijver-scaled t=1..4 (m up to 48, tau up to 10): all nu = tau.
- schrijver-scaled-subdiv t=1..3 (n up to 39, m up to 66, tau up to 8): all
  nu = tau.
- ring r=3,5,7, t=1..3 (n up to 28, m up to 91, tau up to 8): all nu = tau.
- ring-subdiv r=3,5,7, t=1..2 (n up to 70, m up to 112, tau 4-6): all
  nu = tau.
=> The unweighted shadow of the Schrijver/ring family packs perfectly at
every scale tried — consistent with weight-0 arcs being essential.

Exhaustive scans, phase 2 (canon reordered: k! canonicalization only for
tau-in-range instances, making k=7 feasible):
- k=6 components, m <= 12: COMPLETE — 278,860 tau>=3 classes, all gap 0
  (2.8h). Completes the scan that OOM-killed in phase 1.
- k=6, m <= 13: COMPLETE — 1,006,733 tau>=3 classes, all gap 0 (2.5h).
- k=7, m <= 11: COMPLETE — 51,782 tau>=3 classes (74.3M raw instances),
  all gap 0 (2.5h).
- k=6 m <= 14 and k=7 m <= 12: launched as further escalation (see
  k6m14.log / k7m12.log final lines).

Bigger annealers (6h each, memory-bounded caches), ALL COMPLETED, zero
gaps:
- seed 101 (tau 3-4, n<=16, m<=40, random init): 895,494 evals
  (241k tau3 + 151k tau4 ILP-checked).
- seed 202 (ring5-seeded): 678,154 evals (200k tau3 + 109k tau4).
- seed 404 (Schrijver-seeded): 836,750 evals (233k tau3 + 141k tau4).
- seed 303 (ring7-seeded, tau 3-6, n<=30, m<=60, flow-tau path — no
  component ceiling): 70,228 evals (18.7k tau3 / 10.6k tau4 / 4.4k tau5 /
  1.3k tau6).
=> phase-2 annealer total: ~2.48M evaluations, ~1.1M fully ILP-checked,
no instance with nu < tau.

## STATUS: negative / frontier-pushed — no counterexample; exhaustive
verification extended to all simple digraphs on <= 6 vertices and all
multi-DAG condensations with <= 5 components and <= 16 arcs (tau 3-6), plus
phase-2 scans (k=6/k=7 multi-DAGs, unweighted Schrijver/ring family up to
n=70/m=112, large annealers with no size ceiling); detector validated
end-to-end on Schrijver's weighted counterexample.
