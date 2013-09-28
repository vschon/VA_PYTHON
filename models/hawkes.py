import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
from scipy.optimize import minimize
import ipdb

#utility function

def delta2second(delta):
    '''
    convert a timedelta to float number (in seconds)
    '''
    return delta.total_seconds()

Vdelta2second = np.vectorize(delta2second)

def second2delta(second):
    return timedelta(0,second)

Vsecond2delta = np.vectorize(second2delta)

def df2np(raw):
    '''
    transform raw dataframe to numpy representation
    output:
        ndarray with col time(begin with 0), price mark, rate +, rate -
    '''
    #transform time to seconds beginning at t=0
    value = raw.values
    n = value.shape[0]-1
    anchor = value[n]
    newValue = np.append(np.diff(value,axis=0),np.zeros((n,2)),axis = 1)
    newValue[:,0] = Vdelta2second(newValue[:,0])
    newValue[:,1] = np.sign(newValue[:,1])
    #remove items with no price change
    return (newValue[newValue[:,1] != 0],anchor)


def np2df(data,anchor,ticksize = 0.0001):
    '''
    convert to np representation to df price sequence
    '''
    value = np.cumsum(data[:,:2],axis=0)
    value = value.astype(object,copy=False)
    value[:,0] = Vsecond2delta(value[:,0])
    value[:,1] = value[:,1] * ticksize
    value = value + anchor
    return pd.DataFrame(value,columns=['time','price'])


class simulator:
    def __init__(self,theta):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)

    def setparam(self,theta):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)

    def rate(self,time,prev_index,data):
        '''
        Calculate the rate at time t
        '''
        ratevalue = np.zeros((2,1))
        if(prev_index<0):
            ratevalue = self.mu
        else:
            ratevalue[0,0] = self.mu[0,0] + (data[prev_index,2] - self.mu[0,0])/np.exp(self.beta[0,0]*time)
            ratevalue[1,0] = self.mu[1,0] + (data[prev_index,3] - self.mu[1,0])/np.exp(self.beta[1,0]*time)
        return ratevalue

    def historyrate(self,data):
        '''
        Calculate the historic rate
        '''
        dataNum = data.shape[0]
        for i in range(dataNum):
            ratevalue = self.rate(data[i,0],i-1,data)
            if data[i,1] == 1.0:
                data[i,2:4] = (ratevalue + self.alpha[:,0].reshape(2,1)).reshape(2)
            else:
                data[i,2:4] = (ratevalue + self.alpha[:,1].reshape(2,1)).reshape(2)
        return data


    def simulate(self,dataNum=10,history=pd.DataFrame()):
        if history.shape[0] == 0:
            totalIndex = -1
            subIndex1 =0
            subIndex2 =0
            maxIntensity = np.sum(self.mu)
            anchor = np.array([datetime.now(),0.0])
            #first event
            s = np.random.exponential(1/maxIntensity)
            data = np.zeros((dataNum,4))
            # attribution test
            randomD = np.random.uniform()
            if randomD<=self.mu[0,0]/maxIntensity:
                data[0,0] = s
                data[0,1] = 1.0
                data[0,2:4] = (self.mu + self.alpha[:,0].reshape(2,1)).reshape(2)
                subIndex1+=1
                totalIndex+=1
            else:
                data[0,0] = s
                data[0,1] = -1.0
                data[0,2:4] = (self.mu + self.alpha[:,1].reshape(2,1)).reshape(2)
                subIndex2+=1
                totalIndex+=1
            endIndex = dataNum
        else:
            #if history is provided, continue simulation after history
            historydata,anchor = df2np(history)
            historydata = self.historyrate(historydata)
            totalIndex = historydata.shape[0]-1
            subIndex1 = sum(historydata[:,1] == 1.0)
            subIndex2 = sum(historydata[:,1] == -1.0)

            data = np.append(historydata,np.zeros((dataNum,4)),axis=0)

            #s = data[totalIndex,0]
            endIndex = dataNum + totalIndex + 1

        #general routine
        for i in range((totalIndex+1),endIndex):
            ratevalue = self.rate(data[totalIndex,0],totalIndex,data)
            maxIntensity = np.sum(ratevalue)
            cum_s = 0.0
            while(True):
                s = np.random.exponential(1/maxIntensity) + cum_s
                ratevalue = self.rate(s,totalIndex,data)
                intensity_s = np.sum(ratevalue)
                randomD = np.random.uniform()

                if randomD <= intensity_s/maxIntensity:
                    totalIndex+=1
                    data[totalIndex,0] = s
                    if randomD <= ratevalue[0,0]/maxIntensity:
                        subIndex1 += 1
                        data[totalIndex,1] = 1.0
                        data[totalIndex,2:4] = (ratevalue + self.alpha[:,0].reshape(2,1)).reshape(2)
                    else:
                        subIndex2+=1
                        data[totalIndex,1] = -1.0
                        data[totalIndex,2:4] = (ratevalue + self.alpha[:,1].reshape(2,1)).reshape(2)
                    break
                else:
                    maxIntensity = intensity_s
                    cum_s += s
        if history.shape[0] == 0:
            price = np2df(data,anchor)
            return price,data
        else:
            price = np2df(data[-dataNum:,:2],anchor)
            return price,data

def getR11(N,beta1,pos):
    R11 = np.zeros((N,1))
    for i in range(1,N):
        R11[i,0] = (1+R11[i-1,0])*np.exp(-beta1*(pos[i,0]-pos[i-1,0]))
    return R11

def getR12(N,M,beta1,pos,neg):
    R12 = np.zeros((N,1))
    for i in range(1,N):
        tempsum=0.0
        for j in range(M):
            if neg[j,0] >= pos[i,0]:
                break
            if neg[j,0] >= pos[i-1,0] and neg[j,0] < pos[i,0]:
                tempsum += np.exp(-beta1*(pos[i,0] - neg[j,0]))
        R12[i,0] = R12[i-1,0]*np.exp(-beta1*(pos[i,0]-pos[i-1,0])) + tempsum
    return R12

def getR21(N,M,beta2,pos,neg):
    R21 = np.zeros((M,1))

    for j in range(1,M):
        tempsum=0.0
        for i in range(N):
            if pos[i,0] > neg[j,0]:
                break
            if pos[i,0] >= neg[j-1,0] and pos[i,0] < neg[j,0]:
                tempsum += np.exp(-beta2*(neg[j,0]-pos[i,0]))
        R21[j,0] = R21[j-1,0]*np.exp(-beta2*(neg[j,0]-neg[j-1,0])) + tempsum
    return R21

def getR22(M,beta2,neg):
    R22 = np.zeros((M,1))
    for j in range(1,M):
        R22[j,0] = (1+R22[j-1,0])*np.exp(-beta2*(neg[j,0]-neg[j-1,0]))
    return R22


def likelihood(theta,data):
    '''
    Calculate the likelihood of hawkes model given theta and data
    data is the np decomposed representation of data
    '''
    print theta
    mu = np.array(theta[:2]).reshape(2,1)
    alpha = np.array(theta[2:6]).reshape(2,2)
    #Fix beta to be [1,1,1,1]
    beta = np.ones((2,1))
    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR11(N,beta[0,0],pos)
    R12 = getR12(N,M,beta[0,0],pos,neg)
    R21 = getR21(N,M,beta[1,0],pos,neg)
    R22 = getR22(M,beta[1,0],neg)


    L1 = -mu[0,0]*T -(alpha[0,0]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-pos))) -\
            (alpha[0,1]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-neg))) +\
            np.sum(np.log(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    L2 = -mu[1,0]*T -(alpha[1,0]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-pos))) -\
            (alpha[1,1]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-neg))) +\
            np.sum(np.log(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    print (-L1-L2)
    return -L1-L2

def gradient(theta,data):

    mu = np.array(theta[:2]).reshape(2,1)
    alpha = np.array(theta[2:6]).reshape(2,2)
    beta = np.ones((2,1))

    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR11(N,beta[0,0],pos)
    R12 = getR12(N,M,beta[0,0],pos,neg)
    R21 = getR21(N,M,beta[1,0],pos,neg)
    R22 = getR22(M,beta[1,0],neg)

    gmu1 = -T + np.sum(1/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))
    gmu2 = -T + np.sum(1/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    galpha11 = -np.sum(1-np.exp(-beta[0,0]*(T-pos)))/beta[0,0] + \
            np.sum(R11[1:]/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    galpha12 = -np.sum(1-np.exp(-beta[0,0]*(T-neg)))/beta[0,0] + \
            np.sum(R12[1:]/(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    galpha21 = -np.sum(1-np.exp(-beta[1,0]*(T-pos)))/beta[1,0] + \
            np.sum(R21[1:]/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    galpha22 = -np.sum(1-np.exp(-beta[1,0]*(T-neg)))/beta[1,0] + \
            np.sum(R22[1:]/(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    return -np.array([gmu1,gmu2,galpha11,galpha12,galpha21,galpha22])

def learn(price,theta=(0.5,0.5,0.25,0.25,0.25,0.25)):
    '''
    Learn the params using mle
    '''
    data,anchor = df2np(price)
    data[:,0] = np.cumsum(data[:,0])
    theta = np.array(theta)
    constraint = [(0.0001,1),(0.0001,1),(0.0001,1),(0.0001,1),(0.0001,1),(0.0001,1)]

    return minimize(fun=likelihood,x0=theta,jac=gradient,bounds=constraint,args=(data,),method='L-BFGS-B')


class predictor:
    '''
    hawkes predictor class for learning and preditction
    '''

    def __init__(self,history_,theta=()):
        self.history = history_
        self.fitted = False
        if len(theta) != 0:
            self.params = np.array(theta)
            self.fitted = True

    def setparam(self,theta):
        self.params = np.array(theta)
        self.fitted = True

    def predict(self,refit=False,ahead = 1,density=10,mcNum = 500):
        if refit == True or self.fitted == False:
            params =learn(self.history).values()[4]
            self.setparam(params)
        theta = np.append(self.params,np.ones(2))
        targetTime = self.history.values[-1,0] + timedelta(0,ahead)

        sim = simulator(theta = theta)
        priceforecast = 0.0
        for i in range(mcNum):
            predictionSeries = sim.simulate(dataNum=10,history = self.history)[0]
            predictionSeries = pd.concat([self.history.tail(2),predictionSeries])
            predictionSeries.index = predictionSeries['time']
            forecastIndex = predictionSeries.index.searchsorted(targetTime) - 1
            priceforecast += predictionSeries.values[forecastIndex,1]
        priceforecast /= mcNum
        output = pd.DataFrame({'time':[targetTime],'price':[priceforecast]},columns = ['time','price'])
        #output.index = output['time']
        return output











