# P03 V1 — Direct counterexample search (Woodall's conjecture)

Session: https://app.devin.ai/sessions/d4cbcbc2be0d49e59cd58b01946b4d3d
Branch: runs/P03-v1

## Statement re-verification (done first)

Checked against Open Problem Garden ("Woodall's Conjecture", $5000 Cornuéjols prize),
Wikipedia, and Feofiloff's 2025 survey (ime.usp.br/~pf/dijoins): in every digraph, the
minimum size of a nonempty dicut equals the maximum number of pairwise disjoint dijoins.
Matches problems/P03-woodall-dijoins.md. Still open as of mid-2026: the June 2025
Combinatorica paper "Approximately Packing Dijoins via Nowhere-Zero Flows" (Abdi,
Cornuéjols, Liu, Ravi) proves only *approximate* packing (~ tau/6 dijoins) and states the
conjecture (even tau=3) is open. No claimed proof/counterexample found in a literature
sweep.

## Encoding / harness (runs/P03/v1/search.py)

- Digraphs as multiset of arcs on n labeled vertices (loops excluded; parallel arcs
  allowed in random modes — they simulate weights, cf. Schrijver's weighted CE).
- Dicuts: enumerate all 2^n-2 vertex subsets U with delta^-(U) = 0; dicut = delta^+(U).
  Keep inclusion-minimal dicuts only (others' constraints are implied). tau = min size.
  Skip graphs that are weakly disconnected or strongly connected (no dicut).
- KEY REDUCTION: dijoins are upward-closed (superset of a dijoin is a dijoin), so
  "tau pairwise disjoint dijoins exist" <=> "arc set partitions into tau dijoins".
- Packing test: SAT (CaDiCaL via pysat). Vars x[a,c] (arc a gets color c), exactly-one
  per arc; for every minimal dicut and every color c, clause OR_{a in cut} x[a,c].
  Symmetry breaking: the tau arcs of one fixed minimum dicut are pinned to distinct
  colors (valid: disjoint dijoins each use exactly one arc of a minimum dicut).
- UNSAT => counterexample. Sanity-checked on paths, parallel arcs, cycles.

## Searches run (checkpointed; all counts machine-generated, see *.log)

1. **Exhaustive, all labeled simple digraphs**, n = 3, 4, 5:
   - n=3: 36 instances with a dicut, all pack. n=4: 2228, all pack.
   - n=5: 462,000 instances with a dicut (tau up to 6), ALL pack. ~33 s.
2. **Exhaustive, all non-isomorphic digraphs on 6 vertices** (nauty-geng -c | directg,
   digraph6 stream, 1,530,843 digraphs, 6-way parallel): in progress / see below.
3. **Random multi-digraph sampling** (4 workers x 2 h): n in 4..9, m in 6..30 arcs
   i.i.d.; millions of instances, tau observed up to 17.
4. **Annealing on SAT hardness** (2 workers x 2 h): hill-climb at n=8, m<=~47 keeping
   tau>=3, score = CaDiCaL conflicts (hunt for hard/fragile packing instances).

## Phase 2: multi-DAG reduction (runs/P03/v1/dagsearch.py, multidag_exhaust.py, exhaust_d6.py)

REDUCTION: dicuts contain only arcs between strong components and correspond
exactly to dicuts of the condensation; arcs inside strong components lie in no
dicut. Hence D packs tau dijoins iff its condensation (a DAG with arc
multiplicities) does => WLOG search acyclic multi-digraphs.

5. **Exhaustive, all non-isomorphic oriented graphs on 7 vertices** (geng -c 7 |
   directg -o, 2,120,098 graphs; superset of all simple DAGs on <= 7 vertices):
   1,508,570 with a dicut, tau up to 12 — ALL pack. ~90 s x 4 cores.
6. **Exhaustive multi-DAGs n=4, <=16 arcs** (fixed topological order, all
   supports x all multiplicity compositions): 60,632 with tau>=2 — all pack.
7. **Exhaustive multi-DAGs n=5, <=14 arcs**: 1,241,145 with tau>=2 (tau up to
   11) — all pack. ~50 s x 4 cores.
8. **Exhaustive multi-DAGs n=6, <=13 arcs**: 14,732,328 with tau>=2 (tau up to
   9) — all pack. ~10 min x 6 cores.
9. **Random multi-DAGs** (2 workers x 3 h): n in 4..12, 6..30 arcs, multiplicity
   <= 4: ~1M instances, tau up to 24 — all pack.
10. **Tightness annealing on multi-DAGs** (score = #minimal dicuts that are
    tight at tau, n=8..10): converges to complete-bipartite-like DAGs with
    2^(n-2)+ tight cuts (e.g. tau=8, m=16, 256 minimal dicuts all tight) —
    still SAT with 0 conflicts. These max-tightness instances pack easily.
11. **Exhaustive multi-DAGs n=6, <=15 arcs**: 82,784,664 with tau>=2 (tau up to
    11) — all pack. ~60 min x 6 cores.
12. **Exhaustive multi-DAGs n=7, <=10 arcs**: 1,910,436 with tau>=2 — all pack.
13. **Exhaustive multi-DAGs n=7, <=12 arcs**: 52,138,929 with tau>=2
    (bytau: 2:47.5M, 3:4.33M, 4:261k, 5:25k, 6:1683, 7:52) — all pack.
    ~80 min x 6 cores.
14. **More random multi-DAGs** (2 workers x 70 min, n 6..10, m 8..30,
    multiplicity <= 8): 8.48M instances, tau up to 19 — all pack.

## Near-misses / observations

- Zero UNSAT instances so far; virtually all instances pack with 0 SAT conflicts —
  packing constraints are extremely slack at these sizes (consistent with the
  literature: unweighted CE, if any, is expected to need special structure).
- SAT-hardness annealing mostly inflates tau via parallel arcs; conflicts stay tiny.

## Coverage summary

Exhaustively verified Woodall's conjecture (tau disjoint dijoins exist) for:
- ALL digraphs on <= 6 vertices (via labeled n<=5 + non-isomorphic n=6);
- ALL oriented graphs on 7 vertices (hence all simple DAGs on <= 7 vertices);
- ALL multi-DAGs (== all digraphs up to condensation, integer weights as
  parallel arcs) with n=4 (<=16 arcs), n=5 (<=14 arcs), n=6 (<=15 arcs),
  n=7 (<=12 arcs);
plus ~15M random multi-digraphs/multi-DAGs up to n=14, 30 arcs, mult <= 8,
and tightness-annealed instances. Total >155M instances SAT-checked.
Zero UNSAT instances; SAT solver almost never even hits a conflict.

## Dead ends / lessons

- SAT-conflict annealing is a bad fragility signal here: conflicts stay ~0
  everywhere; parallel arcs inflate tau without creating tension.
- Tightness annealing (maximize tau-size minimal dicuts) converges to
  bipartite-crown-like DAGs (2^(n-2) tight cuts) that still pack trivially —
  such symmetric extremal instances are exactly the ones with clean colorings.
- If an unweighted counterexample exists, it needs > 15 arcs on >= 6
  condensation vertices (or >12 arcs on >=7), i.e. beyond the "tiny witness"
  regime of Schrijver's weighted CE; brute force must be replaced by the
  structural restrictions of Abdi–Cornuéjols–Zlatin (V3/V5 territory).

## STATUS

STATUS: negative — no counterexample; conjecture exhaustively verified for all
digraphs with condensation a multi-DAG within the size bounds above (all
digraphs on <=6 vertices; all simple <=7-vertex DAGs; multi-DAGs n<=7 up to
the stated arc budgets), plus >15M randomized larger instances. No
solutions/P03/verify.py since there is no claimed witness.
