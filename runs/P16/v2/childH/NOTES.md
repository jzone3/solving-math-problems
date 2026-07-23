# P16 childH — session notes (Bound 44, second-order route)

**Bottom line: PROOF INCOMPLETE**, but the dispatched Route 1 conjecture is
now sharply formulated, rigorously reduced, and exhaustively verified:
Bound 44 for ALL graphs ⇐ **Conjecture H** (nonempty c-interval of the
shifted-sum second-order test), verified on all 11,989,762 connected graphs
n ≤ 10 and all 204,994 trees n ≤ 18, with **zero failures**.
Rigorous content in `PROOF44.md`; this file is the experimental log.

## Headline results

1. **Lemma H1** (second-order CW, λ² ≤ max (A_L²y)/y) proved cleanly via
   diag-similarity row sums + symmetry of A_L (ρ(A_L²) = λ² needs Perron:
   λ ≥ |θ| for all eigenvalues θ).
2. **Lemma H1′**: any first-order certificate is inherited by the second-order
   test with the same weight (A_L monotone). This makes the fast scan sound:
   first-order sum (exact interval, childE exp15) as fast path, ord2 fallback.
3. **Lemma H2**: exact expansion of (A_L² (s+c))_e in
   (d, m, P_i = Σ_{k∼i} d_k², W_i = Σ_{k∼i} d_k m_k = (A²d)_i). Per-edge
   condition is LINEAR in c ⇒ exact interval feasibility (Corollary H3),
   same computational shape as childE's first-order criterion, one order up.
4. **Dispatch conjecture confirmed and extended**: shifted-sum weights
   y = s + c pass the second-order test for every connected graph n ≤ 10
   (n=9: 261,080, 8 shards; n=10: 11,716,571, 16 shards, 247 needed the ord2
   fallback, 0 fails) and every tree n ≤ 18 (204,994; childE only reached 14).
   The childE 190-residue and the 8 n≤9 sum-failures all pass.
   NOTE: the dispatch said childE verified ord2 on the 190 with AFFINE-PRODUCT
   weights (exp17); here we verified the SHIFTED-SUM version, which is the one
   with a linear (not quadratic) exact criterion — and it also covers 100%.
5. **Negative results** (kills shortcut hopes): no universal constant c
   (c = −1 fails on 48 graphs n ≤ 8; the intervals of GCdbF? and H?`@f@h touch
   only at c = −2 and other graphs exclude −2); no simple closed-form rule
   (−δ, −min s/2, δ−Δ, … all fail; table in PROOF44 §5). The conjecture is
   irreducibly about interval NONEMPTINESS.
6. **Binding structure** (exp5): on all 198 hard graphs the upper bound comes
   from the max-degree-sum edge (s_e > τ+2) and the lower bound from a
   low-degree edge attached to the dense core. The proof target is the single
   pairwise inequality L_f ≤ U_e for that pair — childE §5(a) one order up.

## Files

- `common.py` — copied from childE (graph6, degrees/m, line graph).
- `exp1_ord2sum.py` — exact linear-in-c ord2-sum feasibility; scan / file modes.
- `exp2_n10.py` — full n=10 scan (ord1 fast path + ord2 fallback); `n10_*.log`.
- `trees_ord2.py` — trees via gentreeg; `trees_ord2.log` (n≤16), `trees17_18.log`.
- `exp3_cvalues.py` — per-graph feasible c-intervals; `exp3.log`.
- `exp4_fixedc.py` — fixed-c universality test (fails; see PROOF44 §5).
- `exp5_binding.py` / `exp5_binding.log` — binding-edge structure on hard graphs.
- `verify_identities.py` — numeric machine-verification of every identity
  (exhaustive n ≤ 7 + 300 random graphs n ≤ 30, several c values incl. near
  the −min s_e boundary and c = 1000).
- `verify_sympy.py` — symbolic verification of the H1 normalization and the
  slope/intercept (σ_e, κ_e) of the linear criterion.
- `exp6_exact_recheck.py` / `exp6.log` — EXACT Fraction-arithmetic recheck of
  ord2-sum feasibility on the 198 hard graphs (190 + 8): all pass, no floats.
- `n9_sumfails.txt` — the 8 childE n≤9 sum-failures (copied from childE NOTES).

## Pitfalls / caveats for successors

- Same off-by-2 trap as childE: ord2 compares against R = τ² = (RHS44−2)²,
  never against RHS44² — `exp1` uses R = max arg44 directly.
- Positivity: c > −min_e s_e (per-graph), not −2δ.
- In the fast path, soundness of skipping ord2 when ord1 holds is Lemma H1′ —
  it needs τ ≥ 0, i.e. R ≥ 0; graphs with R < 0 would be counterexamples to
  Bound 44 itself (λ² ≥ 0) and are reported infeasible, none seen.
- geng shards: `nauty-geng -qc n res/mod` (mod applied only for n ≥ 9/10 in
  the scan scripts); trees: `nauty-gentreeg -q n | nauty-copyg -g`.
- Scans are float64 with 1e−9 tolerances; the 198 known-hard graphs were
  additionally rechecked in exact Fraction arithmetic (exp6, all pass).

## Route map for the next session

1. Prove Conjecture H's pairwise inequality: expand −κ_f/σ_f ≤ −κ_e/σ_e for
   f = binding low-degree edge, e = max-s edge, using Σ_{k∼i} d_k = dᵢmᵢ,
   Σᵢ dᵢmᵢ = Σ_e s_e, and per-edge arg44_e ≤ R to bound P + W at the max-s
   edge. Start with the residue profiles (δ,Δ) ∈ {(2,5),(2,6),(3,6),(3,7)}
   and δ = 1 leaf-heavy class where the binding pair is fully characterized.
2. Or: prove Conjecture H on trees first (bipartite, λ² structure simpler,
   binding data very rigid) as a warm-up theorem worth stating on its own.
3. Exact-arithmetic recheck: done here for the 198 known-hard graphs (exp6,
   all pass in Fraction arithmetic); the ~49 other n=10 fallback graphs (247
   minus the 190; g6 strings not logged) still only have the float check —
   they had ord1-sum near-misses, rerun exp2 with fail-logging if needed.
4. If stuck, ord4 with the same weights gives another exactly-linear criterion
   ((A_L⁴(s+c)) vs R²(s+c)) — untested here for the sum family.

**PROOF NOT COMPLETE. No counterexample. Conjecture H is the target.**
