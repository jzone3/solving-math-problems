#!/bin/bash
cd "$(dirname "$0")"
setsid nohup python3 exhaust_biconn.py 9 > exh9.log 2>&1 </dev/null &
setsid nohup python3 exhaust_biconn.py 10 18 > exh10e18.log 2>&1 </dev/null &
