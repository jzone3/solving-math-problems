"""Smallest witness produced so far by any worker in this directory."""
import glob
import os
import pickle
import sys


def all_witnesses(pat=('greedy_*.pkl', 'tlns_*.pkl', 'coremin_*.pkl',
                       'best_*.pkl')):
    out = []
    for p in pat:
        for f in glob.glob(os.path.join(os.path.dirname(__file__) or '.', p)):
            try:
                S = pickle.load(open(f, 'rb'))
            except Exception:
                continue
            if isinstance(S, list) and S and isinstance(S[0], int):
                out.append((len(S), f))
    return sorted(out)


if __name__ == '__main__':
    ws = all_witnesses()
    if '--path' in sys.argv:
        print(ws[0][1])
    else:
        for n, f in ws:
            print(f'{n:6d}  {f}')
