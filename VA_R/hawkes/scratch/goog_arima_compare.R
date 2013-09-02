library(forecast)

#option 1: Directly operate on price data
#transfer the trainingset into regular time series
goog_regular_trainingset=array(0,c(901,1));
n=dim(goog_trainingset)[1];
count=0;
for(i in 0:900)
{
    for(j in 1:n)
    {
        if(goog_trainingset[j,1]==i)
        {
            goog_regular_trainingset[i+1,1]=goog_trainingset[j,2];
            break;
        }
        if(goog_trainingset[j,1]>i)
        {
            goog_regular_trainingset[i+1,1]=goog_trainingset[j-1,2];
            break;
        }
    }
}
goog_regular_trainingset[901,1]=goog_trainingset[n,2];
goog_ts_reg_traingset=ts(goog_regular_trainingset,start=1,end=901)

#fit arima model to the regular training set
goog_fit=auto.arima(goog_ts_reg_traingset)
plot(forecast(goog_fit,h=300))
