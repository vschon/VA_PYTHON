
beta=array(c(1,1,1,1),dim=c(2,2))
mu=array(c(0.3,0.3),dim=c(2,1))
alpha=array(c(0.2,0.5,0.5,0.05),dim=c(2,2))
theta=c(mu,alpha)
print('record rate')

parResult=array(0,dim=c(10000,6))
for(i in 1:100){
  x=BivariateHawkesSimulation_bynumber_RecordRate(10,mu,alpha,beta)
  par<-constrOptim.nl(par=theta,fn=BivariateHawkesLikelihood_Beta_Fixed_bynumber_C,gr=BivariateHawkesGradient_Beta_Fixed_bynumber_C,
                      hin=BivariateHawkesLikelihood_Beta_Fixed_MLEhin_bynumber_C,
                      control.outer=list(trace=FALSE),control.optim=list(trace=FALSE,fnscale=-0.01),
                      points=x);
  parResult[i,]=par$par
}

estimate=colMeans(parResult[1:100,])

# print('bynumber')
# set.seed(1)
x=BivariateHawkesSimulation_bynumber_RecordRate(10000,mu,alpha,beta)
y=BivariateHawkesSimulation_bynumber_RecordRate(5,mu,alpha,beta,x,TRUE)

