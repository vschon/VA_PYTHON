library(forecast)
library(tseries)

rmse<-function(data){
	number=length(data[,1])
	rmse=sqrt(sum((data[,1]-data[,2])**2)/number)
	return (rmse)
}

CorrectPercentage<-function(forecastTable){
  total=length(forecastTable[,1])
  forecastDirection=array(0,dim=c(total,1))
  realDirection=array(0,dim=c(total,1))
  
  #redifine forecast direction
  
  riseOnRise=0
  fallOnRise=0
  
  riseOnFall=0
  fallOnFall=0
  
  forecastDirection[forecastTable[,1]>0]=1
  forecastDirection[forecastTable[,1]<0]=-1
  realDirection[forecastTable[,2]>0]=1
  realDirection[forecastTable[,2]<0]=-1

  riseOnRise=sum(realDirection>0&forecastDirection>0)
  fallOnRise=sum(realDirection<0&forecastDirection>0)
  fallOnFall=sum(realDirection<0&forecastDirection<0)
  riseOnFall=sum(realDirection>0&forecastDirection<0)

  riseCount=sum(forecastDirection==1)
  fallCount=sum(forecastDirection==-1)
  flatCount=sum(forecastDirection==0)
 
  return (list((riseOnRise+fallOnFall)/(riseCount+fallCount),riseOnRise/riseCount,fallOnRise/riseCount,fallOnFall/fallCount,riseOnFall/fallCount))
}


featureeval<-function(data,name){
	rmse=rmse(data)
	corr=cor(data[,1],data[,2])
	jpeg(paste(name,'_scatterplot.jpeg',sep=''),width=800,height=800)
	plot(data,pch=20,xlab='predicted price change',ylab='real price change',main='prediction vs true scatter plot')
	dev.off()
	correctRate=CorrectPercentage(data)[[1]]	
	return(list("RMSE"=rmse,"CORRELATIOM"=corr,"CORRECT"=correctRate))
}

EvalStats<-function(nameList,prefix){
    resultList= read.table(nameList,sep=',')
    n=dim(resultList)[1]
    rmseTable=array(0,dim=c(n,1))
    correctTable=array(0,dim=c(n,1))
    correlationTable=array(0,dim=c(n,1))

    for(i in 1:n){
        file=paste(resultList[i,1],sep='')
        x=read.table(file,sep=',',header=TRUE)
        eval=featureeval(x,resultList[i,1])
        rmseTable[i,1]=eval[[1]]
        correlationTable[i,1]=eval[[2]]
        correctTable[i,1]=eval[[3]]
    }
rownames(rmseTable)=as.character(resultList[,1])
rownames(correctTable)=as.character(resultList[,1])
rownames(correlationTable)=as.character(resultList[,1])

write.table(rmseTable,paste(prefix,'RMSE.csv',sep=''),sep=',',row.names=TRUE,col.names=FALSE)
write.table(correctTable,paste(prefix,'CorrectRate.csv',sep=''),sep=',',row.names=TRUE,col.names=FALSE)
write.table(correlationTable,paste(prefix,'Correlation.csv',sep=''),sep=',',row.names=TRUE,col.names=FALSE)
 
}
