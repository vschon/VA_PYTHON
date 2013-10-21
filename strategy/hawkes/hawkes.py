import numpy as np
import pandas as pd
import VA_PYTHON as va
import VD_KDB as vd
import datetime as dt
from collections import defaultdict

import ipdb

class hawkesTrader():
    '''
    object to implement hawkes trading strategy
    '''

    def __init__(self):
        #self.data used to store chrononically the time series data
        #time,price,mark,pos rate,neg rate, ratio
        self.data = np.zeros((150000,6),dtype = 'object')

        #store the legal filter for each mode
        self.legalsimfilter = None
        self.legalrealfilter = None
        self.initializelegalfilter()

        #self.currentTime only used to store the currenttime passed from a simulator
        self.currentTime = None

        #set the time
        self.timer = None

        #set the filter used to filter incoming data, one for each data source
        self.filter = None

        #the index of last occupied item in seld.data
        self.n = 0

        #parameters of hawkes parameters
        self.alpha = np.array([0.1,0.6,0.6,0.1]).reshape(2,2)
        self.mu = np.ones((2,1)) * 0.5
        self.beta = np.ones((2,1))
        self.threshold = 2

    def initializelegalfilter(self):

        '''
        set the legal filter for sim and real mode
        To be extened
        '''

        self.legalsimfilter = {'forexquote':self.filter_forexquote}
        self.legalrealfilter = {}

    def simTimer(self):
        '''
        timer used in simulation mode
        '''

        return self.currentTime

    def setMode(self,mode,filter):
        '''set the mode of trader
        set the corresponding data filter
        sim - simulation mode
        real - real trading mode

        set the filter used to receive data

        set the data
        '''

        if mode == 'sim':
            self.timer = self.simTimer
            if filter in self.legalsimfilter.keys():
                self.filter = self.legalsimfilter[filter]
        elif mode == 'real':
            self.timer = dt.datetime.now
            if filter in self.legalrealfitler.keys():
                self.filter = self.legalrealfilter[filter]

    def setparams(self,theta):
        '''
        set the parameters of hawkes process
        theta: 8 items tuple,array
        '''
        self.mu = np.array(theta[:2]).reshape(2,1)
        self.alpha = np.array(theta[2:6]).reshape(2,2)
        self.beta = np.array(theta[6:8]).reshape(2,1)

    def setthreshold(self,k):
        if k>1:
            self.threshold = k
        else:
            print 'K should be larger than 1'

    def filter_forexquote(self,sender,event,msg=None):
        '''
        filter is independet of the strategy core

        filter for simulator
        listener to be registered to simulator
        process incoming data to be analyzed later by the trader

        sent filtered data to core function

        incoming data type
            time
            symbol
            bid
            ask
        '''

        #ipdb.set_trace()
        self.currentTime = msg['time']
        point = msg['data']

        time = point['time']
        price = (point['bid'] + point['ask'])/2.0

        #pass the point to strategy core
        self.core(np.array([time,price],dtype='object'))


    def send_order(self):
        pass

    def core(self,point):
        '''
        core algorithm to trade
        point data:
            1x6 np.array with field time(nptime),price(float)
        '''
        #ipdb.set_trace()

        if self.n == 0:
            #update time and price
            self.data[self.n,:2] = point

            #update pos/neg rate
            self.data[self.n,3:5] = self.mu.reshape(2)

            #update ratio
            self.data[self.n,5] = self.data[self.n,3]/self.data[self.n,4]
            self.n += 1
            mark = 0
        else:
            #get time delta and mark
            delta = (point[0] - self.data[self.n-1,0]).total_seconds()
            mark = np.sign(point[1]-self.data[self.n-1,1])

            if mark == 1.0:
                #if price increases

                self.data[self.n,:2] = point
                self.data[self.n,2] = mark

                #update pos/neg rate
                self.data[self.n,3:5] = (self.data[self.n-1,3:5] - self.mu.reshape(2))/np.exp(self.beta.reshape(2)*delta) + self.mu.reshape(2) + self.alpha[:,0]

                #update ratio
                self.data[self.n,5] = self.data[self.n,3]/self.data[self.n,4]
                self.n += 1
            elif mark == -1.0:
                #if price decreases

                self.data[self.n,:2] = point
                self.data[self.n,2] = mark

                #update pos/neg rate
                self.data[self.n,3:5] = (self.data[self.n-1,3:5] - self.mu.reshape(2))/np.exp(self.beta.reshape(2)*delta) + self.mu.reshape(2) + self.alpha[:,1]

                #update ratio
                self.data[self.n,5] = self.data[self.n,3]/self.data[self.n,4]
                self.n += 1


            if mark != 0:
                if self.data[self.n-1,5] > self.threshold:
                    print self.data[self.n-1]
                    #self.sendorder('market buy')
                    #self.sendorder('market sell after 5 seonds')
                    print 'buy'
                elif self.data[self.n-1,5] < 1/self.threshold:
                    #print self.data[self.n-1]
                    #self.sendorder('market sell')
                    #self.sendorder('market buy after 5 seconds')
                    print 'sell'

