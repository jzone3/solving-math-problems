"""Crossing tight-cut construction: p=12, q=16 (4,3)-biregular with CROSSING
nontrivial tight 3-cuts. Note tight source-sets in this class have sizes
3,6,9 (4k-3 must be divisible by 3), and size-3 tight sets are exactly full
blocks, so crossing pairs must be size-6 sets sharing a block: S1=A+B,
S2=B+C. Blocks A,B,C,D each fully cover 3 private sinks; extra sink
e1 in A+B and e2 in B+C (sharing B's leftovers) make S1, S2 both tight and
crossing. Remaining 6 leftovers form sinks e3,e4. Exhaustive."""
from itertools import combinations
from bipsearch import min_dicuts_bip, packs3

P = 12
A, B, C, D = [0, 1, 2], [3, 4, 5], [6, 7, 8], [9, 10, 11]


def main():
    base = []
    for blk in (A, B, C, D):
        base += [blk, blk, blk]
    n = tau3 = 0
    for e1 in combinations(A + B, 3):
        rem1 = [s for s in range(12) if s not in e1]
        for e2 in combinations([s for s in B + C if s in rem1], 3):
            if not (set(e1) & set(B)) or not (set(e2) & set(B)):
                continue  # require genuine crossing through B
            rem2 = [s for s in rem1 if s not in e2]
            for e3 in combinations(rem2, 3):
                if rem2[0] not in e3:
                    continue
                e4 = [s for s in rem2 if s not in e3]
                sinks = base + [sorted(e1), sorted(e2), sorted(e3), sorted(e4)]
                n += 1
                cuts, tau = min_dicuts_bip(P, sinks)
                if cuts is None or tau != 3:
                    continue
                tau3 += 1
                if not packs3(sinks, cuts):
                    print("UNSAT COUNTEREXAMPLE", sinks, flush=True)
                    with open("counterexample.txt", "a") as f:
                        f.write("CROSSING %r\n" % (sinks,))
                if n % 1000 == 0:
                    print(f"[crossing] n={n} tau3={tau3}", flush=True)
    print(f"[crossing] DONE n={n} tau3={tau3}", flush=True)


if __name__ == "__main__":
    main()
