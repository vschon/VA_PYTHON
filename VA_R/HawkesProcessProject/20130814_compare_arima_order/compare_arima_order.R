source('~/data/va_R/hawkes/hawkes.R')
source('~/data/va_R/tsutil/tsutil.R')
source('~/data/va_R/arima/arima.R')

args=commandArgs(TRUE)
ahead=as.integer(args[1])
step=as.integer(args[2])
arorder=as.integer(args[3])
maorder=as.integer(args[4])
ofile=args[5]

ArimaPrediction(ahead,step,arorder,maorder,ofile,'regData.csv',1000)
