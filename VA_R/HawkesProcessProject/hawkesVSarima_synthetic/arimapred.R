library(forecast)
library(tseries)
source('~/data/va_R/tsutil/tsutil.R')

args=commandArgs(TRUE)
ahead=as.integer(args[1])
step=as.integer(args[2])
arOrder=as.integer(args[3])
maOrder=as.integer(args[4])
ofile=args[5]

reg_price=read.table("regData.csv",sep=',')
reg_price=as.matrix(reg_price)
dprice=diff(reg_price[,2])
n=length(dprice)
testingTime0=as.integer(n/2)
#trainingSet=dprice[0:(n/3)]
#fit=auto.arima(trainingSet,d=0,allowdrift=FALSE)

resultTable=array(0,dim=c(step,2))
count=0

for(i in testingTime0:(testingTime0+step-1)){
    fit=arima(dprice[0:(i-ahead)],order=c(arOrder,0,maOrder),include.mean=FALSE)
    count=count+1
    resultTable[count,1]=sum(forecast(fit,h=ahead)$mean)
    resultTable[count,2]=reg_price[i,2]-reg_price[(i-ahead),2]
    
    print(count)
    print(resultTable[count,])
}

write.table(resultTable,ofile,sep=',')



