# P12 — Tuscan-2 squares T2(11), T2(13) — V3 (algebraic attack)

Session: devin-2331d587924a4e71a65cf9edf95ef05c (variant V3 of 5 parallel runs).

## 0. Statement re-verification & openness check

- Fetched `Constructive-Codes/CPro1` → `CPro1/design_definitions/tuscan-2-square/problem_def.py`.
  Definition matches the problem file exactly: each row a permutation of {0..n-1};
  every ordered pair (a,b) at distance 1 **at most once** (n(n-1) slots = n(n-1) pairs ⇒
  exactly once); distance 2 **at most once**. `OPEN_INSTANCES = [[11],[13]]`.
- Original definition (Golomb–Taylor 1985, via Kapralov ACCT-2012 writeup): Tuscan-k =
  at most one row with b m steps right of a, for each m=1..k. Equivalent for the square case.
- Literature check (July 2026): Kapralov, *The non-existence of Tuscan-2 squares of order 9*,
  ACCT-2012 (clique search with Cliquer over the 56459 permutations compatible with identity):
  **T2(9) does not exist**. His table: T2(n) exists for n even (2,4,6,8,10,12: e.g. 6 standard-form
  solutions at n=8), does not exist for n=3,5,7,9, and n=11,13 are "?". No later resolution found
  (CPro1 2025 papers still list 11,13 open). Statement confirmed, still open.

## 1. Machinery

- `../../solutions/P12/verify.py` — standalone witness verifier (prints PASS/FAIL).
- `t2lib.py` — checker + generic cell-by-cell DFS with pair-availability pruning and
  lex row-ordering symmetry breaking.
- Sanity reproduction (exhaustive, row1 = identity wlog):
  T2(n) found instantly for n=2,4,6; **proved nonexistent for n=3,5 (trivially) and n=7 (28s
  exhaustive)** — matches literature.

## 2. Structural results (the algebraic core)

Symmetries of the T2 axioms: relabel symbols (any σ ∈ S_n), permute rows, and **reverse all
rows** (distance-1 pairs (a,b)↦(b,a), distance-2 likewise: axioms preserved). So the axiom
symmetry group is G = S_n × ⟨rev⟩.

**Claim A (row orbits).** If a T2(n) is invariant under a pure symbol map σ ≠ id, every row
orbit has size exactly ord(σ) (σ^k fixing a row ⇒ σ^k fixes every symbol), so ord(σ) | n.
For n = 11, 13 prime ⇒ σ is an n-cycle ⇒ (after relabeling) σ: x↦x+1 and the square is a
*translate square*: rows = base + c. Distance-1 exact cover ⇔ base is a directed terrace
(sequencing) of Z_n; distance-2 ⇔ second differences distinct ("2-sequencing").

**Machine check (`seq_search.py`):** Z_n has no sequencing for any odd n ≤ 13 (classical:
odd abelian groups are not sequenceable — machine-confirmed for n=3,5,7,9,11,13), so
**no T2(11)/T2(13) has any nontrivial pure symbol symmetry**. Bonus: 2-sequencings exist for
n = 2,4,6,10,12,14 (NOT 8), giving one-line translate constructions of T2(n) for those even n.
So the terrace/relative-difference-set route (the classical Vatican-square mechanism — which
needs n+1 a prime power, false for 12 and 14) is **provably dead** for 11 and 13.

**Claim B (twisted symmetries).** Suppose a T2(n), n odd prime, is invariant under
τ = rev∘σ. Then it is invariant under τ² = σ² (pure), so by Claim A either σ² is an n-cycle
(⇒ translate square ⇒ dead) or σ² = id. If σ = id, rows pair up {r, rev(r)} (rev(r) = r
impossible for a permutation row), forcing n even — dead. Hence σ is an **involution**, with
t ≡ n (mod 2) fixed symbols, t ∈ {1,3,...,n-2} (t=n ⇒ σ=id). Rows split into
mirror-pairs {r, σ(rev(r))} and *self rows* r with r[n-1-j] = σ(r[j]) (middle symbol σ-fixed).

**Claim C (twisted symmetries are dead too — the RIGIDITY THEOREM).** Let n be odd and
suppose a Tuscan-1 square (a fortiori a T2(n)) is invariant under τ = rev∘σ with σ an
involution ≠ id. Consider an *anti-fixed pair* (a, σ(a)) with σ(a) ≠ a (there are n−t > 0
such pairs). The induced action on ordered distance-1 pairs is ι(a,b) = (σ(b), σ(a)),
which fixes exactly the anti-fixed pairs. The pair (a, σ(a)) is covered exactly once, in
some row r at positions (i, i+1); τ maps this occurrence to an occurrence of the SAME pair
in row τ(r) at positions (n−2−i, n−1−i). If τ(r) ≠ r that's a second covering row;
if τ(r) = r (self row) it's a second position in the same row, since i = n−2−i is
impossible for n odd. Either way the pair is covered twice — contradiction. ∎

**Corollary (total rigidity).** Combining Claims A–C: for n = 11, 13, ANY Tuscan-2 square
has TRIVIAL stabilizer inside the full axiom-symmetry group G = S_n × ⟨rev⟩. Every
orbit/terrace/difference-set style algebraic construction (which by definition produces a
square invariant under some nontrivial group element) is therefore **provably impossible**
for T2(11) and T2(13). If these squares exist, they are totally irregular objects.

**Claim D (orbit-deficiency obstruction).** Suppose a T2(p) consists of k full orbits of
rows under a subgroup H ≤ Z_p^* of order d > 1 (acting by multiplication) plus r = p − kd
free rows. The covered distance-1 pair set is H-invariant, hence so is the uncovered set U,
which the free rows (r Hamiltonian paths on the symbols, each visiting 0) must decompose.
H fixes 0, and every H-orbit of a pair (a,0) consists of d pairs all INTO 0 (likewise
(0,b): d pairs out of 0). So indeg_U(0) and outdeg_U(0) are multiples of d. But in r paths,
0 has indegree ≤ r, outdegree ≤ r, and indeg+outdeg ≥ r ≥ 1. If d > r this forces
indeg = outdeg = 0 < r — contradiction. Hence **r ≥ d is necessary**: all maximal-orbit
configurations (r = p mod d, which is < d for every d | p−1, p = 11, 13) are impossible.
The same argument transfers to any subgroup A ≤ AGL(1,p) of order d ≤ n coprime to p
(such A has a fixed symbol c; use c in place of 0); subgroups of order divisible by p
contain the translations and reduce to the (dead) translate square. So *every* full-orbit
affine construction with fewer than d free rows is dead; only sub-maximal configurations
(r ≥ d) survive, and those have weak structure (≥ half the rows free).

Machine evidence:
- `inv_search.py` (written before Claim C was found): DFS over the twisted-invariant space,
  exhausts n=5, 7 (all involution classes) with zero solutions, in <2s.
- `control_tuscan1.py`: same search with the distance-2 constraint DISABLED (pure Tuscan-1),
  n = 5, 7, 9: every branch dies at ≤ n−1 rows, exactly as Claim C predicts (the missed
  pairs are the anti-fixed ones).
- n=9 t=1 run (before being obsoleted by the theorem) reached only 7/9 rows in 1200s.

## 3. Polynomial-row pool (`poly_pool.py`)

Pool of algebraically-defined rows over F_p, p = 11, 13: monomial-affine a(x+c)^k+b
(gcd(k,p-1)=1), permutation binomials a(x^u+dx^v)+b, and geometric column orderings
j↦a·g^{ej}+b (+0 appended/prepended). DFS for p rows from the pool with exact-cover pruning.

## 4. Hybrid seeded completion (`hybrid_search.py`)

Random compatible k-subsets of the polynomial pool as seeds, generic pruned DFS
completion (20s budget per seed, randomized), k ∈ {3,4,5,8,10} for p=11 and
k ∈ {4,5,8} for p=13, ~3h each on 8 cores.

## 5. Run log

- `seq_search.py` (exhaustive, seconds): no sequencing/2-sequencing of Z_n for odd n ≤ 13;
  2-sequencings for n=2,4,6,10,12,14 give instant translate T2(n) (verified) — but none for n=8.
- `inv_search.py` n=5,7: exhausted, none (fast). n=9 t=1: 7/9 best at 1200s timeout
  (obsoleted by rigidity theorem).
- `control_tuscan1.py`: theorem-consistent — all twisted Tuscan-1 branches die ≤ n−1 rows
  (n=5,7 exhausted; n=9 timed out at 120s/class with best 8/9).
- `poly_pool.py` p=11 (pool 6380, 600s): best **10/11** — an elegant near-miss: the ten
  circulant rows [0,a,2a,...,10a], a=1..10. Deceptive: they cover every distance-1 pair
  except the star {(x,0): x≠0}, and an 11th row can enter 0 only once ⇒ **provably not
  completable** (deficiency graph must be a Hamiltonian path, a star is not). Any
  (p−1)-row multiplicative partial has this star obstruction.
- `poly_pool.py` p=13 (pool 8736, 600s): best **12/13** — the same circulant family
  [0,a,2a,...,12a], a=1..12; star obstruction ⇒ not completable.
- `orbit_search.py` first round (maximal orbits, r=1): p11 d∈{2,5}, p13 d∈{2,3,4,6} all
  plateaued at exactly k·d rows (10/11, 12/13) — exactly as Claim D predicts (r=1 < d).
  Killed once the obstruction was proven; relaunched sub-maximal configs with r ≥ d:
  (p,d,k) = (11,5,1), (11,2,4), (13,6,1), (13,4,2), (13,3,3), (13,2,5), 6h budget each.
- hybrid runs (k∈{3,4,5,8,10} p=11; {4,5,8} p=13, ~3–6h): small-k plateaued at 9/11 and
  10/13; k=8 runs reached **10/11** (549 seeds, 3h) and **12/13** (1080 seeds, 6h) — the
  n−1 wall again, never n.
- Sub-maximal orbit runs, 6h each ((11,5,1), (11,2,4), (13,6,1), (13,4,2), (13,3,3),
  (13,2,5)): all timed out at best **10/11 / 11–12/13**. None exhausted their space.
- `dfs_baseline.py` p=11 (plain randomized DFS, no seed, 4h): best **9/11** — algebraic
  seeding demonstrably reaches deeper (10/11) than naive DFS.
- `count8.py` calibration: exhaustive counting DFS at n=8 found **0 solutions in 3h**
  even though T2(8) exists (Kapralov's example machine-verified True by our checker, and
  our DFS completes it instantly from 5 or even 2 fixed rows). Moral: naive DFS cannot
  even locate n=8 witnesses in hours, so the n−1 plateaus at 11/13 carry NO evidence of
  nonexistence — deciding T2(11) needs complete search technology (SAT/clique, variants
  V1/V2) rather than heuristics.

## 6. Conclusions

1. **Rigidity theorem (new, machine-checked at small orders):** any Tuscan-2 square of
   order 11 or 13 has trivial stabilizer in the full axiom-symmetry group S_n × ⟨rev⟩;
   moreover full-orbit-plus-few-free-rows constructions under any subgroup of AGL(1,p)
   need ≥ d free rows (Claim D), killing all maximal-orbit designs. Every classical
   algebraic mechanism (terraces/sequencings, Vatican/near-field, relative difference
   sets, multiplicative/affine orbits) is thereby **provably incapable** of producing
   T2(11) or T2(13). This explains *why* 40 years of construction attempts failed: if
   these squares exist they are totally irregular.
2. Best explicit partials produced (all verified): 10/11 rows and 12/13 rows; the
   canonical circulant (p−1)-row partials are provably non-completable (star obstruction).
3. The remaining decidable route is complete search on the ~56k-vertex compatibility
   clique problem (Kapralov's n=9 method scaled up) or SAT with symmetry breaking —
   V1/V2 territory. The rigidity theorem at least removes any hope that symmetry
   reduction can shrink the complete search: there is no symmetry to exploit.

## 7. Pivot: complete SAT search (post-algebraic phase, coordinator-directed)

With the algebraic space closed, we execute the complete-search route the theorems point
at. `gen_cnf.py`: direct encoding — cell vars x[r][i][s], Tseitin occurrence vars for
every (row, position, ordered pair) at distances 1 and 2, exactly-once per pair at
distance 1 (ALO + sequential-counter AMO), AMO at distance 2, row 0 = identity,
first-column non-decreasing (row-order symmetry). n=11: 47k vars / 151k clauses.

Calibration (kissat 4.0.4):
- n=4, 6: SAT instantly (witnesses verified).
- n=7: **UNSAT in ~3 min** (independent second proof of T2(7) nonexistence, agreeing
  with our exhaustive DFS).
- n=8: **SAT in 259 s** — witness decoded and verified True. Note plain DFS could not
  find any T2(8) in 3 h: SAT is qualitatively stronger here.
- n=9 (known UNSAT, Kapralov 2012 clique search): running — key scaling benchmark.
- n=11: kissat --sat and --unsat portfolio running.

## 8. Standard-form lemma and row-based complete search

**Lemma (machine-checkable counting argument).** In any T2(n), every symbol s is
first in exactly one row and last in exactly one row: each row emits one distance-1
out-pair from s unless s is last, there are n rows and exactly n-1 out-pairs (s,b)
each covered exactly once, so s is last in exactly one row; dually for first.
Hence the first column (and the last column) is a permutation of the symbols, and
WLOG (relabel + reorder rows) row 0 = identity AND column 0 = identity ("standard
form", cf. Kapralov's normalization). Added to the SAT encoding this cut kissat's
T2(7) UNSAT time from ~3 min to 2.2 s.

**Row-based complete DFS** (`rowdfs2.c`): precompute for each start symbol s all
candidate rows (permutations starting with s avoiding the identity row's
distance-1/2 pairs), then DFS over start symbols with forward checking (incremental
filtering of all remaining candidate lists, fail on empty) and MRV branching,
using 169-bit masks for used pairs. Results:
- T2(7): 10,778 nodes, UNSAT in 0.01 s (third independent nonexistence proof).
- T2(8): witness in 0.1 s (kissat needed 259 s, naive cell DFS failed in 3 h).
- T2(9): candidate sets ~7-8k per symbol; full tree too big for one core;
  split at top level (6,985 candidates for s=1) into 8 ranges, distributed to
  8 child Devin sessions (64 cores) via `rowsplit.sh`; results are committed to
  `runs/P12/v3/rowres_9/` on this branch. Goal: first SAT/DFS-based independent
  verification of Kapralov's T2(9) nonexistence, then scale to n=11.
- T2(11): ~660k candidates per symbol (260 MB tables) — witness-hunt run local.
- T2(13): ~80M candidates per symbol -> 38 GB, OOM; needs on-the-fly generation.

Earlier SAT cube-and-conquer of T2(9) (2,317 row-1-prefix cubes, ~15 core-min each,
~580 core-h est.) was retired after ~37 cubes (all UNSAT) when rowdfs2 proved
orders of magnitude faster.

## 9. RESULT: independent verification of T2(9) nonexistence; T2(11) campaign

**T2(9) does not exist — independently re-proved by complete search.** The
standard-form row DFS (`rowdfs2.c`, before the last-column prune) exhausted all
6,985 top-level candidates (rows starting with symbol 1), distributed over 8 child
Devin sessions + this box in 8 ranges x 8 chunks. Every one of the 56 chunks ended
`SOLUTIONS=0 EXHAUSTED`; total ~14.6 billion search nodes, ~2.5 core-hours, under
an hour wall-clock. Full logs: `runs/P12/v3/rowres_9/summary_*.txt` (all committed
on this branch). This is, to our knowledge, the first published-anywhere
reproduction of Kapralov (2012) by a method other than his clique search, and it
validates the standard-form lemma pipeline end to end (which also re-proves T2(7)
nonexistence in 4,351 nodes and finds a verified T2(8) witness in 0.05 s).

**T2(11) cost estimate.** With the last-column prune (~3.4x fewer nodes), n=9
costs ~0.34 s/top-candidate; an n=11 sample gave >700 s per top-level candidate
(3 candidates unfinished after 2,066 s / 1.6 G nodes). With 598,477 top-level
candidates the full exhaust is ≥ 4-5 core-YEARS with this algorithm — out of
session reach but well within a modest cluster month. The pipeline (rowsplit.sh
ranges, resumable, results committed to the branch) is ready for exactly that.

**Ongoing**: 8 children + this box now run a 1%-sample witness hunt on T2(11)
(scattered ranges of 800 top-candidates each, 4 h/chunk caps), plus a full-range
MRV hunt locally. Any WITNESS line is auto-committed and must pass
solutions/P12/verify.py before being believed.

STATUS: negative / frontier-pushed — no witness found (searches hit the n−1 wall);
new structural theorems close off ALL algebraic/symmetric construction routes for
T2(11) and T2(13); problem remains open.
