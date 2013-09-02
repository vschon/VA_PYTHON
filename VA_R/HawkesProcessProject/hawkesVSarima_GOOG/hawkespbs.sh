#!/bin/bash

for NUMBERS in 5 6 7 8 9 10;do
	c="HAWKES$NUMBERS.txt"
	echo $c
	qsub -v AHEAD=$NUMBERS,STEP=2000,OFILE=$c hawkespred.pbs
done
