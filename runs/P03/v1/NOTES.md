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

## Phase 3: seeding from known weighted counterexamples (schrijver_seed.py, d27search.py, fastcuts.py)

Requested escalation: attack the >15-arc / >=6-vertex regime via known hard families.

- **Extracted Schrijver's 1980 counterexample exactly** (12 vertices, 21 arcs,
  9 weight-1 "solid" + 12 weight-0 "dashed") from the vector graphics of
  arXiv:2202.00392 Fig 1 (D1.pdf). Machine-verified: min solid-weight over all
  49 minimal dicuts = 2, and SAT says NO 2 disjoint weighted dijoins (UNSAT) —
  exact match with Schrijver's claims. Seed is faithful.
- **Unweighted expansions of Schrijver's example**: grid over solid-multiplicity
  ms in 1..3, dashed-multiplicity md in 1..8, plus Harvey's tau>=2 extension
  (middle solid arcs -> tau-1 copies) for tau in {3,4,5}: ALL pack (96 configs).
  Subdivision variants (dashed arcs -> paths of length 2..4, each step
  multiplicity 1..3, solid arcs optionally subdivided/doubled): ALL pack.
  The weighted obstruction washes out under every parallel/subdivision
  simulation of weight zero tried — a structural explanation attempt:
  parallel copies inflate the dicuts through dashed arcs, giving the packing
  enough slack exactly where weight-0 arcs used to make it tight.
- **Extracted ACZ's D27** (Abdi-Cornuejols-Zlatin arXiv:2202.00392, Fig D27):
  sink-regular (3,4)-bipartite digraph, 27 vertices, 45 arcs (30 solid + 15
  dashed = minimal dijoin J*). Machine-verified all paper claims: bipartite,
  all 15 sinks in-degree 3, tau=3 (311 minimal dicuts), J* is a dijoin, A-J*
  is a 2-dijoin, and A-J* does NOT partition into 2 dijoins (SAT UNSAT) —
  the strongest known unweighted near-miss. D27 itself still packs 3 dijoins.
- **fastcuts.py**: dicut enumeration via order ideals of the condensation
  poset (ancestor-closed sets), enabling n up to ~50 with bounded ideal count;
  cross-validated against the 2^n enumerator on 3000 random digraphs.
- **Annealing around seeds** (Schrijver expansions at n=12 m<=44; D27 and
  random 2-copy vertex-gluings of D27 at n<=46 m<=100, tau>=3, tightness
  score): tens of thousands of SAT checks, zero UNSAT. (One earlier worker
  round OOM-killed by unbounded ideal enumeration on 52-vertex gluings;
  fixed with max_ideals cap.)

### Why the "LP integrality gap" objective degenerates

The fractional dijoin-packing LP value is ALWAYS exactly tau: the clutter of
minimal dicuts is ideal (Lucchesi-Younger), idealness is preserved under
blocking (Lehman), so the dijoin clutter is ideal, and its fractional packing
value equals the min cardinality of its blocker's members = min dicut size =
tau (uniform y_J weights on tau "fractional dijoins" achieve it). Hence
"maximize LP-vs-ILP gap of the packing LP" is identical to the direct search
for an instance with integer packing < tau — there is no smooth gap signal to
climb, only the 0/1 UNSAT signal, which is why tightness (number of
cardinality-tau minimal dicuts) is used as the annealing proxy instead.

### Why tau=2 gadgets can't give an unweighted CE

Unweighted Woodall for tau=2 is folklore-TRUE (Schrijver's Combinatorial
Optimization, Thm 56.3): any minimal dijoin J has A-J also a dijoin. So the
dyadic/tau=2 weighted gadget literature cannot produce an unweighted witness;
the minimum open case is tau=3, which is where the D27 seed lives.

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

## Phase 3 final tallies

- Schrijver expansion grid (parallel-arc): 96 configs, all pack.
- Schrijver subdivision grids (dash paths len 2-4, mult 1-3, solid subdiv):
  ~60 configs up to n=48, m=162, tau=10, 70k minimal dicuts — all pack.
- Schrijver-seeded annealing at tau>=3 (6 workers x 2-2.5h): ~13M proposal
  steps, every accepted candidate SAT-checked — zero UNSAT.
- D27-seeded annealing (2 workers x 2.5h at n=27): ~48k steps, ~19.5k full
  SAT checks at tau=3, m in 30-60 — zero UNSAT (best tightness: 85 tau-size
  minimal dicuts at m=38).
- D27 2-copy gluing annealing (2 workers x 2.5h, n up to 46, m<=100): ~93k
  steps, ~850 SAT checks (most candidates exceeded cut/ideal caps) — zero
  UNSAT.

## Phase 4: the exact smallest open case, via ACZ's theorems (bipsearch.py)

ACZ's Decompose-Lift-Reduce (arXiv:2202.00392, Thm ~DnL) reduces unweighted
Woodall for tau>=3 to sink-regular (tau,tau+1)-bipartite digraphs: all arcs
source->sink, sinks in-degree exactly tau, sources out-degree tau or tau+1.
tau=2 is folklore-true, so tau=3 in this class is the frontier. Their results
P2 (rho<=1), P3 (rho=2), P4 (rho=3, tau=3, unweighted) settle rho<=3, where
rho = #sinks - #sources and #deg-4 sources = 3*rho. Therefore:

  THE SMALLEST OPEN CASE of Woodall's Conjecture is tau=3, rho>=4:
  (4,3)-biregular bipartite digraphs with p>=12 sources (rho=4 forces
  3*rho=12 <= p; p=12 makes ALL sources out-degree 4), q=p+4>=16 sinks of
  in-degree 3, >= 48 arcs.

Dedicated harness (bipsearch.py): an instance is a list of in-neighbour
triples; every dicut delta^+(U) is determined by S = U cap sources plus the
covered sinks, so full dicut enumeration is a 2^p bitmask sweep, plus the
always-present single-sink dicuts in(t) (so tau <= 3 automatically in this
class). Cross-validated against the general enumerator (fastcuts.py +
2^n reference) on D27 (311 minimal dicuts, exact match) and 2000 random
instances (exact match on all weakly-connected ones). One real bug caught by
this cross-check: the first version missed the dicuts delta^+(V - {t}).

Searches (all tau=3 instances SAT-checked for 3-dijoin-partition):
- exhaustive, no isomorph rejection: ALL in-degree-3 bipartite instances with
  p<=4 sources q<=13 sinks; p=5, q<=11 (253k tau=3 checks); p=6, q<=9
  (10.0M multisets, 2.95M tau=3 checks) - all pack. (By the reduction this
  covers every digraph whose DLR factors are this small; note p<=8 sink-regular
  is closed by theory anyway since rho>=4 forces p>=12 - the exhaustive layer
  is an independent correctness belt for the harness.)
- random sampling p=10/q=13, p=12/q=15: ~50k tau=3 instances - all pack.
- D27-seeded structural annealing (rewire/add/delete sinks, q<=24): ~60k
  SAT checks - all pack.
- open-class annealing: (4,3)-biregular p=12/q=16 (5 workers, incl. 2 seeded
  from constructed instances containing a nontrivial tight 3-cut:
  sources {0,1,2} fully covering three parallel sinks) and p=15/q=20
  (1 worker), degree-preserving double-swaps, tightness+cut-count score:
  ~570k open-case instances SAT-checked - all pack.
- tight-cut-seeded random sampling at p=12/q=16 (all instances containing
  the built-in nontrivial tight 3-cut, rest configuration-model): 259k
  tau=3 instances - all pack.
- Total: >0.8M instances checked inside the smallest open class
  (48-arc (4,3)-biregular, rho=4). Hill-climbing never even retains
  nontrivial tight 3-cuts - packing slack appears structural here too.

## Phase 5 — C-speed mass sampling + structured tight-cut constructions

New checker bireg.c: pure-C reimplementation of the (4,3)-biregular pipeline
(2^p bitmask dicut enumeration, minimality filter, and a watched-count
3-coloring backtracker replacing the SAT solver). Validated against
bipsearch.py (pysat/CaDiCaL) on 200 random p=12 instances: exact match on
minimal-dicut counts AND pack/no-pack results. Throughput ~780 tau=3
instances/s/core at p=12 (~30x the Python+SAT harness).

- configuration-model random sampling, 6 workers x 2 h at p=12/q=16:
  33.06M instances, 33.05M with tau=3 - ALL pack.
- 2 workers x 2 h at p=15/q=20: 838k tau=3 instances - all pack.

Structured constructions (Python, exact enumeration via bipsearch.py) - the
idea: force the tight-cut structure a counterexample would need. Tight
source-sets in this class have 4k-3 = 0 mod 3, i.e. sizes 3, 6, 9; size-3
tight sets are exactly "blocks" (3 sources fully covering 3 private sinks).
- blockcons.py: 4 disjoint blocks + all set-partitions of the 12 leftover
  arcs into 4 extra sinks: exhaustive, 15,400 instances (each with 4 disjoint
  nontrivial tight 3-cuts) - all pack.
- laminarcons.py: laminar family A,B,C,D,A+B,C+D all tight (extra sinks e1
  in A+B, e2 in C+D): exhaustive, 4,000 instances with 6 nested nontrivial
  tight 3-cuts - all pack.
- crossingcons.py: CROSSING tight 6-sets S1=A+B, S2=B+C sharing block B
  (crossing size-3 tight sets are impossible in this class): exhaustive,
  1,080 instances - all pack.
- blockcons15.py: 5-block construction at p=15/q=20, 10,088 sampled
  instances (5 disjoint nontrivial tight 3-cuts each) - all pack.

## Phase 6 — tau=4 smallest open class

ACZ's P4 (settling rho=3) is tau=3-specific, so for tau=4 the class rho=3
is already open: sink-regular (5,4)-biregular bipartite digraphs with 12
sources of out-degree 5, 15 sinks of in-degree 4, 60 arcs.

Checker biregk.c generalizes bireg.c to arbitrary tau=K (K-coloring
backtracker with a 20M-node limit; instances hitting the limit are deferred
to hardk.txt and resolved by resolve_hard.py using the INDEPENDENT
fastcuts.py poset-ideal enumerator + CaDiCaL). Validation: K=3 exact match
vs bipsearch.py (50 instances, cut counts + pack results); K=4 exact match
vs fastcuts+pysat (30 instances).

- 7 workers x 3 h at K=4, p=12/q=15: 9,931,200 instances, ALL tau=4
  (single-sink 4-cuts + random 5-out-regular sources make tau<4 rare),
  all pack into 4 disjoint dijoins.
- 2,770 instances exceeded the backtracker node limit (~0.03%); every one
  independently re-checked (fastcuts + CaDiCaL): all pack. Zero UNSAT.

## STATUS

STATUS: negative / frontier-pushed — no counterexample. Exhaustive: all
digraphs on <=6 vertices; all simple <=7-vertex DAGs; multi-DAGs n<=7 up to
the stated arc budgets; >155M instances total. Seeded phase: Schrijver's 1980
weighted CE and ACZ's D27 near-miss extracted exactly from arXiv:2202.00392
and machine-verified; every unweighted expansion/subdivision/mutation tried
(tau up to 10, n up to 48, m up to 162, ~30k SAT-checked candidates around
the seeds) still packs. Phase 4: identified the exact smallest open case via
ACZ's P2-P4 (tau=3, rho>=4: (4,3)-biregular bipartite, >=12 sources, >=48
arcs), exhausted all bipartite in-degree-3 instances with p<=6 sources q<=9
sinks (2.95M tau=3 checks), and SAT-checked >0.8M instances inside the open
class itself (random, annealed, and tight-cut-seeded) - all pack. Phase 5:
C-speed checker (validated against the SAT harness) pushed the open-class
count to >34M tau=3 instances at p=12/q=16 and ~850k at p=15/q=20, plus
exhaustive structured families forcing disjoint / laminar / crossing
nontrivial tight 3-cuts (~20k instances) - all pack. Phase 6: the tau=4
smallest open class ((5,4)-biregular, p=12/q=15, 60 arcs, open since ACZ's
P4 is tau=3-specific): 9.93M instances checked (hard cases independently
resolved via fastcuts+CaDiCaL) - all pack. No
solutions/P03/verify.py since there is no claimed witness.
