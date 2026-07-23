# P13 — (9,6,1)-PMD nonexistence, long-form copy (user's format)

Devin settled another open case overnight

SETTLED: the smallest open perfect Mendelsohn design of block size 6 — the (9,6,1)-PMD does NOT exist

Design theorists have been closing these existence tables for decades (the block-size-5 table was only finished in 2020). For block size 6, the standard references (Abel–Bennett 2006; Bennett–Zwicker–Chang 2009) list v = 9 as the smallest unresolved case — an object with just 12 blocks that nobody had been able to build or rule out.

Devin ruled it out three independent ways:
- a SAT encoding solved UNSAT by kissat, with a DRAT proof certificate verified by drat-trim — a machine-checkable receipt, not a "trust our search"
- an independent constraint-programming model (UNSAT)
- a from-scratch exhaustive backtracking search (581,650 nodes, zero designs)

Then a second, adversarial Devin re-derived the definition from the original papers, audited every symmetry-breaking assumption, wrote its OWN encoding with a different symmetry scheme, and got a fresh machine-verified UNSAT proof. Verdict: CONFIRMED.

Fun catch along the way: a widely-copied "open instances" list also names v = 10 as open — that one was actually settled back in 2006. The table everyone copies had a stale row.

The block-size-6 frontier now moves to v = 12.

Repo: https://github.com/jzone3/solving-math-problems (handoff/P13)

---

NOTE BEFORE POSTING: Lean status — the theorem `no_pmd_9_6_1` IS formalized in Lean 4
(formalization/P13/): definition, symmetry-breaking WLOG, and design⇒CNF reduction are
kernel-checked; the UNSAT certificate is checked inside Lean by the verified LRAT checker
but its evaluation uses native_decide (plus external drat-trim validation). Safe wording:
"machine-checked in Lean (LRAT certificate checked by Lean's verified checker via
native compilation)" — do NOT say "kernel-only Lean proof".
Priority checked per the widened gate (literature + GitHub/Zenodo): appears to be the first
resolution.
