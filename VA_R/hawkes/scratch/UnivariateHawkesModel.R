library(neldermead);
library(optimx)
library(Rsolnp)
library(alabama)

##____________________________________________________________________________________

UnivariateHawkesLambdaValue<-function(time,history,mu,alpha,beta)
{
    value<-mu;
    history_before_time<-matrix();
    history_before_time<-history[history[,1]<=time];
    for(i in 1:length(history_before_time))
    {
        if(time<history[1,1])
        {
            value<-mu;
        }
        else
        {
            value<-value+alpha*exp(-beta*(time-history_before_time[i]));
        }
    }
    return (value);
}

##____________________________________________________________________________________

UnivariateHawkesSimulation<-function(mu,alpha,beta,T)
{
    lambda<-mu;
    n<-1;s<-(-1/lambda*log(runif(1)));
    #CC print(s)
    t<-matrix(0,1,1);
    if (s<=T)
    {
        t[1,1]<-s;
    }
    else
    {
        return (t); 
    }
    #print(t)
    #CC
    
    out_range<-FALSE;
    while(out_range==FALSE)
    {
        n<-(n+1);
        lambda<-UnivariateHawkesLambdaValue(t[n-1,1],t,mu,alpha,beta)+alpha;
        s<-s-1/lambda*log(runif(1));#
        #CC print(s)
        #print(s)
        if (s>T){break;}
        
        while(out_range==FALSE)
        { 
            #Rejection test
            lambda_s<-UnivariateHawkesLambdaValue(s,t,mu,alpha,beta);
            #print(lambda_s)
            if(lambda_s/lambda>=runif(1))#r
            {
                t<-rbind(t,c(s));
                break; 
            }
            else{
                lambda<-lambda_s;
                s<-s-1/lambda*log(runif(1));
                if(s>=T){
                    out_range<-TRUE;
                    break;
                }
            }
        }
    }
    return (t);
}

##____________________________________________________________________________________

UnivariateHawkesPlot<-function(history,mu,alpha,beta)
{
    time<-seq(0,max(history[,1]),by=0.1);
    y<-c();
    lambda_max<-c();
    for(i in 1:length(time))
    {
        y[i]<-UnivariateHawkesLambdaValue(time[i],history,mu,alpha,beta);
    }
    plot(time,y,xlab="Time",ylab="Intensity",type='l',lwd=2,cex.axis=1.5,cex.lab=1.5);
}


##____________________________________________________________________________________

UnivariateHawkesLikelihood<-function(theta,points)
{
  alpha<-theta[2];
  beta<-theta[3];
  lambda0<-theta[1];
  data_num=dim(points)[1]
  tn<-points[data_num,1]
  R<-matrix(0,data_num,1);
  for(i in 1:dim(R)[1])
  {
    if(i==1){R[i,1]<-0;}
    else
    {
      R[i,1]<-exp(-beta*(points[i,1]-points[i-1,1]))*(1+R[i-1,1])
    }
  }
  part1<-tn-lambda0*tn;
  part2_exp<-0;
  for(i in 1:data_num)
  {
    part2_exp<-part2_exp+exp(-beta*(tn-points[i,1]));
  }
  part2<-(alpha/beta)*(data_num-part2_exp);
  part3<-0;
  for(i in 1:data_num)
  {
    part3<-part3+log(lambda0+alpha*R[i,1]);
  }
  logle<-part1-part2+part3;
  return (logle);
}

##____________________________________________________________________________________

UnivariateHawkesMLEhin<-function(theta,points)
{
  alpha<-theta[2];
  beta<-theta[3]
  h<-rep(NA,1);
  h[1]<-1-alpha/beta;
  h[2]<-alpha;
  h[3]<-beta;
  h;
}

if(FALSE){
#Load data
data<-read.table('goog_2010_dec.csv',header=TRUE,sep=',')
test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
idx<-tapply(1:NROW(data),data$TIME,"[",1)
data_red<-data[idx,c(2:3)]  
day_01_idx<-(data_red$TIME>=as.POSIXct("2010-12-01 09:30:00",format="%Y-%m-%d %H:%M:%S"))&(data_red$TIME<=as.POSIXct("2010-12-01 10:00:00",format="%Y-%m-%d %H:%M:%S"))
day_01<-data_red[t(day_01_idx),]

#Separate positive and negative movement
pos_mov<-array(0,dim=c(1,1));
neg_mov<-array(0,dim=c(1,1));
for(i in 2:length(day_01[,1]))
{
  if(day_01[i,2]>day_01[i-1,2])
  {
    #print(c(as.double(day_01[i,1])))
    pos_mov<-rbind(pos_mov,as.double(day_01[i,1]));
    #print(pos_mov)
  }
  else if(day_01[i,2]<day_01[i-1,2])
  {
    neg_mov<-rbind(neg_mov,as.double(day_01[i,1]));
  }
  else
  {
    pos_mov<-rbind(pos_mov,as.double(day_01[i,1]));
    neg_mov<-rbind(neg_mov,as.double(day_01[i,1]));
  }
}
pos_mov<-as.matrix(pos_mov[-1,]);
pos_mov<-pos_mov-pos_mov[1,1];
pos_mov<-as.matrix(pos_mov[-1,]);
neg_mov<-as.matrix(neg_mov[-1,]);
neg_mov<-neg_mov-neg_mov[1,1];
neg_mov<-as.matrix(neg_mov[-1,]);
x<-UniHawkesSim(1,0.5,0.8,5000);
print('complete simulation')
print(x)
#data_points<-as.matrix(x);
#MLE 
print('start simulation')
#theta<-c(10,4,5);
theta<-c(1.2,0.6,0.8);
result<-UniHawkesLikelihood(theta,data_points);
#print(result)
theta<-c(1.2,0.6,0.8);

#Sample MLE
par<-auglag(par=theta,fn=UniHawkesLikelihood,hin=MLEhin,control.optim=list(trace=2,fnscale=-1),points=data_points)
}
