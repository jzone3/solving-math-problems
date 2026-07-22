# P15 — Covering system with min modulus >= 43 — run notes (variant V1)

Variant V1: mechanize the Nielsen/Owens prime-by-prime distortion method as
code; reproduce 40/42; machine-optimize hole-covering decisions to push to 43+.

## 0. Statement re-verification (original sources)

* Owens, *A Covering System with Minimum Modulus 42*, BYU MS thesis 2014,
  https://scholarsarchive.byu.edu/etd/4329 (PDF fetched & converted).
  Title/abstract confirm: distinct-moduli covering system, min modulus 42,
  improving Nielsen's 40. Construction uses primes through 89.
* Nielsen, *A covering system whose smallest modulus is 40*, J. Number
  Theory 129 (2009). PDF fetched; confirms 40, primes through 103.
* Balister–Bollobás–Morris–Sahasrabudhe–Tiba (2022, arXiv:2211.01417):
  minimum modulus of any distinct-moduli covering system is <= 616,000.
  So the target (>= 43) is *constructive frontier*, not impossibility.
* Literature check (Exa, July 2026): no published construction beating 42
  found. Problem statement in problems/P15-covering-min-modulus.md matches
  the original sources: finite set of residue classes a_i (mod n_i), n_i
  distinct, n_i >= 43, union = Z. Record to beat: 42 (Owens 2014).

## 1. Verifier

`solutions/P15/verify.py` — standalone, stdlib-only. Checks: n_i distinct,
n_i >= claimed min modulus, min modulus >= target, exact cover of Z via
CRT-structured recursive splitting (plus 20k-sample randomized pre-check,
fixed seed). Prints PASS/FAIL. This is the sole arbiter for any claim.

## 2. Feasibility (reciprocal budget)

`feasibility.py`: with primes up to P and all moduli M <= n (n smooth),
the usable reciprocal mass sum_{n>=M, n P-smooth} 1/n = prod p/(p-1) -
sum_{d<M} 1/d. For M=43, primes <= 89: total ~3.9 vs the 1.0 needed —
measure is NOT the obstruction; the obstruction is combinatorial (the
level-1 "ban" on small moduli in each prime direction, i.e. the top of
the tree where only primes 2,3,5,7 provide cheap structure).

## 3. Small-M ground truth (finite-LCM exact search)

`finite_cover.py`: exact backtracking cover of Z_N with distinct divisors
of N that are >= M (max-gain residue choice, reciprocal-sum prune).
Verified witnesses (runs/P15/v1/witnesses_small/, all PASS verify.py):

| M | N     | congruences | nodes | time |
|---|-------|-------------|-------|------|
| 3 | 120   | 14          | 15    | 0.0s |
| 4 | 2520  | 29          | 30    | 0.1s |
| 5 | 10080 | 46          | 47    | 0.5s |
| 6 | 10080 | 64          | 65    | 0.5s |

M=7 at N=10080: no cover found in 600s (645,866 nodes) — fixed-N search
stops scaling immediately; N must grow with M and the search space
explodes. Dead end for reaching 40+; kept as ground-truth generator.

## 4. Mechanized construction engines (the main V1 effort)

Three generations, all under runs/P15/v1/:

* `engine.py` — direct recursive up-arrow engine (emit / finitize /
  split-by-prime). Too slow, uncontrolled recursion. Dead end.
* `greedy.py` — global priority-queue hole filling with generalized
  divisor-chain finitization. CPU-bound in divisor-chain search; did not
  complete. Dead end (profiling data in session logs).
* `builder.py` — the serious attempt: explicit congruence emitter with a
  global distinct-modulus registry. cover_class(r,m) either (a) emits a
  divisor modulus d | m, d >= M (with budgeted measure overshoot beta),
  (b) runs a q^-chain: at level k the q-1 sibling slots mod m*q^k are
  covered recursively, one class descends; chain bottoms are closed by
  Nielsen-style finitization (fresh prime Q, divisor chain d_1..d_Q of
  the bottom modulus, budgeted waste), or (c) closes deep slots directly
  by finitization. Factorizations are threaded through the recursion so
  divisor sets of astronomically deep chain bottoms remain computable.

Iterations & fixes logged: float overflow at m>1e308 (integerized waste
checks); duplicate-radical chain contention (2^k vs 2^k collisions);
primorial-drift (nested trees accumulating all small primes, killing
finitization); sibling contention (all q-1 siblings at a level sharing
modulus m*q^k, only one can take the exact divisor). Each fix moved the
failure deeper but the systemic issue remains: contention is resolved by
escalation (bigger tree primes, deeper nesting) rather than global
optimization, which inflates congruence counts multiplicatively.

FINAL builder outcome: even M=6 does not converge (3M-congruence cap,
~620k direct emits + 290k finitizations, 4.4k trees, 900s). The
registry-greedy recursive design is a NEGATIVE result: without
Owens-style cross-hole set sharing (one set description covering slots
in several holes at once), per-slot contention makes the congruence
count blow up long before the measure or reciprocal budget is at risk.
Any follow-up should implement set descriptions as first-class shared
objects (the pool/ledger model of Section 5) rather than per-slot
emission.

## 5. The 42 -> 43 surgery plan (worked out, not executed)

Analysis of Owens's thesis (done by hand against the PDF): the ONLY
modulus < 43 in his system is a single congruence with modulus exactly
42 = 2*3*7 (the "2" component of the set 3(2,4,3^(1,2)) in the third
input of the 7^ filling the 8- and 16-holes, at 7-level 1). Its removal
uncovers exactly one class R (mod 42). All later "x"-reductions in the
thesis that cite this set cite subsets of R, so re-covering R exactly
keeps every downstream ledger valid. Owens used only primes <= 89, so
97, 101, 103 (and everything above) are entirely fresh: every modulus in
a 97-adic tree over R (d * p^j * 97^k, d | 42, p <= 89) is unused and
>= 97. A pool/ledger estimate (atoms = 8 divisors of 42; gadget primes
2..89 with costs c_p ~ p-1, each usable once per direction with disjoint
inputs) gives a pool of ~57-95 sets vs the 96 needed for a single 97^;
splitting R into two subholes (97-tree + 101-tree) or cascading a second
fresh prime over the shortfall slots clears the bar in the estimate.
STATUS of this line: promising, unproven. It requires a full transcription
of Owens Ch. 3 (plus the Nielsen tables it inherits) into explicit
congruences to make the witness explicit and machine-verifiable; that
transcription (hundreds of set descriptions, residues only partially
pinned down by the prose) did not fit in this session.

## 6. Compute spent (approx)

* finite_cover: ~25 min CPU total (M=3..7).
* engine/greedy: ~1 h CPU (terminated, no output artifacts).
* builder iterations: ~2.5 h CPU across ~8 runs (cong-cap 3M hit twice,
  depth-cap hit twice, several 600s timeouts).

## 7. STATUS

STATUS: negative (for min modulus >= 43); verified explicit covers with
min modulus 3,4,5,6 produced by the machine (finite-LCM search, all
PASS verify.py); the recursive registry-greedy builder does not converge
(documented dead end); best documented path to 43 is the Owens-42-class
surgery with fresh primes 97/101 (Section 5), which needs a faithful
Owens Ch.3 transcription as its remaining step.
