#!/bin/bash

NODES=$1

osascript -e 'tell app "Terminal" 
        do script "cd ../secretsharing/blackbox/; python3 bbss.py  -n '$NODES' "
    end tell'
THRESHOLD=$(($NODES/3))
NONMAL=$(($NODES-$THRESHOLD ))
echo Total Nodes:         $NODES
echo Threshold:           $THRESHOLD 
echo Non Malicious nodes: $NONMAL

for i in `seq 1 $NODES`;
do
    j=$(($i-1))
        osascript -e 'tell app "Terminal" 
            do script "cd ../PSS/bbss_pss/; python3 bbss_pssnode.py -i '$j' -n '$NODES' -m 0"
        end tell'
done 
