source('~/data/va_R/hawkes/hawkes.R')
source('~/data/va_R/tsutil/tsutil.R')

#Simulate a price sequence and verify the prediction power 
alpha=array(c(0.2,0.5,0.5,0.22),dim=c(2,2))
beta=array(c(1,1,1,1),dim=c(2,2))
mu=array(c(0.3,0.3),dim=c(2,1))
#Simulate an entire path
x=BivariateHawkesSimulation(5000,mu,alpha,beta)
ireg_price=BivariateHawkesPriceSimulation_new(x[[1]],x[[4]])
reg_price=TimeSeriesRegularization_C(ireg_price)
write.table(x[[1]],'rawData1.csv',sep=',',col.names=F,row.names=F)
write.table(x[[2]],'rawData2.csv',sep=',',col.names=F,row.names=F)
write.table(x[[3]],'rawData3.csv',sep=',',col.names=F,row.names=F)
write.table(x[[4]],'rawData4.csv',sep=',',col.names=F,row.names=F)
write.table(x[[5]],'rawData5.csv',sep=',',col.names=F,row.names=F)
write.table(reg_price,'regData.csv',sep=',',col.names=F,row.names=F)


