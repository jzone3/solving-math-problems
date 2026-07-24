# P16 childL — session notes (Conjecture J attack)

**Bottom line: PROOF INCOMPLETE, no counterexample.** Rigorous content in
`PROOF_J.md`. Headlines:

1. **Clause (b) collapsed to a single-edge inequality** (Theorem L1):
   (b) ⇔ (B): heavy e (z1_e > ρ₀(e)) satisfies ρ₀(e)(s_e−3)+3z1_e−zs_e > 0,
   plus the boundary case (W=): z1_e = ρ₀(e) ⇒ w_e ≤ 0. Equivalent "excess
   contraction" form Σ_{f∼e}(z1_f−ρ) < z1_e−ρ via the new identity
   Σ_{f∼e} z1_f = zs_e − 2z1_e; equivalently U_e(ρ) > −3, i.e. c = −3
   passes every HEAVY test (only the light half of c = −3 ever fails).
   Verified: all connected n ≤ 9, trees ≤ 16, hard sets, 400 random n ≤ 60;
   min margin exactly 1, attained at near-3-regular graphs with arg44
   constant (=14) on the 2-ball. (B) itself remains unproved.
2. **Parent's suggested s_f = 2 reduction is FALSE** (T₂-center gives −1);
   the correct floor is s_f ≥ 3 (no K₂ edge in connected n ≥ 3). Do not
   repeat this.
3. **Clause (a) proved over the pool tuple universe** (Theorem L2): an exact
   cross-graph scan of all (light, heavy) 2-ball tuples from 93k graphs
   (n ≤ 8, trees ≤ 17, hard sets — ~2·10⁸ pairs) finds EXACTLY ONE
   admissible-window conflict: childJ's T₁-pendant (3,4,21,ρ₀=14) vs
   T₂-center (7,19,109,ρ₀=14). **Lemma X (proved):** any connected graph
   containing the light tuple with ρ₀ ≤ 14 is T₁ itself — and T₁ has no
   heavy edge. So the unique conflict is unrealizable; clause (a) holds for
   every pair whose tuples appear in the pool. This is the T₁/T₂ exclusion
   mechanism, formalized.

## Also established / negative results

- 1-ball version of (B) is FALSE (`G?`acK`, margin −2/3): 2-ball minimal
  even for clause (b).
- Per-neighbor excess bounds, the ρ-cancelling uniform first-shell
  multiplier certificate, and LPs over natural slack features all FAIL for
  (B) (details PROOF_J §5) — the mechanism is not linear in local slacks.
- Degree truncation for parametric work: arg44_g ≥ (s_g−2)²/2 − 2(s_g−2)
  (uses m ≥ 1), so arg44 ≤ ρ bounds all 2-ball degrees by O(√ρ).

## Pitfalls for successors

- `nauty-gentreeg` outputs sparse6 (`:...`), not graph6 — `common.py` here
  parses both (childJ's common.py did too; don't reuse childE's).
- When minimizing q_{e,f}(ρ) over the window, check the interior stationary
  point (leading coeff s_e−s_f can make the min interior).
- Keep every scan in exact Fractions; the conflict margins (−5) and tight
  (B) margins (1) are small integers, and float tol 1e−6 pre-filtering is
  fine only with exact recheck.
- Don't launch two scans appending to one log (early cl_b_n9.log confusion).

## Route map (ranked)

1. Prove (B). Target the margin conjecture D_e ≥ 1; tight cases are
   near-3-regular with arg44-constant 2-balls — try an exchange/perturbation
   argument around regular graphs, or an integer-programming duality on the
   2-ball degree data. All the reformulations are in PROOF_J §3.
2. Prove (W=) (childJ V1 at ρ = z1 = ρ₀) — likely the easier Lemma-P-style
   bounded bash.
3. Clause (a) parametric: enumerate abstract realizable tuples with the
   O(√ρ) degree bound and generalize Lemma X's pinning argument: a light
   edge with ψ_f(ρ) > −3 pins its neighborhood so hard that no heavy edge
   coexists. The pool scan (1 conflict in 2·10⁸) says this is the truth;
   Lemma X is the template proof.

**PROOF NOT COMPLETE. Conjecture J stands; clause (b) is now one
inequality, clause (a) is done over everything ever observed.**
