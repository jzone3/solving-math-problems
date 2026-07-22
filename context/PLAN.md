# Plan: Solving Obscure Open Math Problems with Devin

## Inspiration

On 2026-07-22, Dmitry Rybin announced that the **Dinitz–Garg–Goemans conjecture**
(open ~30 years, single-source unsplittable flow) is **false**, with a counterexample found in
collaboration with GPT 5.6 Pro: a graph with fractional flow cost 58 where any unsplittable flow
with capacity violation ≤ 15 costs ≥ 60.
(https://x.com/DmitryRybin1/status/2079904005652893709)

Why this worked:
- The conjecture has a **finite, machine-checkable witness** — one concrete graph + demands.
- Checking the witness reduces to standard tools (LP for the fractional bound, ILP/exhaustive
  search over unsplittable routings).
- The problem was **important to its community but obscure globally** — almost nobody had thrown
  modern compute or LLM-guided search at it.

## Thesis

There is a long tail of **obscure but community-important open problems** with the same shape.
Because they are obscure, no one has ever spent serious compute or modern AI-guided search on
them. We pattern-match on the DGG success profile and attack many such problems in parallel.

## Selection criteria (pattern-match profile)

A good target problem:
1. **Finite witness**: a counterexample (or existence proof) is a single finite object —
   a graph, design, sequence, matrix, coloring — that a program can verify in seconds/minutes.
2. **Community-important, globally obscure**: cited in surveys / problem collections
   (Open Problem Garden, West's list, Barbados workshop lists, Handbook of Combinatorial Designs,
   erdosproblems.com), but not famous (not RH/Collatz/twin primes).
3. **Low prior compute**: no evidence of large-scale SAT/ILP/metaheuristic attacks; verification
   frontier is small (e.g. "checked up to n=13" decades ago).
4. **Cheap evaluation loop**: candidate → score/verify in a tight loop suitable for
   LP/ILP/SAT/nauty/simulated annealing/LLM-guided search.
5. **Plausibly false or plausibly constructible**: expert commentary or near-misses suggest a
   counterexample/construction might exist at reachable sizes.

## Process

### Phase 1 — Research (parallel child Devin sessions)
Spawn parallel research sessions, each mining a different domain for candidate problems:
1. Classic graph theory problem collections (West, Barbados, Archdeacon, DIMACS).
2. Combinatorial designs / algebraic combinatorics open instances (Handbook of Combinatorial
   Designs, strongly regular graph existence, Hadamard-type problems).
3. Spectral / automated-conjecture graph theory (Graffiti, AutoGraphiX, recently-refuted-adjacent
   conjectures that remain open).
4. Number theory / additive combinatorics / discrete geometry (erdosproblems.com low-attention
   problems, covering systems, unit-distance questions).

Each session writes `research/<domain>.md` with 8–12 candidates scored against the criteria.

### Phase 2 — Curation
Synthesize research into `problems/` — one file per selected problem (target: 10–15) containing:
problem statement, provenance/importance, current verification frontier, attack strategy, and
**5 prompt variants** for solve runs.

### Phase 3 — Solve runs (parallel ultra-mode sessions)
For each problem, launch **5 Devin Ultra sessions**, each with a different prompt variant
(different framing: pure counterexample search, structured construction, SAT encoding,
LP/ILP gap search, literature-first). Sessions run search harnesses, log negative results, and
report any verified witness.

### Phase 4 — Documentation & verification
- Every run logs its approach and outcome in `runs/`.
- Any claimed counterexample/construction must ship with an **independent verifier script**
  (checkable in one command) before being reported.
- Negative results (search spaces exhausted) are documented too — they are publishable-adjacent
  verification-frontier pushes.

## Repo layout

```
context/     — this plan, methodology, initial candidate notes
research/    — raw domain research from Phase 1 child sessions
problems/    — curated problem files with prompt variants (Phase 2)
runs/        — logs and results from solve runs (Phase 3)
solutions/   — verified witnesses + verifier scripts (hopefully non-empty someday)
```
