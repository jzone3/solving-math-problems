"""Edge-flip hill-climb / annealing on the PADDED objective
  Phi(H) = max_{n>=nH} [A/n - 4m^2/n^2] - R(H)^2
(Phi > 0 for any H => counterexample to WoW 129 as H + isolated vertices).
Floats for speed; any positive re-checked with mpmath elsewhere.
Seeds: random G(n,p), clique, clique+noise. Prints best per (n, restart).
"""
import math, random, sys

def phi(n_h, deg, m, R):
    A = sum(d * (d + 1) for d in deg)
    if m == 0:
        return -1e18, n_h
    nstar = 8 * m * m / A
    best = None
    for n in {n_h, max(n_h, int(nstar)), max(n_h, int(nstar) + 1)}:
        v = A / n - 4 * m * m / (n * n) - R * R
        if best is None or v > best[0]:
            best = (v, n)
    return best

def full_R(adj, deg):
    R = 0.0
    for u in range(len(adj)):
        for v in adj[u]:
            if v > u:
                R += 1.0 / math.sqrt(deg[u] * deg[v])
    return R

def run(n, iters, seed, mode):
    rnd = random.Random(seed)
    adj = [set() for _ in range(n)]
    if mode == "clique":
        k = rnd.randint(3, n)
        for i in range(k):
            for j in range(i):
                adj[i].add(j); adj[j].add(i)
        # noise
        for _ in range(rnd.randint(0, 3 * n)):
            u, v = rnd.sample(range(n), 2)
            if v in adj[u]:
                adj[u].discard(v); adj[v].discard(u)
            else:
                adj[u].add(v); adj[v].add(u)
    else:
        p = rnd.random()
        for i in range(n):
            for j in range(i):
                if rnd.random() < p:
                    adj[i].add(j); adj[j].add(i)
    deg = [len(a) for a in adj]
    m = sum(deg) // 2
    R = full_R(adj, deg)
    cur, _ = phi(n, deg, m, R)
    best = cur
    T0 = 0.5
    for it in range(iters):
        T = T0 * (1 - it / iters)
        u, v = rnd.sample(range(n), 2)
        # delta R: edges at u and v change weight
        present = v in adj[u]
        du, dv = deg[u], deg[v]
        ndu, ndv = (du - 1, dv - 1) if present else (du + 1, dv + 1)
        if (present and du == 1) or (present and dv == 1):
            pass
        dR = 0.0
        for w in adj[u]:
            if w == v: continue
            dR += 1/math.sqrt(ndu*deg[w]) - 1/math.sqrt(du*deg[w])
        for w in adj[v]:
            if w == u: continue
            dR += 1/math.sqrt(ndv*deg[w]) - 1/math.sqrt(dv*deg[w])
        if present:
            dR -= 1/math.sqrt(du*dv)
        else:
            dR += 1/math.sqrt(ndu*ndv)
        if ndu == 0 or ndv == 0:
            dR2 = dR  # fine
        deg[u], deg[v] = ndu, ndv
        nm = m - 1 if present else m + 1
        nv, _ = phi(n, deg, nm, R + dR)
        if nv >= cur or rnd.random() < math.exp(min(0.0, (nv - cur)) / max(T, 1e-9)):
            cur = nv; m = nm; R = R + dR
            if present:
                adj[u].discard(v); adj[v].discard(u)
            else:
                adj[u].add(v); adj[v].add(u)
            if cur > best:
                best = cur
        else:
            deg[u], deg[v] = du, dv
        if it % 20000 == 0:
            R = full_R(adj, deg)  # resync float drift
    return best

if __name__ == "__main__":
    ns = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [12, 16, 20, 30, 40, 60]
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 200000
    restarts = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    overall = -1e18
    for n in ns:
        for r in range(restarts):
            mode = "clique" if r % 2 else "rand"
            b = run(n, iters, 1000 * n + r, mode)
            overall = max(overall, b)
            print(f"n={n} restart={r} mode={mode}: best Phi={b:.6f}", flush=True)
    print(f"OVERALL best Phi = {overall:.6f}")
