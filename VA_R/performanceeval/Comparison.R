library(forecast)
library(tseries)
source('~/Desktop/R_Analysis_Framework/TimeSeries/TimeSeriesUtility.R')
library(hexbin)
#Load raw data
####1. Features of HF data####

####1.1 distribution of price change per tick####
data<-read.table('goog_2010_dec.csv',header=TRUE,sep=';')
test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
price=data$PRICE
dprice=diff(price)
n=length(dprice)
n_positive=sum(dprice>0)
n_negative=sum(dprice<0)
n0=sum(dprice==0)
n0_005=sum(dprice>0&dprice<=0.05)
n005_01=sum(dprice>0.05&dprice<=0.1)
n01_=sum(dprice>0.1)


nM005_0=sum(dprice<0&dprice>=-0.05)
nM01_005=sum(dprice< -0.05&dprice>=-0.1)
nM01_=sum(dprice< -0.1)

dprice_dist=c(nM01_/n,nM01_005/n,nM005_0/n,n0/n,n0_005/n,n005_01/n,n01_/n)
jpeg('dprice_dist.jpeg',height=800,width=800)
barplot(dprice_dist,names.arg=c("<-0.1","[-0.1,-0.05)","[-0.05,0)","0","(0,0.05]","(0.05,0.1]",">0.1"),
        main="Distribution of price change per transaction (278322 data points)")
dev.off()

####1.2 distribution of price change per second####

data<-read.table('goog_2010_dec.csv',header=TRUE,sep=';')
test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
idx<-tapply(1:NROW(data),data$TIME,"[",1)
data_red<-data[idx,c(2:3)]  
day_01_idx<-(data_red$TIME>=as.POSIXct("2010-12-01 09:30:00",format="%Y-%m-%d %H:%M:%S"))&(data_red$TIME<=as.POSIXct("2010-12-01 16:00:00",format="%Y-%m-%d %H:%M:%S"))
day_01<-data_red[t(day_01_idx),]
jpeg('price20101201',height=800,width=800)
plot(day_01[,2]~day_01[,1],type='s',xlab='time',ylab='Price',main='price on 2010-12-01')
dev.off()

#transform time type to double
n=dim(day_01)[1]
goog_data=array(0,dim=c(n,2))
goog_data[,1]=as.double(day_01[,1])
goog_data[,2]=as.double(day_01[,2])
goog_data[,1]=goog_data[,1]-goog_data[1,1]


regGoog=TimeSeriesRegularization_C(goog_data)
dGoog=diff(regGoog[,2])

n=length(dGoog)
n_positive=sum(dGoog>0)
n_negative=sum(dGoog<0)
n0=sum(dGoog==0)
n0_005=sum(dGoog>0&dGoog<=0.05)
n005_01=sum(dGoog>0.05&dGoog<=0.1)
n01_=sum(dGoog>0.1)


nM005_0=sum(dGoog<0&dGoog>=-0.05)
nM01_005=sum(dGoog< -0.05&dGoog>=-0.1)
nM01_=sum(dGoog< -0.1)

dprice_dist=c(nM01_/n,nM01_005/n,nM005_0/n,n0/n,n0_005/n,n005_01/n,n01_/n)
jpeg('dGoog_sec_dist.jpeg',height=800,width=800)
barplot(dprice_dist,names.arg=c("<-0.1","[-0.1,-0.05)","[-0.05,0)","0","(0,0.05]","(0.05,0.1]",">0.1"),
        main="Distribution of price change per second (23400 data points)")
dev.off()
####2. ARIMA prediction####
data<-read.table('goog_2010_dec.csv',header=TRUE,sep=';')
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

trainingSet=dGoog[0:(n/3)]
jpeg('differenced_Goog_data.jpeg',width=800,height=800)
plot(trainingSet,type='p')
dev.off()
#find best fit order  arima model
#best fit:ARIMa(3,0,2)
jpeg('differenceACF.jpeg',width=800,height=800)
acf(trainingSet)
dev.off()

jpeg('differencePACF.jpeg',width=800,height=800)
pacf(trainingSet)
dev.off()

fit=auto.arima(trainingSet,d=0,allowdrift=FALSE)
jpeg('Fit_diagnosis.jpeg',width=800,height=800)
tsdiag(fit)
dev.off()

#Use separate code,refer to ARIMA_prediction_*_step.R
s1=read.table('1step.txt',sep=',')
s2=read.table('2step.txt',sep=',')
s3=read.table('3step.txt',sep=',')
s4=read.table('4step.txt',sep=',')
s5=read.table('5step.txt',sep=',')
s6=read.table('6step.txt',sep=',')
s7=read.table('7step.txt',sep=',')
s8=read.table('8step.txt',sep=',')
s9=read.table('9step.txt',sep=',')
s10=read.table('10step.txt',sep=',')


number=length(s1[,1])

####2.1 metric 1: root mean square error####
rmseARIMA=array(0,dim=c(10,1))
rmseARIMA[1]=sqrt(sum((s1[,1]-s1[,2])**2)/number)

rmseARIMA[2]=sqrt(sum((s2[,1]-s2[,2])**2)/number)

rmseARIMA[3]=sqrt(sum((s3[,1]-s3[,2])**2)/number)

rmseARIMA[4]=sqrt(sum((s4[,1]-s4[,2])**2)/number)

rmseARIMA[5]=sqrt(sum((s5[,1]-s5[,2])**2)/number)

rmseARIMA[6]=sqrt(sum((s6[,1]-s6[,2])**2)/number)

rmseARIMA[7]=sqrt(sum((s7[,1]-s7[,2])**2)/number)

rmseARIMA[8]=sqrt(sum((s8[,1]-s8[,2])**2)/number)

rmseARIMA[9]=sqrt(sum((s9[,1]-s9[,2])**2)/number)

rmseARIMA[10]=sqrt(sum((s10[,1]-s10[,2])**2)/number)

jpeg('rmseARIMA.jpeg',width=800,height=800)
plot(rmseARIMA,type='p',xlab='look-ahead steps',ylab='RMSE',main="RMSE of ARIMA model")
dev.off()

####2.2 metric 2: correlation between prediction and true price change####
corrARIMA=array(0,dim=c(10,1))
corrARIMA[1]=cor(s1[,1],s1[,2])
corrARIMA[2]=cor(s2[,1],s2[,2])
corrARIMA[3]=cor(s3[,1],s3[,2])
corrARIMA[4]=cor(s4[,1],s4[,2])
corrARIMA[5]=cor(s5[,1],s5[,2])
corrARIMA[6]=cor(s6[,1],s6[,2])
corrARIMA[7]=cor(s7[,1],s7[,2])
corrARIMA[8]=cor(s8[,1],s8[,2])
corrARIMA[9]=cor(s9[,1],s9[,2])
corrARIMA[10]=cor(s10[,1],s10[,2])

jpeg('correlationARIMA.jpeg',width=800,height=800)
plot(corrARIMA,type='p',xlab='look-ahead steps',,ylab='Correlation',main="Correlation of ARIMA model")
dev.off()

####2.3 metric 3: scatter plot of prediction and true price change####
jpeg('1stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s1,pch=20,xlab='predicted price change',ylab='real price change',main='1-step ahead prediction')
dev.off()

jpeg('2stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s2,pch=20,xlab='predicted price change',ylab='real price change',main='2-step ahead prediction')
dev.off()

jpeg('3stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s3,pch=20,xlab='predicted price change',ylab='real price change',main='3-step ahead prediction')
dev.off()

jpeg('4stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s4,pch=20,xlab='predicted price change',ylab='real price change',main='4-step ahead prediction')
dev.off()

jpeg('5stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s5,pch=20,xlab='predicted price change',ylab='real price change',main='5-step ahead prediction')
dev.off()

jpeg('6stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s6,pch=20,xlab='predicted price change',ylab='real price change',main='6-step ahead prediction')
dev.off()

jpeg('7stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s7,pch=20,xlab='predicted price change',ylab='real price change',main='7-step ahead prediction')
dev.off()

jpeg('8stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s8,pch=20,xlab='predicted price change',ylab='real price change',main='8-step ahead prediction')
dev.off()

jpeg('9stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s9,pch=20,xlab='predicted price change',ylab='real price change',main='9-step ahead prediction')
dev.off()

jpeg('10stepARIMA_scatterplot.jpeg',width=800,height=800)
plot(s10,pch=20,xlab='predicted price change',ylab='real price change',main='10-step ahead prediction')
dev.off()

####2.4 metric 4: percentage of correct prediction####
CorrectPercentage<-function(forecastTable){
  total=length(forecastTable[,1])
  forecastDirection=array(0,dim=c(total,1))
  realDirection=array(0,dim=c(total,1))
  
  #redifine forecast direction
  
  riseOnRise=0
  fallOnRise=0
  
  riseOnFall=0
  fallOnFall=0
  
  for (i in 1:total){
    if(forecastTable[i,1]<0){
      forecastDirection[i]=-1
    }
    else if (forecastTable[i,1]>0){
      forecastDirection[i]=1
    }
    
    if(forecastTable[i,2]<0){
      realDirection[i]=-1
    }
    else if (forecastTable[i,2]>0){
      realDirection[i]=1
    }
    
    if(realDirection[i]>0&&forecastDirection[i]>0) riseOnRise=riseOnRise+1
    if(realDirection[i]<0&&forecastDirection[i]>0) fallOnRise=fallOnRise+1
    if(realDirection[i]<0&&forecastDirection[i]<0) fallOnFall=fallOnFall+1
    if(realDirection[i]>0&&forecastDirection[i]<0) riseOnFall=riseOnFall+1
  }
  
  riseCount=sum(forecastDirection==1)
  fallCount=sum(forecastDirection==-1)
  flatCount=sum(forecastDirection==0)
  
  return (list((riseOnRise+fallOnFall)/(riseCount+fallCount)),riseOnRise/riseCount,fallOnRise/riseCount,fallOnFall/fallCount,riseOnFall/fallCount))
}

correctRateARIMA=array(0,dim=c(10,1))
correctRateARIMA[1]=CorrectPercentage(s1)[[1]]
correctRateARIMA[2]=CorrectPercentage(s2)[[1]]
correctRateARIMA[3]=CorrectPercentage(s3)[[1]]
correctRateARIMA[4]=CorrectPercentage(s4)[[1]]
correctRateARIMA[5]=CorrectPercentage(s5)[[1]]
correctRateARIMA[6]=CorrectPercentage(s6)[[1]]
correctRateARIMA[7]=CorrectPercentage(s7)[[1]]
correctRateARIMA[8]=CorrectPercentage(s8)[[1]]
correctRateARIMA[9]=CorrectPercentage(s9)[[1]]
correctRateARIMA[10]=CorrectPercentage(s10)[[1]]

jpeg('correctRateARIMA.jpeg',width=800,height=800)
plot(correctRateARIMA,type='p',xlab='look-ahead steps',,ylab='Correct Rate',main="Correct Rate of ARIMA model")
dev.off()

####2.5 metric 5: Regression and residual analysis: Model the relationship between prediction and true value####

####3. Hawked process model####
#Data processing

#Distribute duplicated trades uniformly within one second
#Use thinned classification

data<-read.table('goog_2010_dec.csv',header=TRUE,sep=';')

#process data for comparison
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


data<-read.table('goog_2010_dec.csv',header=TRUE,sep=';')
#process data for hawkes process
fullData=TAQDataExtraction(data,beginTime="20101201 09:30:00.000",endTime="20101201 16:00:00.000")
#Decomposed into t,subprocess1,subprocess2,tType
x=TAQHawkesDecomposition(fullData)

steps=5000
count=0
ahead=1
resultTable=array(0,dim=c(steps+100,2))

n=as.double(strptime("20101201 16:00:00.000",format="%Y%m%d %H:%M:%OS"))-as.double(strptime("20101201 09:30:00.000",format="%Y%m%d %H:%M:%OS"))
mu_0<-array(c(0.5,0.5),dim=c(2,1));
alpha_0<-array(c(0.5,0.5,0.5,0.5),dim=c(2,2));
theta<-c(mu_0,alpha_0);
testingTime0=as.integer(n/2)
i=testingTime0
trainingSet=list()

count=0

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

for(i in testingTime0:(testingTime0+100)){
  trainingSet[[1]]=x[[1]][x[[1]]<=(i-ahead)]
  trainingSet[[2]]=x[[2]][x[[2]]<=(i-ahead)]
  trainingSet[[3]]=x[[3]][x[[3]]<=(i-ahead)]
  trainingSet[[4]]=x[[4]][x[[1]]<=(i-ahead)]
  

  
  trainingSet[[5]]=CalculateHistoryRate(trainingSet[[1]],trainingSet[[4]],mu,alpha,beta,length(trainingSet[[1]]))
  
  MCResult=Price_MCSimulation_BivariateHawkes(ahead*5,mu,alpha,beta,500,initialValue=0,history=trainingSet)
  
  count=count+1
  resultTable[count,1]=MCResult[[2]][i]-MCResult[[2]][i-ahead]
  resultTable[count,2]=sum(dGoog[(i-ahead+1):i])

  print(count)
  print(resultTable[count,])
}

r=resultTable[1:100,]

