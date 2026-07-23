#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 exhaust_biconn.py 11 16 > exh11e16.log 2>&1 </dev/null &
