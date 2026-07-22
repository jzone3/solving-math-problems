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
- hybrid runs (k∈{3,4,5,8,10} p=11; {4,5,8} p=13): plateaued at 9/11 and 10/13 within
  minutes; still running.
- `dfs11_baseline.out`: plain randomized DFS from identity row, 4h budget: (running)
