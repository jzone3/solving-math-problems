#!/bin/bash
cd "$(dirname "$0")"
K=/tmp/kissat/build/kissat
[ -f k10sf.log ] || setsid nohup $K t2sf_10.cnf > k10sf.log 2>&1 < /dev/null &
[ -f k11sf_sat.log ] || setsid nohup $K --sat t2sf_11.cnf > k11sf_sat.log 2>&1 < /dev/null &
[ -f k11sf_unsat.log ] || setsid nohup $K --unsat t2sf_11.cnf > k11sf_unsat.log 2>&1 < /dev/null &
[ -f k11sf_def.log ] || setsid nohup $K t2sf_11.cnf > k11sf_def.log 2>&1 < /dev/null &
[ -f k13sf_sat.log ] || setsid nohup $K --sat t2sf_13.cnf > k13sf_sat.log 2>&1 < /dev/null &
sleep 2
pgrep -ac kissat
