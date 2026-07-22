"""Post-process sweep logs: for each COUNTEREXAMPLE graph6, report chromatic
class (3-colorable or not) and twin-freeness; flag twin-free non-3-colorable ones."""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p02lib import parse_graph6, degrees

def kcolorable(n, adj, k):
    col = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count('1'))
    def bt(i):
        if i == n:
            return True
        v = order[i]
        used = {col[u] for u in range(n) if (adj[v] >> u) & 1 and col[u] >= 0}
        for c in range(k):
            if c not in used:
                col[v] = c
                if bt(i + 1):
                    return True
        col[v] = -1
        return False
    return bt(0)

def main():
    tot = chi4 = tfree = both = 0
    for path in sys.argv[1:]:
        for line in open(path):
            m = re.match(r'COUNTEREXAMPLE (\S+)', line)
            if not m:
                continue
            g6 = m.group(1)
            n, adj = parse_graph6(g6)
            tot += 1
            c4 = not kcolorable(n, adj, 3)
            tw = not any(adj[u] == adj[v] for u in range(n) for v in range(u + 1, n))
            chi4 += c4; tfree += tw
            if c4 and tw:
                both += 1
                print(f'TWIN-FREE 4-CHROMATIC: {g6} n={n} deg={degrees(n,adj)}')
            elif c4:
                print(f'4-chromatic (has twins): {g6} n={n}')
    print(f'total={tot} chi>=4:{chi4} twin-free:{tfree} both:{both}')

if __name__ == '__main__':
    main()
