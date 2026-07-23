"""4-colorability CNF encoding + solver helpers."""
import os, subprocess, tempfile

KISSAT = os.path.expanduser('~/p23/kissat/build/kissat')
DRATTRIM = os.path.expanduser('~/p23/drat-trim/drat-trim')

def color_cnf(n, edges, k=4, sym_clique=None):
    """Direct encoding: var(v,c) = v*k + c + 1."""
    cls = []
    for v in range(n):
        cls.append([v*k + c + 1 for c in range(k)])
        for c1 in range(k):
            for c2 in range(c1+1, k):
                cls.append([-(v*k + c1 + 1), -(v*k + c2 + 1)])
    for (u, v) in edges:
        for c in range(k):
            cls.append([-(u*k + c + 1), -(v*k + c + 1)])
    if sym_clique:
        for idx, v in enumerate(sym_clique):
            cls.append([v*k + idx + 1])
    return n*k, cls

def write_cnf(path, nvars, cls):
    with open(path, 'w') as f:
        f.write(f'p cnf {nvars} {len(cls)}\n')
        for c in cls:
            f.write(' '.join(map(str, c)) + ' 0\n')

def solve(nvars, cls, proof=None, timeout=None, quiet=True):
    """Returns ('UNSAT', None) or ('SAT', model) or ('UNKNOWN', None)."""
    with tempfile.NamedTemporaryFile('w', suffix='.cnf', delete=False) as f:
        cnf_path = f.name
    write_cnf(cnf_path, nvars, cls)
    cmd = [KISSAT, '-q', cnf_path]
    if proof:
        cmd.append(proof)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        os.unlink(cnf_path)
        return 'UNKNOWN', None
    out = r.stdout
    if not proof:
        os.unlink(cnf_path)
    else:
        import shutil
        shutil.move(cnf_path, proof + '.cnf')
    if 's UNSATISFIABLE' in out:
        return 'UNSAT', None
    if 's SATISFIABLE' in out:
        model = set()
        for line in out.splitlines():
            if line.startswith('v '):
                for tok in line[2:].split():
                    l = int(tok)
                    if l > 0:
                        model.add(l)
        return 'SAT', model
    return 'UNKNOWN', None

def is_4colorable(n, edges, timeout=None, sym_clique=None):
    nvars, cls = color_cnf(n, edges, 4, sym_clique=sym_clique)
    st, model = solve(nvars, cls, timeout=timeout)
    return st, model
