# P03 — Woodall's conjecture, V3 run (τ=3 targeted enumeration)

Session: https://app.devin.ai/sessions/d9627b2d22344bbf8de500ab861b6d53
Variant: **V3 — τ=3 targeted**: restrict to digraphs with min dicut exactly 3; use
Abdi–Cornuéjols–Zlatin (ACZ) partial results to constrain the class a counterexample must
live in; search within that class.

## 0. Statement re-verification (against original source) & openness check

- Statement used: *in every finite digraph, min size of a nonempty dicut = max number of
  pairwise disjoint dijoins* (Woodall 1978, LNM 642). Cross-checked against:
  - ACZ, "On packing dijoins in digraphs and weighted digraphs" (arXiv:2202.00392, Math.
    Programming): identical definitions (dicut = δ⁺(U), δ⁻(U)=∅; dijoin hits every dicut;
    Woodall conjectures A partitions into τ dijoins). ✓ matches problem file.
  - Feofiloff's Woodall's-conjecture page (ime.usp.br/~pf/dijoins/, updated 2025-04-05):
    conjecture still listed as open. ✓
  - Wikipedia "Woodall's conjecture": unsolved as of retrieval (2026-07-22). ✓
  - Cornuéjols–Liu–Ravi, "Approximately packing dijoins via nowhere-zero flows",
    Combinatorica 45:32 (published 2025-06-02): still frames Woodall as open. ✓
- Conclusion: **statement verified, still open as of July 2026** (incl. τ=3 case).

## 1. Structural constraints a τ=3 counterexample must satisfy (from literature)

Let ρ(3,D,1) = (1/3)·Σ_v ((d⁺(v) − d⁻(v)) mod 3).

1. **ρ ≥ 4** — ACZ (arXiv:2202.00392) prove Woodall's conjecture for τ=3, w=1 whenever
   ρ ∈ {0,1,2,3} (results (i),(ii),(iii) of their abstract; (iii) is exactly τ=3, ρ=3, w=1).
   Hence Σ_v ((d⁺−d⁻) mod 3) ≥ 12, so **at least 6 vertices have imbalance ≢ 0 (mod 3)**,
   and in particular **n ≥ 6** (each term ≤ 2 gives Σ ≤ 2n, and ≥12 ⟹ n ≥ 6).
2. **Not source-sink connected** — Schrijver 1982 / Feofiloff–Younger 1987: Woodall holds
   when every source reaches every sink. So the counterexample has a source s and sink t
   with no directed s→t path (in particular ≥2 sources or ≥2 sinks... more precisely at
   least one blocked (source, sink) pair).
3. **Underlying undirected graph non-planar** — planar case follows from Lucchesi–Younger
   via duality (dijoins ↔ feedback arc sets in the dual).
4. Every source has outdeg ≥ 3, every sink has indeg ≥ 3 (their δ⁺/δ⁻ are dicuts).
5. Not series-parallel (Lee–Wakabayashi) — implied by 3 (non-planar).

These give a very strong filter; the search below only SAT-checks digraphs meeting 1–4.

## 2. Encoding / machinery (runs/P03/v3/core.py)

- Digraph = (n, list of arcs), parallel arcs allowed, loops disallowed.
- Dicuts: exhaustive over all 2ⁿ vertex subsets U with δ⁻(U)=∅ (n ≤ ~16). τ = min size.
- Packing decision: 3 pairwise disjoint dijoins exist ⟺ arcs 3-colorable s.t. every
  (minimal) dicut contains all 3 colors (supersets of dijoins are dijoins, so WLOG a
  partition). Encoded as SAT (exactly-one color per arc + one at-least-one clause per
  minimal-dicut × color); solved with python-sat (Minicard).
  **A τ=3 instance that is UNSAT = counterexample.**
- Cross-validation: SAT decision agreed with brute-force 3^m enumeration on 248 random
  small instances (test_core.py). All unit tests PASS.

## 3. Search harnesses

- `search.py` (v1): random generation + repair-to-τ=3 + hard filters, and a hill-climb on
  minimal-dicut density. Yield of filtered candidates was terrible (~2 full-pass per 2 min):
  random τ=3 digraphs are almost always source-sink connected and have ρ ≤ 3.
- `search2.py` (v2, main engine): structured generator with two sources / two sinks layered
  so s1 cannot reach t2; annealing with soft score = 4000·[not ss-connected] +
  1000·min(ρ,4) + 2000·[non-planar] + 5·(#size-3 minimal dicuts) + #minimal dicuts;
  parallel-arc duplication used as a reachability/planarity-preserving move that shifts
  imbalances mod 3 (pushes ρ up). Every distinct full-pass candidate is SAT-checked.
  Yield: ~1000 full-pass candidates SAT-checked per minute per core.

## 4. Compute log (checkpointed)

| run | params | wall | candidates SAT-checked (full-pass) | UNSAT |
|---|---|---|---|---|
| smoke random | n 6–10, 2 min | 2 min | 2 | 0 |
| smoke anneal | n 6–10, 2 min | 2 min | 1 | 0 |
| smoke search2 | n 8–12, 3 min | 3 min | 3260 | 0 |

(long runs appended below)

## STATUS: (running)
