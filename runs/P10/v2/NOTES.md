# P10 — Brouwer's Laplacian Conjecture — V2 (equality perturbation)

Session: https://app.devin.ai/sessions/1b8eb43d0656466a92c42e6a31568e20
Variant: **V2** — perturb equality-achieving (split/threshold) graphs, hunting sign flips of
the Brouwer deficit d(G) = max_t ( Σ_{i≤t} μ_i − m − t(t+1)/2 ).

## Step 0 — statement & openness re-check (methodology rule)

Statement re-verified against Brouwer–Haemers formulation as quoted in the primary
literature (arXiv:2606.12197 quotes it verbatim): Σ_{i=1}^k λ_i(L) ≤ m + C(k+1,2) for all
1 ≤ k ≤ n. The problem file matches the original — no paraphrase drift.

**CRITICAL FINDING: the problem is NO LONGER OPEN as of July 2026.**

- **Kothari & Tudose, "On Brouwer's Laplacian conjecture", arXiv:2606.12197 (10 Jun 2026)**
  give a full proof. Method: reduce Brouwer to the Grone–Merris–Bai theorem restricted to
  split graphs; they also prove the converse, establishing equivalence Brouwer ⇔ GMB.
- Independently corroborated by three follow-up papers (different author groups) that
  *build on* the proof rather than dispute it:
  - arXiv:2607.03388 (3 Jul 2026) "On Full Brouwer's Laplacian Conjecture" — cites
    "Kothari and Tudose (2026) proved the conjecture"; proves equality holds for some
    1 ≤ k ≤ n−1 iff G is a threshold graph with clique number k+1 (Li–Guo full conjecture).
  - arXiv:2607.17293 (19 Jul 2026) — independent characterization of the same equality case
    ("...which has been confirmed by Kothari and Tudose (2026) recently").
  - arXiv:2607.08452 (9 Jul 2026) — proves two conjectures on generalizations.
- No withdrawal/retraction notice on arXiv as of 2026-07-22.

Consequence for V2: **no counterexample exists**; the equality-perturbation hunt cannot
produce a witness. Moreover 2607.03388 / 2607.17293 prove exactly what V2 was designed to
probe empirically: the equality set is precisely threshold graphs (with clique number k+1),
and every perturbation off that set is strictly inside the feasible region.

Reported this to the orchestrator immediately (before deep compute), per methodology.

## Step 1 — bounded corroboration scan (instead of a futile hunt)

Ran `scan_threshold_perturb.py` (this directory):
- **Exact check** of ALL threshold graphs on n ≤ 20 vertices (all 2^(n−1) creation
  sequences, 2·(2^20 − 1) ≈ 2.1M graphs) using the integer Merris spectrum
  (Laplacian spectrum = conjugate degree sequence) — pure integer arithmetic, no floats.
- **Single-edge perturbation scan** (add / remove / move one edge) of every threshold graph
  on n ≤ 14, computing the Brouwer deficit via dense eigensolve; violation ⇔ deficit > 0.

Results (full logs: `scan_output.txt` for pass 1 [n≤20 exact, n≤12 perturb],
`scan_output_n14.txt` for the escalated pass [n≤14 perturb]):
- **All 1,048,574 threshold graphs on n ≤ 20**: exact integer check passes; the running
  maximum deficit is 0, attained exactly (equality cases), never exceeded.
- **25,108,470 single-edge perturbations** of all threshold graphs on n ≤ 14: **zero
  violations**. Max deficit over all perturbed graphs = 0.000000 (attained only by
  perturbations that land on another threshold graph, e.g. at n=14, t=12);
  2,459,955 perturbed graphs sat at exact equality (still threshold), 5,869,642 strict
  near-misses in (−0.5, 0), the rest ≤ −0.5.

Near-miss structure observed: perturbations that keep the graph threshold sit exactly at
deficit 0 (equality, consistent with the proven equality characterization); all genuinely
non-threshold perturbations were strictly negative. Best strictly-negative deficits cluster
just below 0 at t ≈ clique number − 1, consistent with the "tight regime" note in the
problem file.

## Compute spent

- arXiv literature sweep + PDF verification of 2606.12197: minutes.
- Corroboration scans: ~2 CPU-hours total (pass 1 ≈ 5 min; escalated n≤14 pass ≈ 1.8 h),
  single machine, numpy dense eigensolves + exact integer Merris checks.

## Dead ends / notes for the orchestrator

- P10 should be retired from the open-problem matrix (all 5 variants are moot as
  counterexample hunts). Suggest updating `problems/P10-brouwer-laplacian.md` status and
  `runs/INDEX.md`.
- V5's reading list already contained 2606.12197 — the problem file's own "Status: Open"
  line was stale relative to its citation list.
- No `solutions/P10/verify.py` is produced: there is no witness to verify (and none can
  exist given the proof).

## STATUS: negative — problem CLOSED in the literature (proved, Kothari–Tudose arXiv:2606.12197, June 2026); corroboration scan found no violation and exact equality only on threshold graphs, as the proven characterization requires.
