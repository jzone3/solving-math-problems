#!/bin/bash
cd /home/ubuntu/p20/gen
G=/tmp/distri-GENREG/GENREG95/genreg
n=$1
mkdir -p n$n
for i in $(seq 1 8); do
  ( $G $n 4 6 -a stdout -m $i 8 2> n$n/err.$i.txt | gzip > n$n/asc.$i.gz ) &
done
wait
echo DONE > n$n/done.flag
