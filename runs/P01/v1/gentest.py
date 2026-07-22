import random, subprocess, time
def rand_4reg(n, rng):
    while True:
        edges = set((i,(i+1)%n) for i in range(n))
        p = list(range(n)); rng.shuffle(p)
        e2 = set((min(p[i],p[(i+1)%n]), max(p[i],p[(i+1)%n])) for i in range(n))
        if e2 & edges: continue
        return sorted(edges|e2)
rng = random.Random(7)
for n in (22,26,30,34):
    e = rand_4reg(n,rng)
    inp = f"{n}\n" + "\n".join(f"{a} {b}" for a,b in e)
    t=time.time()
    out = subprocess.run(["./search","count"], input=inp, capture_output=True, text=True)
    print(n, out.stdout.strip(), f"{time.time()-t:.2f}s")
