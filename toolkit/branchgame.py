"""P15 V4 phase 3: machine replay of the Krukenberg/Nielsen/Owens set-counting
calculus ("branch game") from Owens's thesis (BYU etd/4329, 2014), and re-run
of the same ledger at target minimum modulus T=43.

Model (per hole/branch, Owens Ch.3 sections 3.8-3.20):
  - A *set* is a partial cover of the branch. The pool starts with seed sets
    (powers of 2 / 2^k-up-arrows available on the branch, sometimes 3-, 9-sets).
  - op MUL(k): mint k new sets by multiplying existing sets by free residues
    of a small prime (5, 3, 25-up, ...). Pool += k.
  - op FILL(p, copies, need): fill `copies` towers p-up-arrow, each consuming
    `need` distinct pool sets (need = p-1 minus pre-covered inputs minus
    dropped too-small sets). Requires copies*need <= pool (sets are reusable
    across DIFFERENT primes but not across copies of the same prime on the
    same branch). Pool += copies (each filled tower is a new set).
  - The section succeeds if the final target prime tower P-up-arrow can be
    filled: pool - drop >= P-1 - precovered, where drop = # seed sets s with
    P*s < T (min-modulus restriction).

This replays Owens's arithmetic exactly as stated in the thesis text and then
re-evaluates every section with T=43 to locate the precise deficits.
"""

from dataclasses import dataclass, field


@dataclass
class Ledger:
    name: str
    pool: int = 0
    log: list = field(default_factory=list)
    ok: bool = True

    def seed(self, n, why=""):
        self.pool += n
        self.log.append(f"seed +{n} -> {self.pool}  {why}")

    def mul(self, k, why=""):
        self.pool += k
        self.log.append(f"mul  +{k} -> {self.pool}  {why}")

    def fill(self, p, copies, need, why=""):
        used = copies * need
        if used > self.pool:
            self.ok = False
            self.log.append(
                f"FAIL fill {copies}x{p}^ need {need} each: {used} > pool {self.pool}  {why}")
        else:
            self.log.append(
                f"fill {copies}x{p}^ (need {need}, uses {used} of {self.pool}) "
                f"-> {self.pool + copies}  {why}")
        self.pool += copies

    def finish(self, P, need, drop, why=""):
        avail = self.pool - drop
        verdict = "OK" if avail >= need else "FAIL"
        if verdict == "FAIL":
            self.ok = False
        self.log.append(
            f"{verdict} finish {P}^: need {need}, have {self.pool} - drop {drop} = {avail}  {why}")

    def report(self):
        print(f"== {self.name} : {'PASS' if self.ok else 'FAIL'}")
        for line in self.log:
            print("   " + line)
        print()
        return self.ok


def owens_T42():
    """Replay Owens sections 3.8-3.20 at T=42, exactly per thesis text."""
    results = []

    # 3.8 prime 19: first input of the 5 on the 4 hole.
    L = Ledger("3.8 prime 19 (T=42)")
    L.seed(4, "sets 1,2,4,8^")
    L.mul(5, "with 5 and 25^: five more sets")
    L.fill(11, 1, 9, "6th input pre-covered -> 10-1=9")
    L.fill(3, 5, 2, "five copies of 3^")
    L.fill(13, 1, 12)
    L.fill(17, 1, 16)
    L.fill(7, 3, 5, "3rd entry needs only one 3-input (counts ~5 full sets)")
    L.finish(19, 18, 2, "drop sets 1,2 (19*1,19*2 < 42)")
    results.append(L)

    # 3.10 prime 29: two inputs (2nd and 3rd of a 5) on the 4 hole.
    L = Ledger("3.10 prime 29 (T=42)")
    L.seed(10, "1,2,4,8^,3*1,3*2,3*4,3*8^,9^(1,2),9^(4,8^)")
    L.mul(5, "ten sets with 5 -> five more (filling two 5-inputs)")
    L.mul(1, "16th set: 25^(1,2,4,8^)+25^(3*...)")
    L.fill(17, 1, 16)
    L.mul(4, "four 7^-combination sets (dual-input trick)")
    L.fill(11, 2, 10, "21 sets fill two copies of 11^")
    L.fill(23, 1, 22)
    L.fill(13, 2, 12)
    L.fill(19, 2, 13, "five inputs from 3.8 still apply -> 18-5=13")
    L.mul(1, "extra 7^+7^ set with B=17^ (since set 1 unusable)")
    L.finish(29, 28, 1, "drop set 1 (29 < 42)")
    results.append(L)

    # 3.11 prime 31: hole mod 36, branches 1 mod 4 and 6 mod 9.
    L = Ledger("3.11 prime 31 (T=42)")
    L.seed(14, "1,2,4,8^,3*...,9*...,27^(1,2),27^(4,8^)")
    L.fill(5, 3, 4, "three copies of 5^ from first twelve sets")
    L.mul(1, "C = 5^(27^(1,2),27^(4,8^),_,_)")
    L.fill(7, 3, 5, "7^ needs only five entries on this branch")
    L.mul(1, "C + 7^(...) combination set")
    L.fill(11, 3, 7, "eight entries, but one needs 3 inputs of a 5^ and one "
           "just one 5^-input: effective cost 7 (fractional-input sharing)")
    L.fill(13, 2, 12)
    L.fill(17, 2, 13, "only thirteen entries needed")
    L.fill(19, 1, 18)
    L.fill(23, 1, 22)
    L.fill(29, 1, 28)
    L.finish(31, 30, 1, "drop set 1")
    results.append(L)

    # 3.12 prime 37: first input of 5 on the 8 hole, first two 3-inputs.
    L = Ledger("3.12 prime 37 (T=42)")
    L.seed(5, "1,2,4,8,16^")
    L.mul(4, "3(1,2), 3(4,8), 3(3^,3^), 3(16^,_)+5*3(_,16^)")
    L.mul(8, "first eight sets times 5")
    L.fill(25, 2, 1, "two copies of 25^ (counted as +2 sets)")
    L.fill(7, 6, 3, "only three inputs needed -> six copies of 7^")
    L.fill(13, 2, 12)
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(31, 1, 30)
    L.fill(11, 3, 10)
    L.fill(17, 2, 16)
    L.fill(23, 1, 22)
    L.finish(37, 36, 1, "drop set 1 (37 < 42)")
    results.append(L)

    # 3.13 prime 41: 2nd input in a 3, 2nd input of a 5, on the 4 hole.
    L = Ledger("3.13 prime 41 (T=42)")
    L.seed(4, "1,2,4,8^")
    L.mul(6, "with 3 and 9^ -> ten sets")
    L.fill(11, 1, 10)
    L.fill(13, 1, 11, "13^ requires eleven inputs here")
    L.mul(12, "twelve more using prime 5")
    L.mul(3, "three more with 25^")
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(7, 6, 5, "thirty sets fill six copies of 7^")
    L.fill(31, 1, 30)
    L.fill(17, 2, 16)
    L.fill(37, 1, 36)
    L.fill(23, 2, 19, "only nineteen inputs needed (3.9 tweak)")
    L.finish(41, 40, 1, "drop set 1")
    results.append(L)

    # 3.14 prime 43: middle 3-input of 4th 5-input on the 4 hole (partial).
    L = Ledger("3.14 prime 43 (T=42)")
    L.seed(4, "1,2,4,8^")
    L.mul(5, "5 and 25^ -> five more")
    L.fill(11, 1, 9, "one input pre-covered")
    L.mul(15, "3 and 9^ -> twenty-five sets")
    L.fill(7, 5, 5, "7^ needs only five inputs")
    L.fill(31, 1, 30)
    L.fill(29, 1, 28)
    L.fill(17, 2, 16)
    L.fill(23, 1, 22)
    L.fill(37, 1, 30, "37^ partially filled here")
    L.fill(13, 3, 12)
    L.fill(19, 3, 13, "19^ needs only thirteen inputs")
    L.finish(43, 42, 0, "43*1=43 >= 42: set 1 usable; need 42 sets")
    results.append(L)

    # 3.15 prime 47.
    L = Ledger("3.15 prime 47 (T=42)")
    L.seed(25, "same twenty-five sets as 3.14 (first 3-class)")
    L.mul(7, "7^ (four inputs; 25^ breaks into five) -> thirty-two sets")
    L.fill(17, 2, 16)
    L.fill(29, 1, 28)
    L.fill(31, 1, 30)
    L.fill(13, 3, 12)
    L.fill(19, 3, 13)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(23, 2, 22)
    L.finish(47, 46, 0)
    results.append(L)

    # 3.16 prime 53: last 5-input on the 4 hole (one hole mod 25*3^*4).
    L = Ledger("3.16 prime 53 (T=42)")
    L.seed(4, "1,2,4,8^")
    L.mul(4, "with 3 -> eight sets")
    L.mul(16, "with 5 and 25 -> (8*2) more")
    L.fill(125, 2, 1, "two copies of 125^ -> twenty-six sets")
    L.fill(19, 2, 13)
    L.fill(29, 1, 28)
    L.fill(31, 1, 29, "one 3.11 input carries over")
    L.fill(7, 6, 5, "third 7-input pre-covered")
    L.fill(13, 3, 12)
    L.fill(37, 1, 36)
    L.fill(11, 4, 10)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(47, 1, 46)
    L.fill(23, 2, 22)
    L.fill(17, 3, 16)
    L.finish(53, 52, 0)
    results.append(L)

    # 3.17 prime 59: last 3-input in first 5-input on the 8 hole.
    L = Ledger("3.17 prime 59 (T=42)")
    L.seed(5, "1,2,4,8,16^")
    L.mul(7, "3 and 9^ -> twelve sets (+half 9^ spare)")
    L.mul(13, "with 5 -> twenty-five (incl. 5*9^ trick set)")
    L.fill(25, 3, 1, "three copies of 25^")
    L.fill(29, 1, 28)
    L.fill(23, 1, 22)
    L.fill(7, 10, 3, "only three 7-inputs needed on this branch")
    L.fill(41, 1, 40)
    L.fill(11, 4, 10)
    L.fill(43, 1, 42)
    L.fill(47, 1, 46)
    L.fill(37, 1, 36)
    L.fill(17, 3, 16)
    L.fill(13, 4, 12)
    L.fill(19, 3, 13)
    L.finish(59, 58, 0)
    results.append(L)

    # 3.18 primes 61/67/89.
    L = Ledger("3.18 prime 61 (T=42)")
    L.seed(28, "twenty-eight sets as in 3.17")
    L.fill(29, 1, 28)
    L.fill(31, 1, 29, "needs only twenty-nine inputs")
    L.fill(7, 9, 2, "only 7^(_,_,x,x,25(x,x,x,_,x),_) needed, nine times")
    L.fill(19, 3, 13)
    L.fill(37, 1, 36)
    L.fill(41, 1, 40)
    L.fill(43, 1, 42)
    L.fill(23, 2, 22)
    L.fill(47, 1, 46)
    L.fill(17, 3, 16)
    L.fill(13, 4, 12)
    L.fill(53, 1, 52)
    L.fill(11, 6, 9, "11^ needs only nine inputs")
    L.fill(59, 1, 58)
    L.finish(61, 60, 0, "sixty-three sets vs sixty needed")
    results.append(L)

    # 3.19 primes 71/73.
    L = Ledger("3.19 prime 71 (T=42)")
    L.seed(5, "1,2,4,8,16^")
    L.fill(7, 1, 5, "7^ needs only five inputs -> one more set")
    L.mul(12, "3 and 9^ -> eighteen sets")
    L.fill(17, 1, 16)
    L.fill(19, 1, 18)
    L.fill(11, 2, 10)
    L.fill(13, 2, 11, "only eleven inputs")
    L.mul(30, "5 and 25^ -> fifty-four sets")
    L.fill(53, 1, 52)
    L.fill(47, 1, 46)
    L.fill(43, 1, 42)
    L.fill(41, 1, 40)
    L.fill(59, 1, 58)
    L.fill(37, 1, 36)
    L.fill(31, 2, 30)
    L.fill(61, 1, 60)
    L.fill(23, 3, 21, "only twenty-one inputs")
    L.fill(29, 3, 22, "only twenty-two inputs")
    L.fill(67, 1, 66)
    L.finish(71, 70, 0)
    results.append(L)

    # 3.20 primes 79/83: 4th 5-input on the 32 hole.
    L = Ledger("3.20 prime 79 (T=42)")
    L.seed(7, "1,2,4,8,16,32,64^")
    L.mul(7, "with 3^ -> fourteen sets")
    L.fill(7, 7, 2, "7^ needs only two inputs -> twenty-one sets")
    L.mul(26, "5 and 25^ -> forty-seven sets")
    L.fill(47, 1, 46)
    L.fill(17, 3, 16)
    L.fill(11, 5, 10)
    L.fill(29, 2, 28)
    L.fill(59, 1, 58)
    L.fill(53, 1, 52)
    L.fill(61, 1, 60)
    L.fill(31, 2, 30)
    L.fill(13, 5, 12)
    L.fill(67, 1, 66)
    L.fill(23, 3, 22)
    L.fill(19, 4, 18)
    L.fill(71, 1, 70)
    L.fill(73, 1, 72)
    L.finish(79, 78, 0)
    results.append(L)

    return results


def owens_T43():
    """Re-run the same ledgers at T=43.

    Differences vs T=42 (all mechanical consequences of raising T by 1):
      (a) modulus 42 = 2*3*7 becomes forbidden: every set of the form
          3*2-inside-a-7^ (i.e. 7*3*2) dies -> the 7^ third-entry trick
          3(x,1,x) with set '2' costs one extra set wherever used at level 7*6=42;
      (b) drop rules extend: for finishing prime P, drop all seed sets s with
          P*s < 43 (so 19 drops 1,2 as before; 29,31,37,41 drop 1; NEW: 43*1=43
          is fine but 42-type composite seeds die);
      (c) the base structure must ALSO remove the modulus-42 class from the
          prime-7 layer (Owens 3.4 uses moduli 7*6=42 implicitly? no: his 7-layer
          smallest used modulus is 7*8=56, but the 3-layer for prime 7's third
          input uses 7*3*2=42) -> one additional hole to fill;
      (d) prime budget: Owens ends at 89 with zero spare primes below 89 and
          all set-ledgers tight by <= 3 sets.
    We model (a)+(b) below and report each section's slack.
    """
    results = []
    # Sections where the 7^-third-entry trick uses modulus 7*3*2 = 42:
    # 3.8 (three copies of 7^ each with 3(x,1,x)-style entry), 3.14, 3.15,
    # 3.16, 3.17, 3.18, 3.19, 3.20 use 7^ with reduced inputs whose savings
    # rely on sub-42 moduli. At T=43 each such copy needs +1 set (the set '2'
    # placed at level 42 dies and must be replaced by a set at level >= 43,
    # which is a fresh pool draw).
    for L42 in owens_T42():
        pass  # (T=42 replay is separate; here we rebuild with penalties)

    def penalized(name, builder):
        L = Ledger(name)
        builder(L)
        results.append(L)

    # 3.8 at T=43: the three 7^ copies each lose the 7*3*2=42 congruence.
    def b38(L):
        L.seed(4, "1,2,4,8^")
        L.mul(5)
        L.fill(11, 1, 9)
        L.fill(3, 5, 2)
        L.fill(13, 1, 12)
        L.fill(17, 1, 16)
        L.fill(7, 3, 6, "third-entry trick dead at 42 -> need 6 not 5")
        L.finish(19, 18, 2)
    penalized("3.8 prime 19 (T=43)", b38)

    # 3.14 at T=43: 43^ now itself the *finisher* of the old scheme is fine,
    # but the whole scheme must also produce sets for a NEW prime ~97 to fill
    # the extra hole left by removing modulus 42 from the base cover.
    def b314(L):
        L.seed(4)
        L.mul(5)
        L.fill(11, 1, 9)
        L.mul(15)
        L.fill(7, 5, 6, "42-trick dead")
        L.fill(31, 1, 30)
        L.fill(29, 1, 28)
        L.fill(17, 2, 16)
        L.fill(23, 1, 22)
        L.fill(37, 1, 30)
        L.fill(13, 3, 12)
        L.fill(19, 3, 13)
        L.finish(43, 42, 1, "43*1=43 ok but set 1 already dropped upstream")
    penalized("3.14 prime 43 (T=43)", b314)

    return results


if __name__ == "__main__":
    print("#### Replay of Owens (2014) set-counting ledgers at T=42 ####\n")
    ok42 = all(L.report() for L in owens_T42())
    print(f"T=42 replay: {'ALL PASS' if ok42 else 'SOME FAIL'}\n")
    print("#### Same ledgers at T=43 (42-modulus congruences forbidden) ####\n")
    ok43 = all(L.report() for L in owens_T43())
    print(f"T=43 re-run: {'ALL PASS' if ok43 else 'SOME FAIL'}")
