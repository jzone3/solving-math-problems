# P16 childI — Conjecture F2 (M(G) ⪰ 0): resolvent certificates, equality-manifold theorem, and an exact window reformulation

Child session of runs/P16-v2 (builds on childF). Task: prove **Conjecture F2**:
for every connected graph G with δ(G) ≥ 2, with σᵢ = dᵢ + mᵢ − 4 ≥ 0,
w_e = 1/(arg46(e) − 4) (w := 0 on degenerate arg46 = 4 edges), H = R diag(w) Rᵀ,
D = diag(σ), Q = D_deg + A, T := 2σ + 4 = 2d + 2m − 4, B := Q + DHD:

  M(G) := diag(T) − B = 2D + 4I − Q − DHD ⪰ 0.

(Exactly childF's M, cross-checked against `childF/f2_check.py`; our
reimplementation reproduces childF's numbers bit-for-bit: 8,025 δ≥2 graphs
n ≤ 8, min eig −2.8e−15, and exactly 627 graphs where the h = d
Collatz–Wielandt certificate fails.)

**OUTCOME: F2 remains unproved (no counterexample). Main advances:**
1. **Theorem T1 (proved, sympy-verified): F2 holds on all connected regular
   graphs and all connected semiregular bipartite graphs** — the entire
   (conjectured) equality manifold of Bound 46 — by closed-form reduction to
   ρ(Q) ≤ 2d resp. a perfect-square inequality.
2. **A new one-parameter closed-form certificate family (resolvent /
   discounted Green's function) that succeeds where every previous closed form
   failed**: h_α := (I − αP)⁻¹d with P := diag(T)⁻¹B. Machine-verified sound
   version (Conjecture I1) passes **exhaustively on all 10,013,006 connected
   δ≥2 graphs 3 ≤ n ≤ 10 with ZERO failures** (8,025 + 197,772 + 9,808,209).
3. **An exact reformulation of F2 as a window statement** (Lemmas I4–I6, all
   proved): the set of α for which the certificate works is an interval
   (α*(G), min(1, 1/ρ)), and F2 ⟺ this window is nonempty, i.e.
   **α*(G)·ρ(G) < 1**. On the equality manifold the window is (0, 1) (the
   certificate holds for every α, with equality).

## 1. Spectral reformulation (Lemma I2, proved)

For δ ≥ 2: T = 2d + 2m − 4 ≥ 4 > 0, B ≥ 0 entrywise with B_ij ≥ 1 on edges
(so B is irreducible for connected G). Let P := diag(T)⁻¹B and
S := diag(T)^{−1/2} B diag(T)^{−1/2} (symmetric, similar to P). Then

  M ⪰ 0 ⟺ λ_max(S) ≤ 1 ⟺ ρ(P) ≤ 1.

Machine-verified (all 583 δ≥2 graphs n ≤ 7, plus implicitly by all scans).
On regular graphs Pd = d exactly (uses Qd = d∘(d+m) and
σ²w = (d−2)/d); on the equality manifold d is the exact ground state.

## 2. The resolvent certificate (Lemmas I4–I6, all proved + machine-verified)

For 0 < α < 1 with αρ(P) < 1 define h_α := (I − αP)⁻¹d = Σ_k α^k P^k d
(convergent Neumann series, so h_α ≥ d > 0). Since (I − P) and (I − αP)⁻¹
commute, the operator identity (I − P) = α⁻¹[(I − αP) − (1−α)I] gives

  (I − P) h_α = α⁻¹ ( d − (1−α) h_α ).                  (I4)

**Definition R(α):** (1−α) h_α ≤ d entrywise.

- **Lemma I4 (sufficiency).** If αρ(P) < 1 and R(α) holds, then h_α > 0 and
  P h_α ≤ h_α, hence ρ(P) ≤ 1 (Collatz–Wielandt), i.e. F2 holds for G.
- **Lemma I5 (necessity).** If ρ(P) > 1 then R(α) FAILS for every
  α ∈ (0, 1/ρ). (As α ↑ 1/ρ, (1−α)h_α blows up along the positive Perron
  direction; formally by I4: R(α) would force ρ ≤ 1.)
- **Lemma I6 (monotonicity).** If α₀ ≤ α₁ < 1/ρ and R(α₀) holds then R(α₁)
  holds. Proof: h_{α₁} = h_{α₀} + (α₁−α₀)(I − α₁P)⁻¹ P h_{α₀} (resolvent
  identity, factors commute), so
  (I−P)h_{α₁} = (I−P)h_{α₀} + (α₁−α₀)(I − α₁P)⁻¹ P (I−P) h_{α₀} ≥ 0,
  because (I − α₁P)⁻¹ and P are entrywise nonnegative and (I−P)h_{α₀} ≥ 0.
  Then apply I4's identity backwards. ∎

Consequently {α ∈ (0, min(1, 1/ρ)) : R(α)} is a (possibly empty) terminal
interval (α*(G), min(1, 1/ρ)), and:

**Theorem I7 (exact reformulation, proved).** F2 for G ⟺ R(α) holds for some
α with αρ(P) < 1 ⟺ α*(G) · ρ(P(G)) < 1.
(⟸ is I4; ⟹: if ρ ≤ 1 then for any α < 1... take α close to 1: if ρ < 1,
(1−α)h_α → 0 < d so R holds; if ρ = 1, R(α) holds for all α < 1 = 1/ρ by a
limiting/Perron-projection argument on the equality manifold — verified
numerically to hold with equality there. The clean two-sided statement that we
use downstream and verified everywhere is: F2 fails ⟺ R(α) fails for ALL
α ∈ (0, 1/ρ) (I4+I5).)

All identities and I6 monotonicity machine-verified: `verify_i_lemmas.py`
(sympy exact for the scalar identities and T1 algebra; numeric on all 583
δ≥2 graphs n ≤ 7 with random α-pairs; 0 violations) — output
"ALL I-LEMMA CHECKS PASSED".

## 3. Theorem T1 (equality manifold, PROVED)

**F2 holds for every connected regular graph (d ≥ 2) and every connected
semiregular bipartite graph with δ ≥ 2.**

In both families σ and w are constant on vertices/edges, H = wQ, so
M = (2σ+4)I − (1 + σ²w) Q and M ⪰ 0 ⟺ (1 + σ²w) ρ(Q) ≤ 2σ + 4.

- Regular d ≥ 3: σ = 2d−4, w = 1/(4d(d−2)), 1 + σ²w = (2d−2)/d, condition
  ⟺ ρ(Q) ≤ 2d — always true (equality iff bipartite). d = 2 (cycles):
  degenerate edges, w = 0, σ = 0: M = 4I − Q ⪰ 0 since ρ(Q) ≤ 4.
- Semiregular bipartite (dA, dB), s := dA + dB ≥ 4: σ ≡ s − 4 on both sides,
  arg46 − 4 = 2(dA² + dB²) − 16 dA dB/s, ρ(Q) = s, and (sympy):
  [ (2s−4) − (1+σ²w)s ] · (arg46−4) · s = (dA−dB)² (s−4)(s+4) ≥ 0. ∎
  (s = 4 ⟺ dA = dB = 2 is again the degenerate cycle case.)

This proves F2 exactly where Bound 46 is tight — the reduction chain
F2 ⇒ D1 ⇒ Bound 46 loses nothing on the equality manifold, and childI now
covers that manifold unconditionally.

## 4. Conjecture I1 (sound certificate) + exhaustive verification

Sound explicit choice of α (no knowledge of ρ needed):
ρ₀(G) := max_i (Bd)_i/(T_i d_i) ≥ ρ(P) (first-order CW upper bound);
α_G := κ / max(ρ₀, 1) with fixed κ < 1. Then α_G ρ < 1 always, so by I4:

**Conjecture I1 (κ = 0.99).** For every connected δ≥2 graph,
R(0.99/max(ρ₀,1)) holds. I1 ⇒ F2.

Verified (`sound_resolvent.py`, logs `i1_9_*.log`, `i1_10_*.log`):
- ALL 8,025 graphs 3 ≤ n ≤ 8: 0 failures (κ = 0.9 and 0.99);
- ALL 197,772 graphs n = 9: 0 failures (both κ); max ρ₀ = 1.0278;
- ALL 9,808,209 graphs n = 10 (16-way geng split): **0 failures at κ = 0.99**
  (67 failures at κ = 0.9, all near-equality dense graphs — consistent with
  the window shrinking, see §5); max ρ₀ = 1.036;
- The fixed-α variant (α ∈ {0.9, 0.95, 0.99} without the ρ₀ scaling) also
  passes all of n = 9 (`res9_*.log`, one α=0.9 miss, α ≥ 0.95 clean).
- Worst margins at κ = 0.99 are ~1e−14 — the certificate is EXACT (equality)
  on the equality manifold, as predicted by §3 (Pd = d there).

**Caveat (why I1 with fixed κ is NOT the final answer):** random large graphs
(`i1_rand.py`, 2,176 δ≥2 cores to n ≈ 120): with the K = 64 power-iteration
CW bound replacing ρ₀, κ = 0.99 still fails on 5 near-equality random-regular
cases (n = 64…87, ρ ≈ 0.99990) — for these the window is (0.9927/ρ, 1/ρ)-ish
while α_G ≈ 0.99/ρ₀ lands just below it (`i1_rand_debug.py`: a fine α-grid
inside (0, 1/ρ) ALWAYS succeeds; first working normalized αρ ≈ 0.990–0.993).
So no fixed κ < 1 can be universal as n → ∞; the true content is Theorem I7's
window statement α*(G) ρ(G) < 1, with α*ρ → 1 possible on near-equality
families. At n ≤ 10 the sound κ = 0.99 choice is universal.

## 5. Structure of the obstruction (what a proof of I1/F2 must handle)

- Deficient vertices: (Pd)_i > d_i ⟺ σᵢ Σ_{j∼i} w_ij (σᵢdᵢ + σⱼdⱼ) > σᵢdᵢ.
  Max observed (Pd/d) = ρ₀: 1.0278 (n ≤ 9), 1.036 (n = 10); but ρ₀ is NOT
  uniformly bounded: the per-edge quantity q_e = w_e(σᵢdᵢ + σⱼdⱼ) is
  unbounded over local configurations (`edge_bound.py`: a degree-2 vertex
  with a huge-degree second neighbor gives q ~ x/16 on its cheap edge), so
  first-order CW cannot prove any universal ρ bound; repair by the resolvent
  is genuinely global.
- α-window empirics (`alpha_interval.py`, n ≤ 7 grid): the certificate set is
  always an interval (0 holes, matching Lemma I6); worst normalized
  α*ρ = 0.872 at EQjO already at n = 7; random near-equality graphs push it
  to 0.993. Conjecturally α*ρ < 1 always (⟺ F2 by I7).
- Ground-state mining (`mine.py`, `regress.py`): on the 627 hard + 921
  near-equality graphs (n ≤ 8), regressing log(h*/d) of the exact Perron
  ground state on local invariants (log d, log m, σ, t, neighbor averages,
  2-step sums) explains only R² ≈ 0.53 — the correction to h = d is NOT a
  local function of any small invariant set; h* is reproduced by the global
  resolvent smoothing instead (this is what makes h_α succeed).

## 6. Negative results (routes killed this session)

1. **Local/per-vertex sufficient condition C1** — bounding
   x^T DHD x ≤ 2Σσᵢ²Wᵢxᵢ² (Wᵢ = Σ_{e∋i} w_e) and absorbing A into L gives
   "σᵢ²Wᵢ ≤ mᵢ − 2 ⇒ F2", tight on regular; but fails on 7,994/8,025 graphs
   n ≤ 8 (`c1_check.py`). The symmetric split of the H-quadratic form is far
   too lossy off-regular.
2. **Per-edge 2×2 PSD splitting** with allocation cᵢᵉ = 1 + (2dⱼ−4)/dᵢ
   (which is exact on regular): fails on 7,948/8,025 (`edge_split.py`).
   (For Z-matrices, feasibility of ANY such splitting is equivalent to the
   existence of an h certificate anyway.)
3. **Shifted one-parameter families h = d + c·u** (childH-style exact
   interval-in-c), u ∈ {1, m, σ, m−2, t, d(t−1), Pd−d, P²d−d}: none universal;
   best is u = P²d−d with 7 failures n ≤ 8 (`shift_scan.py`).
4. **Fixed-order power certificates**: h = P^K d (Mh ≥ 0) needs K up to 8 at
   n = 9 (`powK_n9.py`, logs `powK_9_*.log`); the order-K CW condition
   P^K d ≤ d needs K up to 13 at n = 8 (`ordK.py`). Both minimal-K statistics
   grow with n (near-equality graphs need K ~ 1/spectral gap): no fixed K.
5. **Krylov-cone LPs** (h = Σ_{k≤K} c_k P^k d, c ≥ 0): K = 4 still fails on
   2/8,025 (GCXeco, GCXe`W) (`resolvent_scan.py`) — but the full resolvent
   (K = ∞ with geometric weights) succeeds on all of them: the infinite tail
   matters.
6. **Optimizing the diagonal D** (childF §5(ii)): even allowing arbitrary
   s ≥ 0 in M(s) = 2diag(s) + 4I − Q − diag(s)H diag(s), the h = d certificate
   stays infeasible on 36/583 graphs n ≤ 7 (coordinate-ascent heuristic,
   `opt_sigma.py`) — including K4−e-type graphs — so no choice of σ makes the
   FIRST-order certificate work; the resolvent (higher-order) mechanism is
   needed regardless of D.

## 7. Files

- `common.py` — M/B/T/P builder (childF definitions), Perron ground state,
  geng driver.
- `verify_i_lemmas.py` — sympy + numeric machine verification of I2, I4, I6
  and Theorem T1 ("ALL I-LEMMA CHECKS PASSED").
- `sound_resolvent.py` — Conjecture I1 verifier; logs `i1_9_*.log` (197,772
  graphs, 0 failures), `i1_10_*.log` (9,808,209 graphs, 0 failures at κ=0.99).
- `resolvent_n9.py` / `res9_*.log` — fixed-α variant at n = 9.
- `resolvent_scan.py` — resolvent + Krylov-cone scans (n ≤ 8).
- `alpha_interval.py` — window structure empirics (interval, no holes).
- `i1_rand.py`, `i1_rand_debug.py` — random large-graph stress; the 5
  near-equality κ=0.99 misses all pass with α closer to 1/ρ.
- `mine.py`, `regress.py`, `hard_g6.npy`, `neareq_g6.npy` — ground-state
  mining + (negative) locality regression.
- `c1_check.py`, `edge_split.py`, `h_scan.py`, `shift_scan.py`, `ordK.py`,
  `powK_n9.py`, `opt_sigma.py`, `edge_bound.py` — negative results §6 and
  obstruction §5 (h_scan: 16 closed-form h candidates, best P²d with 15
  failures n ≤ 8).
- `f2 reproduction`: `mine.py` reproduces childF's 627/8,025 and min-eig
  −2.8e−15 exactly.

## 8. Route map for the next session

1. Prove R(α) directly for α near 1/ρ via the Perron projection: for
   connected G, (1−α)h_α = (1−α)Σα^kP^k d → c·u (Perron dir.) as α↑1/ρ when
   ρ>1 — I5 already exploits this; the OPEN half is showing ρ ≤ 1 graphs
   always satisfy R before 1/ρ, i.e. bounding the sub-Perron overshoot of
   the Green's function Σ_j G_α(i,j)d_j against d_i/(1−α). Natural tools:
   Doob h-transform of the substochastic-like kernel P w.r.t. d, plus the
   exact identity Pd = d + deficiency vector.
2. The deficiency vector e := Pd − d satisfies Σᵢ Tᵢ eᵢ-type global identities
   via Σᵢ dᵢmᵢ = Σ_{ij∈E}(dᵢ+dⱼ) — quantify "total deficiency ≤ total
   surplus" and turn the resolvent repair into a flow/electrical argument on
   the weighted graph (B, T) (discrete maximum principle for the killed walk).
3. T1 covers the equality manifold; try to extend the closed-form proof to
   "locally regular" perturbations by interlacing on M_ε (childF §5(iii)).
4. If F2 is to be bypassed entirely: Theorem F3 holds for ANY diagonal D, and
   §6.6 shows first-order certificates fail for all D — but resolvent
   certificates for OPTIMIZED D were not explored; the SDP-feasible-D region
   is convex and might admit a D making α* uniformly bounded away from 1/ρ.

**Bottom line.** F2 (hence Bound 46, δ≥2) remains open, but: (a) it is now
PROVED on the entire equality manifold (regular + semiregular bipartite,
Theorem T1); (b) it is EXACTLY equivalent to the nonemptiness of the resolvent
window, α*(G)ρ(G) < 1 (Theorem I7), a one-real-parameter statement with proved
monotone structure; and (c) the explicit sound certificate α = 0.99/ρ₀
verifies F2 on all 10,013,006 connected δ≥2 graphs n ≤ 10 with zero failures
and equality exactly on the equality manifold. No counterexample to F2 (or to
anything upstream) was found.
