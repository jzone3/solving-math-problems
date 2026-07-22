"""Exhaustive sweep: read graph6 from stdin (geng -t -d<ceil(n/3)> n),
filter maximal triangle-free, compute exact m*(G); report any counterexample
(m* <= 0 or LP infeasible) and track the minimum m* seen (near-miss frontier)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p02lib import parse_graph6, is_maximal_tf, exact_mstar
from fractions import Fraction

def main():
    total = mtf = 0
    worst = None  # (mstar, g6)
    cex = []
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        total += 1
        n, adj = parse_graph6(line)
        if not is_maximal_tf(n, adj):
            continue
        mtf += 1
        st, ms = exact_mstar(n, adj)
        if st == 'infeasible' or ms <= 0:
            cex.append((line, st, ms))
            print(f'COUNTEREXAMPLE {line} status={st} mstar={ms}', flush=True)
        elif worst is None or ms < worst[0]:
            worst = (ms, line)
            print(f'new min mstar={ms} g6={line}', flush=True)
    print(f'DONE total={total} mtf={mtf} counterexamples={len(cex)} '
          f'min_mstar={worst[0] if worst else None} argmin={worst[1] if worst else None}',
          flush=True)

if __name__ == '__main__':
    main()
