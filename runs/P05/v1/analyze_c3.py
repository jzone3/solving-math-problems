"""Diagnose the t=3 plateau of the C3-symmetric family: which orbit do the three
longest paths always share? Runs short anneals, and for each t=3 optimum with exactly
3 longest paths, classifies the 3 shared vertices (hub / pendant / arm position)."""
import random
import core
from weighted import LP, realize
from c3sym import build, rand_quotient, mutate

def classify(v, k, hp):
    npend = 3 if hp else 0
    if v < 3:
        return f'hub{v}'
    if hp and v < 6:
        return f'pend{v-3}'
    if v < 3 + npend + 3 * k:
        i = (v - 3 - npend) // k
        return f'arm{i}[{(v - 3 - npend) % k}]'
    return f'subdiv{v}'

def main():
    lp = LP()
    found = 0
    for rr in range(200):
        if found >= 12:
            break
        k = random.randint(3, 6)
        arm_e, la, ra, hp, hh = rand_quotient(k, 6)
        cur = (k, arm_e, la, ra, hp, hh)
        adj, w = build(*cur)
        if not core.is_connected(adj):
            continue
        radj = realize(adj, w)
        if len(radj) > 54:
            continue
        ev = lp.score(radj)
        for it in range(3000):
            T = 1.5 * (1 - it / 3000) + 0.05
            cur2 = mutate(cur[0], 8, cur[1], cur[2], cur[3], cur[4], cur[5], 6)
            adj2, w2 = build(*cur2)
            if not core.is_connected(adj2):
                continue
            radj2 = realize(adj2, w2)
            if len(radj2) > 54:
                continue
            ev2 = lp.score(radj2)
            d = (ev2[0] - ev[0]) + 0.01 * (ev[1] - ev2[1])
            if d <= 0 or random.random() < pow(2.718, -d / T):
                cur, ev = cur2, ev2
            if ev[0] == 3:
                break
        if ev[0] != 3:
            continue
        adj, w = build(*cur)
        radj = realize(adj, w)
        L, pl = core.longest_paths(radj, cap=100000)
        masks = sorted(set(m for _, m in pl))
        if len(masks) > 40 or len(masks) < 3:
            continue
        # triple-min: find a minimizing triple
        best = None
        n = len(masks)
        for a in range(n):
            for b in range(a + 1, n):
                for c in range(b + 1, n):
                    x = masks[a] & masks[b] & masks[c]
                    cnt = bin(x).count('1')
                    if best is None or cnt < best[0]:
                        best = (cnt, x)
        cnt, x = best
        verts = [v for v in range(len(radj)) if (x >> v) & 1]
        kk, _, _, _, hp, _ = cur
        labs = [classify(v, kk, hp) if v < len(adj) else f'subdiv(orig<{len(adj)})' for v in verts]
        print(f'run{rr}: t={cnt} L={L} paths={len(masks)} shared={labs} k={kk} hp={hp} hh={cur[5]}', flush=True)
        found += 1

if __name__ == '__main__':
    main()
