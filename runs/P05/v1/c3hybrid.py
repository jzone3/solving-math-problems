"""C3-symmetric hybrids with hypotraceable arms.

Arm = a 3-stub piece (hypotraceable/hypohamiltonian seed minus one cubic vertex, as in
hybridize.py). Three copies of a piece are wired Z3-symmetrically: stub j of copy i is
attached to hub h_{f(j)} shifted by i, where f assigns each of the 3 stubs to hub-slot
'left' (i), 'right' (i+1), or 'skip' (a fresh pendant tip / the third hub i+2).
All assignments f in {L,R,P,T}^3 are tried; optional hub pendant paths.
Exact scoring via ./lp for realized graphs up to 60 vertices... pieces are large
(Petersen-9: fine; VCZ13-12: fine; Thomassen34-33: 3 copies = 102 too big, skipped).
"""
import itertools, json, time
import core
from weighted import LP
from hybridize import pieces_from
import json as _json

PETERSEN = [[1, 4, 5], [0, 2, 6], [1, 3, 7], [2, 4, 8], [0, 3, 9],
            [0, 7, 8], [1, 8, 9], [2, 5, 9], [3, 5, 6], [4, 6, 7]]

def delete_any(adj, v):
    from hybridize import delete_vertex
    return delete_vertex(adj, v)

def load_pieces():
    seeds = core.load_seeds('seeds.jsonl')
    seeds['Petersen'] = PETERSEN
    out = []
    for name, adj in seeds.items():
        if len(adj) > 16:
            continue
        for v in range(len(adj)):
            if 2 <= len(adj[v]) <= 4:
                out.append((f'{name}-d{v}', delete_any(adj, v)))
    return out

def build(piece, assign, hp):
    """piece = (adj, stubs); assign in {'L','R','T','P'}^len(stubs); hp pendant length."""
    padj, stubs = piece
    k = len(padj)
    adj = [[] for _ in range(3)]
    def nv():
        adj.append([]); return len(adj) - 1
    def add(u, v):
        adj[u].append(v); adj[v].append(u)
    def pathto(u, length):
        prev = u
        for _ in range(length):
            x = nv(); add(prev, x); prev = x
        return prev
    for i in range(3):
        off = len(adj)
        for _ in range(k):
            nv()
        for u in range(k):
            for v in padj[u]:
                if u < v:
                    add(off + u, off + v)
        for j, s in enumerate(stubs):
            a = assign[j]
            if a == 'L':
                add(i, off + s)
            elif a == 'R':
                add((i + 1) % 3, off + s)
            elif a == 'T':
                add((i + 2) % 3, off + s)
            else:  # P: pendant tip
                pathto(off + s, 1)
    for i in range(3):
        if hp:
            pathto(i, hp)
    return adj

def main():
    lp = LP()
    pieces = load_pieces()
    print(f'{len(pieces)} pieces', flush=True)
    best = 999
    cnt = 0
    for (name, pc) in pieces:
        ns = len(pc[1])
        for assign in itertools.product('LRTP', repeat=ns):
            if 'L' not in assign and 'R' not in assign:
                continue
            for hp in range(0, 6):
                adj = build(pc, assign, hp)
                if len(adj) > 58 or not core.is_connected(adj):
                    continue
                cnt += 1
                t, L, nm, ovf = lp.score(adj)
                if ovf:
                    continue
                if t < best:
                    best = t
                    print(f'best t={t} L={L} {name} assign={assign} hp={hp} n={len(adj)} masks={nm}', flush=True)
                    if t == 0:
                        _json.dump({'name': name, 'assign': assign, 'hp': hp, 'adj': adj},
                                   open(f'HIT_c3hyb_{int(time.time())}.json', 'w'))
                        print('*** t=0 HIT — verify independently! ***', flush=True)
                        return
    print(f'done {cnt} configs, min t={best}', flush=True)

if __name__ == '__main__':
    main()
