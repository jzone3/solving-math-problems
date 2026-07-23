# P17 — WoW conjectures 20 & 21: RESOLVED (both TRUE)

**Statement** (Fajtlowicz, *Written on the Wall*, verified against the
primary source `handoff/P07/wow-july2004.pdf`, glyph-decoded; see
`runs/P17/v1/NOTES.md` §1). For a graph G with adjacency eigenvalues
λ₁ ≥ … ≥ λₙ, let n⁺/n⁻ be the numbers of positive/negative eigenvalues and
S = Σ_{λᵢ>0} λᵢ (= E(G)/2, since tr A = 0):

- **WoW 20**: n⁺(G) ≤ S.
- **WoW 21**: n⁻(G) ≤ S.

**Resolution.** Both are theorems. They follow from:

> **Theorem (Kumar–Pragada, arXiv:2607.19817, 22 Jul 2026).**
> For every graph G of order n, E(G) ≥ 2(n − α(G)).

This settles Fajtlowicz's 1980s Graffiti conjecture (the one studied via SDP
in arXiv:2509.05814). Copy of the paper:
`runs/P17/v1/kumar-pragada-2607.19817.pdf`.

**Derivation of WoW 20 & 21.** The Cvetković inertia bound gives
α(G) ≤ min{n − n⁺(G), n − n⁻(G)}, i.e. n − α(G) ≥ max{n⁺(G), n⁻(G)}.
Hence

  S = E(G)/2 ≥ n − α(G) ≥ max{n⁺(G), n⁻(G)},

which is exactly WoW 20 and WoW 21. (The paper states this corollary and
that it "resolves [Aouchiche–Hansen survey, Conjectures #20, #21, Table 6]".)

**Proof sketch of the theorem** (2 pages in the paper; hand-checked):
E(G) = 2·min{tr M : M ⪰ 0, M − A(G) ⪰ 0} (SDP formulation, Abiad et al.);
a "neighbourhood deletion inequality" n·E(G) ≥ 4m + Σ_{v} E(G − N[v])
(Lemma 2.2, by exhibiting a feasible M from the deleted subgraphs' optima);
then induction on n using α(G − N[v]) ≤ α(G) − 1:
Σ_v E(G−N[v]) ≥ Σ_v 2(n−1−deg v − (α−1)) = 2n(n−α) − 4m.

**Verification in this repo.**
- `runs/P17/v1/check_kumar_pragada.py`: numerically spot-checks Lemma 2.2,
  Theorem 1.2, and the corollary on 400 random graphs with exact α
  (complement max-clique) — 0 failures.
- `verify_corollary.py` (this directory): independent exact check, floats
  nowhere on the accept path — for a given graph it certifies
  n⁺ ≤ S and n⁻ ≤ S by Sturm root counting and rational root isolation
  (sympy over ℤ), and checks n−α ≥ max{n⁺,n⁻} with exact α by
  branch-and-bound. Run on a corpus of graphs incl. all equality cases.
- `exhaustive_exact_n7.py` (this directory): exact certification of
  max{n⁺,n⁻} ≤ S for ALL 1252 graphs with n ≤ 7 (nauty-geng), no floats on
  the accept path — PASS.
- Consistency: the extensive counterexample search in `runs/P17/v1/`
  (exhaustive n ≤ 9 and connected n = 10, annealing to n = 60, closed-form
  families incl. Kneser ≤ 200, circulants ≤ 300, W_k ≤ 200, trees ≤ 18)
  found no violation — as the theorem now guarantees.

**Attribution.** The resolution is due to Kumar & Pragada (independent
literature result found by this run's mandatory priority check; posted one
day before the run). This repo's contribution: statement fidelity against
the primary WoW source, the implication chain to WoW 20/21, machine
verification, and the negative search record.
