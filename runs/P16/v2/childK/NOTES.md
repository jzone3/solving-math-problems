# P16 childK — Conjecture F2 is FALSE (windmills); diagonal rescue and the repaired conjecture F2″

Child session of runs/P16-v2 (builds on childF + childI). Task was to PROVE
Conjecture F2 (M(G) ⪰ 0 for connected δ≥2 graphs, childF/childI notation)
via childI's window reformulation Theorem I7.

**OUTCOME: F2 is DISPROVED — exactly, symbolically, with a minimal explicit
counterexample at n = 29 (windmill F_14). See `DISPROOF_F2.md`.**
The n ≤ 10 exhaustive + 4,000-random verification of childF/childI was
misleading: the counterexample family starts at n = 29 and random G(n,p)/BA/
regular scans never produce it. Upstream D1 and Bound 46 SURVIVE on all
failing families (checked directly, large margins) — only the childF
*choice of diagonal* σ = d + m − 4 breaks, not the reduction machinery.
Main deliverables:

1. **Disproof of F2** (`sym_disproof.py`, `exact_witness.py`, exact rational):
   windmill F_k = k triangles sharing a hub violates M ⪰ 0 for ALL k ≥ 14;
   at k = 14 (n = 29) the vector x = 1217/554 on the hub, 1 elsewhere gives
   xᵀMx = −2639/554. Sympy closed form on the symmetric quotient:
   det = −k²(k−1)(k³ − 9k² − 75k + 99)/(4(k² + 4k − 3)), whose cubic factor
   changes sign between k = 13 and 14 (largest root ≈ 13.849). ρ(P(F_k)) → ∞.
   Also fail: wheels W_n (n ≥ 40-ish), hub + kC_4, hub + kC_5, hub + kK_3
   (`family_scan.py`). Consequently childI's Conjecture I1 and the window
   statement α*(G)ρ(G) < 1 are false as well (the window is empty on F_14+:
   `windmill.py` shows R(α) fails for all α on a fine grid once ρ > 1),
   and childI Theorem I7 stands but its hypothesis fails.

2. **Upstream check** (`upstream_check.py` + `upstream.log`): on every failing
   family, K = diag(arg46) − A_L² stays PSD (min eig 14–27, growing in size)
   and Bound 46 holds with large margin. **D1 and Bound 46 remain open and
   unfalsified.** The childD/parent exhaustive D1 range (n ≤ 10) plus these
   families give no counterexample to D1.

3. **Why it fails / mechanism.** Windmill outer vertices have (d, m) = (2, k+1),
   so σ = d + m − 4 ≈ k explodes on degree-2 vertices; the outer–outer edges
   have bounded weight w_o → 1/16, so each contributes ≈ k²/2 to dᵀ(DHD)d-type
   mass while the total surplus 2Σd(d−2) ≈ 8k² is fixed: Lemma K1
   (`k1_identity.py`, exact + machine-verified n ≤ 8):
   1ᵀMd = 2Σ_i d_i(d_i−2) − Σ_e w_e(σ_i+σ_j)(σ_i d_i + σ_j d_j),
   which is ≥ 0 for all 8,025 graphs n ≤ 8 but ≈ −k³/2 → −∞ on windmills.
   (This identity is how the counterexample family was FOUND: the k³ growth
   of the friendship-graph LHS made 1ᵀMd < 0 predictable, then M itself
   goes indefinite slightly later, at k = 14.)

4. **Rescue Theorem K3 (proved, sympy exact; `windmill_rescue_proof.py`).**
   Theorem F3 (childF) allows ANY diagonal. For F_k, k ≥ 4, the diagonal
   s_hub = 4k, s_outer = 4 gives M(s) ⪰ 0: closed-form spectrum
   λ_antisym = 11k³+33k²−79k+27 (mult k), λ_sym0 = (k−1)(7k³+17k²−67k+27)
   (mult k−1), plus a 2×2 hub block with det ∝ 3k⁵+9k⁴−82k³+58k²+55k−27 > 0
   (k ≥ 4); positivity via coefficient-positive shifts, float cross-check
   matches spectrum exactly. So the windmills are deep inside the SDP-feasible
   region {s : M(s) ⪰ 0} — only σ = d+m−4 lies outside it.

5. **Conjecture F2′ (exists-diagonal, SDP form).** ∀ connected δ≥2 G ∃ s ≥ 0:
   M(s) ⪰ 0. Verified: exhaustively n ≤ 7 via the Schur-complement LMI
   (childF §5(ii)) with SCS (`f2prime_sdp.py`, `f2prime_n7.log`; single
   "failure" K4 at −1.1e−6 = solver tolerance at an equality-manifold point
   where the unique feasible s = 2d−4 gives min eig exactly 0); windmills by
   Theorem K3; wheels/hub families by explicit grid diagonals
   (`rescue_scan.py`: margins +5…+7). F2′ ⇒ D1 by Theorem F3 (any D).

6. **Conjecture F2″ (repaired closed form — the new crown statement).**
     σ̂_i := d_i − 4 + min(m_i, d_i + c),   c ∈ {2, 4}
   (cap the neighbor-average at d + c; equals childF's σ whenever m ≤ d + c,
   in particular on regular graphs and n ≤ 8 near-regular ones, preserving
   tightness/equality on the equality manifold of Bound 46). Verification
   (`sigma_scan.py`, `f2cap_check.py`, `f2cap_rand.py`, logs cap*_9_*.log,
   f2cap_rand.log, sigma_scan.log):
   - exhaustive ALL 8,025 δ≥2 graphs n ≤ 8: 0 failures (both caps);
   - exhaustive ALL 197,772 δ≥2 graphs n = 9: 0 failures (both caps);
   - exhaustive n = 10 in progress at time of writing (cap2_10_*.log,
     16-way split; check logs for final status);
   - all windmills/wheels/hub-families incl. large sizes: positive margins;
   - complete bipartite K_{a,b} incl. very skew (2,100): positive;
   - 4,000 random/hybrid graphs to n ≈ 150 (incl. windmill-glued-to-regular
     hybrids, partial hub gadgets, skew bipartite minus matchings): 0 failures.
   F2″ ⇒ F2′ ⇒ D1 ⇒ Bound 46 (δ≥2). Failed closed forms: 2d−4 (2,869
   failures n ≤ 8), min(d+m,2d)−4 (windmills still fail!), d+√(dm)−4,
   2√(d(d−2)), 2d−4+clip(m−d,0,c) (EQjO-family fails) — see sigma_scan.log.

## Files

- `DISPROOF_F2.md` — self-contained disproof write-up (the main artifact).
- `sym_disproof.py` / `sym_disproof.log` — sympy exact quotient disproof +
  exact k = 14 witness (−2639/554).
- `exact_witness.py` / `exact_witness.log` — independent full-matrix rational
  builds, exact negative witnesses k = 16, 17, 18, 25; D1/B46 spot checks.
- `windmill.py`, `family_scan.py`, `graphs.py` — counterexample families;
  minimality (k = 13 PSD, k = 14 not) and other failing families.
- `upstream_check.py` / `upstream.log` — D1 + Bound 46 survive everywhere.
- `k1_identity.py` — Lemma K1 identity (1ᵀMd) + exhaustive n ≤ 8 checks.
- `windmill_rescue_proof.py` / `windmill_rescue.log` — Theorem K3.
- `rescue_scan.py` — grid rescue of wheels/hub families (feasible diagonals).
- `f2prime_sdp.py` / `f2prime_n7.log` — SDP feasibility (F2′) exhaustive n ≤ 7.
- `sigma_scan.py` / `sigma_scan.log` — closed-form σ̂ candidate scan.
- `f2cap_check.py` / cap2_9_*.log, cap4_9_*.log, cap2_10_*.log — exhaustive
  F2″ verification (n = 9 done: 0 failures; n = 10 running).
- `f2cap_rand.py` / `f2cap_rand.log` — random/adversarial F2″ stress.
- `common.py` — thin wrapper importing childI's builder (bit-identical M).

## Route map for the next session

1. Try to prove F2″ (or F2′) on hub-dominated graphs: the cap makes σ̂ ≤ 2d−2+c
   ~ O(d) locally, so the per-edge quantity w_e(σ̂_i+σ̂_j)(σ̂_i d_i+σ̂_j d_j) is
   now bounded by O(1) per edge (check: this is the quantity that exploded).
   A per-vertex Collatz–Wielandt h = d certificate for σ̂ should now fail on
   far fewer graphs — re-run childI's machinery (resolvent window) with σ̂;
   all childI lemmas I2, I4–I7 hold verbatim for ANY diagonal (they only use
   B ≥ 0, T > 0), so the window reformulation is still available.
2. If F2″ fails somewhere exotic: fall back to F2′ (SDP feasibility is convex;
   prove nonemptiness by constructing s via local rules + a fixed-point or
   continuity/interlacing argument; K3's explicit windmill spectrum is a
   template for hub-dominated blocks).
3. n = 10 exhaustive for F2″ cap 2 was launched (16-way); finish/extend to
   cap 4 and to targeted n = 30…60 hub-heavy enumerations (hub + mixed
   gadgets) which are the real risk region, NOT small n.
4. Update childF/childI NOTES + runs/INDEX.md to flag F2 as REFUTED (parent
   session should propagate; this branch only adds childK files).
