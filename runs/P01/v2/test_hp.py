"""Cross-check dfs.c's hamiltonian-path test against brute force."""
import random, subprocess, itertools

def hp_brute(n, edges, s, t):
    adjset = set()
    for u, v in edges:
        adjset.add((u, v)); adjset.add((v, u))
    others = [v for v in range(n) if v not in (s, t)]
    for perm in itertools.permutations(others):
        seq = [s] + list(perm) + [t]
        if all((seq[i], seq[i+1]) in adjset for i in range(n - 1)):
            return 1
    return 0

random.seed(7)
bad = 0
for trial in range(400):
    n = random.randint(4, 8)
    edges = [(u, v) for u in range(n) for v in range(u+1, n) if random.random() < 0.45]
    s, t = random.sample(range(n), 2)
    if (s, t) in edges or (t, s) in edges:
        continue
    inp = f"{len(edges)} {s} {t}\n" + "\n".join(f"{u} {v}" for u, v in edges)
    out = subprocess.run(["./dfs", str(n), "0", "0", "hptest"], input=inp,
                         capture_output=True, text=True)
    a = int(out.stdout.strip())
    b = hp_brute(n, edges, s, t)
    assert a == b, (n, edges, s, t, a, b)
print("ALL OK: 400 ham-path cross-checks passed")
