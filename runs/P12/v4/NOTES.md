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
- n=9 exact (UNSAT calibration): still running at 1.5 h, no verdict yet.

STATUS: running
