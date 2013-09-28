source('tsutil.R')
source('hawkes.R')

mu=array(c(0.5,0.5),dim=c(2,1))
alpha = array(c(0.1,0.2,0.3,0.4),dim=c(2,2))
beta = array(c(1,1,1,1),dim=c(2,2))

#data = BivariateHawkesSimulation(dataNum=1000,alpha=alpha,mu=mu,beta=beta)
theta=c(0.5,0.5,0.5,0.5,0.5,0.5)
t =read.table('t.csv')$V1
t1=read.table('t1.csv')$V1
t2=read.table('t2.csv')$V1
data=list()
data[[1]]=t
data[[2]]=t1
data[[3]]=t2
par<-constrOptim.nl(par=theta,fn=BivariateHawkesLikelihood,gr=BivariateHawkesGradient,
                    hin=BivariateHawkeshin,
                    control.outer=list(trace=FALSE),control.optim=list(trace=FALSE,fnscale=-0.01),
                    points=data);

print(par)
