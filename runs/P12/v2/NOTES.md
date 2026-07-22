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
| 9 | (running) | ~10^11 est. | 0 (Kapralov 2012) |

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

(Compute log and outcomes appended below as the run progresses.)
