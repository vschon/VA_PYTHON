
library(compiler)
library(alabama)

dyn.load('~/data/va_R/hawkes/CalculateRMatrix_C.so')
source('~/data/va_R/tsutil/tsutil.R')
####Simulation####
CalculateHistoryRate<-function(t,tType,mu,alpha,beta,total_index){
#   browser()
  tRate=array(0,dim=c(total_index,2))
  for(i in 0:(total_index-1)){
    value<- BivariateHawkesLambdaValue(t[(i+1)],i,t,tType,tRate,mu,alpha,beta);
    if(tType[i+1]==1){
      tRate[(i+1),]=value+t(alpha[,1])
    }
    else{
      tRate[(i+1),]=value+t(alpha[,2])
    }
  }
  return (tRate)
}
BivariateHawkesLambdaValue<-function(time,total_index,t,tType,tRate,mu,alpha,beta)
{
#   browser() 
  #Calulate the lambda value of each coordinate at time seconds 
  #value is 1X2 matrix to store ambda value of each process
  
  #Use markov property of intendity function to calculate intensity
  #Univariate case: lambda(t_n)-mu=(lambda(t_{n-1})-mu+alpha)*exp(t_n-t_{n-1})
  #Bivariate case: lambda1(t_n)=(lambda1(t_{n-1})-mu+1{type1}*alpha11+1{type2}*alpha12)*exp(t_n-t_{n-1})
  #                lambda2(t_n)=(lambda2(t_{n-1})-mu+1{type1}*alpha21+1{type2}*alpha22)*exp(t_n-t_{n-1})
  
  value<- array(0,dim=c(1,2));
  
  if(total_index<1){
    #At the time of the first event, the rate of both process would be the background intensity
    value=t(mu)
  }
  else{
        value[1,1]<- mu[1,1]+(tRate[total_index,1]-mu[1,1])/exp(time-t[total_index])
        value[1,2]<- mu[2,1]+(tRate[total_index,2]-mu[2,1])/exp(time-t[total_index])
  }
  return (value)
}


#______________________________________________________________________________
BivariateHawkesSimulation<-function(dataNumber,mu,alpha,beta,history=list(),historyRateProvided=FALSE)
{
#   browser() 
  
  #simulate a bivariate hawkes process(dataNumber points) given the history events
  #mu:            background intensity M x 1 matrix
  #history:       If history is not provided(history = 0), the default simulation starts from 0
  #alpha,beta:    M x M matrix, with rows i being the parameters of process i
    
  #Initialization:
  if(length(history)==0){
    
    total_index<- 0
    subIndex1<- 0
    subIndex2<- 0;
    max_intensity<- sum(mu);
    
    #First Event
    s<- -log(runif(1))/max_intensity;
    #t:Store event time        
    t<- vector(mode="numeric",length=dataNumber)
    #tType: store corresponding event type
    tType<- vector(mode="numeric",length=dataNumber)
    
    #sub_process stores the sub history of each process
    sub_process1<- vector(mode="numeric",dataNumber)
    sub_process2<- vector(mode="numeric",dataNumber)
    
    #tRate: store rate at each time point(rate before an event happen,e.g. without adding alpha value)
    tRate<- array(0,dim=c(dataNumber,2))
    
    n0=0;
    
    #Attribution test
    randomD<- runif(1);
    if(randomD<= mu[1,1]/max_intensity){
      t[1]<- s;
      sub_process1[1]<- s;
      tType[1]<- 1
      tRate[1,]<- t(mu)+t(alpha[,1])
      n0<- 1;
      subIndex1<- subIndex1+1;
      total_index<- total_index+1; 
    }
    else{
      t[1]<- s;
      sub_process2[1]<- s;
      tType[1]<- -1
      tRate[1,]<- t(mu)+t(alpha[,2])
      n0<- 2;
      subIndex2<- subIndex2+1;
      total_index<- total_index+1; 
    }
    
  }
  else{
    #If history is provided, continue simulation from the history
    total_index<- length(history[[1]]);
    subIndex1<- length(history[[2]])
    subIndex2<- length(history[[3]])
    
    t<- vector(mode="numeric",length=(dataNumber+total_index))
    sub_process1<- vector(mode="numeric",length=(dataNumber+subIndex1))
    sub_process2<- vector(mode="numeric",length=(dataNumber+subIndex2))
    tType<- vector(mode="numeric",length=(dataNumber+subIndex2))
    tRate=array(0,dim=c((dataNumber+total_index),2))
    
    t[1:total_index]<- history[[1]]
    sub_process1[1:subIndex1]<- history[[2]]
    sub_process2[1:subIndex2]<- history[[3]]
    tType[1:total_index]=history[[4]]
    
    #Calculate historic rate
    
    if(historyRateProvided==FALSE){
      tRate[1:tptal_index,]=CalculateHistoryRate(t,tType,mu,alpha,beta,total_index)
    }
    else{
      tRate[1:total_index,]<- history[[5]]
    }
#     browser()

    
    n0<- 0;
    s<- t[total_index];
    
    #Set the termination time
    dataNumber<- dataNumber+total_index
  }
  
  #General Routine
  for(i in (total_index+1):dataNumber){
#     print(i)
#     
    rate<- BivariateHawkesLambdaValue(t[total_index],total_index,t,tType,tRate,mu,alpha,beta)
    max_intensity<- sum(rate)
    
    #Sample a exponential r.v 
    #If X has a standard uniform distribution, Y = − ln(X) / λ has an exponential distribution with rate λ
    
    while(T){
      s<- s-log(runif(1))/max_intensity;
      value<- BivariateHawkesLambdaValue(s,total_index,t,tType,tRate,mu,alpha,beta);
      intensity_s<- sum(value);
      randomD<- runif(1)
      
      #Attribution - Rejection test
      if(randomD <= intensity_s/max_intensity){
        total_index<- total_index+1;
        t[total_index]<- s
        tRate[total_index,]=value
        if(randomD<= (value[1,1]/max_intensity)){
          subIndex1<- subIndex1+1
          sub_process1[subIndex1]<- s;
          tType[total_index]=1
          tRate[total_index,]=value+t(alpha[,1])
          n0<- 1
        }
        else{
          subIndex2<- subIndex2+1
          sub_process2[subIndex2]<- s;
          tType[total_index]= -1
          tRate[total_index,]=value+t(alpha[,2])
          n0<- 2;
        }
        break; 
      }
      else{
        max_intensity<- intensity_s;
      }
    }
  }
  sub_process1<- sub_process1[1:subIndex1]
  sub_process2<- sub_process2[1:subIndex2]
  
  return (list(t,sub_process1,sub_process2,tType,tRate));
}

GenerateHawkesSample<-function(){
#Fast way to generate a sample path
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
}


#####Learning/Fitting#####



BivariateHawkesPriceSimulation_new<-function(t,tType,initialValue=0,scale=0.04)
{

  #Output:
  #   Price - The time and price in a nX2 matrix
  #   The initial price are set to be 100
  
  scale=0.04
  
  #: t - trainingSet[[1]]
  #: tType - trainingSet[[4]]
  
  n=length(t)+1
  price<-array(0,dim=c(n,2))
  price[2:n,1]=t
  price[2:n,2]=cumsum(tType)*scale

  price[,2]=price[,2]+initialValue;
  return (price);
}




#______________________________________________________________________________

Price_MCSimulation_BivariateHawkes<-function(dataNumber,mu,alpha,beta,sampleNum,initialValue=0,history=list()){
  
  #Monte Carlo Simulation of price path using bivariate hawkes model based on given paramerters and history
  #browser()
  maxTime=0;
  
  t=history[[1]]
  tType=history[[4]]
  #get the last integer second of history
  lastIntegerSecond=as.integer(tail(t,n=1))
  
  #last integer seconds must be included in the shared history
  sharedHistoryIndex=(t<=lastIntegerSecond)
  sharedHistory_t=t[sharedHistoryIndex]
  sharedHistory_tType=tType[sharedHistoryIndex]
  sharedHistory=BivariateHawkesPriceSimulation_new(sharedHistory_t,sharedHistory_tType)
  regSharedHistory=TimeSeriesRegularization_C(sharedHistory,lastIntegerSecond)
  
  irregularTailCollection=list()
  
  for(i in 1:sampleNum){
    sim=BivariateHawkesSimulation(dataNumber,mu,alpha,beta,history,historyRateProvided=TRUE);
    tailIndex=(sim[[1]]>lastIntegerSecond)
    sim_t=sim[[1]][tailIndex]
    sim_tType=sim[[4]][tailIndex]
    irregularTailCollection[[i]]=BivariateHawkesPriceSimulation_new(sim_t,sim_tType)
    irregularTailCollection[[i]][1,1]=lastIntegerSecond
    maxTime=max(maxTime,tail(sim_t,n=1))  
  }
  
  maxTime=ceiling(maxTime)
  regularTailCollection=array(0,c((maxTime-lastIntegerSecond),sampleNum))
  
  
  #Transform the irregular time series to regular time series for further analysis
#   browser()
  for(i in 1:sampleNum){
    regularTailCollection[,i]=tail(regSharedHistory[,2],n=1)+TimeSeriesRegularization_C(irregularTailCollection[[i]],maxTime)[2:(maxTime-lastIntegerSecond+1),2]
    #print(TimeSeriesRegularization(irregularSamplePaths[[i]],maxTime))
  }
  
  timeAxis=seq(from=0,to=maxTime,by=1);
  sampleMean=c(regSharedHistory[,2],rowMeans(regularTailCollection))
               
#   sampleSTD=apply(regularTailCollection,1,sd);
  
  
  return(list(timeAxis,sampleMean,regularTailCollection))
}


BivariateHawkesLikelihood<-function(theta,points)
{
  
  #To calculate the lkelihood value given certain parameters, with beta fixed
  
  #Set the beta value to be 1
  beta_value=1;
  
  #Initialze the parameter value
  mu_1<-theta[1];mu_2<-theta[2];
  alpha_11<-theta[3];alpha_12<-theta[5];alpha_21<-theta[4];alpha_22<-theta[6];
  beta_1<-beta_value;beta_2<-beta_value;   
  
  #points:    list 1: total time(Nx1 matrix), 
  #           list 2: time of subprocesses
  
  t<-points[[1]]; 
  t1<-points[[2]];
  t2<-points[[3]];
  
  #N: total points number of sub process 1
  N<-length(t1);
  
  #M: total points number of sub process 2
  M<-length(t2);
  
  #datanum_total: total points number of superpositioned process
  datanum_total<-length(t);
  #   print("Initialization finished, begin calculating R")
  
  #calculate R cubic
  
  R_11<- .C("R11MatrixCalculation",result=double(N),as.integer(N),as.double(beta_1),as.double(t1))[[1]]
  
  
  R_12<- .C("R12MatrixCalculation",result=double(N),as.integer(N),as.integer(M),as.double(beta_1),as.double(t1),as.double(t2))[[1]]
  
  
  R_21<- .C("R21MatrixCalculation",result=double(M),as.integer(N),as.integer(M),as.double(beta_2),as.double(t1),as.double(t2))[[1]]
  
  
  R_22<- .C("R22MatrixCalculation",result=double(M),as.integer(M),as.double(beta_2),as.double(t2))[[1]]
  
  
  T<-t[datanum_total];
  #   print(theta)
  L1=-mu_1*T-(alpha_11/beta_1)*sum(1-exp(-beta_1*(T-t1)))-(alpha_12/beta_1)*sum(1-exp(-beta_1*(T-t2)))+sum(log(mu_1+alpha_11*R_11[2:N]+alpha_12*R_12[2:N]))
  #   print("begin calculating likelihood L2")
  L2=-mu_2*T-(alpha_21/beta_2)*sum(1-exp(-beta_2*(T-t1)))-(alpha_22/beta_2)*sum(1-exp(-beta_2*(T-t2)))+sum(log(mu_2+alpha_21*R_21[2:M]+alpha_22*R_22[2:M]))
  
  L=L1+L2
  
  return (L);
}

#______________________________________________________________________________
BivariateHawkesGradient<-function(theta,points){
  
  
  beta_value=1
  mu_1<-theta[1];mu_2<-theta[2];
  alpha_11<-theta[3];alpha_12<-theta[5];alpha_21<-theta[4];alpha_22<-theta[6];
  beta_1<-beta_value;beta_2<-beta_value   
  #points:dataset,type list, with list 1 being the total time(Nx1 matrix), and list2 being a list of the time of subprocesses
  t<-points[[1]]; 
  t1<-points[[2]];
  t2<-points[[3]];
  N<-length(t1);
  M<-length(t2);
  
  #datanum_total: total points number of superpositioned process
  datanum_total<-length(t);
  
  #calculate R cubic
  
  R_11<- .C("R11MatrixCalculation",result=double(N),as.integer(N),as.double(beta_1),as.double(t1))[[1]]
  
  
  R_12<- .C("R12MatrixCalculation",result=double(N),as.integer(N),as.integer(M),as.double(beta_1),as.double(t1),as.double(t2))[[1]]
  
  
  R_21<- .C("R21MatrixCalculation",result=double(M),as.integer(N),as.integer(M),as.double(beta_2),as.double(t1),as.double(t2))[[1]]
  
  
  R_22<- .C("R22MatrixCalculation",result=double(M),as.integer(M),as.double(beta_2),as.double(t2))[[1]]
  
  
  T<-t[datanum_total];
  
  #Calculate gradient of mu_1,mu_2
  gmu_1=-T+sum(1/(mu_1+alpha_11*R_11[2:N]+alpha_12*R_12[2:N]))
  #     print('Calculating Gradient gmu2')
  
  gmu_2=-T+sum(1/(mu_2+alpha_21*R_21[2:M]+alpha_22*R_22[2:M]))
  
  #Calculate the gradient of alpha
  
  galpha_11=-sum(1-exp(-beta_1*(T-t1)))/beta_1+sum(R_11[2:N]/(mu_1+alpha_11*R_11[2:N]+alpha_12*R_12[2:N]))
  
  galpha_12=-sum(1-exp(-beta_1*(T-t2)))/beta_1+sum(R_12[2:N]/(mu_1+alpha_11*R_11[2:N]+alpha_12*R_12[2:N]))
  
  galpha_21=-sum(1-exp(-beta_1*(T-t1)))/beta_2+sum(R_21[2:M]/(mu_2+alpha_21*R_21[2:M]+alpha_22*R_22[2:M]))
  
  galpha_22=-sum(1-exp(-beta_1*(T-t2)))/beta_2+sum(R_22[2:M]/(mu_2+alpha_21*R_21[2:M]+alpha_22*R_22[2:M]))
  
  g=c(gmu_1,gmu_2,galpha_11,galpha_21,galpha_12,galpha_22)
  
  g;
  
}

#______________________________________________________________________________

BivariateHawkeshin<-function(theta,points)
{
  #Set the beta value to be fixed
  beta_value=1
  
  mu_1<-theta[1];mu_2<-theta[2];
  alpha_11<-theta[3];alpha_12<-theta[5];alpha_21<-theta[4];alpha_22<-theta[6];
  beta_1<-beta_value;beta_2<-beta_value; 
  h<-c(mu_1,mu_2,
       alpha_11,alpha_12,alpha_21,alpha_22,
       1-alpha_11/beta_1,1-alpha_12/beta_1,1-alpha_21/beta_2,1-alpha_22/beta_2);
  h;
}
