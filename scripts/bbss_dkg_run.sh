#!/bin/bash

NODES=$1

osascript -e 'tell app "Terminal" 
        do script "cd ../secretsharing/blackbox/; python3 bbss.py  -n '$NODES' "
    end tell'
THRESHOLD=$(($NODES/3))


if [ $(($NODES%3)) -eq 0 ]
then 
    THRESHOLD=$(($(($NODES/3)) - 1))
fi

NONMAL=$(($NODES-$THRESHOLD ))
echo Total Nodes:         $NODES
echo Threshold:           $THRESHOLD 
echo Non Malicious nodes: $NONMAL

for i in `seq 1 $NODES`;
do
    j=$(($i-1))
        osascript -e 'tell app "Terminal" 
            do script "cd ../DKG/bbss_dkg/; python3 bbssnode.py -i '$j' -n '$NODES' -m 0"
        end tell'
done 
    
