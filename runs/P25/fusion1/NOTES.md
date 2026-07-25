# P25 fusion1 — K3(6,1) cyclic-symmetry feasibility

## Coordination and scope

This is a continuation of the original `runs/P25/v1` symmetry sweep.  The
original run left 22 cyclic-symmetry classes undecided after its feasibility
ILP passes.  To avoid duplicating its work, fusion1 consumes exactly those
classes in reverse sorted order, beginning with
`lam=[3,1,1,1], assign=('id','sigma','sigma','sigma')`.

The class list is deduplicated from the `UNDECIDED` lines in
`runs/P25/v1/logs/feas*.txt`.  The scheduler runs six one-thread SAT workers;
classes that time out are sent to a two-worker ILP fallback lane, with two
HiGHS threads per ILP job.  A 72-word SAT witness is a world-record result:
stop all work, verify it immediately, and report it.

## SAT formulation

For a class `(lam, assign)`, the v1 coordinate-cycle and symbol-map encoding
constructs the cyclic monomial action and its orbits on the 729 ternary words.
There is one Boolean variable `x_j` for each orbit.

* 729 covering clauses are emitted, one for every word `w`.
* A covering clause contains every orbit variable whose orbit intersects the
  radius-1 Hamming ball of `w`.
* The size bound is `sum_j |orbit_j| x_j <= 72`.
* The weighted bound is encoded by expanding each orbit variable into one
  repeated literal per orbit member and feeding those literals to a capped
  unary totalizer.

Kissat runs without proof output during normal search to prevent disk
exhaustion.  If a class returns UNSAT, the scheduler queues a single
confirmation pass with textual DRAT output and DRAT-Trim; at most one proof is
ever retained, and it is deleted immediately after checking.

## Validation

* **Cardinality/UNSAT sanity:** target 56 on
  `lam=[6], assign=('sigma',)` returned UNSAT in approximately 0.1 seconds.
  This target is below the sphere-covering bound `729/13 ~= 56.08`.
* **SAT decode path:** target 77 on
  `lam=[6], assign=('tau',)` returned SAT, decoded 77 words, and passed
  `runs/P25/v1/verify.py`.
* **ILP cross-check:** target 77 on
  `lam=[4,1,1], assign=('id','id','tau')` found a 76-word code.  This is
  consistent with the v1 sweep's reported invariant minimum of 73 (a
  76-code is feasible but not optimal).  The decoded 76-word file was
  independently rechecked with `verify.py` and passed.

## Run plan and budgets

The target is 72 words.  Each class receives up to two hours of SAT search.
SAT timeouts enter the HiGHS orbit ILP fallback with a four-hour limit and two
threads.  The scheduler processes the 22 classes in reverse sorted order,
maintains four SAT workers, two PB workers, and allows up to two concurrent
ILP jobs (roughly eight cores at maximum load).

The PB track uses RoundingSat's native OPB parser and cutting-planes/LP
reasoning.  It emits one Boolean variable per orbit, 729 covering inequalities
of the form `sum(x_j) >= 1`, and the native weighted inequality
`sum(|orbit_j| x_j) <= 72`.  It runs two PB workers with the same two-hour
per-class budget, while the SAT lane is reduced to four workers.  Classes
that time out in both the SAT and ILP lanes are appended to
`logs/cube_queue.txt` for a later cube-and-conquer pass; that pass is not part
of fusion1.

All per-class CNFs, Kissat logs, decoded witnesses, ILP results, and scheduler
events are under `runs/P25/fusion1/logs/`.  No proof files are retained during
normal SAT search.

## Results

| Class | Engine | Result | Seconds |
|---|---|---|---:|
| `lam=[2, 2, 1, 1] assign=('id', 'id', 'id', 'id')` | SAT | UNDECIDED | 7200.103 |
| `lam=[2, 1, 1, 1, 1] assign=('id', 'tau', 'tau', 'tau', 'tau')` | SAT | UNDECIDED | 7200.105 |
| `lam=[2, 1, 1, 1, 1] assign=('id', 'id', 'tau', 'tau', 'tau')` | SAT | UNDECIDED | 7200.109 |
| `lam=[2, 1, 1, 1, 1] assign=('id', 'id', 'id', 'tau', 'tau')` | SAT | UNDECIDED | 7200.102 |
| `lam=[3, 1, 1, 1] assign=('id', 'sigma', 'sigma', 'sigma')` | PB | UNDECIDED | 7200.130 |
| `lam=[3, 1, 1, 1] assign=('id', 'id', 'sigma', 'sigma')` | PB | UNDECIDED | 7200.134 |
| `lam=[2, 1, 1, 1, 1] assign=('id', 'id', 'id', 'id', 'tau')` | SAT | UNDECIDED | 7200.105 |
| `lam=[2, 1, 1, 1, 1] assign=('id', 'id', 'id', 'id', 'id')` | SAT | UNDECIDED | 7200.110 |
| `lam=[1, 1, 1, 1, 1, 1] assign=('tau', 'tau', 'tau', 'tau', 'tau', 'tau')` | SAT | UNDECIDED | 7200.110 |
| `lam=[1, 1, 1, 1, 1, 1] assign=('sigma', 'sigma', 'sigma', 'sigma', 'sigma', 'sigma')` | SAT | UNDECIDED | 7200.108 |
| `lam=[3, 1, 1, 1] assign=('id', 'id', 'id', 'sigma')` | PB | UNDECIDED | 7200.120 |
| `lam=[2, 2, 2] assign=('id', 'id', 'id')` | PB | UNDECIDED | 7200.127 |
| `lam=[3, 1, 1, 1] assign=('id', 'sigma', 'sigma', 'sigma')` | ILP | UNDECIDED | 14400.019 |
| `lam=[3, 1, 1, 1] assign=('id', 'id', 'sigma', 'sigma')` | ILP | UNDECIDED | 14400.022 |

The initial two-class PB wave and initial two-class ILP wave both completed. No SAT/FEASIBLE-at-72 or UNSAT result occurred; no DRAT confirmation pass was required. The scheduler advanced to subsequent classes.

## Focused cube-and-conquer: sigma^6

The blanket scheduler was stopped before starting the focused attack on
`lam=[1,1,1,1,1,1]`, `assign=('sigma',)*6`.  Code inspection and exhaustive
action checks confirm that sigma is translation by the all-ones vector, with
243 size-3 cosets and no fixed points.  The quotient ball incidence matrix has
243 rows and columns, every row and column sum equal to 13, and the exact LP
minimum is `243/13 = 18.6923076923` orbits.  Thus the integer counting bound
is 19 orbits, well below the target of 24.

Translation by every ternary vector was checked to permute the cosets, and
random invariant covers remained covers after every tested translation.
Therefore fixing the zero coset (words `000000`, `111111`, `222222`) is
valid.  Coordinate-permutation commutation and zero-coset preservation were
also exhaustively checked.  No S6 lex-leader constraints were added because
they were not needed for the initial cheap symmetry break; a 120-second
target-77 fixed-zero-coset SAT/ILP sanity attempt remained undecided.

The focused CNF fixes orbit variable 1 true and uses a pure at-most-24
cardinality constraint.  Ten equally high-occurrence orbit variables were
selected for the initial cube (`x2` through `x11`), producing 1024 cubes.
The run launched with eight Kissat workers and 600 seconds per cube under
`logs/cube_sigma_10/`.  At launch: total 1024, refuted 0, SAT 0, pending
1024; the first eight cubes were active and no cube had resolved after the
initial few minutes.

The negative-split run was subsequently killed.  The replacement positive
tree has 2160 cheap group maps (the 3 translations in the subgroup times all
720 coordinate permutations).  At depth 4 it generated 3125 cubes from 3497
tree nodes, with 1340 symmetry duplicates removed and no cardinality or
covering-bound prunes at that depth.  A target-77 validation run on the first
eight depth-4 cubes was stopped after roughly 7 minutes: all eight timed out,
with zero refutations and zero SAT witnesses.  This is not treated as an
encoding failure: the class is unresolved by design, and its invariant
minimum may exceed 77.  Cube-and-conquer was dropped rather than spending
further blanket time.

## Final run record

The reverse-order fusion1 attack deliberately complements the original
session: the original session owns the front of the sorted undecided list,
while fusion1 attacks from the back.  No result below changed the global
72-word bound.  All listed bounded runs were `UNDECIDED`; no 72-word witness
and no infeasibility proof was obtained.

| Class | Engine | Budget | Result |
|---|---|---:|---|
| `[3,1,1,1]`, `('id','sigma','sigma','sigma')` | SAT | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','id','sigma','sigma')` | SAT | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','id','id','sigma')` | SAT | 2h | UNDECIDED |
| `[2,2,2]`, `('id','id','id')` | SAT | 2h | UNDECIDED |
| `[2,2,1,1]`, `('id','id','tau','tau')` | SAT | 2h | UNDECIDED |
| `[2,2,1,1]`, `('id','id','id','tau')` | SAT | 2h | UNDECIDED |
| `[2,2,1,1]`, `('id','id','id','id')` | SAT | 2h | UNDECIDED |
| `[2,1,1,1,1]`, `('id','tau','tau','tau','tau')` | SAT | 2h | UNDECIDED |
| `[2,1,1,1,1]`, `('id','id','tau','tau','tau')` | SAT | 2h | UNDECIDED |
| `[2,1,1,1,1]`, `('id','id','id','tau','tau')` | SAT | 2h | UNDECIDED |
| `[2,1,1,1,1]`, `('id','id','id','id','tau')` | SAT | 2h | UNDECIDED |
| `[2,1,1,1,1]`, `('id','id','id','id','id')` | SAT | 2h | UNDECIDED |
| `[1,1,1,1,1,1]`, `('tau',)*6` | SAT | 2h | UNDECIDED |
| `[1,1,1,1,1,1]`, `('sigma',)*6` | SAT | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','sigma','sigma','sigma')` | PB | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','id','sigma','sigma')` | PB | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','id','id','sigma')` | PB | 2h | UNDECIDED |
| `[2,2,2]`, `('id','id','id')` | PB | 2h | UNDECIDED |
| `[3,1,1,1]`, `('id','sigma','sigma','sigma')` | ILP | 4h | UNDECIDED |
| `[3,1,1,1]`, `('id','id','sigma','sigma')` | ILP | 4h | UNDECIDED |
| `[1,1,1,1,1,1]`, `('sigma',)*6` | negative cubes | 600s × 8 | UNDECIDED |
| `[1,1,1,1,1,1]`, `('sigma',)*6` | positive cubes | 600s × 8 | UNDECIDED |

Tooling completed: orbit SAT with capped totalizer and DRAT-on-demand,
RoundingSat native PB, HiGHS orbit ILP, and two cube harnesses (negative
literal cubes and positive canonicalized branching).  Validation included
target-56 UNSAT, target-77 SAT/decode verification on the earlier `[6],tau`
class, and the independent verified 76-word ILP cross-check.

The original front-runner should continue its front-order ILP work over the
22 classes still marked `UNDECIDED` in the v1 feasibility logs, excluding any
future decisive results.  Recommended next approaches are LMT-style
isomorph-free branch-and-bound, deeper canonicalized positive cubes with
stronger propagation, or distributing per-class budgets across a cluster.
The sigma^6 quotient minimization below is the final focused attempt in this
run.  The launcher log contains 14 distinct full-budget SAT classes (the
earlier planning note said 12; the table above is the authoritative
per-class record).

## Final quotient minimization

HiGHS minimized the 243-variable quotient model with the zero orbit fixed,
eight threads, zero MIP gap, and a 10800-second wall limit:

```text
status=HighsModelStatus.kTimeLimit
elapsed=10800.063
objective=26.000000000000465
dual_bound=24.0
```

Thus it found an incumbent of 26 quotient orbits (78 words), with a dual
bound of 24.0.  This does not eliminate 72: a dual bound of at least 24.01
would have been needed to prove an optimum above 24, and no 72-word witness
was found.  The sigma^6 class remains unresolved.
