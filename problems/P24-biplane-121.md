# P24 — The undecided biplane: 2-(121,16,2) design

**Statement.** A biplane of order 14 is a 2-(121,16,2) symmetric design. Its existence is the
smallest undecided biplane case (only 5 nontrivial biplanes are known; existence open for
order 14). Prior work eliminated many automorphism-group cells: e.g. automorphisms of various
orders/structures are excluded in the literature (see Radziszowski-adjacent design surveys and
the dedicated papers of Janko et al.).

**Approach.** Finish the automorphism-cell eliminations with modern SAT + symmetry breaking:
enumerate the remaining feasible |Aut| cells from the literature, encode orbit-matrix /
tactical-decomposition existence per cell as SAT/ILP, and kill cells with DRAT certificates.
Full nonexistence is out of reach; each newly killed cell is a citable increment; killing the
last nontrivial-group cells would prove "any 2-(121,16,2) design is rigid" — a publishable
theorem.

**Verification gate:** pin the exact list of already-eliminated automorphism cells against the
primary literature FIRST (do not redo known cells); DRAT certificates for each new elimination;
independent orbit-matrix derivation; widened priority check incl. GitHub/Zenodo. Lean: per-cell
LRAT replay possible but low priority.
