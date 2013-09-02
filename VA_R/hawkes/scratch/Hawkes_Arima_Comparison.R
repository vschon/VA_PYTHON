library(Rcpp) 
library(forecast)
source('~/Desktop/R_Analysis_Framework/HawkesProcessModel/MultivariateHawkesModel.R')
source('~/Desktop/R_Analysis_Framework/TimeSeries/TimeSeriesUtility.R')

####1. Simulate a sample path####
mu<-array(c(0.25,0.25),dim=c(2,1));
alpha<-array(c(0.08,0.3,0.3,0.03),dim=c(2,2));
beta<-array(c(1,1,1,1),dim=c(2,2));
mu_0<-array(c(0.5,0.5),dim=c(2,1));
alpha_0<-array(c(0.5,0.5,0.5,0.5),dim=c(2,2));
theta<-c(mu_0,alpha_0);

xTraining<-BivariateHawkesSimulation_bynumber(3000,mu,alpha,beta);
xTrainingResult<-list(xTraining[[1]],list(xTraining[[2]],xTraining[[3]]))
xTesting<- BivariateHawkesSimulation_bynumber(2000,mu,alpha,beta,
                                              history=xTraining)
xTestingResult<-list(xTesting[[1]],list(xTesting[[2]],xTesting[[3]]))
trainingSet=BivariateHawkesPriceSimulation(xTrainingResult,100)
regTrainingSet=TimeSeriesRegularization_C(trainingSet)

#trainingSetEnd: last time value in seconds of training set, = last index-1
trainingSetEnd=regTrainingSet[dim(regTrainingSet)[1]]


steps=200
HawkesPrediction=array(0,dim=c(trainingSetEnd+(steps+1)*3+1,2))
HawkesPrediction[,1]=0:(trainingSetEnd+(steps+1)*3)
HawkesPrediction[1:(trainingSetEnd+1),2]=regTrainingSet[,2]

#predictionIndex: the index of the first prediction value
predictionIndex0=trainingSetEnd+2
predictionIndex=trainingSetEnd+2

testingSet=BivariateHawkesPriceSimulation(xTestingResult,100)
regTestingSet=TimeSeriesRegularization_C(testingSet)
testingSetEnd=regTestingSet[dim(regTestingSet)[1]]

####2. Use training set to learn parameters####
par<-constrOptim.nl(par=theta,fn=BivariateHawkesLikelihood_Beta_Fixed_bynumber_C,gr=BivariateHawkesGradient_Beta_Fixed_bynumber_C,
                    hin=BivariateHawkesLikelihood_Beta_Fixed_MLEhin_bynumber_C,
                    control.outer=list(trace=FALSE),control.optim=list(trace=FALSE,fnscale=-0.01),
                    points=xTrainingResult);

####3. Monte Carlo simulation (3 seconds/10 points ahead) ####

MCResult=Price_MCSimulation_BivariateHawkes(20,mu,alpha,beta,10,100,history=xTraining)
HawkesPrediction[predictionIndex:(predictionIndex+2),2]=MCResult[[2]][predictionIndex:(predictionIndex+2)]


# plot(HawkesPrediction[predictionIndex:(predictionIndex+2),],type='p',col='blue',xlim=c((predictionIndex-1),(predictionIndex+2)),ylim=c(101.2,101.4),xlab='',ylab='')
# par(new=TRUE)
# plot(regTestingSet[predictionIndex:(predictionIndex+2),],type='s',col='red',xlim=c((predictionIndex-1),(predictionIndex+2)),ylim=c(101.2,101.4),xlab='',ylab='')



####4. Extend the training set to include the new data and repeat previous simulation ####

for(i in 1:(steps)){
    trainingSetEnd=trainingSetEnd+3 # This is time
    predictionIndex=trainingSetEnd+2 # This is index
    xTraining1=list()   
    xTraining1[[1]]<-xTesting[[1]][xTesting[[1]]<=trainingSetEnd];
    xTraining1[[2]]<-xTesting[[2]][xTesting[[2]]<=trainingSetEnd];
    xTraining1[[3]]<-xTesting[[3]][xTesting[[3]]<=trainingSetEnd];
    xTrainingResult1<-list(xTraining1[[1]],list(xTraining1[[2]],xTraining1[[3]]))
    trainingSet1=BivariateHawkesPriceSimulation(xTrainingResult1,100)
    regTrainingSet1=TimeSeriesRegularization_C(trainingSet1,trainingSetEnd)
    MCResult1=Price_MCSimulation_BivariateHawkes(20,mu,alpha,beta,10,100,history=xTraining1)

    HawkesPrediction[predictionIndex:(predictionIndex+2),2]=MCResult1[[2]][predictionIndex:(predictionIndex+2)]
}

####Derive the Hawkes results####

forecastTable=array(0,dim=c((steps+2),3))
forecastTable[1,1:2]=regTestingSet[predictionIndex0-1,1:2]
forecastTable[1,3]=regTestingSet[predictionIndex0-1,2]
for (i in 2:(steps+1)){
  forecastTable[i,1:2]=regTestingSet[(predictionIndex0-1+3*(i-1)),1:2]
  forecastTable[i,3]=HawkesPrediction[(predictionIndex0-1+3*(i-1)),2]
}

# plot(forecastTable[,1],forecastTable[,2],col='blue',type='p')
# par(new=TRUE)
# plot(forecastTable[,1],forecastTable[,3],col='red',type='p')

forecastDirection=forecastTable[2:(steps+2),3]-forecastTable[1:(steps+1),2]
realDirection=forecastTable[2:(steps+2),2]-forecastTable[1:(steps+1),2]

correctCount_rise=0
correctCount_fall=0
correctCount=0

totalCount_rise=0
totalCount_fall=0
totalCount=0

fallGivenRise=0
flatGivenRise=0

riseGivenFall=0
flatGivenFall=0

for (i in 1:(steps+1)){
  if(forecastDirection[i]<=-0.005){
    forecastDirection[i]=-1
    totalCount_fall=totalCount_fall+1
  }
  else if (forecastDirection[i]>=0.005){
    forecastDirection[i]=1
    totalCount_rise=totalCount_rise+1
  }
  else{
    forecastDirection[i]=0
  }
  
  if(realDirection[i]<=-0.01){
    realDirection[i]=-1
  }
  else if (realDirection[i]>=0.01){
    realDirection[i]=1
  }
  
  if(realDirection[i]>0&&forecastDirection[i]>0) correctCount_rise=correctCount_rise+1
  if(realDirection[i]<0&&forecastDirection[i]>0) fallGivenRise=fallGivenRise+1
  if(realDirection[i]<0&&forecastDirection[i]<0) correctCount_fall=correctCount_fall+1
}
correctCount=correctCount_fall+correctCount_rise
totalCount=totalCount_fall+totalCount_rise
print('predicting rise')
print(correctCount_rise/totalCount_rise)
print(fallGivenRise/totalCount_rise)
print('predicting fall')
print(correctCount_fall/totalCount_fall)
print(correctCount/totalCount)





####ARIMA prediction####
trainingSetEnd=regTrainingSet[dim(regTrainingSet)[1]]
ARIMAPrediction=array(0,dim=c(trainingSetEnd+steps*3+1,2))
ARIMAPrediction[,1]=0:(trainingSetEnd+steps*3)
ARIMAPrediction[1:(trainingSetEnd+1),2]=regTrainingSet[,2]

predictionIndex0=trainingSetEnd+2
predictionIndex=trainingSetEnd+2

testingSet=BivariateHawkesPriceSimulation(xTestingResult,100)
regTestingSet=TimeSeriesRegularization_C(testingSet)
testingSetEnd=regTestingSet[dim(regTestingSet)[1]]

fit=auto.arima(regTrainingSet[,2])
ArimaResult=forecast(fit,h=3)
ARIMAPrediction[predictionIndex:(predictionIndex+2),2]=array(ArimaResult[[4]])

for(i in 1:(steps-1)){
  trainingSetEnd=trainingSetEnd+3 # This is time
  predictionIndex=trainingSetEnd+2 # This is index
  xTraining1=list()   
  xTraining1[[1]]<-xTesting[[1]][xTesting[[1]]<=trainingSetEnd];
  xTraining1[[2]]<-xTesting[[2]][xTesting[[2]]<=trainingSetEnd];
  xTraining1[[3]]<-xTesting[[3]][xTesting[[3]]<=trainingSetEnd];
  xTrainingResult1<-list(xTraining1[[1]],list(xTraining1[[2]],xTraining1[[3]]))
  trainingSet1=BivariateHawkesPriceSimulation(xTrainingResult1,100)
  regTrainingSet1=TimeSeriesRegularization_C(trainingSet1,trainingSetEnd)
  fit=auto.arima(regTrainingSet1[,2])
  ArimaResult=forecast(fit,h=3)
  ARIMAPrediction[predictionIndex:(predictionIndex+2),2]=array(ArimaResult[[4]])
}

####Derive the ARIMA results####

forecastTable=array(0,dim=c((steps+2),3))
forecastTable[1,1:2]=regTestingSet[predictionIndex0-1,1:2]
forecastTable[1,3]=regTestingSet[predictionIndex0-1,2]
for (i in 2:(steps+2)){
    forecastTable[i,1:2]=regTestingSet[(predictionIndex0-1+3*(i-1)),1:2]
    forecastTable[i,3]=ARIMAPrediction[(predictionIndex0-1+3*(i-1)),2]
}

# plot(forecastTable[,1],forecastTable[,2],col='blue',type='p')
# par(new=TRUE)
# plot(forecastTable[,1],forecastTable[,3],col='red',type='p')

forecastDirection=forecastTable[2:(steps+2),3]-forecastTable[1:(steps+1),2]
realDirection=forecastTable[2:(steps+2),2]-forecastTable[1:(steps+1),2]

correctCount_rise=0
correctCount_fall=0
correctCount=0

totalCount_rise=0
totalCount_fall=0
totalCount=0

fallGivenRise=0
flatGivenRise=0

riseGivenFall=0
flatGivenFall=0

for (i in 1:(steps+1)){
    if(forecastDirection[i]<=-0.005){
        forecastDirection[i]=-1
        totalCount_fall=totalCount_fall+1
    }
    else if (forecastDirection[i]>=0.005){
        forecastDirection[i]=1
        totalCount_rise=totalCount_rise+1
    }
    else{
        forecastDirection[i]=0
    }
    
    if(realDirection[i]<=-0.01){
        realDirection[i]=-1
    }
    else if (realDirection[i]>=0.01){
        realDirection[i]=1
    }
    
    if(realDirection[i]>0&&forecastDirection[i]>0) correctCount_rise=correctCount_rise+1
    if(realDirection[i]<0&&forecastDirection[i]>0) fallGivenRise=fallGivenRise+1
    if(realDirection[i]<0&&forecastDirection[i]<0) correctCount_fall=correctCount_fall+1
}
correctCount=correctCount_fall+correctCount_rise
totalCount=totalCount_fall+totalCount_rise
print('predicting rise')
print(correctCount_rise/totalCount_rise)
print(fallGivenRise/totalCount_rise)
print('predicting fall')
print(correctCount_fall/totalCount_fall)
print(correctCount/totalCount)


plot(1:(steps+1),realDirection,type='l')
par(new=TRUE)
plot(1:(steps+1),forecastDirection,col='red')
