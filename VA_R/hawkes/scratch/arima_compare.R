library(forecast)

#option 1: Directly operate on price data
#transfer the trainingset into regular time series
regular_trainingset=array(0,c(301,1));
n=dim(trainingset)[1];
count=0;
for(i in 0:300)
{
    for(j in 1:n)
    {
        if(trainingset[j,1]==i)
        {
            regular_trainingset[i+1,1]=trainingset[j,2];
            break;
        }
        if(trainingset[j,1]>i)
        {
            regular_trainingset[i+1,1]=trainingset[j-1,2];
            break;
        }
    }
}
regular_trainingset[301,1]=trainingset[n,2];
ts_reg_traingset=ts(regular_trainingset,start=1,end=301)

#fit arima model to the regular training set
fit=auto.arima(ts_reg_traingset)
plot(forecast(fit,h=300))

