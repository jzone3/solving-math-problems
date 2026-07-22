# P15 — V5 (literature-first) run notes

Session: https://app.devin.ai/sessions/63d681e694694b4fb0b4f846eca6da53
Branch: runs/P15-v5

## 1. Statement re-verification against original sources (2026-07-22)

- **Owens 2014 thesis** (scholarsarchive.byu.edu/etd/4329, PDF fetched, `papers/owens-thesis.pdf`):
  confirmed — constructs a covering system with distinct moduli, minimum modulus **42**,
  using all primes up to 89 (plus a large finitizing prime). Built entirely by hand,
  prime-by-prime hole-filling in Nielsen's up-arrow notation.
- **Nielsen 2009** (J. Number Theory 129, `papers/nielsen40.pdf`): min modulus **40**, primes up to 103.
- **Hough 2015** (Annals 181): every distinct covering system has min modulus ≤ 10^16.
- **BBMST** ("On the Erdős Covering Problem: the density of the uncovered set",
  arXiv:1811.03547, Invent. Math. 2022, `papers/bbmst-uncovered.*`): Theorem 8.1 —
  min modulus ≤ **616,000**.
- Literature check for anything > 42 (Exa searches, July 2026): nothing found beating 42.
  Recent related work (Klein–Koukoulopoulos–Lemieux j-th smallest modulus 2022; squarefree-moduli
  bounds 2025; function-field analogues 2024–26) — none touches the constructive record.
  **Problem confirmed open as stated.**

## 2. KEY LITERATURE FINDING — the V5 premise as written is misdirected

The problem file suggests BBMST's machinery is "EXISTENCE machinery … semi-constructive;
extract an explicit construction from their proof at any min modulus > 42".

**This is backwards.** BBMST Theorem 8.1 (verified directly in the paper text) states:
*if all moduli are distinct and ≥ 616,000, the system does NOT cover Z.* Their distortion
method bounds the density of the UNCOVERED set from below — it is a **nonexistence
(obstruction) theorem**, exactly like Hough's. There is no covering system anywhere in
their proof to extract; the number 616,000 is where their obstruction stops working, not
where a construction lives. The same holds for Hough 2015. Nothing in the
Hough/BBMST line can produce a witness for min modulus ≥ 43.

Consequence: the only known constructive technology is the
Erdős → Krukenberg (18) → Choi (20) → Morikawa (24) → Gibson (25) → Nielsen (40) → Owens (42)
lineage: prime-by-prime hole-filling over a smooth modulus tree. V5 therefore pivots to:
digest that lineage quantitatively, then compute with it (per V5's "…and only then compute").

## 3. Digest of the constructive method (Nielsen/Owens)

Structure of Owens's 42 construction (full read of thesis):
- Universe is a tree of prime-power branches: 2^6 · 3^4 · 5^3 · 7^2 · (higher primes)^1, with
  p↑ notation = one class mod p^k for every k ≥ 1 (finitized at the end by one unused large prime).
- Start with 2↑(1); delete moduli 2,4,8,16,32 (< 42) leaving holes = classes 2^k mod 2^{k+1},
  k=1..5 (density 31/32 minus the 64↑ tail).
- Prime 3 works inside branch 1 mod 2 (3↑(2,4↑) minus moduli 6..36); primes 5,7 fill the
  2-power holes; each later prime p fills one specific residual hole by assembling p−1 (or fewer,
  using inherited coverage) "sets" from products of unused smaller-prime moduli ≥ 42.
- Bookkeeping is purely combinatorial: at each hole, count assemblable sets vs inputs needed.
  Owens: primes ≤ 89 suffice for 42 (Nielsen needed ≤ 103 for 40); the improvement came from
  relocating the prime 5 and a trick with 19.
- Owens's own conclusion: pushing past 42 "would likely need … a similar dramatic change early
  on" (placement of 3/81↑, of 5) and "would likely require even more large primes".

## 4. Budget analysis (machine-verified, `budget.py`, exact rationals)

Necessary condition sum 1/m_i ≥ 1 over distinct p-smooth moduli ≥ N:
- N=42, primes ≤ 89 (Owens's palette): available budget 3.92 (excess +2.92)
- N=43, primes ≤ 89: 3.90 (+2.90); ≤ 103: 4.15; ≤ 127: 4.46
- Crossing point is already at primes ≤ 13 for N=43.

So the naive reciprocal-sum budget is NOT the obstruction — the constructions run out of
*alignment efficiency* (each class only covers what remains uncovered in its branch), not of
raw density. The binding constraint is the per-hole set-assembly count (each prime p consumes
p−1 sets of its own). This motivates a computational search where the machine optimizes the
alignment — which no published work has done.

## 5. Computational plan (this run)

Engine A (`greedy_cover.py`): exact direct search over a smooth universe N
(profile mirrors the literature: 2^a 3^b 5^c 7^d 11 13 …). Universe residues held as a
numpy uint8 array; usable moduli = divisors of N that are ≥ target minimum modulus, each
usable once; greedy (with variants: ascending-modulus, max-gain, randomized restarts +
hole-repair) picks (modulus, residue) to maximize newly covered residues via
reshape-sum counting. Any complete cover is re-verified independently (`verify_cover.py`,
different code path: CRT-free direct sweep). Escalate N and the target min modulus as far
as memory/time allow; record the max min-modulus achieved fully automatically.

(Notes below are appended as runs complete.)

## 6. Engine A results (direct greedy over smooth Z_N, exact & verified)

| universe N | factors | L | outcome |
|---|---|---|---|
| 5040 | 2^4 3^2 5 7 | 3 | **COVER** (24 classes, verified PASS) |
| 151200 | 2^5 3^3 5^2 7 | 6 | **COVER** (verified PASS) |
| 21621600 | 2^5 3^3 5^2 7 11 13 | 9 | **COVER** (205 classes, verified PASS) |
| 21621600 | same | 12 | **COVER** (405 classes, verified PASS) |
| 21621600 | same | 14 | FAIL, best 88792/21621600 uncovered (4.1e-3) over 8 restarts |
| 129729600 | 2^6 3^4 5^2 7 11 13 | 14 | FAIL, best 63090 uncovered (4.9e-4) |
| 129729600 | same | 16 | FAIL, best 447416 (3.4e-3) |
| 129729600 | same | 18 | FAIL, best 1.3e6 (1.0e-2) |

Local-search repair (repair.py, reassign one class at a time, 300 s) moves ~1% of the
uncovered mass — hopeless: the failure is structural misalignment, not local.

Diagnosis (literature-informed): pure per-class greedy cannot discover the nested
q↑-chain alignment that all record constructions use ("keep the partial cover as densely
packed as possible", Nielsen §2 Example 2 remark). Also note the Mirsky–Newman constraint:
a perfectly disjoint (zero-overlap) distinct-moduli cover cannot exist, so the necessary
overlap has to be placed intelligently — exactly what the q↑ tail-filling trick
(j mod p ∩ 0 mod q^{K-j}) does. Next: Engine B implements that machinery directly.

## 7. Engine B / Engine C — mechanizing the arrow calculus, and why naive versions fail

**Engine B** (`engine_b.py`): per-cell recursive chains (cover cell a mod M by a q-chain,
children covered recursively, tail finitized with prime p via
CRT(j mod p, chain-ancestor), the generalization of Nielsen's Example 1 trick).
Works at L=3 (25 congruences, verify_tree PASS) with a prime-diversification order,
but thrashes exponentially from modulus-registry conflicts at L >= 6:
each child cover is derived independently, so the (q-1)·K children per chain
each burn a disjoint set of moduli — combinatorial starvation.

**Engine C** (`engine_c.py`): proper arrow semantics — an input recipe R_j is built ONCE
and reused at every chain level k (moduli s^k·m all distinct along the chain "for free").
This is the actual mechanism of q↑ notation. Still fails, and the failure is instructive:
with strictly coprime layering (recipe moduli coprime to all ancestor chain primes),
the s-1 sibling inputs of a chain need pairwise-disjoint covers of Z, and below the
first two inputs ("1" and "2↑") the palette of small primes is exhausted — costs explode
as p·s^{p-1} for ever larger fresh primes.

**Finding:** the power of the Nielsen/Owens calculus is *not* just level-reuse; it is
essentially the **inherited-coverage mechanism** (the "x" entries in their tables):
recipes whose moduli are NOT coprime to the ambient branch, sound only because the
overlapping part is already covered by earlier congruences. Inheritance is not an
optimization — without it the recursion starves at L as low as 6. Any real mechanization
(the V1 program) must implement partial-cover-aware recursion; that is exactly where all
of Owens's hand-bookkeeping ("only thirteen inputs needed on this branch") lives.

## 8. Engine A at scale — automated record so far

Deeper 2-adic tail matters enormously (as the literature's 64↑ suggests):
- 2^7·3^4·5^2·7·11·13 (N=259,459,200): **L=14 COVER FOUND** (916 congruences,
  restart 1 of 12; both verifiers PASS: verify_cover.py direct sweep over lcm and
  verify_tree.py CRT-structured DFS). `witness_L14_N259459200.json`.
- Same profile with 3^5 (N=389M): restart 0 uncovered 90206 — worse than 2^7 bump.

L=15/16 sweeps running (2^7 and 2^8 profiles).
