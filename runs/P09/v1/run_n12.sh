#!/bin/bash
# Full exhaustive n=12 sweep in 64 parts, 8 parallel
cd "$(dirname "$0")"
mkdir -p c12
seq 0 63 | xargs -P 8 -I{} sh -c 'if [ ! -f c12/n12_p{}.done ]; then nauty-geng -q 12 {}/64 2>/dev/null | ./bn_check 12 n12p{} > c12/n12_p{}.out 2> c12/n12_p{}.log && touch c12/n12_p{}.done; fi'
echo ALLDONE > c12/n12_ALL.done
