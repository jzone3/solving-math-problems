# P10 V1 — Annealed counterexample search for Brouwer's conjecture

Session: devin-bbcab6049937490fa6660ffa0f590089 (variant V1 of 5 parallel runs)
Date: 2026-07-22

## 0. Statement re-verification & openness check (REQUIRED FIRST STEP)

Statement in problems/P10-brouwer-laplacian.md matches the canonical form (Brouwer–Haemers,
*Spectra of Graphs* §3.2; Wikipedia "Brouwer's conjecture"): for all 1 ≤ t ≤ n,
Σ_{i≤t} μ_i(L(G)) ≤ m + t(t+1)/2. Statement match: CONFIRMED.

**Openness check: THE CONJECTURE APPEARS TO BE PROVED.**
- Kothari & Tudose, *On Brouwer's Laplacian conjecture*, arXiv:2606.12197 (v1, 10 Jun 2026,
  not withdrawn as of 2026-07-22). Claims a full proof via a nuclear-norm bound on centered
  Laplacians of split graphs + the Grone–Merris–Bai theorem for split graphs; also proves the
  converse implication (equivalence Brouwer ⇔ GMB).
- Independent corroboration: arXiv:2607.17293 (*Characterizing the equality case in Brouwer's
  inequality*, Jul 2026) states the conjecture "has been confirmed by Kothari and Tudose (2026)"
  and characterizes equality: equality at index k iff G is a threshold graph with clique
  number k+1.
- The problem file's "Status: Open in general (July 2026)" is therefore STALE. Note the file
  itself lists 2606.12197 in the V5 reading list ("verify none closes the conjecture") — it does
  close it, pending refereeing.

Decision: proceed with V1 anyway as an **independent computational sanity check** of the
claimed proof (a verified counterexample would refute the preprint; expected outcome is
negative). Reported to orchestrator immediately.

## 1. Encoding & method

- Score(G) = max_t (Σ_{i≤t} μ_i − m − t(t+1)/2), μ from numpy eigvalsh on L = D − A (float64).
- Violation ⇔ Score > 0. Equality (Score = 0) attained by threshold graphs (dense attractors),
  so the anneal saturates at ~0 (float noise ~6e-14); any candidate with Score > 1e-9 is
  reported and must be re-verified exactly (solutions/P10/verify.py, mpmath 60-digit symmetric
  eigensolve, PASS only on strict violation beyond 1e-20).
- Search: simulated annealing over single edge flips, geometric cooling T0=0.5 → 1e-4,
  random G(n,p) init with p ~ U(0.15, 0.9) (covers all densities incl. dense t≈n/2 regime).
- Code: runs/P10/v1/search.py. Verifier: solutions/P10/verify.py (tested on K4−e equality
  case at n=4,t=2: reports FAIL/no-violation, excess ≈ 6e-61 — i.e. exact equality).

## 2. Compute log

- Smoke test: n=12–14, 5 s/n, seed 1 → best scores +5.7e-14 (float noise on equality graphs).
- Pass 1: 8 workers (seeds 1–8), n = 12..60, 60 s/n each, random G(n,p) inits,
  481,440,142 anneal steps total. Results: results/pass1_seed*.jsonl.
- Pass 2: seeds 9–12 threshold-graph inits n=40..60 @120 s/n + seeds 13–16 random inits
  n=45..60 @300 s/n; 316,161,168 anneal steps. Results: results/pass2_*.jsonl.
- Pass 3: seeds 17–24 (4 random + 4 threshold inits), n=12..60 @90 s/n;
  737,684,831 anneal steps. Results: results/pass3_*.jsonl. Zero violations.
- Total ≈ 1.54e9 single-edge-flip anneal steps over ~5 wall-hours on 8 cores.

## 3. Results

- **Zero violations** in all passes: no graph ever scored above the 1e-9 float-noise
  threshold. Max observed score ≈ +3.4e-13 = eigvalsh rounding noise on exact-equality
  (threshold) graphs.
- The anneal robustly converges to the equality surface: best graphs are threshold-like,
  with the maximizing index t ≈ n/2 and dense edge counts (e.g. n=40: t=20, m=408;
  n=60: t=28, m=893) — exactly the "tight regime" flagged in the problem file, and
  consistent with the equality characterization of arXiv:2607.17293 (threshold graphs,
  clique number t+1).
- No near-misses strictly between noise and violation: the landscape appears capped at 0.
- Independent verifier sanity check: solutions/P10/verify.py on the n=4 equality witness
  (K4 minus an edge, t=2) gives excess ≈ 6e-61 → FAIL (no violation), as expected.

## Dead ends / notes

- Random-init anneals at n≥55 sometimes stall slightly below equality within 60 s
  (n=60 best −1e-4 in pass 1); threshold inits and longer budgets fix this — hence pass 2/3.
- No candidate ever required exact re-verification beyond the noise filter (none > 1e-9).

## STATUS

**negative** — no counterexample found (≈1.54e9 annealed edge flips, n=12–60, all densities,
random + threshold-graph initializations). Fully consistent with the Kothari–Tudose proof
(arXiv:2606.12197): Brouwer's conjecture appears to be a THEOREM as of June 2026, so the
expected and obtained outcome of V1 is negative. Main actionable finding for the
orchestrator: the problem's "open" status is stale; recommend marking P10 as closed by the
literature (pending refereeing) and pointing V5 at verifying the Kothari–Tudose argument.
