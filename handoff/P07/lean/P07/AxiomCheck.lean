/-
Axiom audit for every main theorem.  Expected output for each: only the
three standard axioms `[propext, Classical.choice, Quot.sound]` — no
`Lean.ofReduceBool` (no `native_decide` anywhere), no `sorryAx`.
-/
import P07.Lollipop
import P07.Main
import P07.Dumbbell

-- Theorem 1 (conjecture 154) chain
#print axioms P07.lollipop_dist_eq
#print axioms P07.lollipop_connected
#print axioms P07.lollipop_card_edges
#print axioms P07.lollipop_distSum
#print axioms P07.conjecture154_int_violation
#print axioms P07.conjecture154_int_violation_pair
#print axioms P07.conjecture154_false_real_form
#print axioms P07.conjecture154_false_pair_convention
#print axioms P07.dev_eigenvalues_eq
#print axioms P07.graffiti_conjecture_154_false

-- Theorem 2 (conjecture 143) partial lemmas
#print axioms P07.dumbbell_dist_eq
#print axioms P07.dumbbell_connected
#print axioms P07.dumbbell_card_edges
#print axioms P07.dumbbell_distSum
#print axioms P07.conjecture143_false_iff
