# P21 v1 — Hoffman–Singleton packings/decomposition of K50 (prescribed-automorphism SAT)

Session: runs/P21-v1. Approach per problem file: prescribed-automorphism exact search.

## 1. Statement fidelity (checked against primary source)

Primary source fetched 2026-07-23: Douglas West's open problem page
`dwest.web.illinois.edu/openp/hoffsing.html`.

> **Question:** Does K50 decompose into 7 copies of the Hoffman-Singleton graph?
> **Partial results:** Meszka and Šiagiová [MS] have found five edge-disjoint copies of the
> Hoffman-Singleton graph in K50, using voltage graph methods.
> [MS] J. Combinatorial Designs (2003), doi:10.1002/jcd.10049.

Matches problems/P21-hoffman-singleton-k50.md verbatim in substance (7·175 = C(50,2) = 1225).
Attribution note from Mačaj's 2018 slides: the question is credited to A. Rosa (2002);
Schwenk's K10/Petersen problem (1983) is the small analogue.

Convention choices in our encoding:
- "copy of HoSi" = subgraph of K50 isomorphic to the Hoffman–Singleton graph. We never test
  isomorphism: a 7-regular girth-≥5 graph on 50 vertices is automatically the unique
  (7,5)-Moore graph (Hoffman–Singleton 1960; uniqueness also Fan–Schwenk 1993, O'Keefe–Wong).
  girth ≥ 5 for a subgraph = no triangle and no 4-cycle. Connectivity is forced: any
  component of a 7-regular girth-5 graph has ≥ 1+7+42 = 50 vertices.
- "decompose" = partition E(K50) into 7 such copies; "k-packing" = k pairwise edge-disjoint
  copies (leftover unconstrained).

## 2. PRIORITY CHECK (mandatory widened scope per context/METHODOLOGY.md)

Searches performed 2026-07-23:
- Exa web search: "Hoffman-Singleton decomposition K50 seven copies", "six edge-disjoint
  copies Hoffman-Singleton K50", "Meszka Siagiova packing Hoffman-Singleton",
  "Wilsch Macaj Hoffman-Singleton ovals", "7-packing Hoffman-Singleton K50 solved".
- arXiv API: all:"Hoffman-Singleton" (+packing, +K50) — no packing/decomposition preprint.
- GitHub repo+code search: "hoffman-singleton", "Hoffman-Singleton K50" — only unrelated
  repos (graph drawing, FPGA, percolation, WoW-284).
- Zenodo API: "Hoffman-Singleton" — 3 unrelated/crank records (2-adic spectral, prime-cycle
  double covers); none claims a packing/decomposition of K50.
- OpenReview: nothing relevant (no hits for Hoffman-Singleton packing).

**KEY PRIORITY FINDING — the problem file's frontier claim is out of date.**
Martin Mačaj, *On packings of disjoint copies of the Hoffman-Singleton graph into K50*,
slides, Workshop Pilsen 2018 (`iti.zcu.cz/wl2018/pdf/wl2018_macaj.pdf`):
- "There exist exactly 1602 6-packings of HoSi with an automorphism of order 7."
  So **6-packings EXIST and are fully classified under an order-7 automorphism**; a 6th
  disjoint copy is NOT a new record (contrary to problems/P21 file, which states best = 5).
- All 1602 remainders (the 7th color class, 175 edges) are pairwise non-isomorphic and have
  girth 3 or 4 ⇒ **no 7-decomposition in which all seven copies share an order-7
  automorphism** (implied negative; our independent SAT run below re-derives it).
- Their order-5 search "for 7-packings" was reported only via by-products (>500000 collapsed
  matrix decompositions); no 7-packing announced. Compute quoted: ~4 CPU-years (GAP, 2018).
- Šiagiová–Meszka 2003 packings all have automorphism group of order 25, and they only
  searched that class.
- Wilsch–Mačaj, CSGT 2024 abstract (graphs.vsb.cz/csgt2024): complete classification of
  edge-disjoint HoSi *quintuples* sharing an order-25 automorphism group, via ovals in
  PG(2,5). Question still stated as open in June 2024.

Residual risks: Mačaj's 6-packing result appears to be unpublished (slides only, we found no
journal version); a published paper might contain more (e.g. order-5 negative results).
Wiley JCD full text of [MS] is paywalled (abstract + slides used).

**Conclusion: the 7-decomposition question remains open (as of mid-2024 at least). The
"new record" bar for this run is a 7-decomposition, or new negatives beyond Mačaj's, or an
independent verified 6-packing witness (reproduction, not priority).**

## 3. Encoding (runs/P21/v1/search_sat.py)

Prescribed automorphism group G ≤ Sym(50); each color class required G-invariant, so
colors are assigned to G-orbits of edges. Constraints (all exact / boolean):
- each edge orbit: ≤1 color (=1 for k=7);
- each vertex, each color: degree exactly 7 (totalizer cardinality; orbit weights handled by
  aux-duplicated equivalent literals — weights 1,2 at generic vertices, 7 at a fixed vertex);
- no monochromatic triangle and no monochromatic 4-cycle, one clause per G-orbit
  representative of triangles/C4s per color;
- symmetry breaking (C7 case): the 7 orbits through the fixed vertex are matched
  bijectively to colors 0..6.
Each color class is then 7-regular with girth ≥5 on ≤50 vertices ⇒ HoSi. Solver:
CaDiCaL 1.9.5 via python-sat. Verifier: verify.py (pure integer, independent logic).

Groups tried (natural subgroups of Aut(HoSi) = PSU(3,5):2 with semiregular-ish actions):
- C7: cycle type 1 + 7·7 (HoSi order-7 automorphisms fix exactly 1 vertex). 175 edge orbits.
- C5 fixed-point-free: cycle type 5^10 (the Fix=∅ class). 245 edge orbits.
- C5×C5 semiregular (two vertex orbits of 25): 49 edge orbits. (Šiagiová–Meszka class.)
- C25 semiregular: 49 edge orbits.

## 4. Runs & results

(times on 8-vCPU, 32 GB box; CaDiCaL single-threaded per instance)

| group | k | orbits | vars | clauses | result | time |
|---|---|---|---|---|---|---|
| C5×C5 | 7 | 49 | 8323 | 166852 | **UNSAT** | 2.5 s |
| C5×C5 | 6 | 49 | 7134 | 142827 | (running) | |
| F21 twisted | 6 | 175 | 44040 | 933619 | **UNSAT** | 4.2 s |
| F21 twisted | 7 | 175 | 51380 | 1089996 | **UNSAT** | 4.2 s |
| C7    | 7 | 175 | 51380 | 1087548 | (running) | |
| C7    | 6 | 175 | 44040 | 931509 | (running) | |
| C7 fixed-copy | 7 | 175 | 51380 | 1087723 | (running) | |
| C7 fixed-copy | 6 (×6 miss classes) | 175 | 44040 | 931684 | (running) | |
| C5fpf | 7 | 245 | 40915 | 1196335 | (running) | |

(to be updated as runs finish)

### F21 twisted search (build_and_solve_twisted)

Motivated by Mačaj's statistics table; NB his |Aut| column refers to the *remainder graph*,
not the packing, so F21-invariant packings were not actually promised. We searched anyway:
G = F21 = ⟨σ,τ | σ⁷=τ³=1, τστ⁻¹=σ²⟩ acting with vertex orbits 1 + 4·7 + 21 (τ fixes 5
vertices, matching the K_{1,4} fixed subgraph of order-3 HoSi automorphisms; this action is
unique up to conjugacy given the fixed-point data). Counting fixed-vertex edge orbits forces
the color action π of τ to be a 3-cycle on 3 colors fixing the rest (identity and (3,3)-type
are impossible: only 4 τ-invariant fv orbits exist and the 21-edge fv orbit must split over a
3-cycle of colors). Result: **UNSAT for both k=6 and k=7 in ≈5 s** ⇒ no 6-packing and no
7-decomposition admits this F21 action, even allowing τ to permute the copies.

### Fixed-copy reduction (soundness proof)

Claim: N(⟨σ⟩) ≤ S₅₀ acts transitively on σ-invariant HoSi copies. Proof: given copies H, H'
with σ ∈ Aut(H) ∩ Aut(H'), pick an isomorphism φ: H → H'. Then φ⁻¹σφ and σ generate
order-7 (Sylow) subgroups of Aut(H) ≅ PSU(3,5):2, so ∃α ∈ Aut(H) with
(φα)⁻¹⟨σ⟩(φα) = ⟨σ⟩, i.e. g = φα ∈ N(⟨σ⟩) and g(H) = H'. ∎
Hence if any σ-invariant 6-packing/7-decomposition exists, one exists containing our fixed
copy H₀ (first output of enum_copies_c7.py), so freezing H₀ as color 0 loses no generality.
For k=6 the un-used fixed-vertex class is iterated over the 6 possibilities (miss=1..6).

### Copy enumeration + exact cover (abandoned)

enum_copies_c7.py enumerated 1.33M σ-invariant HoSi copies (blocking-clause SAT loop,
~200/s), but a counting argument shows the total is ≈16471·E₇ where E₇ = #order-7 elements
of PSU(3,5):2 (tens of thousands), i.e. hundreds of millions of copies — full enumeration +
exact cover (cover.c / cover2.c) is infeasible on this box and was abandoned in favor of the
fixed-copy SAT.

## 5. Negative results / dead ends

- No fully C5×C5-symmetric 7-decomposition exists (UNSAT above, 2.5 s) — consistent with
  Šiagiová–Meszka/Wilsch–Mačaj finding only 5-packings in this class.
- No F21-symmetric 6-packing or 7-decomposition in the unique fixed-point-compatible action,
  even with the order-3 element permuting the copies (UNSAT, ≈4 s each).
- Mačaj's 2018 classification implies no 7-decomposition where all copies share an order-7
  automorphism (all 1602 six-packing remainders have girth < 5); our C7 k=7 SAT run aims to
  re-derive this independently.
