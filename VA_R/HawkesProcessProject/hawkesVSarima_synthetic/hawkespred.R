source('~/data/va_R/hawkes/hawkes.R')
source('~/data/va_R/tsutil/tsutil.R')

args=commandArgs(TRUE)
ahead=as.integer(args[1])
step=as.integer(args[2])
ofile=args[3]
#ahead=1
#step=1000
#ofile="hawkes1.csv"

#read data
x=list()
x[[1]]=read.table('rawData1.csv',sep=',')$V1
x[[2]]=read.table('rawData2.csv',sep=',')$V1
x[[3]]=read.table('rawData3.csv',sep=',')$V1
x[[4]]=read.table('rawData4.csv',sep=',')$V1
x[[5]]=read.table('rawData5.csv',sep=',')$V1
#debug(BivariateHawkesPriceSimulation_new)
ireg_price=BivariateHawkesPriceSimulation_new(x[[1]],x[[4]])
reg_price=read.table('regData.csv',sep=',')

alpha=array(c(0.2,0.5,0.5,0.22),dim=c(2,2))
beta=array(c(1,1,1,1),dim=c(2,2))
mu=array(c(0.3,0.3),dim=c(2,1))
#Simulate an entire path
totalSeconds=max(reg_price[,1])
#The time of the first prediction
testingTime0=as.integer(totalSeconds/2)

#Make 1000 predictions
resultTable=array(0,dim=c(step,2))

trainingSet=list()

count=0
for (i in testingTime0:(testingTime0+step-1)){
    trainingSet[[1]]=x[[1]][x[[1]]<=(i-ahead)]
    trainingSet[[2]]=x[[2]][x[[2]]<=(i-ahead)]
    trainingSet[[3]]=x[[3]][x[[3]]<=(i-ahead)]
    trainingSet[[4]]=x[[4]][x[[1]]<=(i-ahead)]
    trainingSet[[5]]=CalculateHistoryRate(trainingSet[[1]],trainingSet[[4]],mu,alpha,beta,length(trainingSet[[1]]))
    MCResult=Price_MCSimulation_BivariateHawkes(ahead*20,mu,alpha,beta,500,initialValue=0,history=trainingSet)
   count=count+1
   resultTable[count,1]=MCResult[[2]][i]-MCResult[[2]][i-ahead]
   resultTable[count,2]=reg_price[i,2]-reg_price[(i-ahead),2]

   print(count)
   print(resultTable[count,])
}

write.table(resultTable,ofile,sep=',')
