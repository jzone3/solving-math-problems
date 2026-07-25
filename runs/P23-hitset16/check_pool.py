import pickle,sys,time,os,subprocess,tempfile
from sat import color_cnf,write_cnf,KISSAT,DRATTRIM
pkl,tag=sys.argv[1:3]
pts,edges=pickle.load(open(pkl,'rb')); nvars,cls=color_cnf(len(pts),edges,4)
print(f'{tag}: vertices={len(pts)} edges={len(edges)} clauses={len(cls)} vars={nvars}',flush=True)
with tempfile.TemporaryDirectory(prefix='p23hitset-') as d:
 cnf=os.path.join(d,tag+'.cnf'); proof=os.path.join(d,tag+'.drat')
 write_cnf(cnf,nvars,cls); t=time.time()
 r=subprocess.run([KISSAT,'-q',cnf,proof],capture_output=True,text=True)
 print(f'kissat_seconds={time.time()-t:.3f}',flush=True); print(r.stdout, end='')
 if 's UNSATISFIABLE' not in r.stdout: print('status=NOT_UNSAT'); sys.exit(2)
 t=time.time(); q=subprocess.run([DRATTRIM,cnf,proof],capture_output=True,text=True)
 print(f'drat_trim_seconds={time.time()-t:.3f}',flush=True); print(q.stdout,end=''); print(q.stderr,end='')
 if 's VERIFIED' not in q.stdout: print('drat=status_NOT_VERIFIED'); sys.exit(3)
 print('drat=VERIFIED')
