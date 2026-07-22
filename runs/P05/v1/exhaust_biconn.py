"""Exhaustive min-triple-intersection over all biconnected graphs of order n
(nauty-geng -C = 2-connected, isomorph-free). Reports the minimum t and counts.
Usage: python3 exhaust_biconn.py n [maxedges]
"""
import subprocess, sys
import core, search

def g6_to_adj(line):
    data = [ord(c) - 63 for c in line.strip()]
    n = data[0]
    assert n < 63
    bits = []
    for x in data[1:]:
        bits += [(x >> (5 - i)) & 1 for i in range(6)]
    adj = [[] for _ in range(n)]
    k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]:
                adj[i].append(j); adj[j].append(i)
            k += 1
    return adj

def main():
    n = int(sys.argv[1])
    maxe = sys.argv[2] if len(sys.argv) > 2 else None
    args = ['nauty-geng', '-C', str(n)]
    if maxe:
        args.append(f'0:{maxe}')
    p = subprocess.Popen(args, stdout=subprocess.PIPE, text=True, bufsize=1 << 20)
    best = None
    cnt = 0
    hist = {}
    for line in p.stdout:
        cnt += 1
        adj = g6_to_adj(line)
        r = core.longest_paths(adj, cap=50000, node_budget=2_000_000)
        if r is None:
            print('SKIP (budget):', line.strip())
            continue
        L, paths = r
        t = search.triple_score(paths, work_cap=500000)
        hist[t] = hist.get(t, 0) + 1
        if best is None or t < best[0]:
            best = (t, line.strip(), L, len(paths))
            print(f'n={n} new min t={t} g6={line.strip()} L={L}v paths={len(paths)}', flush=True)
            if t == 0:
                print('*** t=0 HIT — verify! ***')
                return
    print(f'n={n}: {cnt} biconnected graphs, min t={best[0]}, hist={sorted(hist.items())}', flush=True)

if __name__ == '__main__':
    main()
