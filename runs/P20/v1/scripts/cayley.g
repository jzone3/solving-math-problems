# Enumerate 4-valent Cayley graphs on non-abelian groups of order lo..hi,
# print edge lists of those with girth >= 6 (girth check done in Python later;
# here we only do cheap pruning: no involution pairs that force 4-cycles is hard,
# so we export all connection sets up to group-automorphism equivalence).
lo := 26;; hi := 120;;
out := OutputTextFile("/home/ubuntu/p20/cayley_graphs.txt", false);;
SetPrintFormattingStatus(out, false);
for n in [lo..hi] do
  for k in [1..NrSmallGroups(n)] do
    G := SmallGroup(n, k);
    if IsAbelian(G) then continue; fi;
    A := AutomorphismGroup(G);
    elems := Filtered(Elements(G), x -> x <> One(G));
    invs := Filtered(elems, x -> x^2 = One(G));
    noninvs := Filtered(elems, x -> x^2 <> One(G));
    # connection sets S = S^{-1}, |S| = 4:
    cands := [];
    # (a) two inverse-pairs {a,a^-1,b,b^-1}, a,b non-involutions, b <> a^{+-1}
    for i in [1..Length(noninvs)] do
      a := noninvs[i];
      for j in [i+1..Length(noninvs)] do
        b := noninvs[j];
        if b = a^-1 then continue; fi;
        S := Set([a, a^-1, b, b^-1]);
        if Length(S) = 4 then Add(cands, S); fi;
      od;
    od;
    # (b) one inverse-pair + two involutions
    for a in noninvs do
      for i in [1..Length(invs)] do
        for j in [i+1..Length(invs)] do
          S := Set([a, a^-1, invs[i], invs[j]]);
          if Length(S) = 4 then Add(cands, S); fi;
        od;
      od;
    od;
    # (c) four involutions
    for c in Combinations(invs, 4) do
      Add(cands, Set(c));
    od;
    # dedup up to Aut(G)
    reps := [];
    seen := [];
    for S in cands do
      if S in seen then continue; fi;
      orb := Orbit(A, S, OnSets);
      UniteSet(seen, orb);
      Add(reps, S);
    od;
    for S in reps do
      if Size(Subgroup(G, S)) <> n then continue; fi;  # connected only
      # export: map elements to 1..n
      el := Elements(G);
      pos := x -> Position(el, x);
      edges := [];
      for x in el do
        for s in S do
          y := x * s;
          if pos(x) < pos(y) then Add(edges, [pos(x), pos(y)]); fi;
        od;
      od;
      if Length(edges) = 2 * n then
        PrintTo(out, "G ", n, " ", k, "\n");
        for e in edges do PrintTo(out, e[1], " ", e[2], "\n"); od;
        PrintTo(out, "END\n");
      fi;
    od;
  od;
  Print("done order ", n, "\n");
od;
CloseStream(out);
QUIT;
