# Solving Open Math Problems

A research system in which many parallel [Devin](https://devin.ai) sessions hunt for and settle
obscure but genuinely open problems in graph theory, spectral graph theory, combinatorial
designs, and number theory. Candidate problems are curated from the literature, attacked by
independent solve sessions with different strategies, adversarially reviewed, and — where
possible — verified down to machine-checkable certificates (Lean 4 kernel proofs and/or
DRAT-checked SAT proofs). Settled results are packaged into self-contained handoff folders
for human researchers.

## Results so far

| ID | Problem (one-liner) | Status | Verification | Links |
|----|---------------------|--------|--------------|-------|
| P02 | Brandt/West regular-supergraph statement: every maximal triangle-free graph with δ ≥ n/3 has a regular supergraph via vertex multiplications | **REFUTED** (9-vertex witness + Farkas certificate) | Lean 4 (kernel-checked, no `sorry`) | [solutions/P02](solutions/P02) · [handoff/P02](handoff/P02) · [formalization/P02](formalization/P02) |
| P06 | Graffiti / WoW 698: L2 norm of negative adjacency eigenvalues ≤ Randić index | **PROVED TRUE** (WoW 129 remains open; exhaustive to n = 11) | Lean 4 + adversarial review | [solutions/P06](solutions/P06) · [handoff/P06](handoff/P06) · [formalization/P06](formalization/P06) |
| P07 | Graffiti 154 (2m·μ² ≤ n³) and 143 (variance of positive eigenvalues ≤ m/μ) | **REFUTED** — but **priority belongs to demonstrandum-research** (public 2026-06-12, six weeks earlier; see [PRIORITY.md](handoff/P07/PRIORITY.md)). Independent value here: the Lean formalization of the 154 refutation | Lean 4 (154, both readings) | [solutions/P07](solutions/P07) · [handoff/P07](handoff/P07) · [formalization/P07](formalization/P07) |
| P08 | Graffiti 39/40: deviation of the distance matrix ≤ number of positive (39) / negative (40) adjacency eigenvalues | **PROVED TRUE** | Lean 4 + adversarial review | [solutions/P08](solutions/P08) · [handoff/P08](handoff/P08) · [formalization/P08](formalization/P08) |
| P13 | (9,6,1)-perfect Mendelsohn design — smallest open case of the block-size-6 PMD spectrum | **NONEXISTENT** (adversarially confirmed) | Lean 4 + DRAT (drat-trim `s VERIFIED`) | [solutions/P13](solutions/P13) · [handoff/P13](handoff/P13) · [formalization/P13](formalization/P13) |
| P14 | Three balanced ternary designs left open by the CPro1 campaigns: BTD(14,18;7,1,9;7,4), BTD(12,15;6,2,10;8,6), BTD(12,20;4,3,10;6,4) | **NONEXISTENT** (adversarially confirmed); 4th instance BTD(14,28;8,3,14;7,6) undecided | DRAT-certified SAT + independent CP-SAT (**machine-verified, not Lean**) | [solutions/P14](solutions/P14) · [handoff/P14](handoff/P14) |

All other problems (P01–P25, see [problems/README.md](problems/README.md)) are open or
in progress; live per-run status is tracked in [runs/INDEX.md](runs/INDEX.md).

## How the pipeline works

1. **Research** — survey the literature for obscure open problems with small plausible
   witnesses (`research/`), then curate a problem catalog with formal statements and attack
   plans (`problems/`, criteria in `context/PLAN.md`).
2. **Parallel solves** — each problem gets up to 5 parallel Devin Ultra sessions, one per
   prompt variant (direct search, structured construction, SAT/SMT, LP/ILP duality,
   literature-first reasoning). Protocol: `context/METHODOLOGY.md`. Logs land in
   `runs/<Pxx>/<variant>/`.
3. **Adversarial review** — a hostile second session tries to break every claimed result:
   independent re-verification, statement fidelity against the original source, priority
   search.
4. **Certificates** — results are pushed to machine-checkable form: standalone `verify.py`
   scripts, DRAT-checked UNSAT proofs, and Lean 4 kernel formalizations (`formalization/`).
5. **Handoff** — each settled result becomes a self-contained package for a human
   researcher (`handoff/<Pxx>/`), including original sources, proofs, certificates, and
   priority notes.

## Directory map

| Directory | Contents |
|-----------|----------|
| [problems/](problems) | Curated problem catalog P01–P25: statements, status, attack plans, prompt variants |
| [runs/](runs) | Per-run working logs and code, one folder per problem × variant; status matrix in `INDEX.md` |
| [solutions/](solutions) | Headline artifacts per settled problem: proofs, witnesses, certificates, `verify.py` |
| [handoff/](handoff) | Self-contained verification packages for human researchers |
| [formalization/](formalization) | Lean 4 projects machine-checking the settled results |
| [social/](social) | Tweet drafts and result graphics |
| [research/](research) | Literature surveys used to source candidate problems |
| [context/](context) | Project plan, methodology, and initial candidate lists |

## Verification levels

- **Lean 4** — statement and proof checked by the Lean kernel (no `sorry`, no extra axioms).
- **DRAT** — SAT-solver UNSAT proof independently checked by drat-trim (`s VERIFIED`).
- **Adversarially reviewed** — a separate hostile session independently re-verified the
  claim, the statement fidelity, and priority.

Accuracy over polish: every claim here links to its certificates, and priority caveats
(notably [P07](handoff/P07/PRIORITY.md)) are preserved verbatim in the handoff packages.
