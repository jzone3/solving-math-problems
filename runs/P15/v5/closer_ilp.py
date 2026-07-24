"""ILP closer: take a stalled partial cover, extract the exact residual cells
by subtraction, and close the residual with a global set-cover/assignment ILP
over candidate covers, instead of greedy DFS.

Candidates per residual cell (a mod M):
  - direct take: any unused divisor-compatible modulus m with m | k*M ...
    here restricted to m = M and unused divisors d | M, d >= L;
  - finisher chain: reserve-prime 2-chain (always available, cost ~2p);
  - 2-chain with palette tail: tail mods p*M*2^(K+1-j) + level takes M*2^k.

Each candidate is a set of (residue, modulus) classes. ILP: choose exactly one
candidate per cell s.t. all chosen moduli are pairwise distinct (each modulus
used at most once globally). Objective: minimize total classes.
"""
import json
import sys
import time
from math import gcd

import pulp

PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
          67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
          139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]


def _sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0:2] = b"\0\0"
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = b"\0" * len(s[i * i::i])
    return [i for i in range(2, n + 1) if s[i]]


TAIL_PRIMES = [p for p in _sieve(50000) if p > 199]


def crt(r1, m1, r2, m2):
    assert gcd(m1, m2) == 1
    inv = pow(m1, -1, m2)
    return (r1 + m1 * ((r2 - r1) * inv % m2)) % (m1 * m2)


def residual_cells(cong, cap=200000):
    cong = sorted(cong, key=lambda t: t[1])
    cells = {(0, 1)}
    for r, m in cong:
        new = set()
        for (a, M) in cells:
            g = gcd(M, m)
            if a % g != r % g:
                new.add((a, M))
                continue
            lcm = M // g * m
            for i in range(lcm // M):
                c = (a + i * M) % lcm
                if c % m != r:
                    new.add((c, lcm))
        cells = new
        if len(cells) > cap:
            raise RuntimeError(f"residual blowup {len(cells)}")
    return cells


def coalesce(cells):
    cells = set(cells)
    changed = True
    while changed:
        changed = False
        for (a, M) in list(cells):
            if (a, M) not in cells:
                continue
            for q in PRIMES:
                if M % q:
                    continue
                Mp = M // q
                sibs = [((a % Mp) + i * Mp, M) for i in range(q)]
                sibs = [(s % M, M) for s in [x for x, _ in sibs]]
                if all(s in cells for s in sibs):
                    for s in sibs:
                        cells.discard(s)
                    cells.add((a % Mp, Mp))
                    changed = True
                    break
    return cells


def divisors(n):
    divs = [1]
    nn = n
    for p in PRIMES:
        if p * p > nn:
            break
        e = 0
        while nn % p == 0:
            nn //= p
            e += 1
        if e:
            divs = [d * p**k for d in divs for k in range(e + 1)]
    if nn > 1:
        divs = [d * nn**k for d in divs for k in range(2)]
    return divs


def chain2_candidates(a, M, L, used, n_p=40):
    """2-chains with tail prime p: classes and their modulus set."""
    out = []
    pool = [p for p in PRIMES if p > 2] + TAIL_PRIMES[:60]
    cnt = 0
    for p in pool:
        if M % p == 0:
            continue
        K = max(p - 1, 1)
        while p * M * 2 ** (K + 1 - p) < L:
            K += 1
        mods = [p * M * 2 ** (K + 1 - j) for j in range(1, p + 1)] + \
               [M * 2 ** k for k in range(1, K + 1)]
        if any(m in used for m in mods) or len(set(mods)) != len(mods):
            continue
        classes = []
        for j in range(1, p + 1):
            anc = M * 2 ** (K + 1 - j)
            classes.append((crt(a % anc, anc, j % p, p), p * anc))
        for k in range(1, K + 1):
            classes.append(((a + M * 2 ** (k - 1)) % (M * 2 ** k),
                            M * 2 ** k))
        out.append(classes)
        cnt += 1
        if cnt >= n_p:
            break
    return out


def main(path, L=None, out_path=None):
    w = json.load(open(path))
    L = L or w["L"]
    cong = [(int(r), int(m)) for r, m in w["congruences"]]
    used = {m for _, m in cong}
    print(f"partial cover: {len(cong)} classes; extracting residual ...",
          flush=True)
    t0 = time.time()
    cells = residual_cells(cong)
    print(f"residual: {len(cells)} cells, {time.time()-t0:.1f}s", flush=True)
    cells = coalesce(cells)
    print(f"coalesced: {len(cells)} cells", flush=True)
    if not cells:
        print("already a cover!?")
        return
    meas = sum(1.0 / M for _, M in cells)
    print(f"residual measure {meas:.3e}; min mod "
          f"{min(M for _, M in cells)}, max mod {max(M for _, M in cells)}")

    # build candidates
    cand = {}  # cell -> list of class-lists
    for (a, M) in cells:
        lst = []
        if M >= L and M not in used:
            lst.append([(a % M, M)])
        for d in sorted(divisors(M), reverse=True):
            if d >= L and d != M and d not in used:
                lst.append([(a % d, d)])
                break
        lst.extend(chain2_candidates(a, M, L, used, n_p=25))
        if not lst:
            print(f"NO candidates for cell {a} mod {M}")
            return
        cand[(a, M)] = lst

    # ILP
    prob = pulp.LpProblem("closer", pulp.LpMinimize)
    x = {}
    mod_users = {}
    for cell, lst in cand.items():
        for i, classes in enumerate(lst):
            v = pulp.LpVariable(f"x_{cell[0]}_{cell[1]}_{i}", cat="Binary")
            x[(cell, i)] = v
            for _, m in classes:
                mod_users.setdefault(m, []).append(v)
    for cell, lst in cand.items():
        prob += pulp.lpSum(x[(cell, i)] for i in range(len(lst))) == 1
    for m, vs in mod_users.items():
        if len(vs) > 1:
            prob += pulp.lpSum(vs) <= 1
    prob += pulp.lpSum(len(cand[cell][i]) * v for (cell, i), v in x.items())
    print(f"ILP: {len(x)} vars, {len(cells)} cells, "
          f"{sum(1 for vs in mod_users.values() if len(vs) > 1)} "
          f"conflict constraints; solving ...", flush=True)
    t0 = time.time()
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=1800))
    print(f"status {pulp.LpStatus[status]}, {time.time()-t0:.1f}s", flush=True)
    if pulp.LpStatus[status] != "Optimal":
        print("ILP FAILED")
        sys.exit(1)
    add = []
    for (cell, i), v in x.items():
        if v.value() and v.value() > 0.5:
            add.extend(cand[cell][i])
    final = cong + add
    mods = [m for _, m in final]
    assert len(set(mods)) == len(mods), "modulus collision in ILP output"
    print(f"closed: +{len(add)} classes, total {len(final)}, "
          f"min mod {min(mods)}")
    op = out_path or path.replace(".json", "_closed.json")
    with open(op, "w") as f:
        json.dump({"L": L, "congruences": [[r, m] for r, m in final]}, f)
    print(f"wrote {op}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else None)
