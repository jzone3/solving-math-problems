# P19 — Wide Partition Conjecture (Chow–Taylor / Latin Tableau Conjecture)

**Statement.** A partition λ is **Latin** iff it is **wide**. λ is Latin if there is a tableau of
shape λ whose i-th row is a permutation of {1,…,λᵢ} and all columns have distinct entries; λ is wide
if μ ⪰ μ′ (dominance order vs conjugate) for every subpartition μ ⊆ λ. Latin ⇒ wide is known; the
converse is the conjecture. VERIFY exact definitions against the original: Chow–Fan–Goemans–Vondrák,
Adv. Appl. Math. 31 (2003) 334–358, and the June-2025 reformulation Chow–Tiefenbruck, Electron. J.
Combin. 32(2) #P48.

**Why it matters.** Implied by Rota's basis conjecture (free-matroid case): a counterexample refutes
a natural strengthening path to Rota — headline 5 if false. Fresh 2025 activity proves it's cared
about and open.

**Witness.** A single wide-but-not-Latin partition λ. Verifier: (a) wideness — dominance check over
all subpartitions (prune); (b) non-Latinness — UNSAT/exact-cover proof that no Latin tableau exists
(CP-SAT with a DRAT certificate where possible). Fully mechanical, finite, Lean-formalizable.

**Attack.** Enumerate wide partitions by size (they're sparse); test Latinness with CP-SAT; bias
toward near-tight wide partitions (many dominance equalities — where Rota-style obstructions live).
No systematic exhaustive check appears published, so "wide ⇒ Latin verified for |λ| ≤ N" is itself a
new citable frontier: report the frontier reached regardless of outcome.

**Priority.** Run the widened check (GitHub/Zenodo/OpenReview + literature) per
context/METHODOLOGY.md before claiming.

Obs 4 / Tract 4 / Headline 4 (5 if false).
