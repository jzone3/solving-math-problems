import sys, time
sys.path.insert(0,'.')
from t2lib import dfs_t2
t=time.time()
cnt = dfs_t2(8, count_all=True, time_budget=10800)
print("T2(8) completions of identity row (unordered rows, lex-sorted):", cnt, f"{time.time()-t:.0f}s")
