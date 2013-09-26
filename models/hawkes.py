import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
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
        self.beta = np.array(theta[6:10]).reshape(2,2)

    def setparam(self,theta):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:10]).reshape(2,2)

    def rate(self,time,prev_index,data):
        '''
        Calculate the rate at time t
        '''
        ratevalue = np.zeros((2,1))
        if(prev_index<0):
            ratevalue = self.mu
        else:
            ratevalue[0,0] = self.mu[0,0] + (data[prev_index,2] - self.mu[0,0])/np.exp(time - data[prev_index,0])
            ratevalue[1,0] = self.mu[1,0] + (data[prev_index,3] - self.mu[1,0])/np.exp(time - data[prev_index,0])
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
            return price
        else:
            price = np2df(data[-dataNum:,:2],anchor)
            return price





















class learner:
    pass

class predictor:
    pass

class hawkes:
    '''
    hawkes class for learning and preditction
    '''

    def __init__(self,raw_):
        self.raw = raw_
        self.alpha = np.zeros((2,2))
        self.beta = np.ones((2,2))
        self.mu = np.ones((2,1))
        self.data = self.preprocess(self.raw)
        self.dataNum = self.data.shape[0]
        self.rateCalculated = False


    def delta2second(self,delta):
        '''
        convert a timedelta to float number (in seconds)
        '''
        return delta.total_seconds()

    def preprocess(self,raw):
        '''
        transform raw dataframe to numpy representation
        output:
            3D ndarray with col time(begin with 0), price mark, rate
        '''
        #transform time to seconds beginning at t=0
        value = raw.values
        n = value.shape[0]-1
        newValue = np.zeros((n,4))
        Vdelta2second = np.vectorize(self.delta2second)
        newValue[:,0] = Vdelta2second(value[:,0] - value[0,0])[1:]
        newValue[:,1] = np.sign(np.diff(value[:,1]))
        #remove items with no price change
        return newValue[newValue[:,1] != 0]

    def simulation(self):
        pass
