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
- Pass 1 (launched 20:2x UTC): 8 parallel workers (seeds 1–8), n = 12..60, 60 s per n per
  worker ≈ 6.5 core-hours. Results in runs/P10/v1/results/pass1_seed*.jsonl.
- (further passes appended below)

## 3. Results

(appended as passes complete)

## STATUS

(pending — will be finalized at end of session)
