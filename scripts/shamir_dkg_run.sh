#!/bin/bash

NODES=$1

osascript -e 'tell app "Terminal" 
        do script "cd ../secretsharing/shamir/; python3 shamirsharing.py  -n '$NODES' "
    end tell'
THRESHOLD=$(($NODES/3))
NONMAL=$(($NODES-$THRESHOLD))
echo Total Nodes:         $NODES
echo Threshold:           $THRESHOLD 
echo Non Malicious nodes: $NONMAL

for i in `seq 1 $NODES`;
do
    j=$(($i-1))
    if [ $i -gt $NONMAL ]
    then
        osascript -e 'tell app "Terminal" 
            do script "cd ../DKG/sss_dkg/; python3 sssnode.py -i '$j' -n '$NODES' -m 1"
        end tell'
    else
        osascript -e 'tell app "Terminal" 
            do script "cd ../DKG/sss_dkg/; python3 sssnode.py -i '$j' -n '$NODES' -m 0"
        end tell'
    fi 
done 
    
