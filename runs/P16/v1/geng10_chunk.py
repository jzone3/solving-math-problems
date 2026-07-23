import sys, subprocess, math
import numpy as np
from exhaustive_geng import g6_to_adj, margins
res, mod = int(sys.argv[1]), int(sys.argv[2])
proc = subprocess.Popen(["nauty-geng","-c","-q","10",f"{res}/{mod}"], stdout=subprocess.PIPE, text=True, bufsize=1<<20)
best44=(-1e18,None); best46=(-1e18,None); cnt=0
for line in proc.stdout:
    line=line.strip()
    if not line: continue
    cnt+=1
    m44,m46 = margins(g6_to_adj(line))
    if m44 is not None and m44>best44[0]: best44=(m44,line)
    if m46 is not None and m46>best46[0]: best46=(m46,line)
    if (m44 or -1)>1e-9: print("VIOLATION44",line,m44,flush=True)
    if (m46 or -1)>1e-9: print("VIOLATION46",line,m46,flush=True)
print(f"chunk {res}/{mod} graphs={cnt} best44={best44} best46={best46}")
