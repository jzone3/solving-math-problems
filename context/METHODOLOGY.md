# Methodology: Solve-Run Protocol

## Per-problem run matrix

Each curated problem in `problems/` gets **5 parallel Devin Ultra sessions**, one per prompt
variant. Variants deliberately vary the attack framing so at least one avoids local minima:

| Variant | Framing |
|---|---|
| V1 | **Direct counterexample search**: build a generator + verifier, random/annealed search over small instances. |
| V2 | **Structured construction**: exploit algebraic/symmetric structure (Cayley graphs, block designs, blowups of known near-misses). |
| V3 | **SAT/SMT encoding**: encode the finite witness as SAT/SMT (with symmetry breaking, e.g. SAT-modulo-symmetries) and run solvers hard. |
| V4 | **LP/ILP duality gap**: where the conjecture compares two optimization quantities, script both (LP relaxation vs. ILP) and search instances maximizing the gap. |
| V5 | **Literature-first + LLM reasoning**: digest all known partial results and near-misses, then reason toward either a proof sketch or a targeted witness family, and only then compute. |

Not every variant fits every problem; per-problem files may override with problem-specific
variants (still 5 total).

## Session rules (inherited by every solve run)

1. Start from the problem file in `problems/`; do not re-derive the statement from scratch.
2. Any claimed result MUST include `solutions/<problem>/verify.py` (or equivalent): a
   standalone script, no exotic deps, that independently checks the witness and prints PASS.
3. Log everything to `runs/<problem>/<variant>/NOTES.md`: encoding choices, sizes searched,
   compute spent, near-misses, dead ends. Negative results are results.
4. Never trust the LLM's arithmetic — every bound and witness must be machine-verified.
5. Push work to branch `runs/<problem>-<variant>`; the orchestrator folds results back.

## Verification standard

A problem is only marked SOLVED when:
- the witness verifies with the independent script,
- a second, differently-written verifier (ideally by a different session) agrees,
- the problem statement match is confirmed against the original source (avoid solving a
  paraphrase — see the Erdős #728 ambiguity incident).

## Run tracking

`runs/INDEX.md` tracks the matrix: problem × variant × session link × status
(queued / running / negative / near-miss / SOLVED).

## Formalization gate (mandatory for every Lean formalization and every claimed solution)

Before any result is presented as settled, all three checks must be completed and documented:

1. **Statement fidelity** — the Lean statement (and the operational encoding used in search/verifiers)
   must be checked word-by-word against the ORIGINAL problem source (not a paraphrase, not the
   catalog file). Document every convention choice (matrix entries used, population vs sample
   statistics, multiplicity, strict vs non-strict inequalities, connectivity assumptions) and why it
   matches the source. Independent confirmation by a second session is required.
2. **Priority check** — a dedicated literature search that nobody has already resolved the problem
   (and that key lemmas are credited if previously published). Record the searches performed, what
   was found, and any unread/paywalled sources as explicit residual risks.
3. **Survey of efforts (bonus but expected)** — a short survey of prior attacks on the specific
   problem: exhaustive-search frontiers, partial results, related theorems, who worked on it.

Deliverable: a PRIORITY.md / fidelity section in the corresponding solutions/<Pxx>/ folder.
