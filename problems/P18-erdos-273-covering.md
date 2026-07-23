# P18 — Erdős #273: covering system with all moduli of the form p−1, p ≥ 5 prime

**Statement.** Does there exist a finite covering system of the integers (congruences aᵢ mod nᵢ
covering every integer) in which every modulus nᵢ = p−1 for some prime p ≥ 5 (moduli drawn from
{4, 6, 10, 12, 16, 18, 22, 28, 30, 36, …}), with distinct moduli as required by the covering-system
convention used in the source — VERIFY the exact convention (distinct vs repeated moduli) against
Erdős–Graham 1980 p.24 and https://www.erdosproblems.com/273 before anything else.

**Why it matters.** Selfridge solved the p = 3 variant (moduli dividing 360); this is the surviving
sibling. Tied to primitive-root/Sierpiński covering machinery. The statement is already formalized
in Lean (Google DeepMind Formal Conjectures repo — find and reuse it; fidelity-check it too).

**Openness.** erdosproblems.com/273 marked open (Oct 2025 edit); the 2026 Adenwalla resolution of
neighboring #204 (arXiv:2501.15170) confirms the cluster is active but #273 untouched. Run the
widened priority check (GitHub/Zenodo/OpenReview) per context/METHODOLOGY.md.

**Witness.** A finite list of congruences. Verifier: 10 lines — check each modulus+1 is a prime ≥ 5
and every residue mod lcm is covered. Exact, instant, ideal Lean `decide` target.

**Attack.** Set cover over Z/L for smooth L = lcm of many usable p−1 values (2^a·3^b·5^c·7^d…);
ILP/SAT exact cover; Selfridge's 360 construction as structural seed; reuse P15 machinery. Density
heuristic: Σ 1/(p−1) diverges over usable moduli, so a construction plausibly exists.

Obs 4 / Tract 4 / Headline 4 (an Erdős-problem resolution with a Lean witness).
