# childN session notes

**Headline: (B), clause (b), Conjecture J, and Conjecture H are ALL FALSE.**
See `PROOF_B.md`.  Run `python3 verify_counterexamples.py` for the exact,
self-contained verification of both counterexample trees (T40, T52).

Chronology of the session:

1. exp1–exp8: reproduced baselines; explored η-contraction and multiplier
   certificates for (B)/(W=).  The multiplier certificate Q(ρ) (first-shell
   slack cancellation, `exp9_symbolic.py`: m_k-dependence cancels exactly)
   was always negative on real graphs but has a huge abstract exceptional set
   (`exp10b_fast_scan.py`).
2. exp11/exp11b: 2-shell abstract relaxation of (B) — float adversary showed
   "violations" at (4,3),(4,4,4),(1,4); at first these looked like relaxation
   artifacts fixed by integrality (t·m_k ∈ ℤ).
3. exp12 (1-ball, exact integrality): abstract w > 0 configs appear at
   (4,3),(5,5,5),(1,3) — realized as an n = 35 tree, **falsifying W1B**
   ("z1 ≥ ρ₁ ⇒ w ≤ 0"), previously verified true on all small cases.
4. exp14 (full 2-shell exact adversary): config (5,3),(5,5,5,5),(1,3) with
   w = 4 and all 2-ball arg44 < z1 → realized as the n = 52 tree T52 →
   **(B) and clause (b) falsified** (D_e = −22/5).
5. exp17 (minimization over the tree family): (4,3),(4,4,4),(1,4) with
   w = 0 → the n = 40 tree T40 (D_e = −3/2).  On T40 the global R equals
   ρ₀(e) = 197/8 < z1_e = 25, and the H-interval is [−76/39, −7] with
   c > −3 required → **Conjecture H falsified**.  Bound 44 still holds on
   both trees.
6. exp18/exp15/exp16/verify_counterexamples: exact verification, three
   independent implementations; r-ball scan (T40 kills every radius r ≥ 2
   simultaneously since ρ_r = R for all r).
7. exp20: 60k random skewed trees n ≤ 39 — no random H-counterexample; the
   structure is delicate (tuned to leave slack 3/8 below z1).

Key mechanism ("pad just beyond the horizon"): second-shell children get
leaf padding; the padding edges lie outside B₂(e) so their arg44 never enters
ρ₀(e), letting the adversary inflate zs_e (hence w_e) while keeping the 2-ball
quiet.  T40 goes further: the *whole graph* is quiet (R = ρ₀), which is what
kills the global certificate v = s + c·1 (needs c ≤ −7, positivity needs
c > −3).

Open ends:
- (W=) at exact equality z1 = ρ₀: no realized violation yet (moot for J).
- True minimal counterexamples: somewhere in 11…40 vertices (19…40 for trees).
- Bound 44 remains open and true on all tests; next certificates to try are
  listed in PROOF_B.md §5.
