#!/bin/bash

for NUMBERS in 1 2 3 4 5;do
	c="HAWKESlong$NUMBERS.txt"
	echo $c
	qsub -v AHEAD=$NUMBERS,STEP=1000,OFILE=$c hawkespred.pbs
done
