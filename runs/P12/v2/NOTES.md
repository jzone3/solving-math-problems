# P12 — Tuscan-2 squares T2(11), T2(13) — V2 (exhaustive DFS) run notes

Session: https://app.devin.ai/sessions/ff73f474ceca40689ceedd732ff1ead0
Variant: V2 — row-by-row exhaustive backtracking with pair-availability pruning
and isomorph rejection (standard form).

## 1. Statement re-verification (against original sources)

- **CPro1 repo** `CPro1/design_definitions/tuscan-2-square/problem_def.py`
  (github.com/Constructive-Codes/CPro1, fetched 2026-07-22): definition matches
  the problem file exactly — n×n array, rows are permutations of {0..n-1},
  every ordered pair (a,b): exactly one row with b directly right of a, at most
  one row with b two positions right of a. `OPEN_INSTANCES = [[11],[13]]`.
- **Kapralov, "The non-existence of Tuscan-2 squares of order 9"**, ACCT-2012
  (Pomorie), pp. 173–175 (moi.math.bas.bg/moiuser/~ACCT2012/b30.pdf): general
  Tuscan-k definition uses "at most one row" for every m ∈ {1..k}; for an n-row
  square this forces exactly-one at m=1 by counting (n(n−1) adjacency slots =
  n(n−1) ordered pairs). Consistent with CPro1's verifier. The paper:
  - proves T2(9) does NOT exist (Cliquer clique search over the 56459
    permutations compatible with the identity row);
  - reports exactly **6** standard-form T2(8);
  - its table shows T2(11), T2(13) open ("?") as of 2012; T2(10), T2(12) exist
    (n+1 prime ⇒ Vatican square exists).
- **Openness as of July 2026**: Exa literature search (Tuscan-2 / Tuscan-k,
  2025–2026) found nothing newer than Kapralov 2012 and the two CPro1 papers
  (arXiv:2501.17725, 2505.23881), where the whole tuscan-2-square type resisted
  the LLM-heuristic attack. Treating T2(11), T2(13) as open. ✔

## 2. Encoding and symmetry breaking (isomorph rejection)

Standard form (same normalization as Golomb–Taylor / Kapralov):
- In any T2(n), each symbol is FIRST in exactly one row and LAST in exactly one
  row (out-degree counting: symbol a supplies n−1 dist-1 successors over n rows,
  missing one exactly when a is last; similarly for predecessors/first).
- Symmetry group used: symbol relabelling (S_n) × row reordering (S_n). Relabel
  so some row is the identity, then sort rows by first symbol ⇒ row 0 =
  identity, row i starts with symbol i. Every T2(n) is equivalent to a standard
  form, so exhausting standard forms decides existence. (Global reversal
  x→n−1−x + row-reverse is a further factor-2 symmetry, NOT used — searches
  below therefore over-count by ≤2×, harmless for existence.)

DFS state (see `t2dfs.c`, `t2dfs2.c`, `t2dfs3.c`):
- `used1[a]`, `used2[a]`: bitmasks of used dist-1 / dist-2 successors of a;
- `lastmask`: symbols already used as a row-end (last column must be a
  permutation — checked at position n−1);
- per-cell candidate mask = not-in-row ∧ ¬used1[prev] ∧ ¬used2[prev2].

Pruning (v2/v3 additions, function `feasible()` — the "pair-availability"
pruning): over the unplaced set U of the current row with tail y:
- succ(u)=¬used1[u]∧U empty ⇒ u forced row-end: must not be in lastmask, at
  most one such u;
- pred(u) (incrementally maintained `avail_in[u]`) empty ⇒ prune; at most one
  u with pred(u)={y};
- U must contain an allowed end (∉ lastmask);
- v3: all of U reachable from y in the dist-1 availability digraph.

## 3. Validation of the searcher (counts vs literature)

Standard-form solution counts, full exhaustion:

| n | solutions | nodes (t2dfs3) | literature |
|---|---|---|---|
| 4 | 1 | 13 | 1 (Kapralov table) ✔ |
| 5 | 0 | 47 | 0 ✔ |
| 6 | 1 | 1 586 | 1 ✔ |
| 7 | 0 | 151 595 | 0 ✔ |
| 8 | 6 | 95 180 162 | 6 (Kapralov) ✔ |
| 9 | **0** | 432 790 910 996 | 0 (Kapralov 2012) ✔ |

n=9 full exhaustion (t2dfs2, single core, 201 min CPU / 311 min wall under
contention): **0 solutions**, 4.33·10^11 nodes, 6298 standard-form second rows.
This independently re-proves Kapralov's T2(9) nonexistence with a completely
different method (DFS vs. clique search) — end-to-end validation that the
searcher + symmetry breaking are complete.

All six found T2(8) verify with `solutions/P12/verify.py` (PASS).
Node growth ≈ ×700 per n step. Pruning gains were modest: n=8 nodes
134M (t2dfs, plain) → 97.8M (degree pruning) → 95.2M (+reachability).

## 4. Feasibility estimate for full exhaustion

Extrapolating ×~700/step: n=9 ≈ 7·10^10, n=10 ≈ 5·10^13, n=11 ≈ 3·10^16 nodes.
At ~3·10^7 nodes/s/core × 8 cores ⇒ n=11 full exhaustion ≈ **years**; out of
reach this session even with the improved pruning (which bought only ~30%).
A 1/1000 slice of n=10 ran >15 min before being killed ⇒ n=10 exhaustion also
multi-day+; deprioritized in favor of witness hunting on the open sizes.

## 5. Witness hunt on T2(11), T2(13)

`hunt.sh`: randomized-restart exhaustive DFS (t2dfs3 `-r seed -1 -L 3e9`):
value order shuffled per node, restart every 3·10^9 nodes (~2 min), workers on
distinct seed ranges. 6 workers on n=11, 1 worker on n=13, alongside the n=9
exhaustion (8 cores saturated). Any solution found is copied to
`FOUND_n<k>_seed<s>.txt` and must pass `solutions/P12/verify.py`.

Hunt outcome (final, ~11h wall, 8 cores; ≈90 core-hours ≈ 3.5·10^12 nodes on
n=11, ≈10 core-hours on n=13):
- **T2(11): no witness found.** 1504 randomized restarts (mix of t2dfs4
  fail-first/L=1e9–2e9 and t2dfs3 in-order/L=5e9). Deep restarts routinely
  complete 9 of 11 rows (maxrow=9 in all 229 t2dfs3 restarts; one early run
  completed 10 rows and died in the last row). The last 1–2 rows are massively
  overconstrained — consistent with (but of course not proving) nonexistence.
- **T2(13): no witness found.** 193 restarts; searches routinely reach rows
  10–11 of 13 (maxrow=10: 32×, maxrow=11: 161×), never row 12.

## 6. Dead ends / structural notes

- **Cyclic construction impossible for odd n**: rows = translates row_i =
  row_0 + i (mod n) would need row_0's consecutive differences to be all n−1
  nonzero residues; these telescope to row_0[n−1] − row_0[0] = Σ(all nonzero
  residues) = n(n−1)/2 ≡ 0 (mod n) for odd n, forcing first = last symbol —
  contradiction. So no Z_11/Z_13-translate T2 exists; any witness must be
  non-cyclic. (Matches why n+1 prime constructions use Z_{n+1}^* instead.)
- Pruning lever was weak: degree + reachability pair-availability pruning cut
  only ~30% of nodes (n=8: 134M→95M) — the DFS tree size is intrinsic; a
  fundamentally different method (SMS/clique with strong isomorph rejection,
  cf. V1/V3) is needed for full n=11 exhaustion.

## 7. Phase 2 (resumed session): complete-solver attack (CP-SAT / kissat)

After V2 DFS was exhausted, escalated to untried complete-search machinery:
- `t2cpsat.py`: OR-Tools CP-SAT model (integer cells + boolean channeling,
  exactly-one over the 110 dist-1 pair-occurrence literals, at-most-one for
  dist-2, standard-form units, redundant last-column alldifferent).
- `t2cnf.py`: DIMACS CNF (direct encoding + Tseitin pair vars, pairwise AMO)
  for kissat 4.0.4 (built from source); supports cubes fixing row 1.
- `cubes11.txt`: all **549 012** standard-form second rows for n=11
  (row 0 = identity, row 1 starts with 1, compatible at dist 1 and 2)
  — the top-level cube set for cube-and-conquer.

Calibration results:
- n=8: CP-SAT finds a valid T2(8) in seconds (verified PASS); kissat SAT in
  ~7 min single-thread.
- n=9 (known UNSAT): **CP-SAT failed to prove UNSAT in 4h × 8 workers
  (status UNKNOWN, ~90k det-time)** — vs. 3.4 core-hours for the dedicated
  DFS exhaustion. kissat on n=9 UNSAT: >4h, still running at write-up.
  Generic complete solvers are ~10×+ SLOWER than the specialized DFS here,
  so a SAT-based decision of T2(11) needs ≳10^5 core-hours with these
  encodings — out of reach on this box; would need SMS/clique-style global
  isomorph rejection beyond the standard form to become feasible.
- n=11 witness hunt via CP-SAT (6 workers, 12h): running; no feasible
  solution so far.

## 8. STATUS

STATUS: negative (frontier-pushed on n=9). Summary:
- T2(9) nonexistence INDEPENDENTLY RE-PROVED by full exhaustion (0 solutions,
  4.33·10^11 nodes) — first non-clique verification of Kapralov 2012; method
  end-to-end validated on exact counts n=4..8 (incl. the six T2(8)).
- T2(11): full standard-form exhaustion estimated ~3·10^16 nodes (≈years on
  this box) — infeasible here; ~90 core-hours of randomized-restart exhaustive
  DFS found no witness, best partials 10/11 complete rows.
- T2(13): no witness in ~10 core-hours; best partials 11/13 rows.
Both open cells remain open; recommend V3-style SAT-modulo-symmetries or
Kapralov-style clique search with modern hardware for a decision at n=11.
