# P12 — Tuscan-2 squares T2(11), T2(13) — V5 (literature-first + reformulation)

Session: https://app.devin.ai/sessions/6382e82d9822463084bdbaaaf4846fad
Variant: V5 — verify definition vs original sources, digest partial results, reformulate as
Hamiltonian-path decomposition, then targeted computation.

## Phase A — Definition verification (avoid paraphrase drift)

Sources checked:
1. **CPro1 repo** `Constructive-Codes/CPro1`, `design_definitions/tuscan-2-square/problem_def.py`
   (cloned, verifier read in full). Definition: n×n array, each row a permutation of n symbols;
   every ordered pair (a,b) of distinct symbols has **exactly one** row with b directly right of a,
   and **at most one** row with b two positions right of a. OPEN_INSTANCES = [[11],[13]].
2. **Kapralov, "The non-existence of Tuscan-2 squares of order 9"**, ACCT-2012, pp. 173–175
   (PDF fetched and read). Uses the original Golomb–Taylor definition: r×n Tuscan-k rectangle =
   each row a permutation, and for each m ∈ {1..k}, any ordered pair (a,b) has b m steps right of
   a in **at most one** row. Tuscan-k square = n×n Tuscan-k rectangle.
3. Golomb & Taylor, "Tuscan squares — a new family of combinatorial designs",
   *Ars Combinatoria* 20B (1985), 115–132. (NB: the problem file cites "IEEE Trans. IT"; the 1985
   Tuscan-squares paper is actually in Ars Combinatoria per Kapralov's reference list — the
   Golomb–Taylor IEEE-IT papers are the related Vatican/Florentine sequence papers. Same authors,
   same year; the statement itself is unaffected.)

**Equivalence check (m=1: "at most one" vs CPro1 "exactly one")**: in an n×n array with n rows,
each row contributes n−1 adjacent ordered pairs → n(n−1) pairs total = number of ordered pairs of
distinct symbols. Hence pairwise-distinct ("at most once") ⟺ every pair appears exactly once.
The two phrasings agree for squares. For m=2 there are n(n−2) slots < n(n−1) pairs, so "at most
once" is the right condition. **Definition in problems/P12 file matches the original.** Columns
need NOT be permutations (Tuscan, not Latin).

## Phase B — Literature status (as of July 2026)

- T2(n) exists whenever n+1 is prime (Vatican squares from the multiplication-table / Williams
  construction: row i = (i, 2i, ..., ni) mod p, p = n+1); covers n = 4, 6, 10, 12, 16, 18, ...
  These are even. All known T2 orders are even.
- T2(8) exists; Kapralov enumerated all 6 standard-form T2(8).
- Nonexistence known: T2(3), T2(5) (no Tuscan-1 of orders 3,5 at all — OEIS A004078:
  1,0,1,0,736,466144 for n=2..7), T2(7) = 0 (Kapralov's table), and **T2(9) = 0**
  (Kapralov ACCT-2012, exhaustive: 56459 permutations compatible with identity, compatibility
  graph with 203,140,075 edges, Cliquer found no 8-clique).
- So the odd-order record is: 3,5,7,9 all nonexistent; **n = 11, 13 are the first unknown cases**,
  and every known T2 has even order. Working conjecture guiding this run: T2(n) does not exist for
  odd n ≥ 3 — i.e. the expected answer for 11 (and 13) is NO, so complete search / structural
  obstructions are the right weapons, while keeping a construction search alive for upsets.
- Fresh searches (Exa, July 2026) for "Tuscan-2 order 11", Kapralov follow-ups, 2023–2025 SAT
  attacks: nothing newer than ACCT-2012 found. CPro1 (both 2025 papers) failed on the whole type.
  **Problem confirmed still open.**

## Phase C — Reformulation

### C1. Hamiltonian-path decomposition form
Identify the rows with directed Hamiltonian paths on vertex set S (|S| = n): row v1..vn ↦ Ham
path v1→v2→...→vn of the complete digraph K*_n. The m=1 condition says: the n paths **decompose
the arc set of K*_n** (n rows × (n−1) arcs = n(n−1) arcs, each exactly once). Such decompositions
exist for all n (Tillson: decomposition into Ham *circuits* for n≠4,6; Ham-path decompositions =
Tuscan-1 squares exist for all n except 3,5). The m=2 condition: for each path P = v1..vn, its
"square arcs" {(v_j, v_{j+2})} (n−2 per row, i.e. the arcs of the two parity-interleaved subpaths
of P) must be **globally distinct** across rows — a packing of n(n−2) arcs into K*_n. So:

> T2(n) ⟺ a decomposition of K*_n into n Hamiltonian paths P_1..P_n such that the squared paths
> P_1²,...,P_n² are arc-disjoint.

### C2. Consequences (proved by counting; all machine-checkable on any witness)
- **First and last columns are permutations of S**: symbol a has 10 out-pairs (a,·), so a is
  non-last in exactly n−1 rows → last exactly once; dually first exactly once. (So the standard
  symmetry-breaking "row 1 = identity, rows sorted by first symbol, first column = 0..n−1" is WLOG.)
- Distance-2 arcs: n(n−2) of the n(n−1) arcs appear; exactly n arcs never occur at distance 2.
- Reversal of all rows and relabeling of symbols are automorphisms of the problem; row order free.

### C3. Shortcut-array reformulation (new, V5)
For each symbol b, b is interior in exactly n−2 rows. Where b is interior with neighbor pattern
x,b,y, record A(x,b) = y. Then A is a partial (n×n)-array with n(n−2) filled cells
(domain: x≠b minus the one x that precedes b where b is row-last), entries ≠ x, b, and:
- **column-injective** (each in-arc (x,b) occurs once, and its successor y is determined; distinct
  x's give distinct interior occurrences with distinct y's — since out-arcs (b,y) each occur once),
- **row-injective ⟺ the Tuscan-2 (m=2) condition** (shortcut arcs (x,y) through varying b distinct).
So T2(n) ⟺ a Ham-path decomposition whose "shortcut array" is a partial Latin-like square
(99 cells for n=11, row- and column-injective, off-diagonal, A(x,b)∉{x,b}). No parity obstruction
found from this yet (counts balance: Σ_y #cells(y) = n(n−2), each y-cell-set a partial permutation
matrix avoiding row y, col y, hence ≤ n−1 = 10 — no contradiction). Kept as the cleanest target
for a future algebraic nonexistence proof.

### C4. Symmetric-family obstructions (negative structural results, this run)
- **Cyclic symbol symmetry impossible for odd n**: if σ (an n-cycle on symbols, wlog x↦x+1 mod n)
  maps the row set to itself, rows form one orbit {r+i}, and the m=1 condition forces the n−1
  consecutive differences of r to be pairwise distinct = a directed terrace / sequencing of Z_n.
  Z_n is sequenceable iff n is even (Gordon 1961), so no such T2(11)/T2(13). Any order-11 symbol
  automorphism of T2(11) is an 11-cycle ⇒ **T2(11) admits no symbol automorphism of order 11**
  (same for 13).
- **Multiplicative 10-orbit + 1 extra row impossible for n=11**: rows {c^k·r mod 11} (c a
  primitive root) fix the position of 0; pairs through 0 in r's 0-position cover all (0,x),(x,0);
  the nonzero adjacent gaps of r have ratio-classes each contributing all 10 pairs of that ratio;
  r has at most 9 nonzero gaps < 10 ratio classes, so ≥1 full ratio class (10 arcs) is missing,
  and if exactly one class ρ is missing the 11th row must consist precisely of the 10 arcs
  (a, ρa) — a geometric progression on the 10 nonzero symbols — leaving nowhere to place symbol 0
  without creating a duplicate 0-arc. **Dead for n=11 (and the same argument kills n=13 with its
  order-12 multiplicative group).**
- With reversal added (group ⟨x↦cx⟩×⟨rev⟩, |·|=10 for n=11): orbit sizes on rows divide 10; no
  fixed rows (σ≠id fixes no sequence; rev fixes none since entries distinct); the only involution
  (1,rev) fixes none; so all orbits have size 10, and 10 ∤ 11 ⇒ no such symmetry either.
### C5. Full symmetry classification for T2(11)/T2(13) and the mirror subspace
The automorphisms of the design are generated by symbol relabelings σ (rows → rows as a set)
and reverse-relabel maps φ_τ : r ↦ τ∘r∘ρ (ρ = position reversal; both preserve the T2 axioms).
- σ ≠ id fixes no row (σ∘r = r pointwise ⇒ σ = id), so all row-orbits of a prime-order σ have
  size p ⇒ p | n ⇒ p = 11 (resp. 13) ⇒ σ is an n-cycle ⇒ sequencing of Z_n, impossible for odd n
  (C4). **Hence T2(11) and T2(13) admit no nontrivial symbol automorphism.**
- If φ_τ is an automorphism, φ_τ² = (relabeling by τ²) ⇒ τ² = id. φ_τ permutes the n (odd) rows
  with orbit sizes 1,2 ⇒ some row r is φ_τ-fixed: τ∘r∘ρ = r ⇒ τ = r∘ρ̃∘r⁻¹ (ρ̃(j)=n−1−j),
  automatically an involution with exactly one fixed symbol. Relabeling the square by r⁻¹ makes
  r the identity row and τ the map x ↦ n−1−x. **So any T2(11) with ANY nontrivial automorphism
  is equivalent to one containing the identity row and invariant under M(r)_j = 10 − r_{10−j}.**
This mirror subspace is small enough to exhaust (see D5) — but in fact it is empty, by the
following new theorem.

### C6. THEOREM (rigidity): for odd PRIME n, no Tuscan-k square of order n has a nontrivial
automorphism; and for ALL odd n, no Tuscan-k square is mirror-symmetric (φ_τ-invariant).
Proof. (i) (n an odd prime.) A symbol relabeling σ≠id with σ(rows)=rows fixes no row (σ∘r = r
pointwise ⇒ σ = id), so replacing σ by a power of prime order p, all row-orbits have size p ⇒
p | n ⇒ p = n ⇒ σ is an n-cycle on symbols, wlog x ↦ x+1 (mod n); the row set is then closed
under r ↦ r+1, so the n−1 consecutive differences of any single row must be pairwise distinct,
i.e. a sequencing of Z_n — which does not exist for odd n (Gordon 1961). So σ = id.
(ii) A reverse-relabel automorphism φ_τ (r ↦ τ∘r∘ρ) has φ_τ² = relabeling by τ², hence τ² = id by
(i). φ_τ permutes the n (odd) rows with orbits of size ≤ 2, so some row r is φ_τ-fixed, and
conjugating by r⁻¹ we may assume the square contains the identity row and is invariant under
M(r)_j = (n−1) − r_{n−1−j}, whose arc action is the involution μ(a,b) = (n−1−b, n−1−a).
(iii) **Self-mirror arc contradiction.** The n−1 arcs (a, n−1−a), a ≠ (n−1)/2, satisfy μ(e) = e.
If such an arc e lies in row r, then e = μ(e) lies in M(r). Since each arc occurs at distance 1
exactly once, M(r) = r. But a fixed row (r_j + r_{n−1−j} = n−1) contains e as an adjacency
(r_j, r_{j+1}) with r_{j+1} = n−1−r_j = r_{n−1−j} ⇒ j+1 = n−1−j ⇒ j = (n−2)/2, not an integer for
odd n. So no row can contain any self-mirror arc — yet the distance-1 condition requires all
n(n−1) arcs, including the n−1 self-mirror ones, to be covered. Contradiction. ∎
(For even n, j = (n−2)/2 is an integer and mirror-symmetric Tuscan squares do exist — our search
found mirror-symmetric T2(4) and T2(6), machine-verified PASS. This confirms the parity mechanism.)

**Corollary: any T2(11) or T2(13), if one exists, has trivial automorphism group (fully rigid).**
This (a) explains why every algebraic/structured construction attempt fails for odd orders,
(b) means symmetry-based search-space reductions beyond the standard normalization are impossible,
and (c) is consistent with — and gives a structural reason to believe — the odd-nonexistence
conjecture.

Conclusion: **every natural algebraic construction route for odd n is obstructed** — consistent
with the all-even record and the odd-nonexistence conjecture. Computation should therefore aim at
(a) validated complete search on T2(11), (b) opportunistic construction search on T2(13).

## Phase D — Computation log

Machine: 8-core Linux VM, gcc -O3 -march=native -fopenmp.

### D1. Searcher validation (dfs.c — simple row-by-row DFS; dfs2.c — candidate-list + forward checking)
Normalization used by both (WLOG per C2): row 0 = identity; remaining rows have first
symbols 1..n-1 (one per class); last column a permutation (candidates with last symbol n-1
excluded). Counts of normalized T2(n):
| n | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|
| # | 1 | 0 | 1 | 0 | 6 | 0 |
Matches the literature exactly (Kapralov's table: T2(8) has 6 standard-form squares;
T2(5), T2(7) nonexistent; T2(9) = 0). Both programs agree on n ≤ 8.

### D2. Independent reproduction of Kapralov 2012: T2(9) = 0
`dfs2 9`: full exhaustion of the normalized space, 6298 top-level class-1 candidates,
786,244,822 search nodes, 753 s wall (54 min CPU), **solutions = 0**. This independently
re-proves the nonexistence of Tuscan-2 squares of order 9 with a different method
(forward-checked candidate lists vs Kapralov's Cliquer clique search). Pipeline validated.
Second, independently written searcher (dfs.c, plain row-by-row DFS, no candidate lists):
`dfs 9` full exhaustion, 6985 top-level seeds, 601,421,057,591 nodes, 7991 s × 2 threads,
**solutions = 0** — the two differently-coded programs agree, meeting the two-verifier standard.

### D3-pre. Note on searcher speed
dfs2's coverage prune (union of surviving candidates' dist-1 arcs must cover all unused arcs)
cut n=9 nodes from 786M to 298M (753s → 590s wall). Still, per-seed subtrees at n=11 cost
~30–60 CPU-minutes each (measured on the running frontier job), so full exhaustion of the
549,012 class-1 seeds needs on the order of 10⁴ CPU-days ≈ 30+ CPU-years — out of scope for
this session but plausibly within reach of a serious SAT/parallel-cluster effort (T2(11) sits
just past the feasible frontier; note Kapralov's n=9 needed "a long time" in 2012 and takes
10 min today).

### D3. T2(11) candidate-space statistics
Identity-compatible candidate rows (per first-symbol class, last symbol ≠ 10): 549,012
(class 1) up to 660,232 (class 10); total 6,026,973 (~368 MB of 128-bit arc masks).
(Kapralov's n=9 analogue was 56,459 total.) T2(11) ⟺ a choice of one candidate per class,
pairwise arc-disjoint at distance 1 & 2 with distinct last symbols — an 11-clique problem
~100× larger than the n=9 one.

### D4. Annealing witness hunt (anneal.c)
Cost = Σ max(0, pair-count − 1) over dist-1 and dist-2 pair counts; moves: in-row swaps and
segment reversals; geometric cooling with restarts (6 CPU-hours each order).
- n=8 (control, solutions exist): reaches cost 3 quickly but does NOT find a perfect square in
  minutes — corroborates CPro1's finding that local search is ineffective on this design type.
- n=11: best ever = 13 violated constraints (plateau); n=13: best ever = 23 (plateau).
Local search alone shows no sign of a nearby witness at either open order (weak evidence for
nonexistence, consistent with the odd conjecture).

### D5. Machine verification of the C6 theorem (mirror.c / mirror2.c — two independent programs)
Two independently written exhaustive searchers for M-invariant (mirror-symmetric) Tuscan squares
containing the identity row: mirror.c (candidate lists + 128-bit arc masks) and mirror2.c
(direct DFS, per-symbol 16-bit masks; also handles n=13).
- Even control: mirror-symmetric T2(4), T2(6) exist (found by both mechanisms where applicable);
  witnesses verified PASS by verify.py.
- Odd cases (theorem predicts 0, both programs agree): T2 mode n=5,7,9 → 0; Tuscan-1 mode
  (dist-2 constraints off — a much larger space) n=5,7,9 → 0 despite T1(7), T1(9) existing in
  huge numbers. Exactly matches the self-mirror-arc parity proof.
- n=11 (T2 mode, mirror.c): full exhaustion run — see result line below.

### D6. T2(11) frontier run (dfs2 with coverage pruning) — cost estimate
Long-running partial exhaustion over class-1 seeds. Honest negative: individual class-1 seed
subtrees each cost on the order of 1+ CPU-hour (none of the first seeds completed within
30+ CPU-minutes each across several attempts). Extrapolation: ≥ 549,012 CPU-hours ≈ 60+
CPU-years for full exhaustion with this searcher — T2(11) is ~10⁵× harder than T2(9)
(which takes ~1 CPU-hour today). A cluster-scale SAT/parallel effort is the right next step;
a single-VM complete search is out of reach.

### D5a. Lemma machine checks (lemma_check.py — standalone, no deps, prints PASS/FAIL)
- No sequencing of Z_n for n = 5, 7, 9, 11, 13 (exhaustive DFS): ALL PASS.
- No M-fixed row contains a self-mirror arc, n = 5, 7, 9 (full enumeration): ALL PASS.
These are the two computational ingredients of theorem C6.

### D5b. Mirror exhaustion results at the open orders
- mirror2 11 (direct DFS, T2 mode): **full exhaustion, solutions = 0**, 10,717,468,881 nodes,
  805 s × 2 threads. Machine-verifies theorem C6 at order 11: no mirror-symmetric T2(11).
- mirror2 13: same search at order 13 (result line appended when the run completes).
