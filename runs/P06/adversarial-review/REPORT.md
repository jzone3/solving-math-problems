# Adversarial review + priority check: P06 claim "WoW 698 is TRUE (s⁻ ≤ R)"

Reviewed artifacts (branch `fold-p06-v5`): `solutions/P06/PROOF-698.md`,
`solutions/P06/verify.py`, `runs/P06/v5/NOTES.md`. Review conducted in hostile
mode per `context/METHODOLOGY.md` (Formalization gate). Independent verifier:
`verify_adversarial.py` (this directory), written from scratch — prints
`ADVERSARIAL-PASS`.

## Executive verdicts

| Step | Verdict |
|---|---|
| 1. Statement fidelity (WoW #698 wording, glossary, refutationGBR bug) | **CONFIRMED** |
| 2. Proof correctness (main chain) | **CONFIRMED** |
| 2b. Equality analysis | **CONFIRMED** (one writeup nit, one edge-case nit; conclusion unaffected) |
| 3. Priority of the RESULT s⁻(G) ≤ R(G) | **APPEARS NEW** (no prior statement found; see residual risks) |
| 3b. Priority of the "sharp intermediate inequality" λ₁² + R² ≥ 2m | **NOT substantively new** — one-line AM–GM corollary of a PUBLISHED 1993 result; the "appears to be new" claim in PROOF-698.md must be downgraded |
| 4. Prior efforts on WoW 698 | Surveyed below; nothing beyond Roucairol–Cazenave (whose encoding was vacuous) |

---

## 1. Statement fidelity — CONFIRMED

Decoded the July 2004 WoW PDF (`handoff/P07/wow-july2004.pdf`; Type-3 fonts
break pdftotext, so pages were rasterized at 150 dpi and OCR'd with tesseract,
then the relevant region was inspected visually). Page 104 (printed page
number 104), exact text:

> **698.** *lenght of negative eigenvalues ≤ the Randic Index.*

(sic "lenght"; the relation glyph is **≤**, not `<` — visually confirmed from
the page image, consistent with neighbors 695–697 which all use ≤.)

Glossary confirmations (Brewster–Dinneen–Faber, Discrete Math 147 (1995),
glossary; fetched from cs.auckland.ac.nz/~mjd/graffiti/graffiti1.pdf):

- "**Length** (of a vector). The square root of the sum of the squares of the
  components." → L2 norm. ✔
- "**Eigenvalue(s).** Unless otherwise specified, the eigenvalue(s) of the
  adjacency matrix of the graph." → adjacency spectrum. ✔

So the faithful reading is exactly the one proved:
s⁻(G) := √(Σ_{λᵢ<0} λᵢ²) ≤ R(G), adjacency eigenvalues, non-strict.

**refutationGBR Laplacian bug — CONFIRMED.** Cloned
github.com/RoucairolMilo/refutationGBR at HEAD;
`src/models/conjectures/GenerateGraph.rs`, block `if CONJECTURE == 698` (lines
~1691–1718) computes `SymmetricEigen::new(invariants::laplacian_matrix(...))`
and sums squares of eigenvalues `< -1e-8`. The Laplacian is PSD, so the tested
quantity is identically 0 and the encoded statement `0 ≤ R(G)` is vacuous, as
claimed. (Their MCTS "no counterexample" evidence for 698 is therefore void —
which cuts both ways: it also means 698 had received *no* genuine search
pressure from that paper.)

## 2. Proof attack — CONFIRMED correct

Re-derived every step from scratch:

1. **λ₁ ≥ S/m** (S = Σ_E √(d_u d_v)): Rayleigh with x_u = √d_u; xᵀAx =
   Σ_u Σ_{v∼u} √(d_u d_v) = 2S, xᵀx = Σd_u = 2m; x ≠ 0 iff m ≥ 1. Holds for
   disconnected graphs and graphs with isolated vertices (those coordinates
   are 0; every edge has d_u, d_v ≥ 1). ✔
2. **m² ≤ S·R**: Cauchy–Schwarz, (Σ_e 1)² ≤ (Σ_e w_e)(Σ_e w_e⁻¹) with
   w_e = √(d_u d_v) > 0. ✔
3. **λ₁R ≥ (S/m)R ≥ m** and AM–GM ⇒ λ₁² + R² ≥ 2λ₁R ≥ 2m. ✔
4. **s⁻² = 2m − s⁺² ≤ 2m − λ₁² ≤ R²** using trace(A²) = 2m and s⁺² ≥ λ₁²
   (λ₁ > 0 whenever m ≥ 1; zero eigenvalues contribute to neither side). ✔

No gaps found. Conventions: simple graphs (the WoW universe — multigraphs out
of scope); m = 0 gives 0 ≤ 0. The chain never divides by zero for m ≥ 1.

**Independent verifier** (`verify_adversarial.py`, no code shared with their
`verify.py`): exact sympy charpoly check of the K_{a,b}(+isolated) equality
family (a,b ≤ 12); exact check that regular complete multipartite K_{k×a},
k ≥ 3, has λ₁² > m strictly; full chain checked on **all labeled graphs
n ≤ 7** (2,097,152 at n = 7) and 3000 random graphs n ≤ 70 including forced
disconnections and isolated vertices; every near-equality case (|s⁻ − R| <
1e−7; 1,389 total) re-certified at 50-digit precision (mpmath) **and**
combinatorially tested to be exactly complete-bipartite-plus-isolated.
Result: `ADVERSARIAL-PASS` — no violation, equality exactly on the claimed
family. Their `verify.py` also reruns to PASS.

### 2b. Equality analysis — CONFIRMED, two nits

Equality s⁻ = R forces: (i) s⁺ = λ₁ (one positive eigenvalue), (ii) AM–GM
equality λ₁ = R, (iii) λ₁R = m ⇒ λ₁² = R² = m, (iv) C–S equality: d_u d_v
constant over edges, (v) Rayleigh equality: √d is a λ₁-eigenvector.

- Smith's theorem usage is sound: a connected graph with exactly one positive
  eigenvalue is complete multipartite (Smith 1970); each non-trivial component
  contributes a positive eigenvalue, so (i) forces a single non-trivial
  component. ✔
- k ≥ 3 exclusion: PROOF-698.md's parenthetical "trace(A²)/2 = m < λ₁² can be
  checked directly" is asserted, not proved, for general K_{n₁,…,n_k} — a
  **writeup nit**. The (b)+(c) route it also offers does close the case
  rigorously: in a complete multipartite graph with k ≥ 3 every pair of parts
  is adjacent, so d_u d_v constant (iv) forces all parts equal, i.e. K_{k×a},
  regular, λ₁ = (k−1)a, and λ₁² = (k−1)²a² > k(k−1)a²/2 = m ⇔ k > 2 —
  verified exactly (A2). Recommend making this the primary argument in the
  writeup.
- K_{a,b}: spectrum {±√(ab), 0^{n−2}}, s⁻ = √(ab) = R — verified exactly via
  charpoly (A1). ✔
- **Edge-case nit:** m = 0 graphs also satisfy equality (0 = 0) but are not in
  the stated family "single complete bipartite component + isolated vertices".
  The equality statement should read "iff m = 0 or …". Cosmetic.

## 3. Priority — the result appears NEW; the intermediate inequality is NOT

**Damaging finding for the novelty claims of the lemmas.** The Li–Shi survey
("A Survey on the Randić Index", MATCH 59 (2008)), Theorem 2.16, cites:

- **Favaron, Mahéo, Saclé**, *Some eigenvalue properties in graphs
  (Conjectures of Graffiti — II)*, Discrete Math. 111 (1993) 197–220:
  **λ₁ ≥ m/R** for connected graphs — i.e. step 3's product inequality
  **λ₁R ≥ m is a published 1993 theorem** (extension to disconnected graphs
  with m ≥ 1 is a triviality over components).
- Elphick–Wocjan, *Bounds and power means for the general Randić index*
  (arXiv:1508.07950), §3, credit the same FMS paper with
  ((1/m)Σ_E √(d_i d_j))² ≤ λ₁² — i.e. **step 1 (λ₁ ≥ S/m) is also FMS 1993**,
  and their Theorem 1 (R_α ≥ mλ^{2α}, α < 0) generalizes λ₁R ≥ m. Runge and
  Hofmeister are credited with the α = −1 analogue R₋₁ ≥ m/λ₁².
- Step 2 (m² ≤ SR) is bare Cauchy–Schwarz; step 4's s⁻² ≤ 2m − λ₁² is a
  standard trace identity manipulation (ubiquitous in the s⁺/s⁻ "square
  energy" literature, e.g. Elphick–Farber–Goldberg–Wocjan arXiv:1409.2079).

Consequently the "sharp intermediate inequality λ₁² + R² ≥ 2m (appears to be
new)" in PROOF-698.md is a **one-line AM–GM corollary of FMS 1993's λ₁R ≥ m**.
As a stated inequality it may never have been written down, but it carries no
substantive novelty and must not be advertised as a new inequality without
crediting FMS. **PROOF-698.md should be revised to cite FMS 1993 for steps
1–3.** The equality characterization of λ₁² + R² = 2m (complete bipartite +
isolated) may be new in print.

**The final result s⁻(G) ≤ R(G) (WoW 698 itself) was not found anywhere:**

- The s⁺/s⁻ ("square energy") literature — Abiad, de Lima, Desai, Guo, Hogben,
  Madrid (ELA 39, 2023); Elphick–Linz (ELA 2024 / arXiv:2311.11530);
  Akbari–Kumar–Mohar–Pragada (E-JC 2025); Ning et al (arXiv:2605.24668);
  Liu (arXiv:2607.18031, July 2026) — contains **no mention of the Randić
  index** (grepped full texts of 2311.11530, 2607.18031, 1409.2079).
- Randić-index surveys (Li–Shi 2008; Li–Shi–Wang works) relate R to λ₁ (FMS,
  Aouchiche–Hansen AutoGraphiX conjectures: R+λ₁ ≥ 2√(n−1), Rλ₁ ≥ n−1,
  signless-Laplacian variants) — never to eigenvalue norms / s⁻.
- Closest published relative: **Arizmendi–Arizmendi, "Energy of a graph and
  Randić index", LAA 609 (2020): E(G) ≥ 2R(G)**. Neither implies the other:
  E/2 = Σ_{λ<0}|λ| (L1 of the negative part) ≥ s⁻ (L2), so E ≥ 2R lower-bounds
  the L1 norm by R while 698 upper-bounds the L2 norm by R. Should be cited
  as related work.
- Searches for a resolution of Graffiti/WoW conjecture 698 (Fajtlowicz's
  bibliographies, DeLaViña's WoW pages, Semantic-Scholar/Exa queries) found
  nothing; the only modern attack is Roucairol–Cazenave (ECAI 2025), whose
  Table lists **698 as Open ("698 O")** and whose search encoding was vacuous
  (§1).

**Verdict:** the 698 resolution (theorem + equality characterization) appears
to be new; its proof is a short assembly of known 1993 lemmas — near-trivial
modulo literature, which slightly raises the risk that it exists as a remark
somewhere unindexed.

### Residual risks

1. FMS 1993 original (paywalled; read via the Li–Shi and Elphick–Wocjan
   citations) — conceivably FMS or a contemporary already remarked
   s⁻ ≤ R; their paper is literally about Graffiti conjectures. **Unread
   primary source = the main residual risk.** (698 postdates FMS: the WoW
   context around #700 is dated ~Nov 1989–Jun 1990, but FMS attacked the
   0–583 range per their paper's scope; still, a direct read is advised.)
2. MATCH / chemical-graph-theory literature is vast and poorly indexed; a
   corollary of the form "2m − λ₁² ≤ R²" could hide in a bounds compendium
   (e.g. Bozkurt Altındağ's Randić-energy bound papers were not exhaustively
   read).
3. Fajtlowicz's WoW status annotations after July 2004 are not public; a
   private resolution would not be visible.
4. OCR of the broken-font PDF was page-targeted, not full-document; the
   operative page (104) was verified visually, so fidelity risk is minimal.

## 4. Prior efforts on WoW 698 (survey)

- **Fajtlowicz, WoW (July 2004 listing):** #698 appears in the block dated
  around late 1989/1990, unannotated (no counterexample/proof mark), i.e.
  open as of July 2004. Neighboring conjectures carry annotations (e.g. 699
  "comp. [EPS]"), so absence of a mark is meaningful.
- **Brewster–Dinneen–Faber 1995** (computational attack on Graffiti,
  Discrete Math 147): their published table covers other WoW numbers
  (691, 725–728 etc. appear); **698 is not treated**. Their glossary is the
  definitional authority used above.
- **Favaron–Mahéo–Saclé 1993:** did not address 698 (predates its wide
  circulation), but proved the two lemmas that resolve it.
- **Roucairol–Cazenave 2022 (arXiv:2207.03343) / ECAI 2025:** MCTS refutation
  searches over WoW; 698 listed Open; encoding vacuous (Laplacian bug,
  confirmed in §1) — so no genuine computational frontier existed for 698
  before this project's n ≤ 10 exhaustive scan (runs/P06/v5).
- **This repo (runs/P06/v5):** exhaustive n ≤ 10, annealing to n = 80, proof.

## Bottom line

The theorem and its proof are **correct** (independently re-derived and
machine-verified); the statement is **faithful** to the original source; the
resolution of WoW 698 **appears to be new**, but the proof's ingredients are
1993-vintage published results (Favaron–Mahéo–Saclé), so PROOF-698.md's
novelty claim for λ₁² + R² ≥ 2m should be retracted/reworded and FMS 1993 +
Elphick–Wocjan + Arizmendi–Arizmendi cited before any public announcement.
