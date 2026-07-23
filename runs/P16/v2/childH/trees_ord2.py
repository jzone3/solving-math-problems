"""childH: ord2-sum test on all trees n in [nmin, nmax]."""
import subprocess
import sys

from common import g6_adj
from exp1_ord2sum import ord2_sum_feasible


def trees(n):
    p = subprocess.Popen(f"nauty-gentreeg -q {n} | nauty-copyg -g", shell=True,
                         stdout=subprocess.PIPE, text=True)
    for line in p.stdout:
        yield line.strip()


if __name__ == "__main__":
    nmin, nmax = int(sys.argv[1]), int(sys.argv[2])
    for n in range(nmin, nmax + 1):
        tot, fails = 0, []
        for g6 in trees(n):
            tot += 1
            if not ord2_sum_feasible(g6_adj(g6)):
                fails.append(g6)
        print(f"trees n={n}: {tot}, ord2-sum fails={len(fails)}", flush=True)
        for g in fails[:100]:
            print("FAIL", g)
