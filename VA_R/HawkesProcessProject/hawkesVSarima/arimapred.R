library(forecast)
library(tseries)
source('~/data/va_R/tsutil/tsutil.R')

args=commandArgs(TRUE)
#print(args)
#print(class(args))
#print(dim(args))
#print(length(args))
ahead=as.integer(args[1])
step=as.integer(args[2])
ofile=args[3]
#print(ahead)
#print(step)
#print(ofile)

data<-read.table('~/data/vaData/goog_2010_dec.csv',header=TRUE,sep=';')
test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
idx<-tapply(1:NROW(data),data$TIME,"[",1)
data_red<-data[idx,c(2:3)]  
day_01_idx<-(data_red$TIME>=as.POSIXct("2010-12-01 09:30:00",format="%Y-%m-%d %H:%M:%S"))&(data_red$TIME<=as.POSIXct("2010-12-01 16:00:00",format="%Y-%m-%d %H:%M:%S"))
day_01<-data_red[t(day_01_idx),]

n=dim(day_01)[1]
goog_data=array(0,dim=c(n,2))
goog_data[,1]=as.double(day_01[,1])
goog_data[,2]=as.double(day_01[,2])
goog_data[,1]=goog_data[,1]-goog_data[1,1]


regGoog=TimeSeriesRegularization_C(goog_data)
dGoog=diff(regGoog[,2])
n=length(dGoog)
testingTime0=as.integer(n/2)
nTesting=n-testingTime0+1

trainingSet=dGoog[1:(n/3)]

fit=auto.arima(trainingSet,d=0,allowdrift=FALSE)

resultTable=array(0,dim=c(step,2))

count=0

for(i in testingTime0:(testingTime0+step-1)){
  fit=arima(dGoog[0:(i-ahead)],order=c(3,0,2),include.mean=FALSE)
  count=count+1
  resultTable[count,1]=sum(forecast(fit,h=ahead)$mean)
  resultTable[count,2]=regGoog[i,2]-regGoog[(i-ahead),2]

}

r=resultTable[1:step,]
write.table(r,ofile,sep=',')

