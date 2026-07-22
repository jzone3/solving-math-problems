#!/bin/bash
cd "$(dirname "$0")"
pkill -f '^\./anneal 117' ; pkill -f '^\./anneal 120'; pkill -f '^\./anneal 132'
sleep 1
B48=$(python3 - <<'EOF'
import json,re
s=open('/tmp/cwm.json').read(); s=re.sub(r',\s*}','}',s)
d=json.loads(s)
pos,neg=d['CW(48,6)']['sets'][0]
b=[0]*48
for i in pos: b[i]=1
for i in neg: b[i]=-1
print(','.join(map(str,b)))
EOF
)
nohup ./lift 96 24 6 $RANDOM 12000 "2,0,0,1,0,2,1,1,2,-2,1,0,0,-2,0,-1,2,2,-1,-1,0,0,-1,0" 60 > logs/lift_96_24.log 2>&1 &
nohup ./lift 96 48 6 $RANDOM 12000 "$B48" 60 > logs/lift_96_48.log 2>&1 &
nohup ./lift 105 21 6 $RANDOM 12000 "1,0,1,-2,0,-1,1,1,0,1,4,0,-1,1,1,0,1,-2,0,-1,1" 60 > logs/lift_105_21.log 2>&1 &
nohup ./lift 112 16 6 $RANDOM 12000 "0,1,1,-1,-3,-1,2,1,0,1,1,-1,3,-1,2,1" 60 > logs/lift_112_16.log 2>&1 &
nohup ./lift 96 16 6 $RANDOM 12000 "1,0,-1,2,0,0,1,1,1,0,3,2,-2,0,-3,1" 60 > logs/lift_96_16.log 2>&1 &
(
for combo in "35 3 6" "39 3 6" "30 4 7" "44 3 9" "33 4 9" "28 4 6" "24 5 7" "26 5 9"; do
  set -- $combo
  ./fold $1 $2 $3 $RANDOM 1200 20 >> folds/fold_$1_$3.txt 2>> folds/fold.err
done
) > /dev/null 2>&1 &
echo launched
