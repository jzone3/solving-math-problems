# Graffiti conjectures 39 & 40 — resolved TRUE (proof + Lean formalization)

Self-contained verification package for a math researcher.

## The claim

For every finite connected simple graph G:

- **Conjecture 39**: dev(D) ≤ n⁺(G)
- **Conjecture 40**: dev(D) ≤ n⁻(G)

where dev(D) is the population standard deviation of all n² ordered entries of the distance
matrix (diagonal included), and n⁺/n⁻ are the numbers of positive/negative adjacency
eigenvalues counted with multiplicity.

**Both are TRUE.** Proof: dev(D) ≤ diam/2 ≤ ⌊(diam+1)/2⌋ ≤ min(n⁺, n⁻), via Popoviciu's
inequality, the fact that a diametral geodesic is an induced path, and eigenvalue interlacing.
Full write-up: `PROOF.md`.

## Original statement

`wow-july2004.pdf` — Fajtlowicz, *Written on the Wall* (July 2004 revision), entries 39 and 40:

> 39. The deviation of the distance matrix is not more than the number of positive eigenvalues.
> 40. The deviation of the distance matrix is not more than the number of negative eigenvalues.

Note the PDF's Type-3 fonts break text extraction; read it visually. The operational
definitions above match the encoding used by Roucairol–Cazenave (ECAI 2025,
`roucairol-cazenave-2025.pdf`, arXiv:2409.18626), whose Table 1 lists 39/40 as open after
searching all graphs and trees to n = 50; see their Rust source
(github.com/RoucairolMilo/refutationGBR) for the exact conventions.

## How to verify

1. **Read the proof** (`PROOF.md`) — 4 steps, elementary.
2. **Numeric spot-check** (`verify.py`, needs numpy/networkx):
   `python3 verify.py` — validates the inequality chain on exhaustive small graphs + random graphs.
3. **Adversarial review** (`ADVERSARIAL-REVIEW.md`) — an independent hostile check of every step
   with a from-scratch exact-arithmetic verifier (exhaustive n ≤ 7, nine deviation conventions),
   statement-fidelity audit against WoW and RC-2025, and a priority search.
4. **Lean formalization** (`lean/`): machine-checked end-to-end in Lean 4 + mathlib.
   ```
   cd lean && lake exe cache get && lake build
   ```
   Main theorems: `P08.graffiti_conjecture_39/40` in `P08/Main.lean` (encoding documented in the
   module docstring). No `sorry`, no added axioms; `#print axioms` yields
   `[propext, Classical.choice, Quot.sound]`.

## Novelty / prior art

- No published resolution of Graffiti 39/40 found (details in `ADVERSARIAL-REVIEW.md` §4).
- The spectral half, diam(G) ≤ 2·min(n⁺, n⁻), IS published: Geng–Wu–Wang, *Linear and
  Multilinear Algebra* 68 (2020) 1633–1641; sharpened by Xu–Zhen–Wong (arXiv:2312.02680).
  The contribution here is connecting it with the (elementary) Popoviciu bound dev(D) ≤ diam/2
  to settle the two conjectures — plus the formal proof.
- Residual risk: Favaron–Mahéo–Saclé, Discrete Math. 111 (1993) is paywalled and was not read
  directly; indirect evidence (RC-2025's audit, WoW's own annotations) indicates 39/40 were not
  resolved there.
