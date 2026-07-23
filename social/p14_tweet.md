# P14 — three BTD nonexistence results, long-form copy (user's format)

Devin closed three more open design-theory instances

SETTLED: three balanced ternary designs proven NOT to exist —
BTD(14,18;7,1,9;7,4), BTD(12,15;6,2,10;8,6), BTD(12,20;4,3,10;6,4)

Balanced ternary designs generalize the classical block designs statisticians have used
since Fisher — except points can appear in a block twice. Their existence tables have been
worked on since the 1980s (Billington's surveys). These three parameter sets were the last
survivors of a dedicated 2025 computational campaign (CPro1) — searched hard, never built,
never ruled out.

Devin ruled all three out, each two independent ways:
- a constraint-programming model: INFEASIBLE
- an independent SAT encoding solved UNSAT by kissat, with a DRAT proof certificate
  verified by drat-trim — machine-checkable receipts (the proofs run 1–40 GB each)

The only search-space-reducing trick is double-lex symmetry breaking — a published, proven
technique (CP 2002) — and the encoders were positive-controlled by reproducing known
designs first.

Then a second, adversarial Devin re-derived the definition from the primary literature,
validated the encodings by brute-force model counting on small cases, confirmed all three
were genuinely open, re-ran the whole pipeline, and wrote its OWN encoding.

One instance is still standing: BTD(14,28;8,3,14;7,6) resisted ~19 hours of solver time.
The hunt continues.

Repo: https://github.com/jzone3/solving-math-problems (handoff/P14)

---

NOTE BEFORE POSTING: hold until the adversarial review verdict (runs/P14/v1/ADVERSARIAL_REVIEW.md)
is CONFIRMED. No Lean formalization for P14 (proof certificates are 1-40 GB — beyond
Lean-checkable size); say "machine-verified (DRAT certificates)" NOT "Lean-verified".
