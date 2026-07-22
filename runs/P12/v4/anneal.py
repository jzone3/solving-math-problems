#!/usr/bin/env python3
"""Simulated annealing / restart local search for T2(n).

State: n rows, each a permutation of 0..n-1. Cost = duplicate dist-1 slots +
duplicate dist-2 slots (0 => valid T2(n); see t2_common.cost).

Moves: swap two symbols within a row; reverse a segment of a row;
relocate one symbol within a row. Incremental cost via pair multiset counts.

Usage: anneal.py n [seconds] [seed]
Writes best_T2_{n}_seed{seed}.txt (best array found) and prints best cost trace.
"""
import random
import sys
import time

from t2_common import cost, write_witness


class State:
    def __init__(self, n, rng):
        self.n = n
        self.rng = rng
        self.rows = [list(rng.sample(range(n), n)) for _ in range(n)]
        self.c1 = {}  # (a,b) -> count at dist 1
        self.c2 = {}
        self.cost = 0
        for r in self.rows:
            for i in range(n - 1):
                self._add(self.c1, (r[i], r[i + 1]))
            for i in range(n - 2):
                self._add(self.c2, (r[i], r[i + 2]))

    def _add(self, d, p):
        v = d.get(p, 0)
        if v >= 1:
            self.cost += 1
        d[p] = v + 1

    def _rem(self, d, p):
        v = d[p]
        if v >= 2:
            self.cost -= 1
        d[p] = v - 1

    def _row_pairs(self, r, lo, hi):
        """Pairs of row r touching columns in [lo,hi]."""
        n = self.n
        row = self.rows[r]
        out1, out2 = [], []
        for i in range(max(0, lo - 1), min(n - 1, hi + 1)):
            out1.append((row[i], row[i + 1]))
        for i in range(max(0, lo - 2), min(n - 2, hi + 2)):
            out2.append((row[i], row[i + 2]))
        return out1, out2

    def apply(self, r, lo, hi, newseg):
        """Replace rows[r][lo:hi+1] with newseg, updating cost. Returns undo."""
        p1, p2 = self._row_pairs(r, lo, hi)
        for p in p1:
            self._rem(self.c1, p)
        for p in p2:
            self._rem(self.c2, p)
        old = self.rows[r][lo:hi + 1]
        self.rows[r][lo:hi + 1] = newseg
        p1, p2 = self._row_pairs(r, lo, hi)
        for p in p1:
            self._add(self.c1, p)
        for p in p2:
            self._add(self.c2, p)
        return old

    def random_move(self):
        n, rng = self.n, self.rng
        r = rng.randrange(n)
        kind = rng.random()
        if kind < 0.5:  # swap two positions
            i, j = rng.sample(range(n), 2)
            lo, hi = min(i, j), max(i, j)
            seg = self.rows[r][lo:hi + 1]
            seg2 = seg[:]
            seg2[0], seg2[-1] = seg2[-1], seg2[0]
            return r, lo, hi, seg2
        elif kind < 0.8:  # reverse segment
            i, j = rng.sample(range(n), 2)
            lo, hi = min(i, j), max(i, j)
            return r, lo, hi, self.rows[r][lo:hi + 1][::-1]
        else:  # relocate symbol from i to j
            i, j = rng.sample(range(n), 2)
            lo, hi = min(i, j), max(i, j)
            seg = self.rows[r][lo:hi + 1]
            if i < j:
                seg2 = seg[1:] + [seg[0]]
            else:
                seg2 = [seg[-1]] + seg[:-1]
            return r, lo, hi, seg2


def run(n, seconds, seed):
    rng = random.Random(seed)
    best = None
    best_cost = 10 ** 9
    t_end = time.time() + seconds
    restart = 0
    while time.time() < t_end:
        restart += 1
        st = State(n, rng)
        T = 3.0
        alpha = 0.99998
        stall = 0
        while time.time() < t_end and stall < 400000:
            r, lo, hi, seg = st.random_move()
            c0 = st.cost
            old = st.apply(r, lo, hi, seg)
            d = st.cost - c0
            if d > 0 and rng.random() >= pow(2.718281828, -d / T):
                st.apply(r, lo, hi, old)
                stall += 1
            else:
                stall = stall + 1 if d >= 0 else 0
                if st.cost < best_cost:
                    best_cost = st.cost
                    best = [row[:] for row in st.rows]
                    print(f"[seed {seed} restart {restart}] cost {best_cost}", flush=True)
                    if best_cost == 0:
                        return best, 0
            T = max(T * alpha, 0.15)
        # restart
    return best, best_cost


def main():
    n = int(sys.argv[1])
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 300
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    best, bc = run(n, seconds, seed)
    assert cost(best) == bc, "incremental cost mismatch"
    out = f"best_T2_{n}_seed{seed}.txt"
    write_witness(best, out)
    print(f"FINAL n={n} seed={seed} best_cost={bc} -> {out}", flush=True)


if __name__ == "__main__":
    main()
