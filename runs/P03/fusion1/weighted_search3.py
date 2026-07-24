"""Modest weighted Woodall search for tau_w=3."""

import random
import sys
import time

from weighted import pack_w, random_dag, tau_w, weakly_connected


def search(seconds=300, seed=0):
    rng = random.Random(seed)
    started = time.time()
    tries = tau3 = 0
    while time.time() - started < seconds:
        tries += 1
        n = rng.randint(6, 12)
        arcs = random_dag(rng, n, rng.randint(n + 2, min(30, 2 * n + 8)))
        if not weakly_connected(n, arcs):
            continue
        weights = [rng.randint(1, 3) for _ in arcs]
        tw, _ = tau_w(n, arcs, weights)
        if tw != 3:
            continue
        tau3 += 1
        ok, classes = pack_w(n, arcs, weights, 3, time_limit=10)
        if not ok:
            ok2, _ = pack_w(n, arcs, weights, 2, time_limit=10)
            if ok2:
                print("WEIGHTED_GAP", {"n": n, "arcs": arcs,
                      "weights": weights, "tau_w": tw,
                      "pack2": ok2}, flush=True)
                return
    print({"tries": tries, "tau_w_3": tau3,
           "seconds": round(time.time() - started, 1)}, flush=True)


if __name__ == "__main__":
    search(int(sys.argv[1]) if len(sys.argv) > 1 else 300,
           int(sys.argv[2]) if len(sys.argv) > 2 else 0)
