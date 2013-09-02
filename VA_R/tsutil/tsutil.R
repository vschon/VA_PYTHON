#set working directory

dyn.load('~/data/va_R/tsutil/TimeRegularizationC.so')

TimeSeriesRegularization_C<-function(irregularTimeSeries,terminationLength=0){
  
  #Transform irregular time series into regular time series
  #Time scale: second
  #terminationLength: The termination length of the regular time series
  
  #Get the minimum beginning time
  minTime=ceiling(min(irregularTimeSeries[,1]))
  #Get the maximum endding time
  maxTime=ceiling(max(irregularTimeSeries[,1]))
  
  if(terminationLength!=0){maxTime=max(maxTime,terminationLength);}
  
  regularTimeSeriesLength=maxTime-minTime+1;
  n=dim(irregularTimeSeries)[1];
  regularTimeSeries=array(0,c(regularTimeSeriesLength,2));
  regularTimeSeries[,1]=seq(from=minTime,to=maxTime,by=1)
  
  
  regularTimeSeries=.C("TimeRegularizationC",as.integer(regularTimeSeriesLength),as.integer(n),as.double(irregularTimeSeries),as.double(regularTimeSeries))[[4]]
  regularTimeSeries=array(regularTimeSeries,dim=c(length(regularTimeSeries)/2,2))
  return(regularTimeSeries);
}

PriceDecomposition<-function(price)
{
    #Decompose the price path into N+ and N-
    
    n=dim(price)[1]
    #x will be transmitted to mle function to estimate parameters
    x=list();
    #Store the total event time into x[[1]]
    x[[1]]=as.matrix(price[-1,1])
    #print(x[[1]])
    
    #sub_process:used to store the time of N+ and N-
    sub_process=list();
    sub_process[[1]]=array(0,dim=c(n,1));#positive coordinate
    sub_process[[2]]=array(0,dim=c(n,1));#negative coordinate
    n_positive=0;
    n_negative=0;
    
    #Decompose the price into N+ and N-
    for(i in 2:n)
    {
        if (price[i,2]>price[i-1,2])
        {
            n_positive=n_positive+1;
            sub_process[[1]][n_positive,1]=price[i,1]
        }
        else if(price[i,2]==price[i-1,2])
        {
            n_positive=n_positive+1
            n_negative=n_negative+1
            sub_process[[1]][n_positive,1]=price[i,1]
            sub_process[[2]][n_negative,1]=price[i,1]
        }
        else
        {
            n_negative=n_negative+1
            sub_process[[2]][n_negative,1]=price[i,1]
        }
    }
    
    #Delete the unfilled entries in sub_process
    sub_process[[1]]=as.matrix(sub_process[[1]][-(n_positive+1):-n,1]);
    sub_process[[2]]=as.matrix(sub_process[[2]][-(n_negative+1):-n,1]);
    
    x[[1]]=as.matrix(x[[1]][-1,]);
    x[[2]]=sub_process;
    
    return (x)
}

TAQDataExtraction<-function(rawData,beginTime="20101201 09:30:00.000",endTime="20101201 16:00:00.000"){
  #Retrieve Data in certain time range
  #return list(time,price) for further processing
  
  price=rawData$PRICE
  time=strptime(paste(paste(rawData$DATE,rawData$TIME),'.000',sep=''),"%Y%m%d %H:%M:%OS")
  
  extractIndex=(time>=strptime(beginTime,format="%Y%m%d %H:%M:%OS"))&(time<=strptime(endTime,format="%Y%m%d %H:%M:%OS"))
  
  time=time[extractIndex]
  price=price[extractIndex]
  
  return (list(time,price))
}

TAQHawkesDecomposition<-function(processedData){
  time=processedData[[1]]
  price=processedData[[2]]
  n=length(price)
  
  #distribute trades with duplicated time uniformly
  d0=1
  dEnd=1
  while(TRUE){
    currentTimeStamp=time[d0]
    
    duplicateNumber=0
    while(currentTimeStamp==time[(d0+duplicateNumber)]){
      duplicateNumber=duplicateNumber+1
      if((d0+duplicateNumber)>n){
        break
      }
    }
    
    #     duplicateNumber=sum(time==currentTimeStamp)
    dEnd=d0+duplicateNumber-1
    
    if(duplicateNumber>1)
    {
      time[d0:dEnd]=time[d0:dEnd]+seq(from=0.000,to=0.999,by=(0.999/(duplicateNumber-1)))
    }
    
    if(dEnd>=length(price)){
      break
    }
    d0=dEnd+1
  }
  
  
  beginningTime=as.double(time[1])
  
  #Exclude trades that do not involve price change
  dprice=diff(price)
  riseIndex=which(dprice>0)+1
  rise=as.double(time[riseIndex])-beginningTime
  fallIndex=which(dprice<0)+1
  fall=as.double(time[fallIndex])-beginningTime
  tIndex=which(dprice!=0)+1
  t=as.double(time[tIndex])-beginningTime
      
  #get tType
  tType=dprice[dprice!=0]
  tType[tType>0]=1
  tType[tType<0]=-1    
  
  return (list(t,rise,fall,tType))
}

TAQRegularization<-function(data,beginTime="20101201 09:30:00",endTime="20101201 16:00:00",isOutput=FALSE){
    taqdates=as.POSIXct(as.character(data$DATE),format="%Y%m%d")
    data$TIME=as.POSIXct(paste(taqdates,data$TIME))
    data$DATE=NULL
    date_idx=(data$TIME>=as.POSIXct(beginTime,format="%Y%m%d %H:%M:%S"))&(data$TIME<=as.POSIXct(endTime,format="%Y%m%d %H:%M:%S"))
    data=data[t(date_idx),]
    idx=tapply(1:NROW(data),data$TIME,"[",1)
    data=data[idx,c(2:3)]
    n=dim(data)[1]
    googData=array(0,dim=c(n,2))
    googData[,1]=as.double(data[,1])
    googData[,2]=as.double(data[,2])
    googData[,1]=googData[,1]-googData[1,1]
    regGoog=TimeSeriesRegularization_C(googData)
    if (isOutput==TRUE) write.table(regGoog,'regularizedPriceData.csv',sep=',',row.names=F,col.names=F)
    return (regGoog)
}

