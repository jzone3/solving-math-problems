/-
P13: the SAT encoding of "(9,6,1)-PMD exists", mirrored in Lean.

This reproduces, clause for clause and variable for variable, the CNF produced
by `runs/P13/v3/gen_cnf.py 9` in "no symmetry breaking" mode (see
`scripts/gen_nobreak.py` in this directory): the *unsymmetrized* encoding, so
that the reduction "PMD ⇒ satisfying assignment" needs no WLOG argument at all.

Variables:
* `x bl p s`  — block `bl` (0..11), position `p` (0..5) holds symbol `s` (0..8);
* `e t u j bl p` — Tseitin product variable: block `bl` has symbol `u` at
  position `p` and symbol `wOf u j` at position `p + (t+1)` (cyclically);
  `j : Fin 8` indexes the 8 possible partners `w ≠ u` in increasing order.

Clauses (in the exact order emitted by the generator):
* per block, per cell: exactly-one symbol (ALO + pairwise AMO);
* per block, per symbol: at most one position;
* per distance `t+1`, per ordered pair `(u, wOf u j)`: Tseitin definitions of
  all 72 product variables, then exactly-one (ALO + pairwise AMO) over them.

`enc` maps these variables to the DIMACS numbering of the generator (minus 1,
because `Std.Sat.CNF Nat` variables are shifted by 1 when printed as DIMACS).
-/
import Std.Sat.CNF
import Std.Sat.CNF.Dimacs
import P13.Defs

namespace P13

set_option maxRecDepth 10000

open Std.Sat

/-- Variables of the (9,6,1)-PMD CNF. -/
inductive V where
  | x (bl : Fin 12) (p : Fin 6) (s : Fin 9)
  | e (t : Fin 5) (u : Fin 9) (j : Fin 8) (bl : Fin 12) (p : Fin 6)
deriving DecidableEq

/-- Cyclic distance represented by `t : Fin 5`, i.e. `t + 1 ∈ {1,…,5}`, as an
element of `Fin 6` (position offset). -/
def dOf (t : Fin 5) : Fin 6 := ⟨t.val + 1, by omega⟩

/-- The `j`-th point different from `u`, in increasing order. -/
def wOf (u : Fin 9) (j : Fin 8) : Fin 9 :=
  if j.val < u.val then ⟨j.val, by omega⟩ else ⟨j.val + 1, by omega⟩

/-- All ordered pairs `(a, b)` with `a` strictly before `b` in `l`
(Python: `for i: for j > i`). -/
def ltPairs : List α → List (α × α)
  | [] => []
  | a :: l => (l.map fun b => (a, b)) ++ ltPairs l

/-- The 72 slots (block, position), in generator order. -/
def slots : List (Fin 12 × Fin 6) :=
  (List.finRange 12).flatMap fun bl => (List.finRange 6).map fun p => (bl, p)

/-- Clauses for one cell: the cell holds at least one and at most one symbol. -/
def cellClauses (bl : Fin 12) (p : Fin 6) : List (CNF.Clause V) :=
  ((List.finRange 9).map fun s => (V.x bl p s, true)) ::
    (ltPairs (List.finRange 9)).map fun q =>
      [(V.x bl p q.1, false), (V.x bl p q.2, false)]

/-- Clauses for one block: exactly-one symbol per cell, then each symbol in at
most one position. -/
def blockClauses (bl : Fin 12) : List (CNF.Clause V) :=
  ((List.finRange 6).flatMap fun p => cellClauses bl p) ++
    (List.finRange 9).flatMap fun s =>
      (ltPairs (List.finRange 6)).map fun q =>
        [(V.x bl q.1 s, false), (V.x bl q.2 s, false)]

/-- Tseitin definition clauses of the 72 product variables for distance
`t + 1` and ordered pair `(u, wOf u j)`. -/
def defClauses (t : Fin 5) (u : Fin 9) (j : Fin 8) : List (CNF.Clause V) :=
  slots.flatMap fun q =>
    [[(V.e t u j q.1 q.2, false), (V.x q.1 q.2 u, true)],
     [(V.e t u j q.1 q.2, false), (V.x q.1 (q.2 + dOf t) (wOf u j), true)],
     [(V.e t u j q.1 q.2, true), (V.x q.1 q.2 u, false),
      (V.x q.1 (q.2 + dOf t) (wOf u j), false)]]

/-- All clauses for distance `t + 1` and ordered pair `(u, wOf u j)`:
Tseitin definitions, then exactly-one coverage (ALO + pairwise AMO). -/
def coverClauses (t : Fin 5) (u : Fin 9) (j : Fin 8) : List (CNF.Clause V) :=
  defClauses t u j ++
    (slots.map fun q => (V.e t u j q.1 q.2, true)) ::
      (ltPairs slots).map fun q =>
        [(V.e t u j q.1.1 q.1.2, false), (V.e t u j q.2.1 q.2.2, false)]

/-- The full clause list, in generator order. -/
def cnfList : List (CNF.Clause V) :=
  ((List.finRange 12).flatMap fun bl => blockClauses bl) ++
    (List.finRange 5).flatMap fun t =>
      (List.finRange 9).flatMap fun u =>
        (List.finRange 8).flatMap fun j => coverClauses t u j

/-- The CNF over the structured variable type `V`. -/
def pmdCnfV : CNF V := ⟨cnfList.toArray⟩

/-- Variable numbering of the generator (DIMACS number minus 1). -/
def enc : V → Nat
  | .x bl p s => bl.val * 54 + p.val * 9 + s.val
  | .e t u j bl p =>
      648 + (t.val * 72 + u.val * 8 + j.val) * 72 + bl.val * 6 + p.val

/-- Left inverse of `enc`. -/
def dec (n : Nat) : V :=
  if h : n < 648 then
    .x ⟨n / 54, by omega⟩ ⟨n / 9 % 6, by omega⟩ ⟨n % 9, by omega⟩
  else
    let m := n - 648
    .e ⟨m / 5184 % 5, by omega⟩ ⟨m / 576 % 9, by omega⟩ ⟨m / 72 % 8, by omega⟩
      ⟨m / 6 % 12, by omega⟩ ⟨m % 6, by omega⟩

theorem dec_enc (w : V) : dec (enc w) = w := by
  cases w with
  | x bl p s =>
      have hbl := bl.isLt; have hp := p.isLt; have hs := s.isLt
      simp only [enc, dec]
      rw [dif_pos (by omega)]
      congr 1 <;> (apply Fin.ext; simp only []; omega)
  | e t u j bl p =>
      have ht := t.isLt; have hu := u.isLt; have hj := j.isLt
      have hbl := bl.isLt; have hp := p.isLt
      simp only [enc, dec]
      rw [dif_neg (by omega)]
      congr 1 <;> (apply Fin.ext; simp only []; omega)

/-- The CNF over `Nat` variables, exactly as in the DIMACS file refuted by
kissat (variable `n` here = DIMACS variable `n + 1`). -/
def pmdCnf : CNF Nat := pmdCnfV.relabel enc

end P13
