# New candidate open problems — automated/computer-generated conjecture corpora

Research date: 2026-07-23. Scope: mine the automated-conjecture corpora **not yet elevated to problem
files** in this repo (P01–P15) for 8–12 new, genuinely-open, finite-witness, Lean-formalizable targets.
Repo status confirmed: P06 covers Graffiti **129/698**, P07 covers **143/154**, P08 covers **39/40**;
P09 = Bollobás–Nikiforov, P10 = Brouwer. All candidates below avoid those.

Sources pulled and read locally:
- Written on the Wall (Fajtlowicz), July-2004 PDF — https://independencenumber.wordpress.com/wp-content/uploads/2012/08/wow-july2004.pdf
- Roucairol–Cazenave 2025, *Refutation of Spectral Graph Theory Conjectures with Search Algorithms* (arXiv:2409.18626 / IASE-ECAI 2025 PDF) + Rust invariant code https://github.com/RoucairolMilo/refutationGBR
- Wagner 2021, *Constructions in combinatorics via neural networks* (arXiv:2104.14516)
- Taieb–Roucairol–Cazenave–Harutyunyan 2025, *Automated Refutation … Maximum Laplacian Eigenvalue* (LION19) — 68 Brankov–Hansen–Stevanović (BHS) conjectures
- **Damnjanović–Ha–Stevanović, June 2026, arXiv:2606.14550** — the current status ledger for all 68 BHS Laplacian-spectral-radius bounds
- DeLaViña, *Written on the Wall II / Graffiti.pc* list (cms.dt.uh.edu) + West REGS-2009 page (dwest.web.illinois.edu/regs/graffiti.html) + DeLaViña's `resolvedT.htm`
- Aouchiche–Hansen, *A survey of automated conjectures in spectral graph theory* (LAA 432, 2010); *Open problems on graph eigenvalues studied with AutoGraphiX* (GERAD G-2012-27 / EJCO 2013)

Scoring: **Obscurity** (1 famous … 5 nearly lost), **Tractability** (1 hard witness … 5 one-eigensolve),
**Headline** (1 niche … 5 "AI settles 30-year automated conjecture"). All are finite-witness /
machine-verifiable; "Lean" column flags how clean a Lean statement is.

| # | Problem | Corpus | Obs | Tract | Head | Lean |
|---|---------|--------|-----|-------|------|------|
| N1 | **BHS Laplacian bounds #44 & #46** (last 2 open of 68) | BHS/AGX-style | 4 | 5 | 5 | ✔✔ |
| N2 | WoW 20 & 21 (inertia ≤ energy) | Graffiti | 4 | 5 | 4 | ✔✔ |
| N3 | WoW 712 & 714 (temperature vs non-positive spectrum) | Graffiti | 5 | 5 | 3 | ✔ |
| N4 | WoW 252 & 254 (minimum Laplacian gap) | Graffiti | 5 | 4 | 3 | ✔ |
| N5 | WoW gravity family 219/284/290/292/295 | Graffiti | 5 | 3 | 3 | ✘ (def risk) |
| N6 | WoW 195, 198, 262 (misc survivors) | Graffiti | 5 | 4 | 3 | ✔ |
| N7 | Randić index ≥ radius−1, and ≥ average distance | Graffiti/CGT | 3 | 4 | 4 | ✔✔ |
| N8 | Shor's peak-location conjecture (distance char. poly of trees) | Wagner-adjacent | 3 | 4 | 4 | ✔ |
| N9 | Brualdi–Cao max permanent of 312-avoiding 0-1 matrices | Wagner-adjacent | 3 | 3 | 4 | ✔ |
| N10 | Graffiti.pc #84 & #143 (largest induced tree lower bounds) | Graffiti.pc | 5 | 4 | 3 | ✔ |
| N11 | Graffiti.pc #174/#177/#179 & #199 (leaves+bipartite / Ham. path) | Graffiti.pc | 5 | 4 | 3 | ✔ |
| N12 | Graffiti.pc #247 (total domination ≥ 2·path-cover, regular) | Graffiti.pc | 5 | 4 | 3 | ✔ |

---

## N1 — BHS Laplacian-spectral-radius bounds #44 and #46 (the only two left open)  ★ top pick

**Statement.** For every connected graph G on ≥2 vertices, is the largest Laplacian eigenvalue μ(G)
bounded by the edge-max of these functions of vertex degree dᵢ and neighbor-average-degree mᵢ?

- **#44:** μ(G) ≤ max_{i∼j} √( 2 + 2( (dᵢ−1)² + (dⱼ−1)² + mᵢmⱼ − dᵢdⱼ ) )
- **#46:** μ(G) ≤ max_{i∼j} √( 2 + 2(dᵢ² + dⱼ²) − 16·dᵢdⱼ/(mᵢ+mⱼ) + 4 )

**Provenance/importance.** Brankov–Hansen–Stevanović (LAA 414, 2006) auto-generated 68 candidate
Laplacian-spectral-radius upper bounds. Al-Yakoob–Ghebleh–Kanso–Stevanović (2024) refuted 30 by
RL+exhaustive; Taieb et al. (LION 2025) refuted 2 more (#45, #48) by Monte-Carlo search;
**Damnjanović–Ha–Stevanović (arXiv:2606.14550, June 2026)** then confirmed 22 and refuted 12 more —
Theorem 1.1 explicitly states **"the only candidate bounds left open are #44 and #46."**

**Openness evidence.** Directly from the June-2026 status paper (Table 2, marked "open"). This is the
freshest possible openness certificate — literally the residue of a corpus that three separate
compute teams have been grinding down for two years.

**Witness/verifier.** One connected graph G. Verifier: compute L(G)=D−A, μ = λmax(L) (one eigensolve);
for every edge ij compute the RHS; PASS if μ − max_{ij} RHS > 1e-6. Damnjanović et al. build
counterexamples via *equitable partitions*, so the winning family is likely quotient-structured and
small (≤ ~30 vertices) — exactly what MC search under-explores.

**Difficulty.** Medium. Three teams failed to refute, and #44/#46 survived the human proof pass, so
they may be TRUE — but no proof exists and no large-n / equitable-partition-guided search has been
aimed specifically at these two. A dedicated ILP/annealing sweep over equitable-partition quotients,
plus an attempted Collatz–Wielandt proof (the technique that settled the other 22), is the play.

**Headline 5:** "AI closes the Brankov–Hansen–Stevanović list" is a clean, self-contained story.

---

## N2 — Written on the Wall 20 & 21: inertia controlled by energy  (Roucairol–Cazenave survivors)

**Statement.** For every graph G:  (20) n⁺(G) ≤ Σ_{λᵢ>0} λᵢ  and  (21) n⁻(G) ≤ Σ_{λᵢ>0} λᵢ (= E(G)/2),
where n⁺/n⁻ = number of positive/negative adjacency eigenvalues and E = energy. Source: WoW conj. 20, 21;
refutationGBR `GenerateGraph.rs` (CONJECTURE==20 / ==21) compares `poseigvec.len()`/`num_eig_neg`
against `sum_eig_pos`.

**Importance.** Directly adjacent to the *square-energy* line (min{s⁺,s⁻} ≥ n−1) that generated a wave
of 2024–2026 papers and was proved July 2026 (Liu–Tang–Zhang, arXiv:2607.18031); positive-square-energy
refinements are still appearing (arXiv:2506.07264). WoW 20/21 are the natural next automated targets in
that hot neighbourhood.

**Openness evidence.** Marked "O" (open) in the Roucairol–Cazenave 2025 Table 1; not among their refuted
set; not in the Favaron–Mahéo–Saclé (*Graffiti II*, DM 111 1993) resolved cases.

**Witness/verifier.** One graph, one dense eigensolve; PASS if n⁺−E/2 > 0 (resp. n⁻−E/2). Structured
candidates: complete multipartite / Kneser / line graphs, whose spectra are closed-form, let you scan
n≫50 analytically. Frontier: exhaustive n≤10 (1995); MCTS n≤50 (2025).

**Difficulty.** Medium; the tightness ratio is a smooth score, ideal for annealing, and the closed-form
families make the n>50 regime (never searched) cheap.

---

## N3 — WoW 712 & 714: Fajtlowicz "temperature" vs non-positive spectrum

**Statement.** With t(v)=d(v)/(n−d(v)):  (712) min_v t(v) ≤ #{i: λᵢ ≤ 0};  (714) −mean(non-positive
adjacency eigenvalues) ≤ Σ_v 1/t(v). Source: WoW conj. 712, 714; refutationGBR (CONJECTURE==712/714).

**Importance/obscurity.** "Temperature" is a pure Graffiti invention existing only in this orbit;
several temperature conjectures fell to Brewster–Dinneen–Faber (DM 147, 1995) but these two survived
30+ years. Zero dedicated literature.

**Openness.** "O" rows in Roucairol–Cazenave 2025 (714 searched to n=100). **Witness:** one graph;
712 pushes toward near-complete-multipartite graphs (few non-positive eigenvalues, high min degree),
an enumerable closed-form family. **Difficulty:** medium; trivial invariants, one eigensolve.

---

## N4 — WoW 252 & 254: minimum Laplacian spectral-gap conjectures

**Statement.** For connected G, let the min gap between consecutive sorted Laplacian eigenvalues be δL.
(252) δL ≤ Σ_v 1/dualdeg(v) (dualdeg = average neighbor degree); (254) δL ≤ Σ_v 1/odd(v)
(odd(v)=#vertices at odd distance from v). Source: WoW 252, 254; refutationGBR (CONJECTURE==252, and
the min-derivative encoding).

**Importance.** Minimum spectral gaps resist analytic control (why no proof), but are perfect for
numerics. **Openness:** "O" in Roucairol–Cazenave 2025. **Witness:** one connected graph with a
well-separated Laplacian spectrum and large dual-degree/odd-distance sums — Paley/conference/quasi-random
dense graphs are the natural family (nearly-simple spectra). **Difficulty:** medium — dense graphs tend
to repeated Laplacian eigenvalues (gap 0), so a counterexample needs a dense graph with simple spectrum;
risk it is simply true.

---

## N5 — WoW gravity-matrix family: 219, 284, 290, 292, 295

**Statement (representatives).** With the WoW gravity matrix Gr(G)[u,v] = (1/(n−1))·d(u)d(v)/dist(u,v):
219 (triangle-free): λ₂(Gr) ≤ n(n−1)/2 − m; 292/295 (girth ≥5): smallest positive adjacency eigenvalue
(292) resp. #positive distance eigenvalues (295) ≤ n/mean(Gr); 284, 290 related gravity bounds.
Source: WoW 219,284,290,292,295; refutationGBR (CONJECTURE==219/284/290/292/295).

**Critical fidelity note.** The Aouchiche–Hansen survey uses an **erroneous** gravity definition; the
correct one is WoW p.52 = Brewster–Dinneen–Faber. Roucairol–Cazenave 2025 §5.2 show 290's status
FLIPS between the two definitions — so any attack must use the WoW/BDF definition and re-verify. This
is why the sub-family is essentially untouched for 30 years.

**Openness.** "O" rows in Roucairol–Cazenave 2025 (using the correct definition). **Witness:** one
triangle-free / girth-≥5 graph; girth constraints make SAT-modulo-symmetries (Kirchweger–Szeider SMS)
exhaustive small-n sweeps genuinely applicable — nobody has done this. **Difficulty:** harder (3);
double definitional ambiguity + girth constraints. High obscurity, lower Lean-cleanliness until the
definition is pinned down.

---

## N6 — WoW 195, 198, 262 (miscellaneous Roucairol–Cazenave survivors)

**Statement (from refutationGBR).** 195: λ₁(A) ≤ max even-distance-count `even_vec` (on graphs where
Σodd ≤ Σeven); 198: −λ₂-smallest(A) ≤ n/mean(Gr) (gravity, girth condition); 262: −λ₁ ≤ max even_vec.
Source: WoW 195/198/262; refutationGBR (CONJECTURE==195/198/262).

**Openness.** "O" rows in Roucairol–Cazenave 2025 Table 1. **Witness:** one graph + one eigensolve
(198 needs the WoW gravity definition — see N5 caveat). **Difficulty:** medium; bundle with N2/N3 in a
shared "graph → invariants → LHS−RHS" harness. Include mainly to complete the survivor sweep; 262 is
the cleanest (adjacency-only).

---

## N7 — Fajtlowicz Randić-index conjectures: R(G) ≥ r(G)−1 and R(G) ≥ ad(G)

**Statement.** For every connected graph, (a) R(G) ≥ r(G) − 1 (R = Randić index Σ_{uv∈E}(d(u)d(v))^{−1/2},
r = radius; Caporossi–Hansen's AGX strengthening: R ≥ r for all connected graphs except even paths);
(b) R(G) ≥ ad(G) (average distance). Source: Fajtlowicz, *On conjectures of Graffiti*, DM 72 (1988) 113–118.

**Importance.** The Randić index is *the* central chemical-graph-theory invariant; these are the flagship
surviving Graffiti conjectures there (dozens of MATCH/Filomat papers). **Openness (general case):**
(a) proved only for chemical graphs Δ≤4 (Cygan–Pilipczuk–Škrekovski, MATCH 67, 2012), unicyclic/bicyclic,
cactus (arXiv:2107.00071), and radius-specific cases (Deng, Filomat 29, 2015); **general case open**.
(b) proved for trees; general open. Crucially, **all effort has been proofs — no metaheuristic/SAT
counterexample search has ever targeted the Δ≥5 regime.**

**Witness/verifier.** One connected graph with R < r−1 (resp. R < ad); both sides closed-form/BFS,
ms verification, Lean-clean. Candidate family: dense hubs joined by long subdivided legs (huge radius,
tiny Randić). **Difficulty:** medium; risk it is true (partial results strong), but Δ≥5 is unexplored.
**Headline 4:** lands in an active CGT community.

---

## N8 — Shor's peak-location conjecture for the distance characteristic polynomial of trees

**Statement (Wagner 2021, Conj. 2.7, attributed to P. Shor).** For every tree T on n vertices, the peak
index p_D(T) of the distance characteristic polynomial satisfies
⌊n/2⌋ ≤ p_D(T) ≤ ⌈ n(1 − 1/√5) ⌉.

**Importance.** The Graham–Lovász *unimodality* conjecture for the distance char. poly of trees was
proved (Aalipour et al., 2015, arXiv:1507.02341), and Collins' adjacency-peak conjecture was refuted by
Wagner 2021 — but Shor's specific **location** bounds for the distance polynomial remain the open
survivor Wagner explicitly flags (§2.4). Recent 2023–2024 work (arXiv:2407.03309; LAA 2023) extends
peak-location to Min-4PC / 2-Steiner / block-graph matrices but does **not** settle Shor for trees.

**Openness evidence.** Listed as the one open conjecture in Wagner's tree-polynomial section (2021);
no later paper found resolving it; the 2024 extensions sidestep it.

**Witness/verifier.** One tree T; compute the distance matrix (BFS), its characteristic polynomial
(exact integer arithmetic — trees give integer coefficients), locate the peak, check against the bounds.
Fully exact, Lean-formalizable (integer polynomial + inequality). **Difficulty:** medium; the search is
over trees only (small space), and exact arithmetic removes eigenvalue noise. Risk: the bound may be
provable via matching-polynomial identities (the tool used for the adjacency case).

---

## N9 — Brualdi–Cao maximum permanent of 312-avoiding 0-1 matrices

**Statement (Brualdi–Cao, Question 2.8).** Determine f_{312}(n) = max{ per(A) : A an n×n 0-1 matrix
avoiding the pattern 312 }, and the optimal constructions / limiting shape.

**Importance.** Wagner 2021 (§2.6) used the cross-entropy method + ad hoc tweaks to **disprove**
Brualdi–Cao's guessed optimum (Fibonacci−1), giving the corrected initial segment
1,2,4,8,16,32,64,120,225,424,795,1484,2809, but: optimality is only computer-proved to **n ≤ 8**, the
n=13 construction "is likely not optimal," and the growth constant c with f_{312}(n)=c^{n(1+o(1))}
(bounded 2^{0.89n} ≤ f ≤ 2^{1.15n}) and the limiting shape are **open**.

**Openness evidence.** Wagner 2021 explicitly leaves optimality (n≥9), the constant c, and the limit
shape open; the topic remains active (Brualdi–Goldwasser–Michael permanent problems, arXiv:2502.12787;
pattern-avoiding (0,1)-matrices, arXiv:2005.00379) with no reported resolution.

**Witness/verifier.** For a lower-bound push: one explicit 0-1 matrix with per(A) exceeding the current
best (permanent computed by Ryser's formula — feasible to n≈20; verify with a second implementation).
For optimality at a given n: an ILP / exhaustive-with-symmetry certificate. **Difficulty:** medium-high
(permanent is #P-complete, so exact optimality needs cleverness), but incremental frontier-pushing
(a better construction at some n∈[9,25]) is a concrete, verifiable finite witness. **Headline 4.**

---

## N10 — Graffiti.pc (Written on the Wall II) #84 & #143: largest-induced-tree lower bounds

**Statement.** Let t(G) = #vertices in the largest induced subgraph that is a tree.
(#84, 2004) If G is connected then t(G) ≥ 2r(G)/δ(G) (r=radius, δ=min degree).
(#143, 2005) If G is connected and not a tree then t(G) ≥ (g(G)+1)/δ'(G) (g=girth, δ'=second-smallest
degree). Source: DeLaViña, Graffiti.pc / WoW II; presented on West's REGS-2009 page.

**Importance/obscurity.** DeLaViña's Graffiti.pc corpus is a distinct automated engine (Dalmatian
heuristic) barely mined outside a small circle; these induced-subgraph bounds have no dedicated
follow-up literature. **Openness:** not listed among DeLaViña's `resolvedT.htm` resolved conjectures,
still presented as open on West's page (verify against DeLaViña before a solve run — residual risk).

**Witness/verifier.** A single connected graph G violating the bound. t(G) (max induced tree /
maximum-induced-forest that is connected) is NP-hard in general but trivial to *verify* for a fixed
witness (check the claimed induced tree, and that no larger one exists only needs to be certified for
the counterexample size — small graphs). r, δ, g, δ' are elementary. **Difficulty:** medium; witness
verification easy, search benefits from targeting high-radius low-min-degree graphs.

---

## N11 — Graffiti.pc #174/#177/#179 (L+b lower bounds) and #199 (Hamiltonian-path sufficient condition)

**Statement.** L(G) = max leaves over spanning trees; b(G) = #vertices in largest induced bipartite
subgraph; s(G) = local independence number; α = independence number; γ = domination number.
(#174/#177/#179, 2005) L(G)+b(G) ≥ each of: |V|+s(G)−1, 2α(G)+δ'(G), Δ(G)+s(G)+γ(G).
(#199, 2006) If G is connected with κ(G) ≥ t(G)−2 then G has a Hamiltonian path (sharp: equality holds
for K_{r,r+1} which has a Ham. path; just fails for K_{r,r+2} which does not). Source: Graffiti.pc /
West REGS-2009. DeLaViña–Waller proved only the weaker L+b ≥ |V|+⌈s/2⌉ (#174) and L+b ≥ 2α+1 (#177).

**Openness.** #199 and the full-strength #174/#179 not in `resolvedT.htm`; West's page presents them as
open (verify). **Witness:** one graph — for #174/#179 an eigen-free invariant check; for #199 a graph
with κ ≥ t−2 and **no** Hamiltonian path (Ham-path non-existence is the certificate — verifiable by
exhaustive DP for small n, and κ,t are polynomial). **Difficulty:** medium; #199 is a Boolean
existence witness (either a counterexample graph, or a proof), very clean to state in Lean.

---

## N12 — Graffiti.pc #247: total domination vs path cover for regular graphs

**Statement (2007).** If G is a connected **regular** graph then γ_t(G) ≥ 2p(G), where γ_t = total
domination number and p(G) = minimum number of pairwise-disjoint paths covering V(G). Source:
Graffiti.pc; West REGS-2009 (with proof notes). Known: easy for 1- and 2-regular; 3-regular follows from
Reed's p(G) ≤ (n+2)/9 bound (DeLaViña–Liu–Pepper–Waller–West, Congr. Numer. 185, 2007); **general
r-regular open.**

**Importance/obscurity.** A crisp regular-graph inequality between two classical invariants; the
regularity hypothesis is essential (fails for stars) and equality holds for disjoint unions of cliques —
a clean tightness structure. **Openness:** general r ≥ 4 open per the REGS notes; verify against later
DeLaViña–Pepper total-domination papers (residual risk). **Witness:** one r-regular graph with
γ_t < 2p — both invariants NP-hard but easy to *verify* for a fixed small witness (exhibit the total
dominating set achieving γ_t and the path cover achieving p). **Difficulty:** medium; targeted search
over 4- and 5-regular graphs (SMS-generable) is the unexplored regime.

---

## Recommendations (ranked by expected value per unit compute)

1. **N1 (BHS #44/#46)** — freshest openness certificate (June 2026), single-eigensolve witness,
   equitable-partition structure the prior MC search under-explored, and a self-contained headline
   ("last two of 68"). Highest priority.
2. **N2 (WoW 20/21)** — riding the just-proved square-energy wave; closed-form spectral families make
   the never-searched n>50 regime trivial.
3. **N7 (Randić ≥ radius−1)** — flagship CGT conjecture where *nobody has ever run counterexample
   search* on the Δ≥5 regime; high headline value in an active community.
4. **N8 (Shor peak location)** and **N9 (Brualdi–Cao permanent)** — Wagner-adjacent, exact-arithmetic
   witnesses, concrete finite frontier to push.
5. **N3/N4/N6** — cheap to bundle into the shared Graffiti harness (graph → invariants → LHS−RHS);
   run alongside N2.
6. **N10/N11/N12 (Graffiti.pc)** — highest obscurity, distinct corpus, but **require a fidelity/priority
   pass against DeLaViña's resolved lists first** (some may have been settled in papers not indexed).
7. **N5 (gravity family)** — maximal obscurity but blocked on the definitional ambiguity; only attack
   after pinning the WoW-p.52 gravity definition (and expect Lean-formalization friction).

**Shared harness note.** N2–N6 reuse one loop; the refutationGBR Rust file
(`src/models/conjectures/GenerateGraph.rs`) contains reference implementations of every exotic invariant
(temperature, dual degree, even/odd vectors, gravity matrix, Randić) and is the ground-truth encoding to
cross-check any Python/Lean statement against — essential given the documented A–H-survey definition
errors.

**Cross-check against exclusions.** Verified NOT to select: Graffiti 197 (refuted, C₁₇), 137/139/29/30/
289/301/302/321/166/189/711/715 (refuted), 322 (definition-dependent), BHS #45/#48 (refuted by Taieb
2025) and the 12 refuted by Damnjanović–Ha–Stevanović 2026, Wagner's A–H 2.1/2.3/2.4 & Brualdi–Cao
*guess* (refuted), transmission-regularity/DL-cospectrality (resolved by Wagner 2021), Graham–Lovász
unimodality (proved 2015), square-energy min{s⁺,s⁻}≥n−1 (proved 2026).
