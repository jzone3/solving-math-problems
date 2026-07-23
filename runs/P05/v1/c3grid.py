"""Exhaustive parametric grid over the C3-symmetric spur-arm family.

Arm = path of a unit edges from left terminal to right terminal, with up to two spurs
(dead-end paths) of lengths s1,s2 attached at positions d1,d2 along the arm. Hubs may
carry a pendant path of length hp and direct hub-hub chords of length hh (0 = absent).
Vertices are all unit (weights realized as subdivisions implicitly: everything is unit
edges here, lengths ARE the subdivision counts). Exact scoring via ./lp.

The hope: longest path = deep-spur ... hub ... deep-spur using ONE hub only (or two),
whose Z3 rotations have empty common intersection (t=0).
"""
import itertools, json, sys, time
from weighted import LP

def build_graph(a, spurs, hp, hh):
    """Returns adjacency list. Hubs 0,1,2. Arm i: path of a edges between hub i and
    hub i+1 (a-1 internal vertices); spurs (d,s): path of s edges hanging at internal
    position d (1..a-1); hp: pendant path of hp edges at each hub; hh: hub-hub path of
    hh edges (1 = direct edge)."""
    adj = [[] for _ in range(3)]
    def nv():
        adj.append([])
        return len(adj) - 1
    def add(u, v):
        adj[u].append(v); adj[v].append(u)
    def path(u, v, length):
        prev = u
        for _ in range(length - 1):
            x = nv(); add(prev, x); prev = x
        add(prev, v)
    for i in range(3):
        # arm path with internal vertices, remembering them for spur attachment
        internal = []
        prev = i
        for _ in range(a - 1):
            x = nv(); add(prev, x); internal.append(x); prev = x
        add(prev, (i + 1) % 3)
        for (d, s) in spurs:
            tip = nv()
            if s > 1:
                path(internal[d - 1], tip, s)
            else:
                add(internal[d - 1], tip)
        if hp:
            tip = nv()
            if hp > 1:
                path(i, tip, hp)
            else:
                add(i, tip)
        if hh:
            if hh > 1:
                x = nv()
                path(i, x, hh - 1); add(x, (i + 1) % 3)
            else:
                add(i, (i + 1) % 3)
    return adj

def main():
    lp = LP()
    best = (999,)
    cnt = 0
    t0 = time.time()
    for a in range(2, 9):
        for hp in range(0, 9):
            for hh in [0, 1]:
                spur_opts = [(d, s) for d in range(1, a) for s in range(1, 9)]
                # one spur
                combos = [[sp] for sp in spur_opts]
                # two spurs (d1<=d2)
                combos += [[s1, s2] for s1, s2 in itertools.combinations_with_replacement(spur_opts, 2)]
                for spurs in combos:
                    adj = build_graph(a, spurs, hp, hh)
                    if len(adj) > 60:
                        continue
                    cnt += 1
                    t, L, nm, ovf = lp.score(adj)
                    if ovf:
                        continue
                    if (t,) < best:
                        best = (t,)
                        print(f'best t={t} L={L} a={a} spurs={spurs} hp={hp} hh={hh} n={len(adj)} masks={nm}', flush=True)
                        if t == 0:
                            json.dump({'a': a, 'spurs': spurs, 'hp': hp, 'hh': hh, 'adj': adj},
                                      open(f'HIT_c3grid_{int(time.time())}.json', 'w'))
                            print('*** t=0 HIT — verify independently! ***', flush=True)
                            return
    print(f'done {cnt} configs in {time.time()-t0:.0f}s, min t={best[0]}', flush=True)

if __name__ == '__main__':
    main()
