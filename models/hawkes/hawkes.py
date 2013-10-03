import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
from scipy.optimize import minimize
import getR
import os
import VD_KDB as vd
import VA_PYTHON as va
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
    #ipdb.set_trace()
    #transform time to seconds beginning at t=0
    value = raw.values
    anchor = value[-1]

    # get index of entires with no price change
    index = np.where((value[1:,1]==value[0:-1,1])==True)
    value = np.delete(value,index,0)
    n = value.shape[0] - 1
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
    return pd.DataFrame(value,columns=['time','quantity'])


class simulator:

    def __init__(self,theta=(0.5,0.5,0.5,0.5,0.5,0.5,1,1),scale = 0.001):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)
        self.scale = scale
        self.history = pd.DataFrame()
        self.rateCalculated = False
        self.historydata = None
        self.anchor = None

    def setparam(self,theta,scale):
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:]).reshape(2,1)
        self.scale = scale

    def sethistory(self,history = pd.DataFrame()):
        #ipdb.set_trace()
        self.history = history
        if self.history.shape[0] != 0:
            self.historydata,self.anchor = df2np(self.history)
            self.historydata = self.historyrate(self.historydata)

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
        self.rateCalculated = True
        return data

    def simulate(self,dataNum=10):
        if self.history.shape[0] == 0:
            totalIndex = -1
            subIndex1 =0
            subIndex2 =0
            maxIntensity = np.sum(self.mu)
            self.anchor = np.array([datetime.now(),0.0])
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
            totalIndex = self.historydata.shape[0]-1
            subIndex1 = sum(self.historydata[:,1] == 1.0)
            subIndex2 = sum(self.historydata[:,1] == -1.0)

            data = np.append(self.historydata,np.zeros((dataNum,4)),axis=0)
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
        if self.history.shape[0] == 0:
            price = np2df(data,self.anchor,self.scale)
            return price,data
        else:
            price = np2df(data[-dataNum:,:2],self.anchor,self.scale)
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


def likelihood(theta,data,modelType):
    '''
    Calculate the likelihood of hawkes model given theta and data
    data is the np decomposed representation of data
    '''

    if modelType == '6':
        mu = np.array(theta[:2]).reshape(2,1)
        alpha = np.array(theta[2:6]).reshape(2,2)
    if modelType == '4':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([theta[2],theta[3],theta[3],theta[2]]).reshape(2,2)
    if modelType == '2cross':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([0.0,theta[3],theta[3],0.0]).reshape(2,2)
    #Fix beta to be [1,1,1,1]
    beta = np.ones((2,1))
    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR.getR11(N,beta[0,0],pos)
    R12 = getR.getR12(N,M,beta[0,0],pos,neg)
    R21 = getR.getR21(N,M,beta[1,0],pos,neg)
    R22 = getR.getR22(M,beta[1,0],neg)

    L1 = -mu[0,0]*T -(alpha[0,0]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-pos))) -\
            (alpha[0,1]/beta[0,0])*np.sum(1-np.exp(-beta[0,0]*(T-neg))) +\
            np.sum(np.log(mu[0,0]+alpha[0,0]*R11[1:]+alpha[0,1]*R12[1:]))

    L2 = -mu[1,0]*T -(alpha[1,0]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-pos))) -\
            (alpha[1,1]/beta[1,0])*np.sum(1-np.exp(-beta[1,0]*(T-neg))) +\
            np.sum(np.log(mu[1,0]+alpha[1,0]*R21[1:]+alpha[1,1]*R22[1:]))

    return -L1-L2


def gradient(theta,data,modelType):

    if modelType == '6':
        mu = np.array(theta[:2]).reshape(2,1)
        alpha = np.array(theta[2:6]).reshape(2,2)
    if modelType == '4':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([theta[2],theta[3],theta[3],theta[2]]).reshape(2,2)
    if modelType == '2cross':
        mu = np.array([theta[0],theta[0]]).reshape(2,1)
        alpha = np.array([0.0,theta[3],theta[3],0.0]).reshape(2,2)

    beta = np.ones((2,1))

    pos = data[data[:,1] == 1.0,0].reshape(-1,1)
    neg = data[data[:,1] == -1.0,0].reshape(-1,1)
    pos = pos.astype(float,copy=False)
    neg = neg.astype(float,copy=False)
    N = pos.shape[0]
    M = neg.shape[0]
    T = data[-1,0]

    R11 = getR.getR11(N,beta[0,0],pos)
    R12 = getR.getR12(N,M,beta[0,0],pos,neg)
    R21 = getR.getR21(N,M,beta[1,0],pos,neg)
    R22 = getR.getR22(M,beta[1,0],neg)

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


def learn(price,theta=(0.5,0.5,0.25,0.25,0.25,0.25),modelType = '6'):
    '''
    Learn the params using mle
    '''
    data,anchor = df2np(price)
    data[:,0] = np.cumsum(data[:,0])
    theta = np.array(theta)
    constraint = [(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1),(0.00001,1)]

    #learn scale
    temp  = np.diff(price.values[:,1])
    scale = np.mean(np.abs(temp[temp!=0]))
    #learn params
    args = (data,modelType)
    output = minimize(fun=likelihood,x0=theta,jac=gradient,bounds=constraint,args=args,method='L-BFGS-B')
    params = output['x']

    if modelType == '4':
        params[1] = params[0]
        params[4] = params[3]
        params[5] = params[2]
    if modelType == '2cross':
        params[1] = params[0]
        params[2] = 0.0
        params[5] = 0.0
        params[4] = params[3]

    result = {'scale':scale,'params':params,'output':output}
    return result

class predictor:
    '''
    hawkes predictor class for learning and preditction
    '''

    def __init__(self,history_,theta = np.array([]), scale = 0.001,modelType = '6'):
        self.history = history_
        self.fitted = False
        self.scale = scale
        self.modelType = modelType
        if theta.shape[0] != 0:
            self.params = np.array(theta)
            self.fitted = True

    def setparam(self,theta,scale):
        self.params = np.array(theta)
        self.scale = scale
        self.fitted = True

    def changeHistory(self,history_):
        self.history = history_

    def predict(self,refit=False,ahead = 1,density=30,mcNum = 500,modelType = '6'):
        if refit == True or self.fitted == False:
            self.modelType = modelType
            result =learn(self.history,modelType = self.modelType )
            params = result['params']
            scale = result['scale']
            self.setparam(params,scale)
        theta = np.append(self.params,np.ones(2))
        targetTime = self.history.values[-1,0] + timedelta(0,ahead)

        sim = simulator(theta = theta,scale = self.scale)
        sim.sethistory(self.history)
        priceforecast = 0.0
        for i in range(mcNum):
            predictionSeries = sim.simulate(dataNum= (ahead*density))[0]
            predictionSeries = pd.concat([self.history.tail(2),predictionSeries])
            predictionSeries.index = predictionSeries['time']
            forecastIndex = predictionSeries.index.searchsorted(targetTime) - 1
            priceforecast += predictionSeries.values[forecastIndex,1]
        priceforecast /= mcNum
        output = pd.DataFrame({'time':[targetTime],'quantity':[priceforecast]},columns = ['time','quantity'])
        return output


class forex_backtestor:

    def __init__(self,qconn):
        self.qconn = qconn
        self.price = pd.DataFrame()
        self.trainBegin = None
        self.trainEnd = None
        self.testBegin = None
        self.testEnd = None
        self.train = pd.DataFrame()
        self.test = pd.DataFrame()
        self.symbol = None
        self.date = None
        self.ahead = 1
        self.window = timedelta(0,300)

        self.scale = 0.0
        self.params = None

    def summary(self):
        print 'SYMBOL: ' + self.symbol
        print 'Training Set: ' + str(self.trainBegin) + ' to ' + str(self.trainEnd)
        print 'Testing Set: ' + str(self.testBegin) + ' to ' + str(self.testEnd)
        print 'Moving window: ' + str(self.window)

    def setqconn(self, qconn):
        self.qconn =  qconn

    def fetch(self,date,symbol):
        command = 'select time,quantity:bid from forex_quote where date= ' + date +',symbol = `' + symbol.upper()
        self.symbol = symbol
        self.price = vd.pyapi.qtable2df(self.qconn.k(command))
        self.price.index = self.price['time']
        return self.price

    def split(self,trainBegin,trainEnd,testBegin,testEnd,timewindow):
        self.trainBegin = parse(trainBegin)
        self.trainEnd= parse(trainEnd)
        self.window = timedelta(0,timewindow)
        self.testBegin = parse(testBegin)
        self.testEnd = parse(testEnd)
        self.train = self.price[self.trainBegin:self.trainEnd]
        self.test = self.price[self.testBegin:self.testEnd]

    def backtest(self,args = {},params = {}):
        '''
        args:
            date - date for backtest
            symbol - symbol for backtest
            trainBegin,trainEnd,testBegin,testEnd - string, range of training and testing set
            window - time window of hisotry to make prediction
            ahead - seconds looking ahead
        '''

        if len(args) != 0:
            self.fetch(args['date'],args['symbol'])
            self.split(args['trainBegin'],args['trainEnd'],args['testBegin'],args['testEnd'],args['window'])
            self.ahead = args['ahead']

        if len(params) == 0:
            result = learn(self.train)
            self.scale = result['scale']
            self.params = result['params']['x']
        else:
            self.scale = params['scale']
            self.params = params['params']

        backtest_result = {'true':np.zeros((self.test.shape[0],1)),'predict':np.zeros((self.test.shape[0],1))}

        p = predictor(history_ = None, theta = self.params)
        count = 0
        for i,row in self.test['time'].iteritems():
            historyEnd = row.to_datetime()
            historyBegin = historyEnd -  self.window
            history = self.price[historyBegin:historyEnd]
            targetTime = historyEnd + timedelta(0,self.ahead)

            p.changeHistory(history)

            prediction = p.predict(ahead = self.ahead)
            predict_change = prediction.values[0,1] - self.price.ix[historyEnd,'quantity']

            historyEndIndex = self.price.index.searchsorted(historyEnd)
            nextTime = self.price.ix[historyEndIndex+1]['time']

            if nextTime > targetTime:
                #if no tick change within prediction period, use the next tick change as the true value
                truevalue = self.price.ix[nextTime.to_datetime(),'quantity']
            else:
                #if there is tick change, use the last one as true price
                targetTimeIndex = self.price.index.searchsorted(targetTime)
                truevalue = self.price.ix[targetTimeIndex-1,'quantity']

            true_change = truevalue - self.price.ix[historyEnd,'quantity']
            #ipdb.set_trace()
            backtest_result['true'][count,0] = true_change
            backtest_result['predict'][count,0] = predict_change
            count += 1
            print true_change,predict_change

        return backtest_result

def hawkesfeat(timeseries,args):
    '''
    Generate hawkes feature: positive rate/negtive rate
    args['params']: 1X8 ndarray containing the params of hawkes process
    '''

    #Assign parameters
    params = args['params'] if 'params' in args.keys() else np.array([0.2,0.2, 0.2, 0.7, 0.7, 0.2, 1.0, 1.0])

    #Utilize the rate calculation function in the hawkes simulator
    sim = simulator(theta = params)
    sim.sethistory(timeseries)


    rate = sim.historydata[:,2]/sim.historydata[:,3]
    rate = np.insert(rate,0,params[0]/params[1]).reshape(-1,1)
    time = np.insert(sim.historydata[:,0],0,0.0).reshape(-1,1)
    time = np.cumsum(time,axis=0)

    value = np.hstack((time,rate))
    value = value.astype(object,copy=False)
    value[:,0] = Vsecond2delta(value[:,0])

    anchor = timeseries.values[0]
    anchor[1] = 0.0
    value = value + anchor

    rateseries = pd.DataFrame(value,columns=['time','quantity'])
    rateseries.index = rateseries['time']
    rateseries = rateseries.reindex(timeseries.index,method = 'ffill')

    return rateseries
