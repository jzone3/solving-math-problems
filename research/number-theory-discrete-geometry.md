# Domain research: Number theory, additive combinatorics, discrete geometry

Domain slug: `number-theory-discrete-geometry`
Researched: 2026-07-22. Each candidate was checked to still be open as of July 2026
(including a check of the erdosproblems.com pages and the teorth/erdosproblems
"AI contributions" wiki, last updated 2026-06-30, for AI-assisted resolutions).

Scoring (per context/PLAN.md): **Obscurity** 1–5 (5 = essentially untouched by modern
compute), **Tractability** 1–5 (5 = a finite witness is plausibly findable at reachable sizes
with SAT/ILP/metaheuristics/LLM-guided search).

---

## 1. Odd covering system (Erdős–Selfridge, Erdős Problem #7)

- **Statement.** Is there a covering system of the integers (finite set of residue classes
  $a_i \pmod{n_i}$ whose union is $\mathbb{Z}$) with all moduli $n_i$ **distinct, odd, and $>1$**?
  Source: https://www.erdosproblems.com/7 (open as of 2026-07-21); Open Problem Garden
  https://www.openproblemgarden.org/op/odd_incongruent_covering_systems; Filaseta–Ford–Konyagin,
  "S-covers" (2000) reporting the Erdős \$25 / Selfridge \$2000 prizes.
- **Provenance & importance.** Erdős & Selfridge (with Schinzel), one of the most-cited open
  covering-system questions; prizes on both sides (Erdős \$25 for nonexistence, Selfridge \$2000
  for an explicit example). Central to the covering-systems community post-Hough/BBMST.
- **Status / frontier.** Squarefree odd case ruled out (Balister–Bollobás–Morris–Sahasrabudhe–Tiba,
  2022). Hough–Nielsen (2019): some modulus divisible by 2 or 3. BBMST: any odd covering must have
  lcm of moduli divisible by 9 or 15. No serious published *search* for an explicit odd covering
  with non-squarefree moduli — the constraints (lcm divisible by 9 or 15, moduli with repeated
  prime factors) sharply narrow the search space, and nobody appears to have run SAT/ILP on it.
- **Finite witness.** A covering system IS a finite object: a list of pairs $(a_i, n_i)$.
  Verification = check every residue mod lcm is covered (seconds). Erdős believed one exists.
  Witness size unknown; plausibly hundreds–thousands of congruences over an lcm like
  $3^a 5^b 7^c 11^d \cdots$.
- **Attack.** Fix a candidate lcm $N$ (odd, divisible by 9 or 15); covering with distinct odd
  divisors of $N$ is an exact-cover/set-cover instance → SAT or ILP with symmetry breaking;
  also greedy/prime-by-prime construction à la Nielsen/Owens adapted to odd moduli.
- **Obscurity: 4** — famous inside covering systems, but no evidence of any modern SAT/ILP attack
  on explicit construction. **Tractability: 2** — search space over lcm choices is enormous and
  the answer may be "no"; but any hit is a \$2000-prize result.

## 2. Covering system with minimum modulus > 42

- **Statement.** Construct a covering system with distinct moduli all $> 42$ (Erdős's minimum
  modulus problem, quantitative version). Known: minimum modulus $\le 616{,}000$
  (Balister–Bollobás–Morris–Sahasrabudhe–Tiba, "On the Erdős covering problem", 2022; improving
  Hough's $10^{16}$, Annals 2015). Largest known construction: minimum modulus **42**
  (T. Owens, BYU MSc thesis, 2014, https://scholarsarchive.byu.edu/etd/4329), improving
  Nielsen's 40 (2009).
- **Provenance & importance.** Erdős 1950; the minimum-modulus problem was THE covering-system
  question for 60 years. The residual gap $42 \le d_{\max} \le 616{,}000$ is the community's
  standing quantitative challenge (see Balister's 2018 Oxford slides, memphis.edu).
- **Status / frontier.** Constructive record 42 has stood since **2014**, produced by hand
  (prime-by-prime greedy with clever hole-filling). No published computational optimization
  (ILP/SAT/branch-and-bound over prime-power grids) has ever been applied.
- **Finite witness.** A covering system with min modulus 43+ — finite list of congruences,
  machine-checkable instantly. Owens's 42 system uses primes up to ~similar sizes; a 43–50
  record likely needs a few thousand congruences.
- **Attack.** Formalize Nielsen/Owens's prime-by-prime "distortion" method as an optimization:
  at each prime decide how classes are covered — a huge but structured set-cover; LP relaxations
  of the FFKPY reciprocal-sum inequality can guide feasibility; simulated annealing / ILP
  column generation over divisor lattices. Any improvement (min modulus 43) is publishable.
- **Obscurity: 5** — nobody has thrown compute at the constructive side since 2014.
  **Tractability: 4** — incremental record-breaking is realistic; verification trivial.

## 3. Rational Diophantine septuple

- **Statement.** Does there exist a set of 7 distinct nonzero rationals $\{q_1,\dots,q_7\}$
  such that $q_iq_j + 1$ is a square of a rational for all $i<j$?
  Source: Dujella, "Open problems on Diophantine m-tuples", Problem 3.2,
  https://web.math.pmf.unizg.hr/~duje/pdf/open2.pdf; overview https://dujella.github.io/ratio.html.
- **Provenance & importance.** The central open existence question of the Diophantine m-tuples
  community (Dujella's life's work; traces to Diophantus/Fermat/Euler). Infinitely many rational
  sextuples exist (Dujella–Kazalicki–Mikić–Szikszai 2017), so 7 is exactly the frontier.
- **Status / frontier.** "Almost septuples" exist: sets of 7 rationals where **20 of 21** products
  +1 are squares (Gibbs 2016; Dujella–Kazalicki–Petričević 2018), e.g.
  $\{243/560, 1147/5040, 1100/63, 7820/567, 95/112, 38269/6480, 196/45\}$. Searches have been
  elliptic-curve-parametrization driven, not large-scale compute; no known SAT/lattice/massive
  enumeration attack.
- **Finite witness.** 7 rationals; verification = 21 squareness checks in exact arithmetic.
- **Attack.** Extend known sextuple families: for each of the (infinitely many parametrized)
  sextuples, a 7th element must satisfy 6 simultaneous congruence/square conditions →
  intersect conics / search rational points on associated curves of genus ≤ 2; large distributed
  height-bounded search over the DKMS parametrization; LLM-guided algebraic identities.
- **Obscurity: 4** — well known to a small community, unknown outside; near-misses suggest
  reachable. **Tractability: 3** — witness heights may be large, but structure is rich and the
  near-miss density is encouraging.

## 4. D(n)-quadruples for n ∈ {−3, 3, 5, 8, 12, 20} (Dujella's exceptional set)

- **Statement.** For $n \in \{-3, 3, 5, 8, 12, 20\}$: does there exist a set of four distinct
  positive (nonzero) integers $\{a,b,c,d\}$ with $a_ia_j + n$ a perfect square for all pairs?
  Source: Dujella, "Open problems on Diophantine m-tuples", **Problem 5.1**
  (https://web.math.pmf.unizg.hr/~duje/pdf/open2.pdf); background https://dujella.github.io/dn.html.
- **Provenance & importance.** Dujella (1993) proved D(n)-quadruples exist for ALL
  $n \not\equiv 2 \pmod 4$ outside $S = \{-4,-3,-1,3,5,8,12,20\}$. The cases $n=-1$ (and by
  extension $-4$) were resolved (no quadruple; Bonciocat–Cipu–Mignotte 2022). The remaining six
  values are the entire unresolved exceptional set; conjectured to admit no quadruple.
- **Status / frontier.** Only sporadic triple-extension nonexistence results; no published
  exhaustive search bound for these six n values is prominent in the literature — the community
  works via Pell-equation/Baker-method case analysis, not compute.
- **Finite witness.** A counterexample to the conjecture = 4 integers; verification = 6 square
  checks. (A quadruple would be a major surprise; conversely, pushing an exhaustive frontier to
  e.g. $\max a_i \le 10^{12}$ via the triple-extension structure is a publishable negative result.)
- **Attack.** Enumerate D(n)-triples (Pell-structured, sparse) up to a large bound, test all
  fourth-element extensions via the known reduction to finitely many Pellian intersections;
  direct GPU brute force for small elements; ILP/CRT sieving mod many primes.
- **Obscurity: 4** — inside-community famous, zero modern compute visible.
  **Tractability: 2** — conjecture says no witness exists; value is frontier-pushing + slim
  upset chance.

## 5. Planar integral point set of 8 points in general position

- **Statement.** Do there exist 8 points in the plane, no 3 collinear, no 4 concyclic, with all
  pairwise distances integers? Source: Kreisel & Kurz, "There are integral heptagons, no three
  points on a line, no four on a circle", Discrete Comput. Geom. 39 (2008)
  (https://doi.org/10.1007/s00454-007-9038-6) — solved n=7, explicitly leaving n=8 open;
  status confirmed open in 2026: "Particular examples of planar integral point sets and their
  classification" (2026, https://doi.org/10.46698/q7071-3025-8385-h): "no known example of a
  PIPS of cardinality 8 in general position".
- **Provenance & importance.** A famous question of Erdős (rational-distance sets); the 7-point
  solution was a minor sensation in discrete geometry. Connected to the Erdős–Ulam problem.
- **Status / frontier.** Kreisel–Kurz found the 7-point sets by exhaustive diameter-bounded
  search (~2007 hardware, diameter up to ~15000 in restricted classes). Two decades of Moore's
  law + better number-theoretic sieves (characteristic q, coordinates in $\mathbb{Q}(\sqrt q)$)
  have NOT been applied at scale to n=8.
- **Finite witness.** 8 points with integer coordinates in a quadratic field; verification =
  28 integer-distance checks + collinearity/concyclicity checks.
- **Attack.** Extend the Kurz machinery: fix characteristic q, enumerate integral triangles /
  point ladders over one baseline, prune by distance-integrality mod small primes; GPU-friendly.
  Alternatively grow from the known 7-point sets (they have structure: points on few generalized
  circles) or from "7-clusters" (Kurz 2013).
- **Obscurity: 4** — known to a handful of researchers; last real compute 2007–2013.
  **Tractability: 3** — witness may have large diameter, but hardware gap since 2008 is huge.

## 6. Lonely runner conjecture for 9 runners

- **Statement.** For every set of 8 distinct positive integer velocities $v_1<\dots<v_8$ there is
  a time $t$ with $\|v_i t\| \ge 1/9$ for all $i$ (9 runners incl. the stationary one).
  Source: the $k=8$ case was just proved: "The lonely runner conjecture holds for eight runners",
  arXiv:2509.14111 (Sept 2025), via computer verification + the finite-checking bounds of
  Malikiosis–Santos–Schymura ("Linearly exponential checking is enough for the LRC", Forum Math.
  Sigma 2025) and Tao (2018). The authors state: "minor improvements to our approach could be
  enough to solve the cases of 9 or 10 runners."
- **Provenance & importance.** Wills 1967 / Cusick 1973; major problem in Diophantine
  approximation / view-obstruction; every new k is a publication.
- **Status / frontier.** k ≤ 8 proved (as of Sept 2025); k = 9 open. Finite check: velocities
  bounded by $\binom{n+1}{2}^{n-1}$-type bounds; the k=8 proof needed clever pruning, not raw
  enumeration.
- **Finite witness.** This is a *verification* target rather than counterexample hunt: the
  reduction makes "LRC holds for 9 runners" equivalent to a finite (huge but prunable)
  computation. A counterexample, if it exists, is a single 8-tuple of velocities — also finite.
- **Attack.** Reimplement/scale the arXiv:2509.14111 pruning pipeline (covering arguments on
  velocity tuples, LP certificates per branch) with more compute + better symmetry reduction;
  interval-arithmetic certificates for each surviving tuple.
- **Obscurity: 2** — LRC is semi-famous and the subcommunity is actively computing here (2025).
  **Tractability: 4** — the authors themselves say 9 is within reach; it's a compute race.

## 7. No-three-in-line: D(61) = 122?

- **Statement.** Can one place $2n = 122$ points on the $61\times 61$ grid with no three
  collinear? Source: "Constraint Satisfaction Programming for the No-three-in-line Problem",
  arXiv:2602.07751 (Feb 2026), which found 2n-point configurations for all $n \le 60$ and states
  the smallest unknown case is now $n = 61$ (they attempted 61 and 62 without success).
  Background: Dudeney 1906; Guy–Kelly conjecture that 2n fails for all large n.
- **Provenance & importance.** Classic combinatorial geometry problem; the Guy–Kelly heuristic
  (corrected constant $\pi/\sqrt3 \approx 1.814$) predicts 2n placements die out — every new n
  either extends the record or (if exhaustively refuted) would be the first counter-instance
  ever found, a big deal.
- **Status / frontier.** n ≤ 60 solved (Feb 2026, CP-SAT with symmetry reduction). n = 61 open;
  the recent authors' methods stalled there.
- **Finite witness.** 122 grid points; verification = $\binom{122}{3}$ collinearity checks
  (instant). Nonexistence would need exhaustive SAT/UNSAT proof — much harder but also finite.
- **Attack.** SAT/CP-SAT with stronger symmetry breaking (the 2026 paper used only some
  symmetries), incremental construction from n=60 solutions, ILP with line constraints,
  simulated annealing over near-solutions to seed SAT.
- **Obscurity: 2** — just attacked with modern CP-SAT (Feb 2026); we'd be competing with fresh
  compute. **Tractability: 3** — the marginal-improvement game is well-defined and verification
  is trivial; but the low-hanging fruit was just picked.

## 8. Ninth primary pseudoperfect number / Znám's problem length 9

- **Statement.** Does there exist a squarefree $N = p_1\cdots p_9$ with 9 distinct prime factors
  satisfying $\sum_{i} \frac{1}{p_i} + \frac{1}{N} = 1$ (a primary pseudoperfect number, PPN,
  with $k=9$)? Source: Butske–Jaje–Mayernik, "On the equation $\sum_{p|N} 1/p + 1/N = 1$ ...",
  Math. Comp. (2000) (https://doi.org/10.1090/s0025-5718-99-01088-1) — proved exactly one PPN
  exists for each $k \le 8$; Sondow–MacMillan, arXiv:1812.06566, **Conjecture 1**: exactly one
  $K_9$ exists with $K_9 \equiv 258 \pmod{288}$; OEIS A054377. Closely tied to Znám's problem
  (Brenton–Vasiliu, Math. Mag. 2002) and Egyptian-fraction representations of 1.
- **Provenance & importance.** Egyptian fractions / Sylvester sequence / Giuga numbers /
  algebraic surface singularities community; the $k \le 8$ result is a minor classic of
  computational number theory. A $K_9$ would extend a 26-year-old table.
- **Status / frontier.** Exhaustive for $k \le 8$ (year 2000 compute!). For $k=9$ Curtiss's bound
  gives $K_9 < S_{10}$ (a 106-digit number) — naive search hopeless, but the branch-and-bound
  over prime chains (each prime bounded by Sylvester-like recursions) is highly prunable and has
  never been rerun on modern hardware.
- **Finite witness.** 9 primes; verification = one exact rational arithmetic identity.
- **Attack.** Depth-first search over increasing primes $p_1 < \dots < p_9$ with interval pruning
  ($\sum 1/p_i$ must stay in a shrinking window), exactly the BJM algorithm scaled 10^6×;
  final-prime step reduces to a divisibility/factoring condition — batch with ECM. Also mod-288
  congruence from Sondow–MacMillan prunes hard.
- **Obscurity: 5** — untouched since 2000; near-zero global fame. **Tractability: 3** — search
  space deep but extremely structured; even a partial exhaustion (e.g. $p_1 \le 13$ branch) is a
  citable frontier push.

## 9. Perfect difference families with block size 5: smallest open orders

- **Statement.** A $(v,k,1)$-perfect difference family (PDF) on $\mathbb{Z}_v$... for $k=5$
  (necessary condition $v \equiv 1 \pmod{40}$... precisely: blocks whose differences cover
  $\{1,\dots,(v-1)/2\}$ exactly once): determine existence for the small open orders.
  Source: Ge, Miao, Sun, "Perfect difference families, perfect difference matrices, and related
  combinatorial structures", J. Combin. Des. 18 (2010) (https://doi.org/10.1002/jcd.20259):
  "The existence problems of perfect difference families with block size $k$, $k = 4, 5$ ... are
  two outstanding open problems in combinatorial design theory for more than 30 years."
  For $k=4$ they settled all $t \le 1000$ ($v = 12t+1$) except the definite exceptions $t=2,3$;
  the $k=5$ problem remains wide open with only sporadic constructions.
- **Provenance & importance.** PDFs are the exact objects behind optimal optical orthogonal
  codes (OOCs) and difference triangle sets — coding-theory + design-theory communities both
  care; Handbook of Combinatorial Designs (Abel–Buratti chapter) lists the open cases.
- **Status / frontier.** $k=5$: only algebraic constructions for special orders; small open
  orders have never (visibly) been attacked with SAT or clique-search on Cayley-difference
  structures. (Exact list of smallest open $v$ to be extracted from the Handbook/Ge–Miao–Sun
  tables during Phase 2.)
- **Finite witness.** A PDF is a small list of base blocks (each a 5-subset of $\mathbb{Z}_v$);
  verification = multiset-equality of differences. For the smallest open orders the object is
  tiny (tens of blocks).
- **Attack.** SAT/CP encoding (each unordered difference hit exactly once — an exact-cover
  instance), clique search in the "compatible blocks" graph, simulated annealing with
  difference-multiset energy; symmetry breaking by multiplier subgroups.
- **Obscurity: 5** — deeply community-internal; no modern-compute evidence.
  **Tractability: 4** — exact-cover instances of this size are prime SAT territory.

## 10. Three consecutive powerful numbers (Erdős–Mollin–Walsh)

- **Statement.** Do there exist three consecutive integers $4k-1, 4k, 4k+1$ all powerful
  ($p \mid n \Rightarrow p^2 \mid n$)? Conjectured NO (Erdős; Mollin–Walsh 1986).
  Source: Mollin–Walsh, "On powerful numbers", Int. J. Math. Math. Sci. 9 (1986); recent
  activity: arXiv:2503.21485 (2025, special-case nonexistence), arXiv:2605.06697 (May 2026,
  3-AP's of powerful numbers with $d = 2\sqrt N + 1$, conjecturing consecutive-in-sequence
  progressions exist). erdosproblems.com tag: powerful numbers.
- **Provenance & importance.** Erdős conjecture with a striking equivalent (Mollin–Walsh):
  a witness exists iff some $m \equiv 7 \pmod 8$ squarefree has fundamental unit
  $T + U\sqrt m$ with an odd $k$ making $T_k$ even-powerful and $U_k \equiv 0 \pmod m$ odd.
  Granville: existence relates to Wieferich-type prime statements.
- **Status / frontier.** No published large-scale search of the Pell-equation criterion; direct
  search over powerful numbers is heavily bounded (~$10^{22}$ scale by density arguments) but the
  *structured* Pell search (per $m \equiv 7 \bmod 8$, iterate unit powers, test powerfulness of
  $T_k$) is cheap per-m and appears never systematically pushed.
- **Finite witness.** A single $k$ (three integers); verification = two factorizations.
- **Attack.** For each squarefree $m \equiv 7 \pmod 8$ up to $10^6$: compute fundamental unit
  (continued fractions), iterate odd powers with modular pre-tests (powerful-mod-small-primes
  sieve), escalate to full factorization only on survivors. Pure structured search, GPU-able.
- **Obscurity: 3** — the conjecture is moderately known; the Pell-criterion search angle is
  untouched. **Tractability: 2** — conjectured nonexistent and heuristically ultra-sparse; but
  the search has never been done and a negative frontier is publishable.

## 11. Exact values of the unit-distance function u(n), n = 22–30

- **Statement.** Determine $u(n)$ = max number of unit distances among $n$ points in the plane
  (OEIS A186705) for $n = 22,\dots,30$, where lower/upper bounds currently disagree.
  Source: "The Erdős unit distance problem for small point sets", arXiv:2412.11914 (Dec 2024):
  exact values now known for all $n \le 21$; gaps remain for $22 \le n \le 30$ (e.g. previous
  state $57 \le u(21) \le 68$ was closed to equality). Lower-bound side: Engel et al. (Moser
  lattice searches), Agoston–Pálvölgyi (2022).
- **Provenance & importance.** The finite version of Erdős's \$500 unit-distance problem;
  exact small values feed Polymath16 / chromatic-number-of-the-plane bounds.
- **Status / frontier.** n ≤ 21 exact (2024); the same group's technique (forbidden-subgraph
  generation + algebraic embedder) stalls beyond 21 for compute reasons.
- **Finite witness.** For lower bounds: a point configuration (algebraic coordinates) — instantly
  checkable. For upper bounds: an exhaustive F-free graph enumeration certificate.
- **Attack.** Improve lower bounds via beam search over Moser-ring/lattice configurations
  (arXiv:2406.15317 approach) and via SMT-based embeddability of dense candidate graphs;
  each closed n is a citable result.
- **Obscurity: 2** — active compute community (2024–2026). **Tractability: 4** — incremental,
  well-defined, cheap verification; but we compete with specialists.

---

## Ranking summary (obscurity × tractability, gut-weighted)

| # | Problem | Obs | Trac | Note |
|---|---------|-----|------|------|
| 2 | Covering system min modulus > 42 | 5 | 4 | Best overall fit: pure construction record, untouched since 2014 |
| 9 | (v,5,1)-perfect difference families | 5 | 4 | Tiny SAT-ready witnesses, 30+year open, zero compute |
| 8 | Ninth primary pseudoperfect number | 5 | 3 | 2000-era exhaustion, massively prunable DFS |
| 5 | 8-point integral point set, general position | 4 | 3 | 2007-era search frontier, GPU-able |
| 3 | Rational Diophantine septuple | 4 | 3 | Near-misses (20/21 conditions) known |
| 6 | Lonely runner, 9 runners | 2 | 4 | Compute race; authors say it's within reach |
| 1 | Odd covering system | 4 | 2 | \$2000 prize; hard but SAT-encodable per lcm |
| 11 | u(n) for n=22–30 | 2 | 4 | Incremental but reliable |
| 7 | No-three-in-line D(61) | 2 | 3 | Freshly attacked Feb 2026 |
| 4 | D(n)-quadruples, n ∈ {−3,3,5,8,12,20} | 4 | 2 | Frontier-push value |
| 10 | Three consecutive powerful numbers | 3 | 2 | Structured Pell search never done |

## Excluded during research (resolved / unsuitable)

- **Lonely runner k=8**: proved Sept 2025 (arXiv:2509.14111) — moved target to k=9.
- **D(1) and D(4) quintuples**: nonexistence proved (He–Togbé–Ziegler 2019; Bliznac
  Trebješanin–Filipin 2018). **D(−1), D(−4) quadruples**: resolved (Bonciocat–Cipu–Mignotte).
- **Odd squarefree covering**: ruled out (BBMST 2022).
- **No-three-in-line n=47..60**: solved Feb 2026 (arXiv:2602.07751).
- **Erdős #297 (number of Egyptian-fraction subsets)**: resolved 2024 (Liu–Sawhney et al.).
- **Erdős–Straus 4/n**: too famous, verified to $10^{18}$ — fails obscurity/low-compute criteria.
- **Erdős #206 (greedy underapproximations)**: resolved by Kovač 2024 (measure-zero), and the
  remaining explicit-example question lacks a finite witness.
