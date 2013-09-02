#!/bin/bash

for ARcoef in 1 2 3 4 5 6 7 8 9 10;do
	for MAcoef in 1 2 3 4 5 6 7 8 9 10;do
		for NUMBERS in 1 2 3 4 5 ;do
			c="ARIMA$ARcoef$MAcoef$NUMBERS.txt"
			echo $c
			qsub -v AHEAD=$NUMBERS,STEP=1000,AR=$ARcoef,MA=$MAcoef,OFILE=$c arimacompare.pbs
		done
	done
done
