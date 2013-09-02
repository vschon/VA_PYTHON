library(alabama)

#Read in data and extract the time range
data<-read.table('goog_2010_dec.csv',header=TRUE,sep=',')
test<-as.POSIXct(as.character(data$DATE),format="%Y%m%d")
data$TIME<-as.POSIXct(paste(test,data$TIME))
data$DATE<-NULL
idx<-tapply(1:NROW(data),data$TIME,"[",1)
data_red<-data[idx,c(2:3)]  
day_01_idx<-(data_red$TIME>=as.POSIXct("2010-12-01 10:30:00",format="%Y-%m-%d %H:%M:%S"))&(data_red$TIME<=as.POSIXct("2010-12-01 11:30:00",format="%Y-%m-%d %H:%M:%S"))
day_01<-data_red[t(day_01_idx),]
plot(day_01[,2]~day_01[,1],type='s',xlab='time',ylab='Price')

#transform time type to double
n=dim(day_01)[1]
goog_data=array(0,dim=c(n,2))
goog_data[,1]=as.double(day_01[,1])
goog_data[,2]=as.double(day_01[,2])
goog_data[,1]=goog_data[,1]-goog_data[1,1]

# #Divide the price into training set and testing set
# #Traing set: 300 seonds
# #Testing set: 300 seconds
T=3600
goog_trainingset=goog_data[goog_data[,1]<=T/2,]
goog_testingset=goog_data[goog_data[,1]>T/2]

#divide the price into positive movement and negativement
goog_trainingset_decomposed=PriceDecomposition(goog_trainingset)

#Learn the parameters of the Hawkes process
#Set initial estimation of parameters
goog_mu_0<-array(c(0.2,0.2),dim=c(2,1));
goog_alpha_0<-array(c(0.1,0.1,0.1,0.1),dim=c(2,2));
goog_beta_0<-array(c(0.5,0.5),dim=c(2,1));
goog_theta<-c(goog_mu_0,goog_alpha_0);
goog_par<-constrOptim.nl(par=goog_theta,fn=BiHawkesLikelihood_Beta_Fixed,hin=BiHawkesLikelihood_Beta_Fixed_MLEhin,control.outer=list(trace=FALSE),
                    control.optim=list(trace=FALSE,fnscale=-0.01),points=goog_trainingset_decomposed);
#print(par)
goog_mu_estimate=array(goog_par$par[1:2],dim=c(2,1))
goog_alpha_estimate=array(goog_par$par[3:6],dim=c(2,2))
goog_beta_estimate=array(c(1,1,1,1),dim=c(2,2))


#Use the estimated parameters to do monte carlo simulation
print('Begin Simulation')
loop=10;
goog_samplepaths=matrix(nrow=1000,ncol=loop)

sampleNum=10
goog_simret=Price_MCSimulation_BivariateHawkes(goog_mu_estimate,goog_alpha_estimate,goog_beta_estimate,
                                          T/2,sampleNum,history=goog_trainingset_decomposed);

goog_simret[[1]]=goog_simret[[1]][-10:-1]
goog_simret[[2]]=goog_simret[[2]][-10:-1]
goog_simret[[3]]=goog_simret[[3]][-10:-1]

plot(goog_simret[[1]],goog_simret[[2]],'l',xlim=c(0,T-10),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(goog_simret[[1]],goog_simret[[2]]+goog_simret[[3]],'l',col='green',xlim=c(0,T-10),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(goog_simret[[1]],goog_simret[[2]]-goog_simret[[3]],'l',col='green',xlim=c(0,T-10),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(goog_simret[[1]],goog_simret[[2]]+2*goog_simret[[3]],'l',col='blue',xlim=c(0,T-10),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(goog_simret[[1]],goog_simret[[2]]-2*goog_simret[[3]],'l',col='blue',xlim=c(0,T-10),ylim=c(99.5,101),xlab='',ylab='')
#par(new=TRUE)
#plot(day_01[,2]/5.67245~day_01[,1],type='s',xlab='time',ylab='Price')

#plot(price[,2]~price[,1],type='s',col='red',xlim=c(0,T),ylim=c(99.5,101),xlab='seconds',ylab='Price');
