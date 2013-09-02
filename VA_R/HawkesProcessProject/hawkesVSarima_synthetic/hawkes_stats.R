source('~/data/va_R/tsutil/tsutil.R')
source('~/data/va_R/performanceeval/performanceeval.R')

#load data

rmseTable=array(0,dim=c(1,5))
correctTable=array(0,dim=c(1,5))
correlationTable=array(0,dim=c(1,5))

for(ahead in 1:5){
      file=paste('HAWKESlong',ahead,'.txt',sep='')
      print(file)
      x=read.table(file,sep=',')
      eval=featureeval(x,paste('HAWKES',ahead,sep=''))
      rmseTable[1,ahead]=eval[[1]]
      correlationTable[1,ahead]=eval[[2]]
      correctTable[1,ahead]=eval[[3]]
}


write.table(rmseTable,'HAWKES_RMSE.csv',sep=',')
write.table(correctTable,'HAWKES_correct.csv',sep=',')

write.table(correlationTable,'HAWKES_correlation.csv',sep=',')

