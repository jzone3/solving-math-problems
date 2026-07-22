# P05 — Gallai three longest paths — V5 (literature-first) run notes

Session: devin-8c6b97581e2b430bb0896f4acd910f0c, 2026-07-22. Branch `runs/P05-v5`.

## 1. Statement re-verification (against original source)

- Open Problem Garden page (fetched live 2026-07-22) confirms: Gallai, Problem 6, *Theory of
  Graphs* (Proc. Colloq. Tihany 1966), Academic Press 1968, p. 362. Question: do any three
  longest paths in a connected graph share a common vertex? Two always do (folklore);
  Skupień 1996 (CPC 5:429–436) gives 7 longest paths with empty intersection.
- Still-open check (July 2026): arXiv 2006.16245 (Sarkar) claims a proof, but v3's own
  arXiv comment field says "The paper is erroneous, and poorly written" — retracted in place.
  No other proof or counterexample found in arXiv sweep (searches: "three longest paths",
  "longest paths"+"common vertex", "Gallai"+"longest", sorted by date through 2026-05).
  Newest related work: Norin–Steiner–Thomassé–Wollan 2025 (arXiv:2505.08634, lpt(G) ≤ √(8n));
  Gallai Vertex Problem complexity paper (2026, arXiv:2605.13488) — neither settles P05.
  **Conclusion: problem is still open. Proceed.**

## 2. Literature digest — where the known proofs break

Known Gallai-3-true classes and their proof mechanisms:
- **Outerplanar / series-parallel** (Ehrenmüller–Fernandes–Heise, arXiv:1310.1376): tree-like
  (treewidth-2) decompositions give a "central" block/vertex argument; every longest path must
  cross a central separator of size ≤ 2. Breaks as soon as a 3-connected (K4-minor) piece exists.
- **Graphs whose nontrivial blocks are Hamiltonian** (de Rezende–Fernandes–Martin–Wakabayashi
  2011/2013 line): longest paths inside a Hamiltonian block can be rerouted around the cycle;
  the block-tree has a central block containing all longest paths pairwise, and Hamiltonicity
  forces a common vertex. Breaks for non-Hamiltonian 3-connected blocks where rerouting fails.
- **2K2-free / split / (P5,·)-free etc.** (Golan–Shan 1611.05967; Gao–Shan 1907.13074;
  Lima–Nikabadi 2409.07366): density/forbidden-subgraph forces near-Hamiltonicity
  (max-degree vertex on all longest paths). Breaks for sparse graphs with long induced paths.
- **Fujita–Furuya–Naserasr–Ozeki** (1503.01219): distance-among-longest-paths approach; partial.
- **Gutiérrez–Valqui** (2101.07859): if three longest paths have empty intersection then every
  two of them meet in ≥ 6 vertices. So any counterexample has heavily interleaved path pairs.
- **Brown PhD thesis 2025** (Canterbury, doi:10.26021/15960): exhaustive plantri search —
  any *polyhedral* (3-connected planar) counterexample needs ≥ 18 vertices.

Residual class where all proofs break: sparse graphs with ≥ 3 cut vertices hanging long arms
off a non-Hamiltonian core containing a K4 minor; paths must pairwise overlap a lot (≥6).

## 3. The spider reduction (V5's targeted family)

All known empty-intersection constructions (Walther, Zamfirescu, Skupień) are "arms attached
to a core". For exactly 3 paths the minimal such shape is a 3-arm spider. Reduction:

**Lemma (arm-tuning).** Let H be connected, a,b,c distinct vertices. Let M_xy = max length of
an x–y path in H. Suppose there exist maximum a–b, b–c, a–c paths P1, P2, P3 (maximum per
endpoint pair) with V(P1) ∩ V(P2) ∩ V(P3) = ∅ (this forces c∉P1, a∉P2, b∉P3). Attach pendant
paths (arms) of lengths L_a, L_b, L_c at a, b, c, solving
L_a − L_c = M_bc − M_ab and L_b − L_c = M_ac − M_ab with all L's ≥ |V(H)| (always solvable by
shifting all L's up uniformly: pair-sums grow by 2t, one-arm paths by t). Then in the spider
G: (i) every longest path runs tip-to-tip between two distinct arms (one-arm/zero-arm paths are
shorter by the L ≥ |V(H)| margin; arms are pendant so cannot be partially reused); (ii) the
three tip-to-tip paths arm_a+P1+arm_b, arm_b+P2+arm_c, arm_a+P3+arm_c all have equal length
L_x+L_y+M_xy = the longest-path length; (iii) their common intersection is
V(P1)∩V(P2)∩V(P3) = ∅ (arm_x lies in only the two paths ending there).
So **any core hit ⇒ explicit counterexample to Gallai-3**, of size |V(H)| + L_a+L_b+L_c.

Conversely this searches, for each core size n_H, a family of graphs of unbounded total size —
far beyond the n ≤ 12 direct exhaustive frontier.

Sanity check built in: series-parallel cores can never hit (spider of an SP graph is SP and
SP graphs are Gallai-3-true), so any hit must contain a K4 minor.

## 4. Computation log

Tooling: `spider_ref.py` (trusted slow reference), `spider_search.c` (fast bitmask DFS,
per-pair maximum-path lists, triple check with endpoint-avoidance filters; `-m` reports the
best near-miss = min over valid triples of |P1∩P2∩P3|). Cross-checked on n=7,8 (identical
0-hit counts, same graph counts as geng).

End-to-end validation of the reduction machinery: for the n=8 near-miss core `G???F{`
(triple 0,1,2, predicted min triple intersection 1), `direct_check.py` built the actual
32-vertex spider and brute-force enumerated all longest paths: longest length 18 as
predicted, exactly 3 longest-path vertex sets, min triple intersection 1. Reduction and
direct computation agree exactly.

### Stage 1: 3-arm spider cores (exhaustive)

| Core class | count | hits | best near-miss |
|---|---|---|---|
| all connected n ≤ 8 (geng -c) | 11,996 | 0 | 1 (n=8, G???F{) |
| all connected n = 9 | 261,080 | 0 | 1 (H????B~) |
| all connected n = 10 | 11,716,571 | 0 | 1 |
| all connected n = 11, ≤ 20 edges | 28,908,939 | 0 | 1 |
| all connected n = 12, ≤ 18 edges | 22,028,571 | 0 | 1 |
| all connected n = 13, ≤ 16 edges | 2,778,205 | 0 | 1 |
| all connected n = 14, ≤ 16 edges | 2,142,867 | 0 | 1 |
| subcubic (Δ≤3) n = 12, 13, 14 | 19,430 + 69,322 + 262,044 | 0 | 1 |
| subcubic n = 15, 16 | 1,016,740 + 4,101,318 | 0 | 1 |
| subcubic n = 17 | 16,996,157 | 0 | 1 |
| random sparse n = 15–22, m = n..n+5 (genrang) | tens of millions (ongoing) | 0 | 1 |
| cubic n = 18 | 41,301 | 0 | 1 |
| cubic n = 20 | 510,489 | 0 | 1 |

Every one of ~72M cores has, for every triple (a,b,c) and every choice of per-pair maximum
paths avoiding the third vertex, a common vertex — and the minimum triple intersection is
exactly 1 in the extremal cases, at every size. This is strong evidence for a clean lemma:
"any per-pair-maximum a–b, b–c, a–c paths have a common vertex", which (if true) would kill
the entire pendant-3-arm spider family as a source of Gallai-3 counterexamples.

### Stage 2: generalized arm structures (3 tip-pairs over up to 6 attachment vertices)

`multi_search.c` drops the assumption that the three longest paths pairwise share arm
endpoints: choose any 3 endpoint-pairs among ≤ 6 attachment vertices (no vertex in all
three pairs), require per-pair maximum core paths with empty triple intersection
(CAND lines), then `lp_filter.py` checks integer feasibility of arm lengths with z3
(equal sums for chosen pairs, ≤ for all other tip pairs; one-arm paths dominated by a
uniform shift) and, for any feasible candidate, builds the explicit multi-arm graph and
brute-force verifies.

| Core class | candidate structures | z3-feasible | counterexamples |
|---|---|---|---|
| all connected n = 7 | 31,039 | 0 | 0 |
| all connected n = 8 | 521,717 | 0 | 0 |
| all connected n = 9 | (running) | | |

Stage-2 finding so far: over half a million candidate structures where the three core paths
DO have empty intersection, yet the arm-length system is infeasible **every single time** —
whenever three per-pair-maximum paths avoid a common vertex, some other tip-pair distance is
forced long enough to beat the required common length S. This smells like a min-max/duality
theorem about the "max path-length metric" M on the attachment set.

### Two distinct obstructions (analysis)

The data cleanly separates into two phenomena:

1. **k = 3 attachment vertices (triangle pair structure, stage 1).** An empty triple of
   per-pair maximum paths *never exists at all*: min over mask choices of |P1∩P2∩P3| = 1 in
   every extremal core found (~90M cores). For k=3 the arm-length system is always solvable,
   so this is the only obstruction — and it looks like an unproved but clean lemma:
   *for any distinct a,b,c and any maximum a–b, b–c, a–c paths, the three share a vertex.*
   (This lemma is implied by Gallai-3 via the spider construction, so proving it is strictly
   easier than the conjecture; disproving it disproves Gallai-3.)

2. **k = 4,5,6 attachment vertices (stage 2).** Empty path triples abound (>0.5M structures
   at n=8 alone), but the arm-length feasibility system was infeasible in all cases. z3
   unsat-core analysis of 2058 sampled n=8 candidates (k=4: 400, k=5: 1231, k=6: 427):
   the blocker is 1 inequality in 392 cases, 2 in 1537, 3 in 120, 4 in 9 — i.e. one or two
   non-chosen tip pairs (u,v) always have max-path length M_uv so large that their tip-to-tip
   path would beat the required common longest length S. A min-max statement about the
   "longest-path premetric" M on the attachment set seems to be lurking here.

Independent cross-validation: 327 randomly sampled CAND lines from the n=8 run were
re-verified with the separate Python implementation (`spider_ref.py` machinery): all
maximum lengths, path masks, endpoint memberships, and empty intersections confirmed.

### Stage 3: targeted cores (literature-guided seeds)

- Thomassen's 34-vertex hypotraceable graph (HoG 1353; hypotraceability re-verified by
  machine: no Ham path, all 34 vertex-deletions traceable): best near-miss 25 — as the
  literature digest predicted, hypotraceable graphs per se are terrible 3-spider cores
  because per-pair max paths are near-Hamiltonian and miss only ~a few vertices.
- HoG hypohamiltonian graphs (n ≤ 30: Petersen, 16, 20, 22, 22, 26, 26, 28, 28, 30) and
  Thomassen T34, plus all connected single-vertex-deleted subgraphs of each: 367 cores
  (running).

(updated as runs complete)
