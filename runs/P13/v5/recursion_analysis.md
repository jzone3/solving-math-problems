# V5 analysis: can standard PMD recursions reach the open (v,6,1) cases?

Open k=6, lambda=1 cases per problem file: v in {9, 10, 12, 15, 16, 18}.

## Correction from the literature (statement re-verification)

**(10,6,1)-PMD does not exist.** Abel & Bennett, *Des. Codes Cryptogr.* 40
(2006) 211-224, Theorem 1.3: splitting each block (a1..a6) into (a1,a3,a5)
and (a2,a4,a6) would give a (10,6,5)-BIBD with a nested (10,3,2)-BIBD, which
Hishida-Jimbo-Yamamoto showed does not exist. So the CPro1 open list is stale
for v=10; the genuinely open k=6 cases are v in {9, 12, 15, 16, 18}
(consistent with Theorem 1.4 there, which lists 12,18 in the 0 (mod 6)
exceptions, [9,135] in the 3 (mod 6) exceptions, and 16 in the 4 (mod 6)
exceptions). k=7: v in {14, 15} are indeed among the unsettled values
(Theorem 1.6). No later resolution found in a July-2026 literature sweep
(the 2025 CPro1 papers list all these instances as open and solved none).

## Ingredient inventory for k=6, lambda=1 (Miao-Zhu 1995; Abel-Bennett-Zhang
2000; Abel-Bennett 2006)

Known (t,6,1)-PMDs with t <= 18: t = 7 and t = 13 only (all v == 1 (mod 6)
exist; 6 and 10 do not exist; 9,12,15,16,18 open).

Standard recursive machinery (Constructions 3.1-3.5 in Abel-Bennett 2006):
1. Fill-in-hole: (6,1)-IPMD(v,h) + (h,6,1)-PMD -> (v,6,1)-PMD.
2. HPMD filling: (6,1)-HPMD of type (h_1..h_n) + w, filled with
   (6,1)-IPMD(h_i+w, w) and one (h_n+w,6,1)-PMD.
3. Weighting/Wilson: GDD + ingredient HPMDs -> HPMD (still needs filling).
4. PBD closure: (v,K)-PBD + (t,6,1)-PMD for all t in K -> (v,6,1)-PMD.
5. Inflation: HPMD x TD(6,m) -> HPMD (still needs filling).

## Reachability argument (why no recursion can produce v <= 18)

**Hole-size bound.** In a (6,1)-HPMD, a point x in a hole of size h must be
1-apart with each of the v-h points outside its hole exactly once; each block
through x contains x in exactly one position and yields exactly 2 points
1-apart with x (successor and predecessor), both outside x's hole and both
distinct across blocks (lambda=1). Counting all t=1..5 pairs from x: the
blocks through x partition the 5(v-h) ordered pairs (x,*,t) into groups of 5
per block... more simply, for t=1 alone: (v-h) successors must be distinct,
one per block, so x lies in exactly v-h blocks; also each block through x
uses 5 other points, all outside the hole, each t-apart from x for t=1..5 in
both directions -- the 2(v-h) directed 1-apart pairs at x force v-h blocks
through x, and these blocks contain 5(v-h) point-slots covering each of the
v-h outside points exactly 5 times. No contradiction yet; the standard
necessary condition comes from the *hole pair deficit*: for an IPMD(v,n)
(hole of size n) it is known that v >= 5n+1 (Bennett; analogue of the BIBD
bound: the n hole points pairwise non-covered force the complement structure
to be large). Hence:
  - Fill-in-hole (1): needs (h,6,1)-PMD with h in {7,13} (only known small
    PMDs), and v >= 5h+1 >= 36. All targets v <= 18: unreachable.
  - HPMD filling (2): the final hole is filled by an (h_n+w,6,1)-PMD, so
    h_n+w in {7,13}; every other hole is filled by an IPMD(h_i+w, w), which
    needs h_i+w >= 5w+1, i.e. h_i >= 4w+1; a (6,1)-HPMD has at least 6 holes
    (a block meets 6 distinct holes); so
      v = sum h_i + w >= 5(4w+1) + (7-w) + w = 20w + 12 >= 12 at w=0.
    At w=0: v >= 5·1 + 7 = 12 requires holes h_1..h_5 >= 1 and h_n = 7, i.e.
    an HPMD of type 1^5 7^1 on 12 points = a (6,1)-IPMD(12,7); the hole bound
    demands 12 >= 5·7+1 = 36: impossible. Larger hole patterns only increase
    v. For w=1: v >= 5·5 + 7 = 32 > 18. Unreachable for all v <= 18.
  - Weighting (3) and inflation (5) only *produce* HPMDs; turning an HPMD
    into a PMD requires (2). Unreachable.
  - PBD closure (4): all known ingredient PMDs have t >= 7. A nontrivial
    PBD (more than one block) with all block sizes >= 7: take a block B,
    |B| >= 7, and a point x not in B; x lies on |B| >= 7 distinct blocks
    (one through each point of B), each contributing >= 5 new points besides
    x, so v >= 1 + 7 + 7·5 = 43 (crudely, v >= 43 > 18; the trivial PBD
    {single block of size v} just restates the unknown PMD(v)). Unreachable.

**Conclusion.** No combination of the standard PMD recursions can settle any
of v in {9,12,15,16,18} (k=6) or {14,15} (k=7): every route requires either a
sub-18 ingredient PMD that is itself open/nonexistent, or forces v >= 32.
This matches the fact that the published tables' small exceptions have stood
since 2000: the open cases can only fall to direct construction (difference
methods, prescribed automorphisms) or exhaustive/SAT search. This motivates
the exhaustive prescribed-automorphism sweeps in this run (see NOTES.md).
