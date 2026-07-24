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
maintains six SAT workers, and allows up to two concurrent ILP jobs (roughly
eight cores at maximum load).

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
