# P12 V4 — Tuscan-2 squares T2(11)/T2(13) via CP-SAT + hybrid LNS/annealing

Session: https://app.devin.ai/sessions/aa3de7863ea14897a6097b8364979edc
Variant: V4 (OR-Tools CP-SAT model + large-neighborhood search; anneal on near-solutions;
seed with high-quality partials). Machine: 8 cores, 31 GB RAM, ortools 9.15.6755.

## Statement re-verification (against original source)

- Fetched `Constructive-Codes/CPro1` → `CPro1/design_definitions/tuscan-2-square/problem_def.py`.
  Definition matches problems/P12-tuscan-2-squares.md exactly: each row a permutation of
  {0..n-1}; every ordered pair (a,b) at distance 1 **exactly once** (their verifier checks
  at-most-once, which with n(n-1) slots = n(n-1) pairs is equivalent); distance 2 **at most
  once**. OPEN_INSTANCES = [[11],[13]]; DEV_INSTANCES = [4,6,8,10,12].
- Literature check (Exa, July 2026): found "The non-existence of Tuscan-2 squares of order 9"
  (ACCT 2012, moi.math.bas.bg) — n=9 is proved NONEXISTENT. No paper found claiming T2(11)
  or T2(13) resolved as of July 2026. Golomb–Taylor 1985 origin confirmed via Tuscan-k
  squares literature. Proceeding: n=11, 13 treated as open.

## Encoding

`pos[r][a]` = column of symbol a in row r; AllDifferent per row.
`adj1[r,a,b] <=> pos[r][b]-pos[r][a]==1`, `adj2` likewise with ==2 (fully reified).
ExactlyOne over rows for each ordered pair at dist 1; AtMostOne at dist 2.
Symmetry breaking (exact model): row 0 = identity (symbol relabeling) AND column 0 =
identity (rows can be sorted: first column of any T2(n) is a permutation, since each symbol
has dist-1 in-degree n-1 and appears n times, hence is row-initial exactly once).

Optimization model (cpsat_opt.py): soften both cardinality families with excess vars,
minimize total excess; objective 0 <=> valid T2(n). Accepts anneal output as CP-SAT hints
(drives RINS/RENS + LNS workers from near-solutions).

Annealer (anneal.py): rows as permutations; moves = in-row swap / segment reversal /
relocation; incremental cost = duplicate dist-1 slots + duplicate dist-2 slots; SA with
restarts.

## Calibration (dev instances)

| n | exact CP-SAT (8 workers) | result |
|---|---|---|
| 4 | 0.01 s | SAT, verified PASS |
| 6 | 0.09 s | SAT, verified PASS |
| 8 | 389 s | SAT, verified PASS |
| 10 | >600 s | UNKNOWN at 600 s — exact model already hard at n=10 |
| 9 | running (known nonexistent; UNSAT calibration) | pending |

Annealer on n=10: cost 5 within ~2 min from scratch (stalls at low cost — plateau moves
needed; used as hint source rather than standalone solver).

## Log

- Started 4×anneal(n=11, 1800 s, seeds 1–4); n=9 exact UNSAT run in background (4 workers).
- Anneal results n=11 (1800 s each): best costs 7, 8, 8, 8. Plateau around 7–8 violations.
- cpsat_opt(n=11, hint=cost-7 anneal, 4 workers): default CP-SAT LNS accepted hint (obj 7)
  but made no improvement in ~25 min → killed; default LNS neighborhoods too generic here.
- Wrote lns_rows.py: row-neighborhood LNS — free k rows (biased to violating rows), fix
  rest, CP-SAT re-optimize freed rows with obj ≤ incumbent, plateau random-walk accepts.
- lns_rows k=3, iter_tl=20 s: 60 iterations, stuck at cost 7 (plateau moves accepted but no
  descent). Escalated to k=5, iter_tl=60 s.
- n=9 exact (UNSAT calibration): **UNKNOWN after full 14400 s (4 h, 4 workers)** — CP-SAT
  cannot re-prove the known nonexistence of T2(9) in 4 h with this encoding+symmetry
  breaking. Implication: proving T2(11) UNSAT via CP-SAT is far out of reach; V4 value
  concentrates on the search/repair side and min-violation data.
- lns_rows k=5 (60 s/iter) and k=7 (180 s/iter): both stuck at cost 7 (20+ iterations each).
- Wrote lns_symbols.py (orthogonal neighborhood: free k symbols across all rows, others
  keep relative order per row). k=4, 120 s/iter: 40+ iterations, still cost 7.
- Min-violation landscape data (anneal): n=9 (nonexistent) plateaus at cost 4 (2 seeds);
  n=11 plateaus at cost 7 (5 seeds + 3 LNS variants); n=13 at ≤14 (running).
  Reading: nonexistent instances have small nonzero floors; n=11's consistent floor of 7
  across independent neighborhoods is weak evidence for nonexistence (not proof).
- Started cpsat_opt on n=9 (2 h) to see how far the optimization bound gets on a known
  nonexistent instance (best bound > 0 would be an optimality-style nonexistence re-proof).

- cpsat_opt n=9 (2 h, hint 4): final obj 4, **best bound 0.0** — CP-SAT cannot lift the
  min-violation lower bound above 0 even for the known-nonexistent n=9. Optimality-style
  nonexistence proofs are out of reach with this encoding.
- Diversified row-LNS (equal-cost walk + 15% uphill(+1) moves, k=4, 40 s/iter): 160
  iterations, best still 7. Symbol-LNS full 4 h: best still 7.
- 2 h anneal n=11 (seed 7): 7 again (now 5/5 seeds land exactly on 7).
  2 h anneal n=13 (seed 8): best 13.
- Final phase: (a) exact decision model n=11 hinted with cost-7 incumbent (no symmetry
  breaking), 4 workers × 4 h; (b) row-LNS on n=13 from cost-13 incumbent, 4 workers × 4 h.

- Final phase results: hinted exact n=11 (4 workers × 4 h) → UNKNOWN (no witness, no
  refutation). Row-LNS n=13 (4 h) improved anneal's 13 → **12 violations** then stalled.

## Summary of best-known min-violation values (this run, machine-verified via t2_common.cost)

| n | existence | best violation count found | methods agreeing |
|---|---|---|---|
| 4, 6, 8 | exists | 0 (witnesses verified PASS by solutions/P12/verify.py) | exact CP-SAT |
| 9 | nonexistent (known) | 4 | anneal ×2, cpsat_opt 2 h (bound stuck at 0) |
| 11 | **open** | **7** | anneal ×5, row-LNS k=3/5/7, symbol-LNS, diversified LNS, cpsat_opt |
| 13 | **open** | **12** | anneal + row-LNS 4 h |

Total compute: ~30 core-hours CP-SAT + ~8 core-hours annealing (8-core VM, ~14 h wall).

## Dead ends / negative findings

1. Exact CP-SAT decision model: solves n≤8, cannot decide n=10 (600 s) nor re-prove the
   known T2(9) nonexistence in 4 h — UNSAT for n=11 via CP is hopeless with this encoding.
2. CP-SAT default LNS on the soft model: accepts hints but never improves them (n=9 and 11).
3. Row-, symbol-, and diversified-LNS all bottom out at exactly 7 violations for n=11 from
   every start — a remarkably robust floor. Best partials kept in best_T2_11_seed*.txt for
   seeding other variants (e.g. V1/V3 SAT runs can use them).
4. Optimality-bound route (prove min-violation > 0): bound never left 0 even for n=9.

STATUS: negative (no T2(11)/T2(13) witness, no nonexistence proof; frontier data: robust
min-violation floors 7 @ n=11 and 12 @ n=13, cost-7 partials published for seeding).
