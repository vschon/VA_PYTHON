source('~/data/va_R/tsutil/tsutil.R')
source('~/data/va_R/performanceeval/performanceeval.R')

#load data

rmseTable=array(0,dim=c(20,5))
correctTable=array(0,dim=c(20,5))
correlationTable=array(0,dim=c(20,5))

for(ar in 1:5){
   for(ma in 1:4){
        for(ahead in 1:5){
	    file=paste('ARIMA',ar,ma,ahead,'.txt',sep='')
	    print(file)
            x=read.table(file,sep=',')
	    eval=featureeval(x,paste('ARIMA',ar,ma,ahead,sep=''))
	    rmseTable[((ar-1)*4+ma),ahead]=eval[[1]]
            correlationTable[((ar-1)*4+ma),ahead]=eval[[2]]
	    correctTable[((ar-1)*4+ma),ahead]=eval[[3]]
        }
    }
}

write.table(rmseTable,'ARIMA_RMSE.csv',sep=',')

write.table(correctTable,'ARIMA_correct.csv',sep=',')

write.table(correlationTable,'ARIMA_correlation.csv',sep=',')
