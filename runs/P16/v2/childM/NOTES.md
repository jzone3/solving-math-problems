# P16 childM — Conjecture F2″ (capped σ̂): survives all adversarial attack; exact theorems on every known risk family; h = d route refuted for σ̂

Child session of runs/P16-v2 (builds on childF, childI, childK). Task: stress-test and
try to prove **Conjecture F2″**: with σ̂ᵢ := dᵢ − 4 + min(mᵢ, dᵢ + c), c ∈ {2, 4},
M(σ̂) = 2 diag(σ̂) + 4I − Q − diag(σ̂) H diag(σ̂) ⪰ 0 for every connected δ≥2 graph
(childF/childK notation; F2″ ⇒ D1 ⇒ Bound 46, δ≥2, via Theorem F3).

**OUTCOME: F2″ remains unproved in general but is now MUCH stronger:**
1. **No counterexample** after targeted hub-heavy stress (2,770 graphs n≈11–101,
   the exact regime that killed F2) + simulated-annealing adversarial min-eig descent
   (~500 restarts, n ∈ {12,15,20,25,31,40,45,60}, both caps): all clean.
2. **Theorem M1/M3 (proved, sympy exact): F2″ holds on hub + k copies of ANY connected
   g-regular gadget on L vertices** — simultaneously in (k·L, L, g), both caps, in the
   capped regime; this covers ALL of childK's F2-killing families (windmills F_k,
   wheels W_n, hub+kC₄, hub+kC₅, hub+kK₃/K₄, k=1 "single big gadget" included) exactly.
3. **Theorem M2 (proved, sympy exact): F2″ holds on every semiregular bipartite δ≥2
   graph, including arbitrarily skew ones where one side is capped** (childI's T1 does
   NOT carry over verbatim there — σ̂ ≠ σ on the skew side; this needed a new proof).
4. **The parent's suggested h = d Collatz–Wielandt route is REFUTED for σ̂** (sharp
   negative result with mechanism, §4): capping shrinks T = 2σ̂+4 at low-degree
   vertices next to hubs while (Qd)ᵢ = dᵢ(dᵢ+mᵢ) is unchanged, so ρ₀ = max (Bd)ᵢ/(Tᵢdᵢ)
   ~ k/8 → ∞ on windmills. h = d fails on MORE graphs than for old σ
   (n=9: 24,410 (c=4) / 120,426 (c=2) vs 23,721 (old) of 197,772).
5. **The resolvent window (childI I2, I4–I7, valid for any diagonal) works for σ̂ with an
   adaptive sound α**: certificate verified with ZERO failures exhaustively on all
   205,797 δ≥2 graphs n ≤ 9 (both caps) and on all hub families to n = 1201, with the
   sound α-grid needing ≤ 7 bisection steps below min(1, 1/ρ_K). childI's FIXED
   κ = 0.99/ρ₀ recipe fails badly on large windmills (ρ₀ → ∞ makes α → 0); the
   repaired recipe is α = (1 − 2⁻ʲ)·min(1, 1/ρ_K) with ρ_K the order-K power CW bound.

## 1. Setup and degenerate-edge convention (parent's check request)

`common.py` builds M(s) for any diagonal (bit-compatible with childI/childF; `sanity.py`
reproduces childK exactly: F_13 min-eig +1.027, F_14 −0.1453 for old σ; n ≤ 8 both caps
worst −2.8e−15, 8,025 graphs, 0 failures).

**Degenerate edges are safe for σ̂ (Corollary F1′ extends to every cap c ≥ 0).**
By Lemma F1, arg46 = 4 on an edge iff d = m = 2 at both ends; there
σ̂ = 2 − 4 + min(2, 2+c) = 0. So the w := 0 convention on degenerate edges kills every
occurrence of σ̂ exactly as in childF's F1′, and Theorem F3 (M(σ̂) ⪰ 0 ⇒ D1, δ≥2)
applies verbatim to the capped diagonal. Machine-checked on all 8,025 graphs n ≤ 8
(`sanity.py`: every zero-weight edge has σ̂ = 0 at both ends, both caps).

## 2. Stress tests (no counterexample anywhere)

- `hub_stress.py` / hub_stress.log — 2,770 graphs, both caps: single hub + all random
  mixtures of gadgets {K3, C4, C5, C6, P3, P4, K4} (n up to ~80); two hubs sharing
  gadgets (± hub–hub edge); hub joined to all/random subsets of random d-regular blocks
  (d = 3..6, up to n = 61); two bridged hubs with separate gadget sets; skew K_{a,b}
  plus hub into small/big/both sides (up to n = 103); windmills glued to regular blocks.
  **0 failures**; worst margins ≈ +0.035 (hub + 6-regular partial), everything else ≥ 0.04.
- `adversarial.py` / adv*_*.log — simulated-annealing descent on min-eig over edge flips
  (connected, δ≥2 preserved; random/hub/windmill starts; 1,500 flips per restart; exact
  Fraction recheck wired for any negative — never triggered). Best (i.e. most adversarial)
  min-eig found: +0.008 (n = 15), +0.014 (n = 20), +0.030 (n = 25), +0.048 (n = 31),
  +0.104 (n = 45), +0.19 (n = 60); the descent lands on the near-equality manifold, never
  below 0. **No counterexample, both caps.**
- childK already had exhaustive n ≤ 10 (all 10,013,006 δ≥2 graphs, both caps, 0 failures).

## 3. Exact theorems (new; all sympy-verified, float cross-checked)

**Theorem M1 (`windmill_proof.py`).** M(σ̂)(F_k) ⪰ 0 for ALL k ≥ 2, both caps.
Proof: S_k×Z₂ equitable decomposition (λ_antisym, λ_sym-zero-sum, 2×2 hub block);
each closed-form eigenvalue is a rational function whose shifted numerator/denominator
(k = t + c + 1) has nonnegative coefficients; decomposition matches full float spectrum
at k = c+1, 10, 25; small k (cap inactive) checked in exact rational LDL.

**Theorem M2 (`bipartite_proof.py`).** M(σ̂) ⪰ 0 on every connected semiregular bipartite
δ≥2 graph (degrees p ≥ q ≥ 2), both caps. Via biadjacency SVD, PSD ⟺ t_A, t_B ≥ 0 and
t_At_B ≥ γ²pq (γ = 1 + σ̂_Aσ̂_B w, μ_max = √(pq)). Capped case p = q + c + r (r ≥ 1):
all three conditions have coefficient-positive numerators/denominators after
q = u+2, r = v+1. Uncapped p − q ≤ c re-proved the same way (T1 check). Note K_{2,100}-type
skew graphs cap the SMALL-degree side; this case is genuinely new relative to childI T1.

**Theorem M3 (`hub_gadget_proof.py`, `decomp_check.py`).** Let G = one hub joined to all
vertices of k ≥ 1 disjoint copies of ANY connected g-regular gadget on L vertices
(g ≥ 1, L ≥ g + 1). In the capped regime kL ≥ (g+1)(c+1) (⟺ m_o ≥ d_o + c):
M(σ̂)(G) ⪰ 0, both caps — proved simultaneously in ALL of (K = kL, L, g) by
coefficient positivity of λ(−g), M_hh, det₂ under K = (2+u)(c+1)+t, g = 1+u, L = 2+u+v,
using that λ(ν) is linear in ν with |ν| ≤ g and λ(+g) = (det₂ + kL·M_ho²)/M_hh.
Since k = 1 is allowed, this includes wheels W_n (hub + C_{n−1}) and every
"hub + one/many big regular gadget(s)" family; with g = 1, L = 2 it re-derives M1's
capped case. Concrete gadgets (K2, C4, C5, C6, K4, K5) verified numerically for all
k = 2..25 including uncapped small k; decomposition verified against full spectra.

Every family childK listed as breaking F2 (windmills, wheels, hub+kC₄/C₅/K₃) is
therefore now covered by an EXACT positive theorem for F2″.

## 4. h = d route refuted for σ̂ (parent task 2)

The hoped-for "cap makes per-edge deficiency O(1) ⇒ h = d works" is FALSE, for a reason
orthogonal to the DHD term: with h = d the CW condition at vertex i reads
dᵢ(dᵢ+mᵢ) + σ̂ᵢ Σ_j w_ij(σ̂ᵢdᵢ + σ̂ⱼdⱼ) ≤ (2σ̂ᵢ+4)dᵢ. On a capped vertex (mᵢ > dᵢ + c)
the LHS keeps the full (Qd)ᵢ = dᵢ(dᵢ+mᵢ) (a degree-2 vertex adjacent to a hub of degree
2k has (Qd)ᵢ ≈ 2k) while the cap REDUCES the RHS to (2c+4)·2 = O(1). So
ρ₀ = max (Bd)ᵢ/(Tᵢdᵢ) ≈ (k+3)/(2c+4) → ∞ on windmills (measured: 2.26 at F_14 c=2,
19.25 at F_150), and h = d fails at every capped outer vertex. Exhaustive residue
(`cw_residue.py`, cw8/cw9.log): n = 9 h=d failures 23,721 (old σ) → 24,410 (c=4) →
120,426 (c=2). The capping strictly ENLARGES the h = d residue; any proof of F2″ must be
higher-order (resolvent) or use an h that dampens capped vertices (the exact Perron h on
F_k has h_hub/h_out → const ≈ 3.3 (c=2)/4.9 (c=4) while d_hub/d_out = k → ∞; bounded by
h_hub ≤ (T_out − d_out)h_out locally, so no d-proportional h can work).

## 5. Resolvent window with σ̂ (parent task 3) — repaired sound certificate

All childI lemmas I2, I4–I7 hold for any diagonal (only B ≥ 0, T > 0 used); so
F2″ ⟺ α*(G)·ρ(P) < 1 with P = diag(T)⁻¹B, T = 2σ̂+4, B = Q + ŜHŜ.

- ρ(P) on hub families stays FAR from 1 (F_k: ρ → 0.887 (c=2)/0.846 (c=4); all hub+gadget
  families ≤ 0.89): the cap fixes the spectrum globally even though first-order CW bounds
  explode. The risk region for the window is (as for old σ) the near-equality manifold,
  NOT hubs.
- childI's fixed sound recipe α = 0.99/max(ρ₀,1) FAILS for σ̂ on large hub families
  (`cw_residue.py`, `soundK.py`: violation +6.8 at F_300 c=2) because ρ₀ → ∞ drives
  α → 0 while the window sits near (α*, 1): the window has moved AWAY from 0 on capped
  families. Replacing ρ₀ by the order-K power bound ρ_K = max (P^{K+1}d)ᵢ/(P^Kd)ᵢ (sound
  for any K; K = 16) fixes all of n ≤ 8 but still misses huge windmills at fixed κ = 0.99.
- **Adaptive sound certificate (`sound_adaptive.py`): α_j = (1 − 2⁻ʲ)·min(1, 1/ρ_K),
  j = 1, 2, …** (sound by I4 for every j since α_jρ < 1; monotone by I6 so a scan is
  exact). Result: **exhaustively certifies ALL 205,797 δ≥2 graphs n ≤ 9 (both caps,
  0 failures, max j = 7)** and all hub families (windmills to k = 600, hub+gadget to
  n = 1201, j ≤ 6). Empirically α*(G)·ρ ≤ 1 − 2⁻⁷ everywhere tested: the window never
  degenerates faster than a fixed constant at n ≤ 9 — but childI's near-equality
  random-regular examples (α*ρ → 1) show no fixed j works asymptotically; the true
  content remains α*ρ < 1.

## 6. What resists (map for the next session)

F2″ on general graphs still needs a proof of α*(G)ρ(G) < 1 for P built from σ̂. What we
know now: (i) hubs are handled — exact theorems on all symmetric hub families, ρ bounded
by ≈ 0.89 there, and adversarial descent cannot push min-eig below 0 even seeding from
hub configurations; (ii) the obstruction is back to where it was for old σ: near-equality
(regular-ish) graphs where ρ ↑ 1 with margin governed by the spectral gap — but there
σ̂ = σ (cap inactive for m ≤ d + c), so childI's entire analysis applies verbatim;
(iii) consequently a clean split emerges:
   **(a) cap-active vertices exist ⇒ conjecturally ρ ≤ 1 − ε uniformly** (all evidence:
   every capped family tested has ρ ≤ 0.9; make this a lemma — e.g. show a capped vertex
   forces slack Tᵢ − (B·h)ᵢ/hᵢ ≥ ε·Tᵢ for the resolvent h and propagate by connectivity);
   **(b) no cap active ⇒ σ̂ = σ AND m ≤ d + c everywhere**, a "locally almost regular"
   class containing the equality manifold, where the deficiency tᵢ ≤ 1 + O(c/d)
   pointwise — attack with childI route-map items 1–2 (Doob transform / total
   deficiency ≤ total surplus flow argument) under the extra hypothesis m ≤ d + c,
   which old-σ analysis never had.
- The naive per-edge split of the K1-type identity fails (`per_edge_scan.py`: violation
  up to 114 at two adjacent hubs with degree-2 fringes); any 1ᵀMd-style global argument
  must route hub surplus non-locally.
- Not attempted: SDP-guided *structural* search beyond edge-flip annealing (e.g. weighted
  continuous relaxations); n = 11 exhaustive (≈ 3·10⁹ graphs, out of scope this session).

## 7. Files

- `common.py` — M(s) builder for any diagonal + gadget/windmill constructors.
- `sanity.py` / sanity.log — childK reproduction + degenerate-edge check (§1).
- `hub_stress.py` / hub_stress.log — §2 stress (2,770 graphs, 0 failures).
- `adversarial.py` / adv_*.log, adv2_*.log — §2 annealing attack (clean).
- `windmill_proof.py` / windmill_proof.log — Theorem M1 (PROVED).
- `bipartite_proof.py` / bipartite_proof.log — Theorem M2 (PROVED).
- `hub_gadget_proof.py` / hub_gadget_proof.log, `decomp_check.py` — Theorem M3 (PROVED).
- `cw_residue.py` / cw8.log, cw9.log — §4 h = d residue for σ̂ vs old σ.
- `soundK.py` / soundK_fam.log, soundK_n8.log — fixed-κ order-K certificate (fails on
  large windmills — motivates the adaptive version).
- `sound_adaptive.py` / adaptive_fam.log, adaptive_n8.log, adaptive_9_*.log — §5 sound
  adaptive certificate: exhaustive n ≤ 9 (205,797 graphs × 2 caps, 0 failures) + families.
- `per_edge_scan.py` / per_edge_scan.log — K1-identity for σ̂ + failed per-edge split (§6).

**Bottom line.** F2″ (both caps) survived every attack aimed at where F2 died: exact
theorems now cover all hub-symmetric families (windmills, wheels, hub + any regular
gadgets, skew semiregular bipartite), adversarial searches find nothing, and the sound
adaptive resolvent certificate is exhaustive-clean through n = 9 on top of childK's
n ≤ 10 PSD verification. The h = d shortcut is definitively dead for σ̂ (worse than for
σ). The remaining open core of Bound 46 (δ≥2) is the window statement α*(G)ρ(G) < 1 for
the capped kernel, now with a concrete two-case split (§6) in which the hub case has
strong evidence of uniform slack and the cap-free case inherits childI's machinery plus
the new hypothesis m ≤ d + c everywhere. NOT a complete proof — PROOF_F2PP.md not written.
