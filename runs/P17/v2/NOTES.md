# P17 — WoW 20 & 21 (inertia ≤ energy/2) — V2 run

Session: devin-40d8b3031e384508ae5b0dad8f30fc41. Branch: `runs/P17-v2`. Date: 2026-07-23.
Approach assigned: attempt a PROOF of n⁺ ≤ Σ_{λ>0}λ using square-energy machinery
(arXiv:2607.18031) + exhaustive n ≤ 11 for confidence.

**Bottom line (UPDATED 2026-07-23, second pass): BOTH CONJECTURES ARE NOW THEOREMS.**
Kumar & Pragada, *Energy and independence number*, arXiv:2607.19817 (posted 2026-07-22,
i.e. the day before this run) prove Fajtlowicz's WoW conjecture #543:
  E(G) ≥ 2(n − α(G))    for every graph G.
Combined with the classical Cvetković inertia bound
  α(G) ≤ min{n − n⁺(G), n − n⁻(G)}  ⟺  max{n⁺, n⁻} ≤ n − α = τ,
this yields  n⁺(G) ≤ E/2 = Σ_{λ>0}λ  and  n⁻(G) ≤ E/2, i.e. **WoW 20 and WoW 21 hold for
all graphs**. The paper states this corollary explicitly ("which resolves [4, Conjectures
#20, #21, Table 6]"). See §9 below for our independent verification of their proof
(line-by-line logical check + numerical check of every lemma over all 273,192 connected
graphs n ≤ 9) and for the full corollary derivation. Priority: the result is theirs
(2026-07-22); this run's contribution is independent confirmation, the n ≤ 11 exhaustive
verification (consistent with the theorem), and the exact verifier.

Earlier bottom line from the first pass of this run (before 2607.19817 was found):
NO counterexample and NO complete proof; both conjectures verified
exhaustively for ALL graphs on ≤ 11 vertices (1,006,700,565 connected graphs; disconnected
cases reduce to connected by additivity). Hard-case reduction proved: a counterexample to
WoW 20 must have n⁺ > n⁻, one to WoW 21 must have n⁻ > n⁺. Equality manifolds
characterized.

Note on setup: `problems/P17-wow-20-21.md` does not exist on `master` (it lives on
`origin/catalog-wave2`); it was restored onto this branch from that ref, unmodified.

## 1. Statement fidelity (mandatory gate, done FIRST)

Primary source: Fajtlowicz, *Written on the Wall*, July 2004 PDF
(`handoff/P07/wow-july2004.pdf`). The PDF has Type-3 fonts with no ToUnicode map; decoded
INDEPENDENTLY here by parsing content streams + font `/Differences` arrays and the glyph-name
substitution `/XY` → chr(base36(XY) − 360) (same mapping the P08 review derived; my decoder is
a fresh implementation, `/tmp/decode_wow2.py`, reproduced in §7). Verbatim decodes:

> **20.** The number of positive eigenvalues of a graph is not more than their sum.
> The sum of absolute values of eigenvalues of an integer valued matrix is greater or equal
> to its rank i.e the number of nonzero eigenvalues, [F2]. This is also a partial solution
> to conjecture 21. [F2] S. Fajtlowicz, On Conjectures of Graffiti, II. Congressus
> Numerantium 60 (87), p. 189-197.
>
> **21.** The number of negative eigenvalues of a graph is not more than the sum of its
> positive eigenvalues. comp. conj 20.

Also relevant, decoded near conj. 19: "This conjecture was proved by Favaron, Maheo and
Sacle... comp also conj's 20, 21, 27 and 28. [FMS2]" — FMS Part II (Discrete Math 111,
1993) discusses 20/21 but did not resolve them (they are still listed as open in WoW 2004,
11 years later, and in RC 2025).

Operational encoding (matches problem file and RC code, see §2):
- eigenvalues = adjacency matrix spectrum (WoW glossary: eigenvalues are of the adjacency
  matrix unless otherwise specified), with multiplicity;
- **WoW 20**: n⁺(G) ≤ Σ_{λᵢ>0} λᵢ; **WoW 21**: n⁻(G) ≤ Σ_{λᵢ>0} λᵢ.
- "their sum" in 20 = the sum of the positive eigenvalues themselves (confirmed against RC's
  CONJECTURE==20 code: `coun - su` with both computed from the positive eigenvalue list).
- Since tr(A)=0, Σ_{λ>0}λ = E(G)/2 (half the energy) = Σ_{λ<0}|λ|.
- Both sides additive over disjoint unions ⇒ a minimal counterexample is connected.
- Strictness: "not more than" = ≤; the comparand n± is an integer; equality allowed.

Cross-check of the RC encoding (RoucairolMilo/refutationGBR,
`src/models/conjectures/GenerateGraph.rs`, read from GitHub raw on 2026-07-23):
- CONJECTURE==20 (line 840): counts eigenvalues > 1e-15, compares count − sum. Matches.
- CONJECTURE==21 (line 547): `num_eig_neg` (eig < −1e-4) vs `sum_eig_pos` (eig > 1e-4),
  **adjacency matrix**. Matches. (Unlike their 698 row, no wrong-matrix bug here.)

## 2. Priority check (published + artifact repos)

Searched 2026-07-23:
- **Exa web/paper search**: "Graffiti conjecture 20/21 positive/negative eigenvalues",
  "graph energy at least twice number of negative eigenvalues", "n+ ≤ energy/2",
  "energy rank inertia" (multiple phrasings). No resolution of either conjecture found.
- **Roucairol–Cazenave ECAI-2025** (`handoff/P07/roucairol-cazenave-2025.pdf`) Table 1:
  rows "20 O" and "21 O" — both open after 8 search algorithms to size 50
  (plus "20+ girth ≥ 5 600" in their extended-size table).
- **Brewster–Dinneen–Faber 1995**: exhaustive test of surviving Graffiti conjectures on all
  graphs with ≤ 10 vertices; 20/21 not refuted there.
- **arXiv**: nothing on 20/21. Adjacent recent work found (relevant, not resolving):
  - arXiv:2303.11930, 2409.15504 (square energies s⁺, s⁻);
  - arXiv:2607.18031 (July 2026): **min{s⁺,s⁻} ≥ n−1 PROVED** (used in §5);
  - arXiv:2508.01163 Akbari–Elphick–Kumar–Pragada–Tang: conjecture 2n⁺ ≤ n⁻(n⁻+1);
  - arXiv:2605.07196 Chen–Li (May 2026): counterexamples W_k to the AEKPT conjecture with
    inertia (C(k,2)+1, 0, k−1) — the extreme n⁺≫n⁻ family; checked against WoW 20 in §4
    (it SATISFIES it, margin grows).
- **GitHub**: `gh search repos` for "graffiti conjecture", "written on the wall",
  "fajtlowicz", "refutationGBR"; code search `num_eig_neg`. Only RC's refutationGBR, old
  student projects on other Graffiti numbers, and this repo.
- **demonstrandum-research/artifacts** (the org that scooped P07): RESULTS.md
  (last updated 2026-06-12) catalogs 13 results — Graffiti 143/154 among them, **no 20/21**.
- **Zenodo API**: "Graffiti eigenvalues conjecture" — only street-art/irrelevant records.
- **OpenReview API**: search unavailable (`searchUnavailable: true`) — residual risk.

Residual risks: FMS-II (Discrete Math 111 (1993)) is paywalled — it may contain partial
results on 20/21 (WoW cross-references it) but cannot contain a resolution (WoW 2004 lists
both as live; RC 2025 lists both as open). OpenReview not searchable today.

**Conclusion: both conjectures open as of 2026-07-23. No artifact-repo scoop found.**

## 3. Exhaustive search n ≤ 11 (all connected graphs)

Tool: `scan_p17.c` (geng → graph6 → LAPACK dsyev, float filter, top-8 scores kept per
conjecture; violation score s20 = n⁺ − Σλ⁺, s21 = n⁻ − Σλ⁺; positive ⇔ counterexample).
Zero tolerance 1e-9 on eigenvalue sign; every near-miss in the reported band was re-verified
EXACTLY (see §6). Runs (8-core box, `nauty-geng -q -c n [res/8]`):

| n | connected graphs | max s20 (graph) | max s21 (graph) |
|---|---|---|---|
| 4 | 6 | −0.2361 (CU) | 0.0000 (K4) |
| 5 | 21 | −0.2361 (C5=DUW) | 0.0000 (K5) |
| 6 | 112 | −0.4495 (ECR_) | 0.0000 (K6) |
| 7 | 853 | −0.4587 (FCQb_) | 0.0000 (K7) |
| 8 | 11,117 | −0.5388 (GCQb`o) | 0.0000 (K8); next −0.0941 (GQhTUg) |
| 9 | 261,080 | −0.6631 (H?`@C`w) | 0.0000 (K9); next −0.0806 (HQhTQji) |
| 10 | 11,716,571 | −0.6538 (I?`D@POd?) | 0.0000 (K10); next −0.0645 (IQhTQiitO) |
| 11 | 1,006,700,565 | −0.8283 (J?`D@POd?{?) | 0.0000 (K11); next −0.0561 (JQhTQiiTVT?) |

(n=11 split 8 ways as `geng -c 11 i/8`; part counts 117,940,313 + 126,704,482 + 126,652,309
+ 120,209,801 + 118,214,050 + 132,683,590 + 141,388,129 + 122,907,891 = 1,006,700,565 =
A001349(11). Wall time ≈ 11 min on 8 cores. Logs: `logs/n11.*.txt`.)

**No violation of either conjecture for any graph with ≤ 11 vertices** (disconnected
included, by additivity). This extends the 1995 exhaustive frontier (n ≤ 10) by one order.

WoW 21 near-miss family: K_n-like graphs whose complement has max degree ≤ 2 — spectra of
form {λ1, λ2 small, −θ (0<θ<1), −1^(n−3), ≈−1.8}; margin shrinks slowly (−0.094, −0.081,
−0.064, −0.056 at n = 8..11) but family scans to n = 100 (§4) show it turns around and
diverges negative; the shrink is a small-n boundary effect.

## 4. Family scans (analytic sizes ≫ 50) and annealing

`families.py` (float filter; anything > −1e-6 would go to exact verification — none did):
- complete split CS(a,b), a ≤ 40: max score 0 only at b=... CS(a,1)=K_{a+1} (equality in 21).
- K_n minus partial matchings, cocktail party, Kneser(n,k) n ≤ 12, odd cycles ≤ 59 and
  their blowups, cones over cycles, line graphs L(K_n), complements of paths/cycles
  (n ≤ 100 for the near-miss class: co-C_n, co-P_n, co-kC3/4/5, co-kP2/P3, co-2C_{n/2}):
  all scores strictly negative and diverging (e.g. co-C100 s21 = −52.8).
- **Kneser(2k,k)** = perfect matching graph: eigenvalues ±1 ⇒ **equality in WoW 20**
  (n⁺ = Σλ⁺). Under connectivity only K2 is tight for 20.
- **W_k (Chen–Li)**, the extreme-inertia family (n⁺ = C(k,2)+1, n⁻ = k−1): from their exact
  char poly, Σλ⁺ − n⁺ = C(k−2,2) − 2 + (k−1)ε_k > 0 for k ≥ 5 (ε_k = positive root of
  x²+(k−2)x−1). Checked numerically k ≤ 9 too. Satisfies WoW 20 with margin ~k²/2. The
  reason: its huge positive multiplicity sits at eigenvalue exactly 1, which contributes
  exactly 1 each to the sum.
- Annealing (`anneal.py`, n = 12..20, 60k steps each, 8 seeds): both scores plateau at
  exactly 0 on the equality manifolds and never go positive:
  - WoW 20 equality found by annealer: disjoint unions of edges (matchings + isolated
    vertices; spectrum ±1);
  - WoW 21 equality found by annealer: disjoint unions of cliques (each K_k contributes
    n⁻ = k−1 = Σλ⁺).

## 5. Proof attempt (assigned direction) — what was proved, what failed

Write S⁺ = Σ_{λ>0} λ, r = rank = n⁺ + n⁻, s = n⁺ − n⁻ (signature). tr A = 0 ⇒ E = 2S⁺.

**Proposition 1 (hard-case reduction; essentially Fajtlowicz [F2]).** The product of the
nonzero adjacency eigenvalues is (up to sign) the last nonzero coefficient of the integer
characteristic polynomial, hence has absolute value ≥ 1; AM–GM on the |λ| gives
**E ≥ rank**, i.e. S⁺ ≥ (n⁺+n⁻)/2. Consequently:
- WoW 20 holds for every graph with n⁺ ≤ n⁻ (in particular all bipartite graphs);
- WoW 21 holds for every graph with n⁻ ≤ n⁺.
Equivalently: WoW 20 ⟺ s ≤ E − rank and WoW 21 ⟺ −s ≤ E − rank, where
E − rank = Σ_{λ≠0}(|λ|−1). A counterexample to 20 needs many positive eigenvalues in
(0,1); to 21, many negative eigenvalues in (−1,0).

**Proposition 2 (logarithmic sharpening).** Splitting off λ₁ and applying AM–GM to the
remaining nonzero eigenvalues (product ≥ 1/λ₁): E ≥ r − 1 + λ₁ − ln λ₁ (using
(1/λ₁)^{1/(r−1)} ≥ 1 − (ln λ₁)/(r−1)). Hence WoW 21 holds whenever
n⁻ ≤ n⁺ + 1 and λ₁ − ln λ₁ ≥ 2 (λ₁ ≥ 3.147), and more generally whenever
n⁻ − n⁺ ≤ λ₁ − ln λ₁ − 1. Symmetrically for WoW 20 with s ≤ λ₁ − ln λ₁ − 1.

**Square-energy machinery (assigned): what it gives and where it stops.**
With min{s⁺,s⁻} ≥ n−1 now a theorem (arXiv:2607.18031):
- (S⁺)² ≥ s⁺ ≥ n−1 and (S⁺)² = (Σ|λ⁻|)² ≥ s⁻ ≥ n−1, so S⁺ ≥ √(n−1). This settles both
  conjectures only for n± ≤ √(n−1) — far from enough (n⁻ can be n−1).
- S⁺ ≥ s⁺/λ₁ and S⁺ ≥ s⁻/|λ_n|: WoW 21 follows when s⁻ ≥ n⁻·|λ_n|, i.e. when the negative
  spectrum has mean square ≥ its max modulus — fails exactly in the hard regime (many small
  negative eigenvalues).
- Dead end recorded: no combination of s± ≥ n−1 with Cauchy–Schwarz closes the gap, because
  the conjectures are equality-tight on unions of cliques (21) and matchings (20), where
  s⁻ = n−1 exactly; any slack-free chain would need to reproduce these equality cases
  simultaneously with K_n (λ₁-dominated) and K₂ (balanced) — the standard inequalities
  degrade in opposite directions on these two families.
- Ky Fan / variational: S⁺ = max_P tr(AP) over orthogonal projections. Vertex-disjoint
  stars give S⁺ ≥ Σᵢ√tᵢ; a clique gives S⁺ ≥ ω−1 (= n⁻(K_ω), tight). A proof of 21 along
  these lines needs a combinatorial structure with n⁻ orthonormal vectors of average
  Rayleigh quotient ≥ 1; matchings give S⁺ ≥ μ(G) (proved elsewhere, E ≥ 2μ), but
  n⁻ > μ is possible (K_n: n⁻ = n−1, μ = ⌊n/2⌋), so matching-based certificates cannot
  suffice; clique-based ones stop at ω−1. A mixed clique+star certificate was attempted
  and fails on complements of sparse graphs. Left open.

**Equality structure (new observations, machine-checked exactly for small cases).**
- WoW 21 equality: every disjoint union of complete graphs (+ isolated vertices);
  spectrum of K_k: {k−1, (−1)^{k−1}}, so Σλ⁺ = k−1 = n⁻ exactly. Conjecture: these are
  the ONLY equality cases (verified exhaustively for n ≤ 11: the only s21 = 0 hits were
  the K_n and, over all graphs, unions of cliques).
- WoW 20 equality: graphs with all nonzero eigenvalues = ±1 = disjoint unions of edges
  (+ isolated vertices) among connected-component types; K2 is the only connected one
  (λ = ±1 with a connected graph forces K2: λ₁ = 1 ⇒ no P3 subgraph).

## 6. Exact verification (no floats on the accept path)

`verify.py`: graph6/edge-list → integer characteristic polynomial (sympy over ZZ) → strips
x^k exactly (nullity) → `dup_isolate_real_roots` over QQ with rational eps, refined until no
isolating interval touches 0 → n± counted with multiplicity from rational interval signs →
Σλ⁺ bracketed in a rational interval [lo, hi] refined until it separates from the integer
comparands (exact rational spectrum fallback for the equality cases). Pure rational
arithmetic throughout; PASS/VIOLATION decisions never consult a float.

Spot-verified exactly: K7, K11 (equality, both conjectures, exact interval [k−1,k−1]); C5;
the top n = 8..11 near-misses of both conjectures (GQhTUg, HQhTQji, IQhTQiitO,
JQhTQiiTVT?, J?`D@POd?{?): all PASS. The float scanner and the exact verifier agree on
n±/score for every graph checked.

## 7. Compute + artifacts

- `scan_p17.c` — exhaustive scanner (gcc -O3, LAPACK dsyev). ~3.3 µs/graph at n=10.
- `families.py` — analytic/structured family scan (numpy filter).
- `anneal.py` — simulated annealing on s20/s21 (float filter).
- `verify.py` — exact verifier (sympy/QQ; the only accept-path tool).
- `logs/` — n=9,10 and the 8 n=11 part logs; annealing logs.
- `decode_wow.py` — glyph decoder for the WoW PDF: content-stream parser + `/Differences`
  maps + `/XY → chr(base36(XY)−360)` (independent re-implementation; mapping agrees with
  the runs/P08 derivation). Run: `python3 decode_wow.py handoff/P07/wow-july2004.pdf`.
- Total compute: ≈ 100 core-minutes (n≤11 exhaustive ≈ 85 core-min; scans/anneal ≈ 15).

## 8. Status of the first pass (superseded by §9)

- **Negative result (search): no counterexample to WoW 20 or 21 exists with n ≤ 11 vertices**;
  none found in structured families to n = 100 or by annealing to n = 20.
- **Partial results (proof): Propositions 1–2 (§5) reduce both conjectures to the
  signature-vs-(E − rank) inequality |n⁺ − n⁻| ≤ Σ_{λ≠0}(|λ|−1)**; both directions of this
  reduction are tight on the respective equality manifolds.
- First-pass conclusion "both conjectures remain OPEN" is superseded by §9.

## 9. RESOLUTION: WoW 20 & 21 are theorems (Kumar–Pragada, arXiv:2607.19817)

Second pass, 2026-07-23. Re-ran the priority search targeting the τ/α route after
noticing numerically (all connected graphs n ≤ 9) that **S⁺ = E/2 ≥ τ = n − α with
equality exactly at complete graphs** — a strictly stronger statement than both WoW
conjectures via the Cvetković inertia bound. That statement is Fajtlowicz's WoW
conjecture **#543**, E(G) ≥ 2(n − α(G)), and it was **proved the day before this run**:

- Hitesh Kumar, Shivaramakrishna Pragada, *Energy and independence number*,
  arXiv:2607.19817v1 [math.CO], posted 2026-07-22. Copy archived at
  `handoff/P17/kumar-pragada-2026-energy-independence.pdf`.
- The paper explicitly notes the corollary: with the inertia bound
  α ≤ min{n − n⁺, n − n⁻}, Theorem 1.2 gives E ≥ 2·max{n⁺, n⁻}, "which resolves
  [4, Conjectures #20, #21, Table 6]". So WoW 20 and WoW 21 are **CLOSED (proved)**.

Corollary derivation in full (for the record):
1. (Cvetković) If S is independent, |S| = α, then A[S] = 0; by Cauchy interlacing
   λ_α(A) ≥ λ_α(A[S]) = 0 and λ_{n−α+1}(A) ≤ λ_1... i.e. the α-th largest eigenvalue
   is ≥ 0 and the α-th smallest is ≤ 0, hence n⁻ ≤ n − α and n⁺ ≤ n − α.
2. (Kumar–Pragada Thm 1.2) E ≥ 2(n − α).
3. Therefore Σ_{λ>0}λ = E/2 ≥ n − α ≥ max{n⁺, n⁻} ⇒ WoW 20 and WoW 21. ∎

Independent verification of the Kumar–Pragada proof performed here:
- Logical line-by-line check (§2–3 of the paper). Structure: (i) SDP formulation
  E/2 = min{tr M : M ⪰ 0, M − A ⪰ 0} (Abiad–Coutinho–Juliano–Reijnders, arXiv:2509.05814);
  (ii) with A = P − Q (spectral positive/negative parts), B = P + Q = |A|, the Schur
  complement P_v = P[S(v)] − x_v x_vᵀ/P_vv (S(v) = non-neighbours of v) is PSD and
  P_v − A(G − N[v]) = Q_v ⪰ 0, so 2 tr P_v ≥ E(G − N[v]); (iii) the edge inequality
  ((B_uu−1)² − B_uv²)/B_uu + ((B_vv−1)² − B_uv²)/B_vv ≥ 0, from the 2×2 PSD minors of
  2P and 2Q (xy ≥ (z±1)²) + AM–GM; (iv) summing gives the neighbourhood-deletion
  inequality 4m + Σ_v E(G − N[v]) ≤ n E(G); (v) induction on n with
  α(G − N[v]) ≤ α(G) − 1. Every step checks out; no gaps found.
- Numerical check (`logs/kumar-pragada-check.txt`): for ALL 273,192 connected graphs
  n ≤ 9, minimum slack of Lemma 2.2 (n·E − 4m − Σ_v E(G−N[v])), of Theorem 1.2
  (E − 2(n−α)), and of the inertia bound ((n−α) − max{n⁺,n⁻}) is ≥ 0 (equality attained,
  e.g. complete graphs). Consistent with our independent exhaustive n ≤ 11 verification
  of WoW 20/21 themselves (§4).

Priority: the theorem is Kumar–Pragada's (2026-07-22), found via web search
("energy and independence number") on 2026-07-23; it postdates the priority search of
the first pass of this run by hours, which is why the first pass missed it (the first
pass searched WoW 20/21 phrasings, not #543/τ phrasings — methodology lesson: search
for STRONGER known conjectures implying the target, not just the target itself).
This run's standing contributions: independent confirmation of the proof, the n ≤ 11
exhaustive frontier, the exact rational verifier, and the equality characterizations.
