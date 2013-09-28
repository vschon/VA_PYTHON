#include <R.h> 
#include <cmath>
#include <iostream>

using namespace std;
extern "C" {

void R11MatrixCalculation(double *R11,int *_N,double *_beta_1,double *t1){
  int N=*_N;
  double beta_1=*_beta_1;
  
  R11[0]=0;
  
  for(int i=1;i<N;i++){
    R11[i]=(1+R11[i-1])*exp(-beta_1*(t1[i]-t1[i-1]));  
  }
}

void R12MatrixCalculation(double *R12,int *_N,int *_M,double *_beta_1,double *t1,double *t2){
  double beta_1=*_beta_1;
  int N=*_N;
  int M=*_M;
    

  R12[0]=0.0;
  
  double temp_sum=0.0;

  //fill the R matrix
  for(int i=1;i<N;i++){
    temp_sum=0;
    for(int j=0;j<M;j++){
      if(t2[j]>=t1[i]){break;}
      if((t2[j]>=t1[i-1])&&(t2[j]<t1[i])){
        temp_sum=temp_sum+exp(-beta_1*(t1[i]-t2[j]));
        }
    }

    R12[i]=R12[i-1]*exp(-beta_1*(t1[i]-t1[i-1]))+temp_sum;
  } 
}

void R21MatrixCalculation(double *R21,int *_N,int *_M,double *_beta_2,double *t1,double *t2){
  
  double beta_2=*_beta_2;
  int N=*_N;
  int M=*_M;

  R21[0]=0.0;
  
  double temp_sum=0.0;

  //fill the R matrix
  for(int j=1;j<M;j++){
    temp_sum=0.0;
    for(int i=0;i<N;i++){
      if(t1[i]>=t2[j]){break;}
      if(t1[i]>=t2[j-1]&&t1[i]<t2[j]){
        temp_sum=temp_sum+exp(-beta_2*(t2[j]-t1[i]));}
    }
    R21[j]=R21[j-1]*exp(-beta_2*(t2[j]-t2[j-1]))+temp_sum;
  } 
}

void R22MatrixCalculation(double *R22,int *_M,double *_beta_2,double *t2){
  int M=*_M;
  double beta_2=*_beta_2;
  
  R22[0]=0;
  
  for(int j=1;j<M;j++){
    R22[j]=(1+R22[j-1])*exp(-beta_2*(t2[j]-t2[j-1]));  
  }
}

}
