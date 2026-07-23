"""Laminar block construction: p=12, q=16 (4,3)-biregular instances with a
LAMINAR family of 6 nontrivial tight 3-cuts: blocks A,B,C,D (3 sources each,
each fully covering 3 private sinks) plus extra sink e1 drawn from A+B and
e2 drawn from C+D, making A, B, C, D, A+B, C+D all tight. The remaining 6
leftover arcs form 2 more sinks (any partition, may mix halves).
Exhausts C(6,3)^2 * 10 = 4000 instances."""
from itertools import combinations
from bipsearch import min_dicuts_bip, packs3

P = 12
AB = list(range(6))
CD = list(range(6, 12))


def main():
    base = []
    for b in range(4):
        blk = sorted([3 * b, 3 * b + 1, 3 * b + 2])
        base += [blk, blk, blk]
    n = tau3 = 0
    for e1 in combinations(AB, 3):
        r1 = [s for s in AB if s not in e1]
        for e2 in combinations(CD, 3):
            r2 = [s for s in CD if s not in e2]
            rem = r1 + r2
            for e3c in combinations(rem, 3):
                if rem[0] not in e3c:
                    continue  # fix rem[0] in e3 to avoid double count
                e4 = [s for s in rem if s not in e3c]
                sinks = base + [sorted(e1), sorted(e2), sorted(e3c), sorted(e4)]
                n += 1
                cuts, tau = min_dicuts_bip(P, sinks)
                if cuts is None or tau != 3:
                    continue
                tau3 += 1
                if not packs3(sinks, cuts):
                    print("UNSAT COUNTEREXAMPLE", sinks, flush=True)
                    with open("counterexample.txt", "a") as f:
                        f.write("LAMINAR %r\n" % (sinks,))
                if n % 500 == 0:
                    print(f"[laminar] n={n} tau3={tau3}", flush=True)
    print(f"[laminar] DONE n={n} tau3={tau3}", flush=True)


if __name__ == "__main__":
    main()
