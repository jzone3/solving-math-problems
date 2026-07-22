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
- Targeted reconstruction: fixed the known weight-1 skeleton (three disjoint
  alternating length-3 paths on 12 vertices), hill-climbed over weight-0 arc
  sets. See `redisc.log` / result below.

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

## 5. Results log

(checkpointed as runs proceed; see `results.jsonl`)

- [t0] 3 search seeds (11/22/33) launched, 4h each, + Schrijver-rediscovery run.

## STATUS: (pending — run in progress)
