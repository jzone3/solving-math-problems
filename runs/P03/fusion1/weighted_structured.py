#!/usr/bin/env python3
"""Structured weighted guide search on small incidence gadgets."""
import random
import time

from structured_search import incidence
from weighted import pack_w, tau_w


def sts7():
    return [(0,1,3),(1,2,4),(2,3,5),(3,4,6),
            (0,4,5),(1,5,6),(0,2,6)]


def sts9():
    return [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),
            (2,5,8),(0,4,8),(1,5,6),(2,3,7)]


def run(seconds=900, seed=0):
    rng = random.Random(seed)
    gadgets = []
    for v, blocks in ((7, sts7()), (9, sts9())):
        n, arcs = incidence(v, blocks)
        gadgets.append((f"STS{v}", n, arcs))
    started = time.time()
    tries = tau3 = gaps = 0
    while time.time() - started < seconds:
        name, n, arcs = rng.choice(gadgets)
        tries += 1
        mode = tries % 4
        if mode == 0:
            w = [rng.randint(0, 3) for _ in arcs]
        elif mode == 1:
            w = [1 if v >= n - len(set(y for _, y in arcs)) else 2
                 for _, v in arcs]
        else:
            w = [rng.randrange(1, 4) for _ in arcs]
        tw, _ = tau_w(n, arcs, w)
        if tw != 3:
            continue
        tau3 += 1
        ok3, _ = pack_w(n, arcs, w, 3, time_limit=20)
        if ok3:
            continue
        gaps += 1
        ok2, _ = pack_w(n, arcs, w, 2, time_limit=20)
        print("WEIGHTED_GAP", name, "tau_w=3", "pack3=", ok3,
              "pack2=", ok2, "weights=", w, flush=True)
        if ok2:
            return
    print({"tries": tries, "tau_w_3": tau3, "gaps": gaps,
           "seconds": round(time.time() - started, 1)}, flush=True)


if __name__ == "__main__":
    run(int(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else 900)
