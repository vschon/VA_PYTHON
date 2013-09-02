#!/bin/bash

for NUMBERS in 1 2 3 4 5 6 7 8 9 10;do
	c="ARIMA$NUMBERS.txt"
	echo $c
	qsub -v AHEAD=$NUMBERS,STEP=2000,OFILE=$c arimapred.pbs
done
