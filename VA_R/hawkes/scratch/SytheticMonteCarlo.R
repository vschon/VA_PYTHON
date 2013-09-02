library(alabama)
#Code for monte carlo simulation using sythetic data

#Simulate an upward trend
#Set parameters
mu<-array(c(0.12,0.12),dim=c(2,1));
alpha<-array(c(0.2,0.2,0.2,0),dim=c(2,2));
beta<-array(c(1,1,1,1),dim=c(2,2));
T=1000;
scale<-0.01;

#Simulate the 600 seonds sythetic price movement y

x<-MultivariateHawkesSimulation(mu,alpha,beta,T);
price=BivariateHawkesPriceSimulation(x,100);

n=dim(price)[1]


#Divide the sythetic price into training set and testing set
#Traing set: T/2 seonds
#Testing set: T/2 seconds
trainingset=price[price[,1]<=T/2,]
testingset=price[price[,1]>T/2]

#divide the price into positive movement and negativement
trainingset_decomposed=PriceDecomposition(trainingset)

#Learn the parameters of the Hawkes process
#Set initial estimation of parameters
mu_0<-array(c(0.5,0.5),dim=c(2,1));
alpha_0<-array(c(0.2,0.5,0.2,0.5),dim=c(2,2));
beta_0<-array(c(1,1),dim=c(2,1));
theta<-c(mu_0,alpha_0);
par<-constrOptim.nl(par=theta,fn=BiHawkesLikelihood_Beta_Fixed,hin=BiHawkesLikelihood_Beta_Fixed_MLEhin,control.outer=list(trace=FALSE),
                    control.optim=list(trace=FALSE,fnscale=-0.01),points=trainingset_decomposed);
print(par)
mu_estimate=array(par$par[1:2],dim=c(2,1))
alpha_estimate=array(par$par[3:6],dim=c(2,2))
beta_estimate=array(c(1,1,1,1),dim=c(2,2))

sampleNum=100
simret=Price_MCSimulation_BivariateHawkes(mu_estimate,alpha_estimate,beta_estimate,
                                          T/2,sampleNum,history=trainingset_decomposed);


plot(simret[[1]],simret[[2]],'l',xlim=c(0,T),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(simret[[1]],simret[[2]]+simret[[3]],'l',col='green',xlim=c(0,T),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(simret[[1]],simret[[2]]-simret[[3]],'l',col='green',xlim=c(0,T),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(simret[[1]],simret[[2]]+2*simret[[3]],'l',col='blue',xlim=c(0,T),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(simret[[1]],simret[[2]]-2*simret[[3]],'l',col='blue',xlim=c(0,T),ylim=c(99.5,101),xlab='',ylab='')
par(new=TRUE)
plot(price[,2]~price[,1],type='s',col='red',xlim=c(0,T),ylim=c(99.5,101),xlab='seconds',ylab='Price');
