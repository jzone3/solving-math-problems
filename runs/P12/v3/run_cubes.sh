#!/bin/bash
# usage: run_cubes.sh cubedir jobs
cd "$(dirname "$0")"
D=$1; J=${2:-3}
ls $D/cube*.cnf | xargs -P $J -I{} bash -c '
  f={}; out=${f%.cnf}.res
  [ -f $out ] && exit 0
  /tmp/kissat/build/kissat -q $f > ${f%.cnf}.log 2>&1
  ec=$?
  if [ $ec -eq 10 ]; then echo SAT > $out; grep "^v" ${f%.cnf}.log >> $out
  elif [ $ec -eq 20 ]; then echo UNSAT > $out; rm ${f%.cnf}.log
  else echo UNKNOWN $ec > $out; fi
'
echo "done: $(grep -l UNSAT $D/*.res 2>/dev/null | wc -l) UNSAT, $(grep -l SAT $D/*.res 2>/dev/null | grep -v UNSAT | wc -l) files, total $(ls $D/*.res 2>/dev/null | wc -l)"
