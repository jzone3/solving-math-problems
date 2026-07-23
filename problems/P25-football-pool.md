# P25 — Football pool problem for six matches: K₃(6,1) ∈ [71,73]

**Statement.** K₃(6,1) = minimum size of a ternary covering code of length 6 and covering
radius 1 (min number of words of {0,1,2}⁶ such that every word is within Hamming distance 1
of some codeword). Known: 71 ≤ K₃(6,1) ≤ 73. The upper bound 73 dates to 1980s tabu search
(Wille; see Östergård's covering-code tables); the lower bound 71 is by Linderoth–Margot–Thain,
INFORMS J. Comput. 21 (2009), improving Östergård–Wassermann's 65 (JCTA 2002)
(exact references to be re-pinned by the run). Open for 40+ years.

**Concrete targets:**
1. Find a covering code of size 72 (or 71!) — SAT/ILP with symmetry breaking over the wreath
   product S₃≀S₆ (|group| = 6!·3⁶); modern incremental SAT was never seriously applied.
2. Or prove 72 impossible ⇒ K₃(6,1) = 73 (much harder; 3⁶ = 729 points, cover constraints —
   plausibly within cube-and-conquer reach with strong symmetry breaking).

**Verification gate:** pin exact current bounds against Östergård's tables and recent
literature FIRST (the [71,73] interval must be re-verified); a positive witness is trivially
checkable (verify.py: every word covered); nonexistence needs DRAT + adversarial re-encoding;
widened priority check incl. GitHub/Zenodo covering-code repos. Lean: positive witness =
decidable check, easy; UNSAT via LRAT replay.
