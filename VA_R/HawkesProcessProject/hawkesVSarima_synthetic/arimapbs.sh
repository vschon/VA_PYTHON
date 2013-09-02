#!/bin/bash

for ARcoef in 5;do
	for MAcoef in 5;do
		for NUMBERS in 1 2 3 4 5 ;do
			c="ARIMA$ARcoef$MAcoef$NUMBERS.txt"
			echo $c
			qsub -v AHEAD=$NUMBERS,STEP=1000,AR=$ARcoef,MA=$MAcoef,OFILE=$c arimapred.pbs
		done
	done
done
