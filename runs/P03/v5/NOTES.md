# P03 Woodall's conjecture — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/7aa363207b174207af62780e6f2cc8fb
Variant: V5 — digest known partial results, map the "safe" digraph classes where the
conjecture is proven, design the search to live entirely outside them, then compute.

## 1. Statement re-verification (against original-source formulations)

- Woodall 1978 (via Schrijver's discussion notes, homepages.cwi.nl/~lex/files/woodall.pdf;
  Feofiloff's 2025 survey ime.usp.br/~pf/dijoins; Wikipedia rev. 2026-04-29):
  *In every digraph, the maximum number of pairwise disjoint dijoins equals the minimum
  size of a dicut.* Matches problems/P03-woodall-dijoins.md exactly.
- Equivalent form used here (Schrijver): for k >= 2, A can be partitioned into k
  "strengthening" sets iff every dicut has size >= k. Note: k disjoint dijoins exist iff
  the arc set partitions into k dijoins (supersets of dijoins are dijoins), so the SAT
  check below tests an exact partition.
- Still open as of July 2026: Wikipedia (edited 2026-04) lists it as an unsolved problem;
  the newest literature (Combinatorica 2025 "Approximately Packing Dijoins via
  Nowhere-Zero Flows"; JGT 2026 chordal-digraph min-max paper) all state it open.
  Cornuéjols's $5000 prize (Open Problem Garden) still listed.

## 2. Literature digest → map of safe classes

A counterexample D (min dicut tau = k, no k disjoint dijoins) must avoid ALL of:

| # | Safe class / condition | Source |
|---|---|---|
| 1 | tau <= 2 | Frank's observation (Schrijver's book Thm 56.3): k=2 always packs |
| 2 | non-DAG reducible | contract strong components: WLOG D is a DAG |
| 3 | source-sink connected digraphs (every source reaches every sink by a dipath) | Schrijver 1982 (Min-max relations for directed graphs), Feofiloff–Younger 1987 |
| 4 | rho(k, D) <= 2, where rho = (1/k) * sum_v ((outdeg-indeg) mod k); and for k=3, even rho = 3 | Abdi–Cornuéjols–Zlatin, SIDMA 2023 (arXiv:2202.00392): rho in {0,1} equitable packing, rho=2 packing; rho=3 & tau=3 & w=1 partitions into 3 dijoins. So a tau=3 counterexample needs rho(3,D) >= 4 |
| 5 | planar digraphs (per problem file; via LY-dual feedback-arc-set formulation) | problem file P03; Feofiloff survey |
| 6 | underlying graph chordal | Cornuéjols–Liu–Ravi 2025 (arXiv:2501.10918, IPCO/JGT 2026): weighted chordal digraphs pack |
| 7 | tau >= 6 with NZ 6-flow guarantee: every digraph has floor(tau/6) disjoint dijoins; 6p-edge-connected underlying gives floor(tau*p/(2p+1)) | Combinatorica 2025 (Chen–?, nowhere-zero flows). For tau=3 gives nothing binding, but underlying graphs with NZ 3-flows admit 1 dijoin trivially — not restrictive |
| 8 | Minimal-counterexample structure ("reduced"): acyclic, weakly 3-arc-connected, every dicut of size k determined by a single source or single sink, all sources/sinks have degree exactly k, all internal vertices have degree 3 with (in,out) in {(1,2),(2,1)} | Schrijver's discussion notes, Thm 3 |

Additional notes:
- ACZ 2023 also prove: A always partitions into a dijoin and a (tau-1)-dijoin.
- Dyadic packing (SIDMA 2024): a max *fractional* packing with dyadic values always
  exists — LP side is well-behaved; obstruction, if any, is purely integral.
- Known weighted (Edmonds–Giles) counterexamples: Schrijver 1980 (7 nodes, 14 arcs,
  0/1 weights), Cornuéjols–Guenin 2002 family, Williams. All have tau(w)=2.
  Their unweighted versions pack (weight-0 arcs are the whole obstruction).
- rho >= 4 with the reduced degree shape: sources/sinks (deg 3, k=3) contribute 0 to rho
  (excess ±3 ≡ 0 mod 3). An internal (in=1,out=2) vertex has excess +1 → contributes 1;
  an (in=2,out=1) vertex has excess −1 ≡ 2 mod 3 → contributes 2. rho >= 4 requires the
  internal contributions to sum to >= 12, so at least 6 internal vertices are needed
  (all type (2,1)), and generically more. This lower-bounds counterexample size:
  n >= 2 sources/sinks + 6 internal = 8 vertices, >= 12 arcs.

## 3. Search design (outside ALL safe classes)

Target region for candidates (k=3):
DAG, tau=3, NOT source-sink connected, rho(3,D) >= 4, underlying non-planar,
underlying non-chordal, with the Schrijver reduced degree shape as generation prior
(sources outdeg=3, sinks indeg=3, internal deg-3 (1,2)/(2,1)).

Code: `harness.py` (dicut enumeration by bitmask over closed sets; tau; minimal
dicuts; SAT partition-into-3-dijoins via Glucose4 with exactly-one color per arc and
"every color hits every minimal dicut" clauses; rho/planarity/chordality/ss-connectivity
filters). `search.py` phase A = random shape-constrained screening (SAT-checks *every*
tau=3 sample, so we also cover safe-class instances as sanity), phase B = simulated
annealing on arc rewires toward region-score 0, SAT-checking every region hit.

Sanity tests: `test_harness.py` — ALL PASS (path, K3,3 orientation tau=3 packs 3 not 4,
disconnected => tau 0, smoke DAG).

## 3b. Size lower bound for a minimal tau=3 counterexample (derived here)

Combining the safe classes gives a sharper bound than any single source states:
- Reversal symmetry: reversing all arcs preserves tau and nu, and maps rho to
  rho-bar. So a counterexample needs BOTH rho(3,D) >= 4 and rho(3,rev D) >= 4.
- In the reduced shape (Schrijver): internal type (in1,out2) contributes 1 to rho and
  2 to rho-bar; type (in2,out1) contributes 2 and 1. With a type-A and b type-B
  internals: a + 2b >= 12 and 2a + b >= 12 => a + b >= 8: at least 8 internal vertices.
- Stub balance forces a - b = 3(#sinks - #sources).
- A DAG with a single source is automatically source-sink connected (every vertex is
  reachable from the unique source), and dually for a single sink. So >= 2 sources and
  >= 2 sinks are needed to escape the Schrijver/Feofiloff-Younger safe class.
- Minimum: 2 sources + 2 sinks + 8 internals (a = b = 4), n = 12, 18 arcs.
  (Next shapes: (2,2,10) n=14 / 21 arcs; (3,2,9)+(2,3,9) n=14; etc.)
This focuses the targeted deep runs (`runA_min.log`, `runB_min.log`).

## 4. Run log

- 2026-07-22 ~20:40 UTC calibration: phase A, 60 s, seed 1, sizes up to n=16:
  17135 generated / tau distribution 0:84, 1:1256, 2:8745, 3:7050 / 7050 SAT-checked /
  290 in full target region / **0 non-packing**.

(further checkpoints appended below)
