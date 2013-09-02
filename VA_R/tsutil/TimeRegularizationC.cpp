#include <R.h> 
#include <cmath>
#include <iostream>

using namespace std;
extern "C" {
void TimeRegularizationC(int* regularTimeSeriesLength_,int* n_,double* irregularTimeSeries,double* regularTimeSeries){
  int n=*n_;//row number of irregular time series
  int regularTimeSeriesLength=*regularTimeSeriesLength_; //row number of regular time series 
  
    for(int i=0;i<regularTimeSeriesLength;i++){
        if(irregularTimeSeries[n-1]>=regularTimeSeries[i]){
            for(int j=0;j<n;j++){
                if(irregularTimeSeries[j]==regularTimeSeries[i]){
                    regularTimeSeries[i+regularTimeSeriesLength]=irregularTimeSeries[j+n];
                    break;
                }
                if(irregularTimeSeries[j]>regularTimeSeries[i]){
                    regularTimeSeries[i+regularTimeSeriesLength]=irregularTimeSeries[j-1+n];    
                    break;
                }
            }    
        }
        else{
            for(int j=i+regularTimeSeriesLength;j<2*regularTimeSeriesLength;j++){
              regularTimeSeries[j]=irregularTimeSeries[2*n-1];
            }
          break;
        }
    }
}


}