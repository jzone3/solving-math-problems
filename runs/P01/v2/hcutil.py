"""Shared helpers: call the compiled hc counter; brute-force reference counter."""
import subprocess, itertools, os

HC_BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hc")

def hc_count(n, edges, cutoff=10**9):
    inp = f"{n} {len(edges)} {cutoff}\n" + "\n".join(f"{u} {v}" for u, v in edges)
    out = subprocess.run([HC_BIN], input=inp, capture_output=True, text=True, check=True)
    return int(out.stdout.strip())

def hc_count_brute(n, edges):
    """Reference: enumerate all vertex permutations starting at 0 (multigraph-aware)."""
    from collections import Counter
    mult = Counter()
    for u, v in edges:
        a, b = min(u, v), max(u, v)
        mult[(a, b)] += 1
    def m(u, v):
        return mult[(min(u, v), max(u, v))]
    total = 0
    for perm in itertools.permutations(range(1, n)):
        seq = (0,) + perm
        ways = 1
        for i in range(n):
            ways *= m(seq[i], seq[(i + 1) % n])
            if ways == 0:
                break
        total += ways
    assert total % 2 == 0
    return total // 2
