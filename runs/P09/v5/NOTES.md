# P09 Bollobás–Nikiforov — V5 (literature-first) run notes

Session: devin-f14d36ed797d4ce1bd993e57698d51b9, 2026-07-22.

## 0. Statement re-verification

Original source: Bollobás & Nikiforov, *Cliques and the spectral radius*, JCTB 97 (2007)
859–865, Conjecture 1: for G ≠ K_n with m edges and clique number ω = ω(G),
λ₁² + λ₂² ≤ 2m(1 − 1/ω). Matches the problem file (checked against restatements in
arXiv:2407.19341, arXiv:2501.07137, arXiv:2101.05229, arXiv:2603.26379, all quoting the
same inequality). **Still open in general as of July 2026** — the March 2026 paper
(arXiv:2603.26379) treats only complete multipartite + dense K₄-free cases and calls the
general conjecture open.

## 1. Literature digest → exact open region

Proved cases (as of 2026-07):
- **ω = 2 (triangle-free)**: Lin–Ning–Wu, Comb. Probab. Comput. 2021 (arXiv:1910.12474).
- **Regular graphs, all ω**: Zhang (arXiv:2309.08184). Equality iff balanced Turán graph
  or disjoint union of two equal-size balanced Turán graphs.
- **Few triangles**: Kumar–Pragada (arXiv:2407.19341): t(G) = O(m^{1.5−ε}) triangles ⇒
  conjecture (even the Elphick–Linz–Wocjan generalization) holds. Covers planar,
  book-free, cycle-free graphs.
- **Complete multipartite graphs** (all): arXiv:2603.26379 (λ₂ ≤ 0 there, Nikiforov's
  spectral Turán theorem suffices).
- **Dense K₄-free**: m = Ω(n²), n large (arXiv:2603.26379 stability argument).
- **Random graphs**: a.a.s. (Liu–Bu, arXiv:2501.07137).
- Weakly perfect / Kneser classes for the related s⁺ conjecture (arXiv:2101.05229).

**Open region** (where any counterexample must live):
- irregular, connected (see §2: disjoint unions reduce to Nikiforov's *theorem*),
- Θ(m^{3/2}) triangles (many triangles),
- not complete multipartite,
- ω ≥ 3; for ω = 3 only the non-dense (m = o(n²)) K₄-free regime remains open,
- λ₂ > 0 required in any violation, so it also refutes ELW's s⁺ ≤ 2m(1−1/ω); i.e. the
  search doubles as a s⁺-conjecture search.

## 2. Analytic observations (drive the search design)

- **Disjoint unions can't violate**: for G = H₁ ∪ H₂ with the two top eigenvalues coming
  from the components, score(G) = score_Nikiforov(H₁) + score_Nikiforov(H₂) where
  score_Nikiforov(H) = λ₁(H)² − 2m_H(1−1/ω) ≤ 0 is Nikiforov's proved theorem
  (when ω(H_i) = ω(G); if a component has smaller ω its slack is strictly bigger).
  ⇒ counterexamples must be **connected** with genuinely interacting λ₁, λ₂.
- **Equality set is large**: any union of balanced Turán graphs with the same r,
  T(ar,r) ∪ T(br,r), gives equality (λ₂ = λ₁ of the smaller part, both parts tight for
  Nikiforov). Includes irregular graphs like T(3r,r) ∪ K_r. Verified numerically
  (tightness.py). Perturbation attacks should be centered on this whole family.
- Since the equality graphs are disconnected or complete multipartite (both proved
  regimes), a violation is a *strict crossing* away from a proved boundary — local
  perturbation must overcome a strictly negative first-order margin per edge flip
  (RHS moves by 2(1−1/ω) ≥ 4/3 per added edge; λ contributions are second-order for
  cross edges w.r.t. localized eigenvectors). This is why the conjecture is hard to
  break locally; global/structured families needed.

## 3. Compute log

All scores are score(G) = λ₁² + λ₂² − 2m(1 − 1/ω) with exact ω (Tomita-style
branch-and-bound max-clique, `core.py`) and dense `eigvalsh`. Conjecture ⇔ score ≤ 0.

### Round 1 (checkpoint 20:25 UTC)

- `tightness.py`: equality confirmed to 1e-13 on T(kr,r), unions of equal AND unequal
  balanced Turán graphs (same r), 2K_w. Near-tight but negative: bridged unions
  (≈ −1.0 to −1.45), books, joins K_a ∨ I_t (all ≤ −0.5).
- `perturb.py`: exhaustive 1-flip + 4000 sampled 2-flips around T(kr,r) (r=3..5, k=2..4),
  2×T(kr,r) (r=3,4), 2K_w (w=4..6): **max neighborhood score < 0 everywhere**
  (best ≈ −0.4 to −0.6; typical −0.1 near T(9,3)).
- `perturb3.py`: 3000 sampled 3-flips + 3000 4-flips + greedy 8-step plateau walks around
  ALL unions T(ar,r) ∪ T(br,r), r=3..6, a,b≤3: max < 0; plateau walks return to score ≈ 0
  only at equality graphs themselves.
- `families.py` (parametric, exact): overlapping Turán blobs (best −0.105 at r=3,q=2),
  Turán+pendant-clique (−0.209), K_a ∨ (T∪T) joins (−0.438), bridged unions b=1..8
  (−0.785), C5 blowups (−2.47). All negative.
- `omega3.py wheel`: wheel blowups I_a ∨ C5[x,y,z,y,x], all a≤12, x,y,z≤10, n≤45:
  best −0.985 (a=2, all b=1). K4-free anneal (moves creating K4 rejected), n=30/45,
  32 restarts × 40k steps: best −0.43.
- `anneal.py` round 1: n ∈ {20,24,25,28,30,33,35,36,40,45,48}, inits random/turan-union/
  cliques, ~200 restarts × 20–60k flip steps, exact ω every step: global best over
  non-equality graphs ≈ −0.4 (n=20); turan-union inits sit on the score-0 equality
  plateau and never cross it. A random-init run at n=20 also annealed INTO the equality
  plateau (best exactly 0) without ever exceeding it.

### Round 2 — fixed-ω anneal in the designed open region (`anneal2.py`)

Literature-designed search: fix ω ∈ {3,4,5} (flips changing ω rejected), seeds =
connected roughened Turán-unions (irregular, triangle-rich). n ∈ {24,26,30,32,34,36,38,
40,42,50}, 30–50k steps, ~60 restarts. **All negative**; best −0.32 (n=26, ω=4).

### Round 3 — ELW generalization (`elw.py`)

Also attacked the Elphick–Linz–Wocjan generalization (arXiv:2101.05229 Conj. 2):
Σ_{i≤ω, λᵢ>0} λᵢ² ≤ 2m(1−1/ω). Found its equality plateau is much larger: ANY union of
≤ ω balanced Turán graphs T(kᵢr, r) is exactly tight (verified to 1e-12 for r=3..6, up
to 6 components — includes t·K_w unions). Annealing from these seeds, n ∈ {20,28,36,44},
~45 restarts × 40k steps: reaches 0 on the plateau, never exceeds it. Negative.

### Round 4 — final escalation

anneal2 ω=4 up to n=60 and ω=3/6 variants, 80k steps (~70 restarts), plus ELW anneal
n=52,60: all negative. Best per-run scores collected in `RESULTS-summary.txt`.

### Round 5 — new encodings (after restart, pushing the frontier)

- **Exhaustive geng sweep** (`exhaustive.py`): all connected graphs (disconnected
  reduce to Nikiforov, §2), graph6 parsed in batches, batched `eigvalsh`; exact
  max-clique only where violation is arithmetically possible (violation ⇔
  ω < 2m/(2m−L), L = λ₁²+λ₂², since Σλᵢ² = 2m).
  - n ≤ 9: 0 violations (273k connected graphs), worst score exactly 0 (Turán).
  - **n = 10: all 11,716,571 connected graphs — 0 violations**, worst score 0.
    (Published exhaustive frontier for this conjecture appears to be incidental
    small checks only; this is a full n ≤ 10 certificate.)
  - **n = 11: all 1,006,700,565 connected graphs — 0 violations**, worst score
    exactly 0 (Turán equality graphs). ~4 h wall on 7 cores.
  - Pipeline independently cross-checked (`crosscheck.py`): graph6 parser vs
    networkx on 1200 random geng samples (n = 8..11) and candidate-filter logic vs
    direct score computation — PASS.
  - Together with the disjoint-union reduction (§2), this certifies BN for **all**
    graphs on ≤ 11 vertices (connected or not) — well past any published check.
- **Blowup continuous relaxation** (`blowup.py`): for every pattern H, BN on ALL
  independent-set blowups H[x·N] (N→∞) reduces to max over the simplex of
  f_H(x) = μ₁² + μ₂² − (1−1/ω(H))·xᵀAx, μᵢ from D^{1/2}A_H D^{1/2}, D=diag(x).
  Projected-gradient ascent (12 restarts × 400 iters) over ALL connected patterns
  with ω ≥ 3: |H| ≤ 8 complete (12,913 patterns, 12 restarts × 400 iters), and
  |H| = 9 complete (all 261,080 connected patterns, 259,699 optimized; lighter
  budget 4 restarts × 250 iters). max f = 0 exactly, attained at Turán-type
  patterns/weights; no positive value ⇒ **no counterexample exists among
  independent-set blowups of any pattern with ≤ 9 vertices, at ANY blowup size**
  (≤ 8 with the heavier optimization budget; ≤ 9 with the lighter one).

### Round 6 — new methods (coordinator push #2)

- **Frank–Wolfe / ILP duality attack** (`fw_ilp.py`, CBC via python-mip): iterate
  {compute top-2 eigenpairs → linearize dF/dA_ij = 4λ₁x_ix_j + 4λ₂y_iy_j − 2(1−1/ω)
  → re-choose the ENTIRE edge set by ILP subject to K_{ω+1}-freeness via lazy clique
  cuts}. Global jumps, completely different dynamics from flip search. Result: from
  every start (n ∈ {18,24,30}, ω ∈ {3,4,5}; 6 runs), the linearized global optimum converges
  to the Turán equality plateau with score EXACTLY 0 and never exceeds it — a strong
  dual/variational confirmation that the extremal family is the global maximizer of
  the first-order model.
- **Cones/joins over named spectral-extremal families** (`cones.py`): K_s ∨ H and
  K_s ∨ (H ∪ H) for H ∈ {Paley(q≤41), Kneser(v,k), triangular J(v,2) v≤9, co-C_n,
  hypercube-like}; 120 graphs, all irregular and triangle-rich (open region).
  All negative; best −0.618 (small co-cycle cone). No near-misses.

### Round 7 — relaxation-guided hybrid attack (coordinator push #3)

- `hybrid.py`: used the blowup relaxation as a LOCATOR: ranked every connected
  non-complete-multipartite pattern (|H| ≤ 8, ω ≥ 3) by tightness of max f_H, then
  attacked integer roundings of the tightest patterns' optimal weights at N ∈
  {24,36,48} with exhaustive 1-flips + 3000 sampled 2/3-flips each (regime where the
  continuous certificate does not apply). ~500 rounded blowups attacked. Finding:
  every seemingly-tight non-multipartite pattern optimum collapses onto a Turán
  sub-blowup (optimal weights vanish outside a max clique — e.g. pattern FU~~w =
  K₇ minus P₄ optimizes to weights 1/5 on an internal K₅); all flip attacks negative,
  best exactly 0 on the plateau. No new equality graphs, no violations.
- `gap_analysis.py`: maximized f_H restricted to interior/non-collapsing weights
  (support inducing a non-CM subgraph), all patterns |H| ≤ 7: sup approaches 0
  (largest −9.4×10⁻⁸, pattern FQhV_) but every near-zero case again degenerates to
  the known plateau — e.g. FQhV_'s optimum has support inducing 2K₃ with uniform
  weights = union of two balanced Turán blowups (known disconnected equality
  family), which the CM filter alone doesn't catch. Refined finding: **every tight
  or near-tight blowup direction found is a union of balanced Turán structures**;
  genuinely non-Turán interior directions stay strictly below 0.

### Round 8 — exhaustive n = 12 certificate (coordinator push #4: "keep trying")

- `sweep12.c` + `run12.sh`: optimized C engine (graph6 parse → Householder
  tridiagonalization + QL eigensolve → greedy-clique lower-bound skip → exact
  bitmask branch-and-bound clique for arithmetically-possible violators; any graph
  scoring > −1e–7 logged). Validation: identical candidate sets to the earlier
  Python pipeline on n = 9; n = 10 total = 11,716,571 (exact OEIS match).
- Swept **ALL 164,059,830,476 connected graphs on 12 vertices** (exact match with
  A001349(12)) in 96 geng res/mod parts, 8 workers, ~42 h wall at ~1.1M graphs/s.
- Result: **zero violations**. Exactly 86 graphs came within 1e–7 of the bound;
  `recheck12.py` re-verified all 86 independently with mpmath at 50-digit precision
  and exact clique: every one is an equality graph (|score| < 5e–48) — 82 with
  ω = 2 (unions of ≤ 2 complete bipartite graphs, where λ₁²+λ₂² = m always),
  and 4 with ω ∈ {3,4,6} (unions of same-r balanced Turán graphs: includes
  T(12,3)-, T(12,4)-, T(12,6)-type). PASS printed. Per-part summaries and all
  candidates in `logs12/`.

## 4. Near-misses & dead ends

- Best genuinely non-tight score found anywhere: ≈ **−0.105** (T(9,3)-blobs overlapping
  in a 2-set, family A), then −0.2..−0.6 band for pendant-clique / 1-flip perturbations.
- The equality plateau (unions of same-r balanced Turán graphs; for ELW, unions of up to
  ω of them) acts as a strong attractor for annealing; every crossing attempt loses at
  least ~0.1 immediately. Consistent with the §2 first-order-margin argument.
- Dead end: disjoint-union constructions — provably cannot violate (reduces to
  Nikiforov's theorem, §2).
- Total compute: ~7 h wall on 8 cores — ~400 annealing restarts (~2×10⁷ scored flips)
  with exact ω at every evaluation; structured scans of 6 parametric families;
  1.02×10⁹-graph exhaustive sweep; ~155k simplex optimizations for blowup patterns.

### Round 9 — dense-corner complements, near-equality neighborhoods, rank-2 plateau (coordinator push #5)

Literature re-check (2026-07-25, arXiv API): still no published counterexample; newest
relevant items are arXiv:2607.16746 (Nosal supersaturation), arXiv:2603.26379 (complete
multipartite + dense K₄-free), arXiv:2411.08184 (conic programming: BN with weaker
constants; proves the WEA vector-chromatic conjecture). BN Conjecture 1 remains open.

**New structural discovery (explains all 82 ω=2 near-bound graphs at n=12):** the ω = 2
equality plateau is much larger than unions of complete bipartite graphs. Any bipartite
graph whose biadjacency matrix has rank ≤ 2 satisfies λ₁²+λ₂² = m EXACTLY: rank-2
biadjacency ⇒ only two nonzero singular values σ₁ ≥ σ₂, spectrum {±σ₁, ±σ₂, 0…}, and
Σλᵢ² = 2m gives σ₁²+σ₂² = m. Concrete family: "double complete bipartite" B(a₁,a₂;b₁,b₂)
(a₁ left vertices joined to all b₁+b₂ right vertices, a₂ left vertices joined to the b₁
core only) — includes K_{a,b} minus any star. Verified to 60-digit precision on
K_{7,6}−star (score < 1e-59). Since Lin–Ning–Wu proved ω=2, these are equality points of
a THEOREM, but they form a new perturbation launchpad (below). The analogous tripartite
construction K_{a,b,c} − star is strictly negative for every (a,b,c,k≥1) with a,b,c ≤ 6
— the trick does not extend to ω ≥ 3, consistent with the ω≥3 equality set being exactly
balanced-Turán unions.

Searches this round (all machine-scored, exact ω):
- `cmflip.py` n = 13,14,15,16: exhaustive 1- and 2-edge-edit neighborhoods of EVERY
  complete multipartite graph and every union of two complete multipartite graphs
  (5,615 centers, 32.4M scored graphs). Best = 0 exactly (edits landing back on the
  plateau); nothing positive.
- `rank2flip.py` n = 13,14,15,16: exhaustive 1-/2-edit neighborhoods of every
  B(a₁,a₂;b₁,b₂) rank-2 equality graph (1,661 centers, 8.98M scored graphs). Best
  ≈ +1.8e-13 = eigensolver noise on the plateau itself; no violation.
- Joins K_t ∨ B(rank-2 graph) for t ≤ 3, a,b ≤ 9: all ≤ −0.19 — the plateau collapses
  under joins.
- `sweepC.c` (sweep12 generalized to n ≤ 31 + complement mode): exhaustive DENSE-corner
  certificate — scored the complement of every graph with ≤ 20 edges on n vertices,
  i.e. **every graph on n vertices missing ≤ 20 edges**, for n = 13, 14, 15, 16:
  n=13: 650,474,122 · n=14: 1,598,398,717 · n=15: 2,934,049,691 · n=16: 4,315,234,797
  — 9,498,157,327 dense graphs in total. Zero violations; only 8 graphs within 1e-7 of
  the bound, and all 8 recheck to exact equality at 50-digit precision (`recheckC.py`,
  PASS): they are the Turán-type equality graphs reachable in this window (e.g.
  T(16,8) = O????A?O@?A?A?@??O?A?-complement, K₁₃ minus a perfect matching-like
  K_{1^11,2} cases, etc.). This is the first exhaustive certificate covering n = 13–16
  in the dense regime where the known equality family lives — any counterexample on
  13–16 vertices must be missing MORE than 20 edges.

### Round 10 — ELW exhaustive certificate + dense-corner extension to n = 20 (coordinator push #6)

- **ELW strengthening exhaustively verified for all connected graphs on ≤ 11 vertices**
  (`sweepE.c`: same engine with L = sum of squares of the min(ω, #positive) largest
  eigenvalues; s⁺-based sound rejection filter). n=9: 261,080 · n=10: 11,716,571 ·
  n=11: 1,006,700,565 (matches A001349 exactly). Zero violations; 114 near-bound
  graphs, all exact equalities at 50-digit precision (`recheckE.py`, PASS). The
  stronger conjecture (Liu–Ning problem list #4) survives its first exhaustive sweep.
  Engine cross-checked against elw.py on all 853 connected n=7 graphs (candidate sets
  agree on all graphs with L > RHS-tolerance; the C filter provably cannot miss a
  strict violation since LHS ≤ s⁺ and RHS is increasing in ω).
- **Dense-corner certificate extended to n = 17, 18, 19, 20** (complements of all
  graphs with ≤ 20 edges): n=17: 5,411,909,085 · n=18: 6,107,389,583 ·
  n=19: 6,472,650,039 · n=20: 6,637,246,978 — 24.6e9 more graphs, 34.1e9 total for
  n = 13–20. Zero violations; all 15 near-bound graphs (n=13–20) recheck to exact
  equality at 50 digits (recheckC.py with eigsy, PASS): they are exactly the
  Turán-type equality graphs in the window (T(2k,k) for n=14,16,18,20; K_n minus a
  maximal matching-complement cases with ω=n−1, etc.). **Any counterexample on
  n ≤ 20 vertices must be missing more than 20 edges** (and have n ≥ 13).

### Round 11 — PARTIAL (paused by coordinator)

- `cmflip3.py` n = 13: exhaustive 3-edge-edit neighborhoods of every complete
  multipartite graph and CM-union (619 centers, 47.1M scored graphs, exact ω):
  best +1.2e-13 = plateau noise, no violation. n = 14 was launched but killed at pause.
- n = 13 sparse slice (`sweep12`, connected, m ≤ 26, 8 geng parts): ran ~2 h,
  ~10e9 graphs scanned with zero candidates before coordinator pause; INCOMPLETE —
  no per-part summaries, not a certificate. Restartable via
  `nauty-geng -cq 13 0:26 r/8 | ./sweep12 13`.

Paused on coordinator instruction 2026-07-26; no new work until resume.

## 5. Conclusion

No violation of Bollobás–Nikiforov (nor of the ELW generalization) found. New verified
frontier: BN holds for **every graph on ≤ 12 vertices** (exhaustive, cross-checked;
164,059,830,476 connected graphs at n = 12 alone, plus the disjoint-case reduction) and
for **every independent-set blowup of every pattern on ≤ 9 vertices at every size**
(continuous-relaxation certificate, max f_H = 0 attained only at Turán-type optima).
Heuristic search (exact ω) to n = 90 in the literature-mapped open region found nothing
above −0.1 outside the equality plateau. Any counterexample must have n ≥ 13, is not a
blowup of a small pattern, and is not a local perturbation of the extremal family.

Late additions: fixed-ω anneals at n = 70–90 (19 restarts × 60k steps, ω ∈ {3..6}):
all negative (best −3.78 at n=70 ω=6).

Round 9 additions: any counterexample must (a) have n ≥ 13, (b) if n ≤ 16, be missing
more than 20 edges (dense-corner complement certificate, 9.5e9 graphs), (c) not be
within 2 edge-edits of any complete multipartite graph, union of two complete
multipartite graphs, or rank-2 bipartite equality graph on n ≤ 16 (41M scored
neighborhoods). The ω = 2 near-bound zoo is now fully explained by the rank-2
biadjacency plateau (λ₁²+λ₂² = m for every bipartite graph of biadjacency rank ≤ 2).

STATUS: frontier-pushed (no counterexample; exhaustive certificate n ≤ 12 = 1.64e11
connected graphs at n = 12 + 1.02e9 at n = 11 with all 86 near-bound graphs re-verified
as known equality graphs at 50-digit precision; dense-corner certificate: all graphs on
13–20 vertices missing ≤ 20 edges (34.1e9 graphs, 15 near-bound = exact Turán equalities,
50-digit PASS); ELW strengthening exhaustively verified for all connected graphs n ≤ 11
(1.02e9, 114 near-bounds = equalities, PASS); blowup-family certificate for all
patterns ≤ 9 vertices at all sizes; exhaustive 1-2-edit neighborhoods of every CM /
CM-union / rank-2-bipartite equality graph n ≤ 16; ~2×10⁷ scored heuristic evaluations
to n = 90 — all negative)
