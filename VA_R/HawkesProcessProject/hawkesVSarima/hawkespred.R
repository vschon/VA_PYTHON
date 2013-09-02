library(forecast)
library(tseries)
source('~/data/va_R/tsutil/tsutil.R')
source('~/data/va_R/hawkes/hawkes.R')

args=commandArgs(TRUE)
ahead=as.integer(args[1])
step=as.integer(args[2])
ofile=args[3]

data<-read.table('~/data/vaData/goog_2010_dec.csv',header=TRUE,sep=';')

#process data for hawkes process
fullData=TAQDataExtraction(data,beginTime="20101201 09:30:00.000",endTime="20101201 16:00:00.000")

#process data for comparison

test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
day_01_idx<-(data$TIME>=as.POSIXct("2010-12-01 09:30:00",format="%Y-%m-%d %H:%M:%S"))&(data$TIME<=as.POSIXct("2010-12-01 16:00:00",format="%Y-%m-%d %H:%M:%S"))
day_01<-data[t(day_01_idx),]

idx<-tapply(1:NROW(data),data$TIME,"[",1)
data_red<-data[idx,c(2:3)]  
n=dim(day_01)[1]
goog_data=array(0,dim=c(n,2))
goog_data[,1]=as.double(day_01[,1])
goog_data[,2]=as.double(day_01[,2])
goog_data[,1]=goog_data[,1]-goog_data[1,1]


regGoog=TimeSeriesRegularization_C(goog_data)
dGoog=diff(regGoog[,2])

#Decomposed into t,subprocess1,subprocess2,tType
x=TAQHawkesDecomposition(fullData)

count=0
resultTable=array(0,dim=c(step,2))

n=as.double(strptime("20101201 16:00:00.000",format="%Y%m%d %H:%M:%OS"))-as.double(strptime("20101201 09:30:00.000",format="%Y%m%d %H:%M:%OS"))
mu_0<-array(c(0.5,0.5),dim=c(2,1));
alpha_0<-array(c(0.5,0.5,0.5,0.5),dim=c(2,2));
theta<-c(mu_0,alpha_0);
testingTime0=as.integer(n/2)
trainingSet=list()

count=0
#Learn the parameters
trainingSet[[1]]=x[[1]][x[[1]]<=(testingTime0-100)]
trainingSet[[2]]=x[[2]][x[[2]]<=(testingTime0-100)]
trainingSet[[3]]=x[[3]][x[[3]]<=(testingTime0-100)]
trainingSet[[4]]=x[[4]][x[[1]]<=(testingTime0-100)]
par<-constrOptim.nl(par=theta,fn=BivariateHawkesLikelihood,gr=BivariateHawkesGradient,
                    hin=BivariateHawkeshin,
                    control.outer=list(trace=FALSE),control.optim=list(trace=FALSE,fnscale=-0.01),
                    points=trainingSet);

mu<-array(c(par$par[1:2]),dim=c(2,1));
alpha<-array(par$par[3:6],dim=c(2,2));
beta<-array(c(1,1,1,1),dim=c(2,2));

for(i in testingTime0:(testingTime0+step-1)){
    trainingSet[[1]]=x[[1]][x[[1]]<=(i-ahead)]
    trainingSet[[2]]=x[[2]][x[[2]]<=(i-ahead)]
    trainingSet[[3]]=x[[3]][x[[3]]<=(i-ahead)]
    trainingSet[[4]]=x[[4]][x[[1]]<=(i-ahead)]
    
    trainingSet[[5]]=CalculateHistoryRate(trainingSet[[1]],trainingSet[[4]],mu,alpha,beta,length(trainingSet[[1]]))
    
    MCResult=Price_MCSimulation_BivariateHawkes(ahead*10,mu,alpha,beta,500,initialValue=0,history=trainingSet)
    
    count=count+1
    resultTable[count,1]=MCResult[[2]][i]-MCResult[[2]][i-ahead]
    resultTable[count,2]=sum(dGoog[(i-ahead+1):i])
    print(count)
    print(resultTable[count,])
}
write.table(resultTable,ofile,sep=',')
